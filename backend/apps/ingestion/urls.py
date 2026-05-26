"""
URL routing for ingestion app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ingestion.views import DataSourceViewSet, IngestionJobViewSet, RawRecordViewSet

router = DefaultRouter()
router.register(r'sources', DataSourceViewSet, basename='data-source')
router.register(r'jobs', IngestionJobViewSet, basename='ingestion-job')
router.register(r'raw-records', RawRecordViewSet, basename='raw-record')

urlpatterns = [
    path('', include(router.urls)),
]
