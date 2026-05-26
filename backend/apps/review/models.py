"""
Review and approval models for analyst dashboard
"""
from django.db import models
from apps.tenants.models import Company


class ReviewSession(models.Model):
    """Represents a batch review session by an analyst"""
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='review_sessions')
    analyst = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    records_to_review = models.IntegerField(default=0)
    records_approved = models.IntegerField(default=0)
    records_rejected = models.IntegerField(default=0)
    records_flagged = models.IntegerField(default=0)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review Session - {self.company.name} ({self.status})"


class ReviewQueue(models.Model):
    """Tracks records pending analyst review"""
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High - Flagged'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='review_queue')
    activity_record = models.OneToOneField(
        'normalization.ActivityRecord',
        on_delete=models.CASCADE,
        related_name='review_queue_entry'
    )
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='low')
    reason = models.CharField(max_length=255, blank=True)  # why it needs review
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', 'created_at']
    
    def __str__(self):
        return f"Review Queue - {self.activity_record.id}"
