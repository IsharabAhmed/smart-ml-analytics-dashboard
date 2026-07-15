from rest_framework import serializers
from core.models import Workspace, Dataset, MLModel, Prediction, Visualization
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class WorkspaceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Workspace
        fields = '__all__'

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = '__all__'
        read_only_fields = ['id', 'workspace', 'status', 'metadata', 'created_at', 'updated_at']

class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = '__all__'
        read_only_fields = ['id', 'status', 'model_file', 'metrics', 'feature_importance', 'created_at', 'updated_at']

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'
        read_only_fields = ['id', 'status', 'results_file', 'created_at']

class VisualizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visualization
        fields = '__all__'
