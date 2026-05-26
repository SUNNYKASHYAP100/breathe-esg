"""
Serializers for review app
"""
from rest_framework import serializers
from apps.review.models import ReviewSession, ReviewQueue
from apps.normalization.models import ActivityRecord, AuditLog


class ReviewQueueSerializer(serializers.ModelSerializer):
    activity_record = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewQueue
        fields = ['id', 'company', 'activity_record', 'priority', 'reason', 'created_at']
    
    def get_activity_record(self, obj):
        activity = obj.activity_record
        return {
            'id': activity.id,
            'source_system': activity.source_system,
            'activity_type': activity.get_activity_type_display(),
            'quantity': float(activity.quantity),
            'unit': activity.unit,
            'activity_date': activity.activity_date,
            'status': activity.status,
            'is_flagged': activity.is_flagged,
            'flag_reason': activity.flag_reason,
            'confidence_score': float(activity.confidence_score),
        }


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'activity_record', 'action', 'user', 'changes', 'notes', 'created_at']


class ActivityRecordReviewSerializer(serializers.ModelSerializer):
    audit_logs = AuditLogSerializer(many=True, read_only=True, source='audit_logs.all')
    
    class Meta:
        model = ActivityRecord
        fields = [
            'id', 'company', 'source_system', 'activity_type', 'scope',
            'quantity', 'unit', 'activity_date', 'billing_start_date', 'billing_end_date',
            'category', 'subcategory', 'origin', 'destination', 'distance',
            'confidence_score', 'is_flagged', 'flag_reason', 'status',
            'notes', 'created_at', 'audit_logs'
        ]


class ReviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewSession
        fields = [
            'id', 'company', 'analyst', 'status',
            'records_to_review', 'records_approved', 'records_rejected', 'records_flagged',
            'notes', 'created_at', 'updated_at', 'completed_at'
        ]
