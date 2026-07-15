from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_index, name='dashboard_index'),
    path('dataset/<uuid:pk>/', views.dataset_detail, name='dataset_detail'),
]
