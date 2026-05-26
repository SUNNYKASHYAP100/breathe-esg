"""
URL routing for review app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.review.views import ReviewQueueViewSet, ActivityRecordReviewViewSet, ReviewSessionViewSet

router = DefaultRouter()
router.register(r'queue', ReviewQueueViewSet, basename='review-queue')
router.register(r'records', ActivityRecordReviewViewSet, basename='activity-record-review')
router.register(r'sessions', ReviewSessionViewSet, basename='review-session')

urlpatterns = [
    path('', include(router.urls)),
]
