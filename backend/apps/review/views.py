"""
Review views for analyst dashboard
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from apps.review.models import ReviewSession, ReviewQueue
from apps.review.serializers import ReviewSessionSerializer, ReviewQueueSerializer, ActivityRecordReviewSerializer
from apps.normalization.models import ActivityRecord, AuditLog


class ReviewQueueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReviewQueue.objects.all()
    serializer_class = ReviewQueueSerializer
    
    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        if company_id:
            return ReviewQueue.objects.filter(company_id=company_id).select_related('activity_record')
        return super().get_queryset()


class ActivityRecordReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for reviewing and approving activity records"""
    queryset = ActivityRecord.objects.all()
    serializer_class = ActivityRecordReviewSerializer
    
    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        status_filter = self.request.query_params.get('status')
        
        qs = ActivityRecord.objects.prefetch_related('audit_logs')
        
        if company_id:
            qs = qs.filter(company_id=company_id)
        
        if status_filter:
            qs = qs.filter(status=status_filter)
        else:
            # Default to records pending review
            qs = qs.filter(status__in=['pending_review', 'flagged'])
        
        return qs.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an activity record"""
        activity = self.get_object()
        
        if activity.status == 'locked':
            return Response(
                {'error': 'Cannot approve locked record'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update record
        activity.status = 'approved'
        activity.approved_by = request.user
        activity.approved_at = timezone.now()
        activity.notes = request.data.get('notes', '')
        activity.save()
        
        # Create audit log
        AuditLog.objects.create(
            activity_record=activity,
            action='approved',
            user=request.user,
            notes=request.data.get('notes', '')
        )
        
        # Remove from review queue
        if hasattr(activity, 'review_queue_entry'):
            activity.review_queue_entry.delete()
        
        return Response(ActivityRecordReviewSerializer(activity).data)
    
    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        """Flag a record for additional review"""
        activity = self.get_object()
        
        activity.is_flagged = True
        activity.flag_reason = request.data.get('reason', '')
        activity.status = 'flagged'
        activity.save()
        
        # Create audit log
        AuditLog.objects.create(
            activity_record=activity,
            action='flagged',
            user=request.user,
            notes=request.data.get('reason', '')
        )
        
        # Add to review queue if not already there
        ReviewQueue.objects.get_or_create(
            activity_record=activity,
            defaults={
                'company': activity.company,
                'priority': 'high',
                'reason': request.data.get('reason', 'Manual flag by reviewer')
            }
        )
        
        return Response(ActivityRecordReviewSerializer(activity).data)
    
    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Lock record for audit - cannot be modified"""
        activity = self.get_object()
        
        if activity.status not in ['approved', 'pending_review']:
            return Response(
                {'error': 'Record must be approved before locking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        activity.status = 'locked'
        activity.save()
        
        # Create audit log
        AuditLog.objects.create(
            activity_record=activity,
            action='locked',
            user=request.user,
            notes='Record locked for audit'
        )
        
        return Response(ActivityRecordReviewSerializer(activity).data)
    
    @action(detail=True, methods=['post'])
    def update_notes(self, request, pk=None):
        """Update notes on activity record"""
        activity = self.get_object()
        
        # Store previous value
        previous_notes = activity.notes
        activity.notes = request.data.get('notes', '')
        activity.save()
        
        # Create audit log
        AuditLog.objects.create(
            activity_record=activity,
            action='updated',
            user=request.user,
            changes={'notes': [previous_notes, activity.notes]},
            notes=request.data.get('notes', '')
        )
        
        return Response(ActivityRecordReviewSerializer(activity).data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get review statistics for company"""
        company_id = request.query_params.get('company_id')
        
        if not company_id:
            return Response({'error': 'company_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        qs = ActivityRecord.objects.filter(company_id=company_id)
        
        stats = {
            'total': qs.count(),
            'pending_review': qs.filter(status='pending_review').count(),
            'flagged': qs.filter(status='flagged').count(),
            'approved': qs.filter(status='approved').count(),
            'locked': qs.filter(status='locked').count(),
            'by_scope': {
                'scope_1': qs.filter(scope='scope_1').count(),
                'scope_2': qs.filter(scope='scope_2').count(),
                'scope_3': qs.filter(scope='scope_3').count(),
            },
            'by_source': {
                'sap': qs.filter(source_system='sap').count(),
                'utility': qs.filter(source_system='utility').count(),
                'travel': qs.filter(source_system='travel').count(),
            }
        }
        
        return Response(stats)


class ReviewSessionViewSet(viewsets.ModelViewSet):
    queryset = ReviewSession.objects.all()
    serializer_class = ReviewSessionSerializer
    
    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        if company_id:
            return ReviewSession.objects.filter(company_id=company_id)
        return super().get_queryset()
