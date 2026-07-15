from django.shortcuts import render, get_object_or_404
from .models import Dataset

def dashboard_index(request):
    datasets = Dataset.objects.all().order_by('-created_at')
    return render(request, 'dashboard/index.html', {'datasets': datasets})

def dataset_detail(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    models = dataset.models.all().order_by('-created_at')
    return render(request, 'dashboard/detail.html', {'dataset': dataset, 'models': models})
