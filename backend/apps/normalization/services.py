"""
Normalization services for data transformation
Converts raw data from different sources into standardized ActivityRecord format
"""
from decimal import Decimal
from datetime import datetime
from apps.normalization.models import ActivityRecord, AuditLog
import re


def normalize_sap_record(raw_record, ingestion_job):
    """
    Normalize SAP fuel and procurement data
    Expects columns: Amount, Quantity, Unit, Plant Code, Date, Material Code, Description
    """
    try:
        raw_data = raw_record.raw_data
        
        # Map common SAP column variations
        quantity = extract_numeric(raw_data.get('Menge') or raw_data.get('Quantity') or raw_data.get('Qty'))
        unit = (raw_data.get('Unit') or raw_data.get('Einheit') or '').upper()
        
        # Normalize units
        unit = normalize_unit(unit)
        if not quantity or not unit:
            raise ValueError("Missing quantity or unit")
        
        # Parse date - handle various formats
        date_str = raw_data.get('Date') or raw_data.get('Datum') or ''
        activity_date = parse_date(date_str)
        
        # Determine scope and activity type based on material code
        material_code = raw_data.get('Material Code') or ''
        scope, activity_type = classify_sap_record(
            raw_data.get('Description', ''),
            material_code,
            'sap_fuel' if 'fuel' in ingestion_job.data_source.source_type else 'sap_procurement'
        )
        
        # Create activity record
        activity = ActivityRecord.objects.create(
            company=raw_record.company,
            raw_record=raw_record,
            ingestion_job=ingestion_job,
            source_system='sap',
            activity_type=activity_type,
            scope=scope,
            quantity=Decimal(str(quantity)),
            unit=unit,
            activity_date=activity_date,
            category=raw_data.get('Plant Code', 'Unknown'),
            original_data=raw_data,
            confidence_score=Decimal('0.95')
        )
        
        return activity
    
    except Exception as e:
        raw_record.error_message = str(e)
        raise


def normalize_utility_record(raw_record, ingestion_job):
    """
    Normalize utility electricity data (CSV export from portal)
    Expects columns: Meter ID, Start Date, End Date, kWh, Tariff Type, Cost
    """
    try:
        raw_data = raw_record.raw_data
        
        # Extract consumption
        quantity = extract_numeric(
            raw_data.get('kWh') or raw_data.get('Consumption') or raw_data.get('Usage')
        )
        if not quantity:
            raise ValueError("Missing consumption data")
        
        unit = 'kWh'
        
        # Parse billing period
        start_date = parse_date(raw_data.get('Start Date') or raw_data.get('Billing Start'))
        end_date = parse_date(raw_data.get('End Date') or raw_data.get('Billing End'))
        
        if not start_date or not end_date:
            raise ValueError("Missing billing dates")
        
        # Meter metadata
        meter_id = raw_data.get('Meter ID') or raw_data.get('Meter')
        tariff_type = raw_data.get('Tariff Type') or 'Standard'
        
        activity = ActivityRecord.objects.create(
            company=raw_record.company,
            raw_record=raw_record,
            ingestion_job=ingestion_job,
            source_system='utility',
            activity_type='electricity_purchased',
            scope='scope_2',
            quantity=Decimal(str(quantity)),
            unit=unit,
            activity_date=start_date,
            billing_start_date=start_date,
            billing_end_date=end_date,
            category=meter_id or 'Unknown',
            subcategory=tariff_type,
            original_data=raw_data,
            confidence_score=Decimal('0.98')
        )
        
        return activity
    
    except Exception as e:
        raw_record.error_message = str(e)
        raise


def normalize_travel_record(raw_record, ingestion_job):
    """
    Normalize corporate travel data (flights, hotels, ground transport)
    Expects columns: Type, Origin, Destination, Distance, Cost, Date
    """
    try:
        raw_data = raw_record.raw_data
        
        # Determine travel type
        travel_type = raw_data.get('Type', '').lower()
        
        # Extract origin/destination
        origin = raw_data.get('Origin') or raw_data.get('Departure')
        destination = raw_data.get('Destination') or raw_data.get('Arrival')
        
        if not origin or not destination:
            raise ValueError("Missing origin or destination")
        
        # Get or estimate distance
        distance = extract_numeric(raw_data.get('Distance') or raw_data.get('Miles'))
        
        if not distance:
            # Estimate distance from airport codes
            distance = estimate_distance(origin, destination)
        
        if not distance:
            distance = 0
        
        # Parse date
        travel_date = parse_date(raw_data.get('Date') or raw_data.get('Travel Date'))
        
        # Classify
        activity_type, quantity_unit = classify_travel_record(travel_type)
        
        activity = ActivityRecord.objects.create(
            company=raw_record.company,
            raw_record=raw_record,
            ingestion_job=ingestion_job,
            source_system='travel',
            activity_type=activity_type,
            scope='scope_3',
            quantity=Decimal(str(distance if distance > 0 else 1)),
            unit='km' if distance > 0 else 'trip',
            activity_date=travel_date,
            origin=origin,
            destination=destination,
            distance=Decimal(str(distance)),
            category=travel_type.capitalize(),
            original_data=raw_data,
            confidence_score=Decimal('0.85') if distance == 0 else Decimal('0.95')
        )
        
        return activity
    
    except Exception as e:
        raw_record.error_message = str(e)
        raise


# Utility functions
def extract_numeric(value):
    """Extract numeric value from string"""
    if value is None or value == '':
        return None
    try:
        if isinstance(value, (int, float)):
            return value
        # Remove common thousand separators
        clean = str(value).replace(',', '').replace(' ', '')
        return float(clean)
    except:
        return None


def normalize_unit(unit):
    """Normalize various unit representations"""
    if not unit:
        return None
    
    unit_map = {
        'L': 'L', 'LITRE': 'L', 'LITER': 'L', 'LTR': 'L',
        'GAL': 'gal', 'GALLON': 'gal',
        'M3': 'm3', 'CBM': 'm3',
        'KWH': 'kWh', 'KWHS': 'kWh', 'KW_H': 'kWh',
        'KG': 'kg', 'KILOGRAM': 'kg',
        'TONNE': 'tonne', 'TON': 'tonne', 'MT': 'tonne'
    }
    
    normalized = unit_map.get(unit.upper())
    return normalized or unit


def parse_date(date_str):
    """Parse various date formats"""
    if not date_str:
        return None
    
    formats = [
        '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y',
        '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y',
        '%Y%m%d', '%d%m%Y',
        '%B %d, %Y', '%b %d, %Y',
        '%d %B %Y', '%d %b %Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except:
            continue
    
    # Default to today if parsing fails
    return datetime.now().date()


def classify_sap_record(description, material_code, source_type):
    """Classify SAP record into scope and activity type"""
    desc_lower = description.lower()
    code_lower = material_code.lower() if material_code else ''
    
    # Fuel classification
    if 'petrol' in desc_lower or 'gasoline' in desc_lower or 'diesel' in desc_lower:
        return 'scope_1', 'fuel_combustion'
    
    # Procurement classification
    if 'sap_procurement' in source_type or 'material' in desc_lower:
        return 'scope_3', 'procurement'
    
    # Default
    return 'scope_3', 'procurement'


def classify_travel_record(travel_type):
    """Classify travel into appropriate activity type"""
    type_lower = travel_type.lower()
    
    if 'flight' in type_lower or 'air' in type_lower or 'plane' in type_lower:
        return 'business_travel_flight', 'km'
    elif 'hotel' in type_lower or 'accommodation' in type_lower:
        return 'business_travel_hotel', 'night'
    elif 'taxi' in type_lower or 'car' in type_lower or 'ground' in type_lower or 'uber' in type_lower:
        return 'business_travel_ground', 'km'
    else:
        return 'business_travel_ground', 'km'


def estimate_distance(origin, destination):
    """
    Estimate distance between two cities/airports
    Simplified: returns rough estimates for common routes
    In production, would integrate with maps API
    """
    # Common airport codes and approximate distances
    # This is a simplified mock - in production use haversine or maps API
    distances = {
        ('DEL', 'BOM'): 1300,  # Delhi to Mumbai
        ('BOM', 'DEL'): 1300,
        ('DEL', 'BLR'): 2200,  # Delhi to Bangalore
        ('LAX', 'JFK'): 3950,  # LA to NYC
        ('LHR', 'CDG'): 215,   # London to Paris
    }
    
    key1 = (origin.upper(), destination.upper())
    key2 = (destination.upper(), origin.upper())
    
    return distances.get(key1) or distances.get(key2)
