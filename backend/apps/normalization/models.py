"""
Normalization models for storing processed, normalized emission data
"""
from django.db import models
from apps.tenants.models import Company
from apps.ingestion.models import RawRecord, IngestionJob


class ActivityRecord(models.Model):
    """Normalized emission activity record"""
    SCOPE_CHOICES = (
        ('scope_1', 'Scope 1 - Direct'),
        ('scope_2', 'Scope 2 - Indirect Energy'),
        ('scope_3', 'Scope 3 - Indirect Other'),
    )
    
    ACTIVITY_TYPES = (
        ('fuel_combustion', 'Fuel Combustion'),
        ('electricity_purchased', 'Purchased Electricity'),
        ('business_travel_flight', 'Business Travel - Flight'),
        ('business_travel_hotel', 'Business Travel - Hotel'),
        ('business_travel_ground', 'Business Travel - Ground Transport'),
        ('procurement', 'Procurement'),
    )
    
    STATUS_CHOICES = (
        ('pending_review', 'Pending Review'),
        ('flagged', 'Flagged for Review'),
        ('approved', 'Approved'),
        ('locked', 'Locked for Audit'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='activity_records')
    raw_record = models.OneToOneField(RawRecord, on_delete=models.CASCADE, related_name='activity_record', null=True, blank=True)
    ingestion_job = models.ForeignKey(IngestionJob, on_delete=models.CASCADE, related_name='activity_records')
    source_system = models.CharField(max_length=50)  # 'sap', 'utility', 'travel'
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    
    # Core metrics
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    unit = models.CharField(max_length=50)  # normalized to standard units
    
    # Timestamps
    activity_date = models.DateField()
    billing_start_date = models.DateField(null=True, blank=True)  # for utility data
    billing_end_date = models.DateField(null=True, blank=True)    # for utility data
    
    # Categorization
    category = models.CharField(max_length=100, blank=True)
    subcategory = models.CharField(max_length=100, blank=True)
    
    # For travel data
    origin = models.CharField(max_length=100, blank=True)
    destination = models.CharField(max_length=100, blank=True)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Data quality flags
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=255, blank=True)
    
    # Audit trail
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_review')
    approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_records')
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    original_data = models.JSONField()  # stores the mapped original values
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['company', 'scope']),
            models.Index(fields=['activity_date']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.get_activity_type_display()} ({self.status})"


class AuditLog(models.Model):
    """Audit trail for all changes to activity records"""
    ACTION_CHOICES = (
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('flagged', 'Flagged'),
        ('approved', 'Approved'),
        ('locked', 'Locked'),
    )
    
    activity_record = models.ForeignKey(ActivityRecord, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    changes = models.JSONField(default=dict)  # {field: [old_value, new_value]}
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.activity_record.id} - {self.action} - {self.created_at}"


class SuspiciousFlagRule(models.Model):
    """Rules for flagging suspicious data"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='suspicious_rules')
    activity_type = models.CharField(max_length=30, choices=ActivityRecord.ACTIVITY_TYPES)
    
    field_name = models.CharField(max_length=100)  # e.g., 'quantity'
    condition = models.CharField(
        max_length=20,
        choices=(('gt', 'Greater than'), ('lt', 'Less than'), ('eq', 'Equal to'), ('missing', 'Missing'))
    )
    threshold = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company.name} - {self.activity_type} - {self.field_name}"
