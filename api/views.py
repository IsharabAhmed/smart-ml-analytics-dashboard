from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from core.models import Workspace, Dataset, MLModel, Prediction, Visualization
from api.serializers import DatasetSerializer, MLModelSerializer, PredictionSerializer, VisualizationSerializer
from core.tasks import task_profile_dataset, task_train_model
import pandas as pd
import math

from django.contrib.auth.models import User

class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_workspace(self):
        if self.request.user.is_authenticated:
            workspace, _ = Workspace.objects.get_or_create(user=self.request.user)
        else:
            dummy_user, _ = User.objects.get_or_create(username='anonymous')
            workspace, _ = Workspace.objects.get_or_create(user=dummy_user)
        return workspace

    def get_queryset(self):
        workspace = self.get_workspace()
        if workspace:
            return Dataset.objects.filter(workspace=workspace).order_by('-created_at')
        return Dataset.objects.none()

    def perform_create(self, serializer):
        workspace = self.get_workspace()
        dataset = serializer.save(workspace=workspace, status='PENDING')
        # Trigger Celery task
        task_profile_dataset.delay(dataset.id)

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        dataset = self.get_object()
        try:
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 50))
            
            df = pd.read_csv(dataset.file.path)
            
            # Handle NaNs before converting to dict
            df = df.replace({float('nan'): None})
            
            total_records = len(df)
            total_pages = math.ceil(total_records / per_page)
            
            start = (page - 1) * per_page
            end = start + per_page
            
            paginated_df = df.iloc[start:end]
            
            return Response({
                'data': paginated_df.to_dict(orient='records'),
                'page': page,
                'per_page': per_page,
                'total_records': total_records,
                'total_pages': total_pages
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer

    def get_workspace(self):
        if self.request.user.is_authenticated:
            workspace, _ = Workspace.objects.get_or_create(user=self.request.user)
        else:
            dummy_user, _ = User.objects.get_or_create(username='anonymous')
            workspace, _ = Workspace.objects.get_or_create(user=dummy_user)
        return workspace

    def get_queryset(self):
        workspace = self.get_workspace()
        if workspace:
            return MLModel.objects.filter(dataset__workspace=workspace).order_by('-created_at')
        return MLModel.objects.none()

    def perform_create(self, serializer):
        model = serializer.save(status='PENDING')
        # Trigger Celery task
        task_train_model.delay(model.id)
