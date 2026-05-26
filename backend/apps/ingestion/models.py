"""
Ingestion models for handling data uploads from various sources
"""
from django.db import models
from apps.tenants.models import Company
from django.contrib.auth.models import User


class DataSource(models.Model):
    """Represents a data source (SAP, Utility Portal, Travel Platform)"""
    SOURCE_TYPES = (
        ('sap_fuel', 'SAP - Fuel'),
        ('sap_procurement', 'SAP - Procurement'),
        ('utility_electricity', 'Utility - Electricity'),
        ('travel_flights', 'Travel - Flights'),
        ('travel_hotels', 'Travel - Hotels'),
        ('travel_ground', 'Travel - Ground Transport'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='data_sources')
    source_type = models.CharField(max_length=30, choices=SOURCE_TYPES)
    name = models.CharField(max_length=255)
    configuration = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('company', 'source_type')
    
    def __str__(self):
        return f"{self.company.name} - {self.get_source_type_display()}"


class IngestionJob(models.Model):
    """Tracks data ingestion jobs"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='ingestion_jobs')
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='jobs')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    error_log = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.file_name} ({self.status})"


class RawRecord(models.Model):
    """Stores raw, unprocessed records from ingestion"""
    ingestion_job = models.ForeignKey(IngestionJob, on_delete=models.CASCADE, related_name='raw_records')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='raw_records')
    source_type = models.CharField(max_length=30)
    raw_data = models.JSONField()
    row_number = models.IntegerField()
    processing_status = models.CharField(
        max_length=20,
        choices=(('pending', 'Pending'), ('normalized', 'Normalized'), ('failed', 'Failed')),
        default='pending'
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['ingestion_job', 'row_number']
        indexes = [
            models.Index(fields=['company', 'processing_status']),
        ]
    
    def __str__(self):
        return f"Raw Record {self.id} - {self.company.name}"
