"""
Ingestion views for data upload and processing
"""
import csv
import io
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from apps.ingestion.models import DataSource, IngestionJob, RawRecord
from apps.ingestion.serializers import DataSourceSerializer, IngestionJobSerializer, RawRecordSerializer
from apps.normalization.models import ActivityRecord
from apps.normalization.services import normalize_sap_record, normalize_utility_record, normalize_travel_record


class DataSourceViewSet(viewsets.ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    
    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        if company_id:
            return DataSource.objects.filter(company_id=company_id)
        return super().get_queryset()


class IngestionJobViewSet(viewsets.ModelViewSet):
    queryset = IngestionJob.objects.all()
    serializer_class = IngestionJobSerializer
    
    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        if company_id:
            return IngestionJob.objects.filter(company_id=company_id)
        return super().get_queryset()
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Handle file upload from various sources"""
        company_id = request.data.get('company_id')
        source_type = request.data.get('source_type')  # SAP_CSV, UTILITY_CSV, TRAVEL_API
        file = request.FILES.get('file')
        
        if not all([company_id, source_type, file]):
            return Response({'error': 'Missing required fields: company_id, source_type, file'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from apps.tenants.models import Company
            company = Company.objects.get(id=company_id)
            
            # Get or create data source
            data_source, created = DataSource.objects.get_or_create(
                company=company,
                source_type=source_type,
                defaults={'name': f'{source_type} Import'}
            )
        except Company.DoesNotExist:
            return Response({'error': 'Invalid company'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create ingestion job
        job = IngestionJob.objects.create(
            company=company,
            data_source=data_source,
            uploaded_by=request.user if request.user.is_authenticated else None,
            file_name=file.name,
            file_path=f'uploads/{company_id}/{source_type}/{file.name}',
            status='processing'
        )
        
        # Parse and store raw records
        try:
            content = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(content))
            
            row_count = 0
            for row_num, row in enumerate(reader, start=1):
                RawRecord.objects.create(
                    ingestion_job=job,
                    company=company,
                    source_type=source_type,
                    raw_data=dict(row),
                    row_number=row_num
                )
                row_count += 1
            
            job.total_rows = row_count
            job.status = 'completed'
            job.save()
            
            # Trigger normalization
            self._normalize_records(job)
            
            return Response(IngestionJobSerializer(job).data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            job.status = 'failed'
            job.error_log = [str(e)]
            job.save()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _normalize_records(self, job):
        """Process raw records and create activity records"""
        raw_records = RawRecord.objects.filter(ingestion_job=job, processing_status='pending')
        
        for raw in raw_records:
            try:
                # Route to appropriate normalizer
                if 'sap' in job.data_source.source_type:
                    activity = normalize_sap_record(raw, job)
                elif 'utility' in job.data_source.source_type:
                    activity = normalize_utility_record(raw, job)
                elif 'travel' in job.data_source.source_type:
                    activity = normalize_travel_record(raw, job)
                
                if activity:
                    raw.processing_status = 'normalized'
                    job.processed_rows += 1
                else:
                    raw.processing_status = 'failed'
                    job.failed_rows += 1
                
                raw.save()
            
            except Exception as e:
                raw.processing_status = 'failed'
                raw.error_message = str(e)
                job.failed_rows += 1
                raw.save()
        
        job.save()


class RawRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RawRecord.objects.all()
    serializer_class = RawRecordSerializer
    
    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        if company_id:
            return RawRecord.objects.filter(company_id=company_id)
        return super().get_queryset()
