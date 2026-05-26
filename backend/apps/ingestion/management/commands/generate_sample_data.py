"""
Management command to generate realistic sample data
"""
import csv
import io
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.tenants.models import Company
from apps.ingestion.models import DataSource, IngestionJob, RawRecord
from apps.normalization.services import normalize_sap_record, normalize_utility_record, normalize_travel_record


class Command(BaseCommand):
    help = 'Generate sample ESG data for testing'
    
    def handle(self, *args, **options):
        # Create test company
        company, created = Company.objects.get_or_create(
            name='Acme Corp',
            defaults={'slug': 'acme-corp', 'description': 'Test company for ESG data'}
        )
        
        # Create test user
        user, _ = User.objects.get_or_create(
            username='analyst',
            defaults={'email': 'analyst@acmecp.com', 'is_staff': True}
        )
        
        # Create data sources
        sap_fuel_source, _ = DataSource.objects.get_or_create(
            company=company,
            source_type='sap_fuel',
            defaults={'name': 'SAP Fuel Data'}
        )
        
        utility_source, _ = DataSource.objects.get_or_create(
            company=company,
            source_type='utility_electricity',
            defaults={'name': 'Utility Electricity Data'}
        )
        
        travel_source, _ = DataSource.objects.get_or_create(
            company=company,
            source_type='travel_flights',
            defaults={'name': 'Travel Data'}
        )
        
        # Generate SAP fuel sample data
        self.generate_sap_fuel_data(company, user, sap_fuel_source)
        
        # Generate utility data
        self.generate_utility_data(company, user, utility_source)
        
        # Generate travel data
        self.generate_travel_data(company, user, travel_source)
        
        self.stdout.write(self.style.SUCCESS('Sample data generated successfully'))
    
    def generate_sap_fuel_data(self, company, user, data_source):
        """Generate realistic SAP fuel export data"""
        rows = [
            {'Menge': '1200', 'Unit': 'L', 'Datum': '2024-01-15', 'Material Code': 'FUEL-001', 'Description': 'Diesel Fuel', 'Plant Code': 'PLANT-01'},
            {'Menge': '950', 'Unit': 'L', 'Datum': '2024-01-20', 'Material Code': 'FUEL-002', 'Description': 'Petrol', 'Plant Code': 'PLANT-01'},
            {'Menge': '2100', 'Unit': 'L', 'Datum': '2024-02-10', 'Material Code': 'FUEL-001', 'Description': 'Diesel Fuel', 'Plant Code': 'PLANT-02'},
            {'Menge': '850', 'Unit': 'L', 'Datum': '2024-02-15', 'Material Code': 'FUEL-002', 'Description': 'Petrol', 'Plant Code': 'PLANT-02'},
        ]
        
        job = IngestionJob.objects.create(
            company=company,
            data_source=data_source,
            uploaded_by=user,
            file_name='sap_fuel_2024.csv',
            file_path=f'uploads/sap_fuel_2024.csv',
            status='completed',
            total_rows=len(rows)
        )
        
        for row_num, row in enumerate(rows, 1):
            raw = RawRecord.objects.create(
                ingestion_job=job,
                company=company,
                source_type=data_source.source_type,
                raw_data=row,
                row_number=row_num,
                processing_status='normalized'
            )
            
            try:
                activity = normalize_sap_record(raw, job)
                job.processed_rows += 1
            except:
                raw.processing_status = 'failed'
                job.failed_rows += 1
            
            raw.save()
        
        job.save()
    
    def generate_utility_data(self, company, user, data_source):
        """Generate realistic utility electricity data"""
        base_date = datetime(2024, 1, 1).date()
        rows = []
        
        for month in range(1, 4):  # Jan, Feb, Mar
            start = base_date.replace(month=month)
            end = (start + timedelta(days=30)).replace(day=1) - timedelta(days=1)
            
            rows.append({
                'Meter ID': 'METER-001',
                'Start Date': start.isoformat(),
                'End Date': end.isoformat(),
                'kWh': str(4500 + (month * 200)),  # Seasonal variation
                'Tariff Type': 'Commercial',
                'Cost': '$1200'
            })
        
        job = IngestionJob.objects.create(
            company=company,
            data_source=data_source,
            uploaded_by=user,
            file_name='utility_electricity_2024.csv',
            file_path=f'uploads/utility_electricity_2024.csv',
            status='completed',
            total_rows=len(rows)
        )
        
        for row_num, row in enumerate(rows, 1):
            raw = RawRecord.objects.create(
                ingestion_job=job,
                company=company,
                source_type=data_source.source_type,
                raw_data=row,
                row_number=row_num,
                processing_status='normalized'
            )
            
            try:
                activity = normalize_utility_record(raw, job)
                job.processed_rows += 1
            except Exception as e:
                raw.error_message = str(e)
                raw.processing_status = 'failed'
                job.failed_rows += 1
            
            raw.save()
        
        job.save()
    
    def generate_travel_data(self, company, user, data_source):
        """Generate realistic travel data"""
        rows = [
            {'Type': 'Flight', 'Origin': 'DEL', 'Destination': 'BOM', 'Distance': '1300', 'Date': '2024-01-10', 'Cost': '$450'},
            {'Type': 'Flight', 'Origin': 'BOM', 'Destination': 'BLR', 'Distance': '2200', 'Date': '2024-01-15', 'Cost': '$380'},
            {'Type': 'Hotel', 'Origin': 'BOM', 'Destination': 'BOM', 'Distance': '', 'Date': '2024-01-10', 'Cost': '$200'},
            {'Type': 'Ground', 'Origin': 'BOM', 'Destination': 'BOM', 'Distance': '50', 'Date': '2024-01-10', 'Cost': '$35'},
            {'Type': 'Flight', 'Origin': 'DEL', 'Destination': 'BLR', 'Distance': '2200', 'Date': '2024-02-05', 'Cost': '$420'},
        ]
        
        job = IngestionJob.objects.create(
            company=company,
            data_source=data_source,
            uploaded_by=user,
            file_name='travel_2024.csv',
            file_path=f'uploads/travel_2024.csv',
            status='completed',
            total_rows=len(rows)
        )
        
        for row_num, row in enumerate(rows, 1):
            raw = RawRecord.objects.create(
                ingestion_job=job,
                company=company,
                source_type=data_source.source_type,
                raw_data=row,
                row_number=row_num,
                processing_status='normalized'
            )
            
            try:
                activity = normalize_travel_record(raw, job)
                job.processed_rows += 1
            except Exception as e:
                raw.error_message = str(e)
                raw.processing_status = 'failed'
                job.failed_rows += 1
            
            raw.save()
        
        job.save()
