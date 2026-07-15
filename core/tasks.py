from celery import shared_task
from core.models import Dataset, MLModel
from core.ml.pipeline import profile_dataframe, auto_train_model
import pandas as pd
import joblib
import os
from django.conf import settings

@shared_task
def task_profile_dataset(dataset_id):
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        dataset.status = 'PROCESSING'
        dataset.save()
        
        # Load CSV
        file_path = dataset.file.path
        df = pd.read_csv(file_path)
        
        # Generate Profile
        profile = profile_dataframe(df)
        
        dataset.metadata = profile
        dataset.status = 'COMPLETED'
        dataset.save()
        return f"Profiled {dataset.name}"
    except Exception as e:
        if 'dataset' in locals():
            dataset.status = 'FAILED'
            dataset.metadata = {"error": str(e)}
            dataset.save()
        return str(e)

@shared_task
def task_train_model(model_id):
    try:
        model_record = MLModel.objects.get(id=model_id)
        model_record.status = 'TRAINING'
        model_record.save()
        
        # Load Data
        df = pd.read_csv(model_record.dataset.file.path)
        
        # Train Model
        pipeline, metrics, feature_importance = auto_train_model(
            df=df,
            task_type=model_record.task_type,
            target_column=model_record.target_column,
            algorithm=model_record.algorithm
        )
        
        # Save Model artifact
        models_dir = os.path.join(settings.MEDIA_ROOT, 'models')
        os.makedirs(models_dir, exist_ok=True)
        model_filename = f"model_{model_id}.pkl"
        model_path = os.path.join(models_dir, model_filename)
        joblib.dump(pipeline, model_path)
        
        # Update record
        model_record.model_file.name = f"models/{model_filename}"
        model_record.metrics = metrics
        model_record.feature_importance = feature_importance
        model_record.status = 'COMPLETED'
        model_record.save()
        
        return f"Trained model {model_id}"
    except Exception as e:
        if 'model_record' in locals():
            model_record.status = 'FAILED'
            model_record.metrics = {"error": str(e)}
            model_record.save()
        return str(e)
