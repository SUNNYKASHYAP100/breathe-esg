"""
Serializers for ingestion app
"""
from rest_framework import serializers
from apps.ingestion.models import DataSource, IngestionJob, RawRecord
from apps.normalization.models import ActivityRecord


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ['id', 'company', 'source_type', 'name', 'configuration', 'created_at']


class IngestionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionJob
        fields = ['id', 'company', 'data_source', 'uploaded_by', 'status', 'file_name', 
                  'total_rows', 'processed_rows', 'failed_rows', 'error_log', 'created_at']
        read_only_fields = ['status', 'processed_rows', 'failed_rows', 'error_log']


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = ['id', 'ingestion_job', 'row_number', 'raw_data', 'processing_status', 'error_message', 'created_at']


class ActivityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityRecord
        fields = [
            'id', 'company', 'source_system', 'activity_type', 'scope',
            'quantity', 'unit', 'activity_date', 'billing_start_date', 'billing_end_date',
            'category', 'subcategory', 'origin', 'destination', 'distance',
            'confidence_score', 'is_flagged', 'flag_reason', 'status',
            'approved_by', 'approved_at', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'original_data']
