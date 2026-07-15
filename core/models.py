from django.db import models
from django.contrib.auth.models import User
import uuid

class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='workspace')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Workspace"

class Dataset(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class MLModel(models.Model):
    TASK_CHOICES = (
        ('CLUSTERING', 'Clustering'),
        ('CLASSIFICATION', 'Classification'),
        ('REGRESSION', 'Regression'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('TRAINING', 'Training'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='models')
    task_type = models.CharField(max_length=20, choices=TASK_CHOICES)
    algorithm = models.CharField(max_length=100, blank=True)
    target_column = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    model_file = models.FileField(upload_to='models/', null=True, blank=True)
    metrics = models.JSONField(null=True, blank=True)
    feature_importance = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.algorithm} - {self.dataset.name}"

class Prediction(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ml_model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='predictions')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='predictions', help_text='Dataset used for prediction')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    results_file = models.FileField(upload_to='predictions/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for {self.ml_model.algorithm} on {self.dataset.name}"

class Visualization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='visualizations')
    ml_model = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='visualizations')
    vis_type = models.CharField(max_length=100)
    config = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vis_type} for {self.dataset.name}"
