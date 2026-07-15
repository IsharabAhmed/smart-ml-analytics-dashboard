import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import xgboost as xgb

def profile_dataframe(df: pd.DataFrame) -> dict:
    """Generates basic summary statistics and profiling information for a dataset."""
    profile = {
        "num_rows": int(df.shape[0]),
        "num_cols": int(df.shape[1]),
        "columns": [],
        "missing_summary": {}
    }
    
    for col in df.columns:
        col_type = str(df[col].dtype)
        num_missing = int(df[col].isna().sum())
        profile["missing_summary"][col] = num_missing
        
        col_info = {
            "name": col,
            "type": col_type,
            "missing": num_missing
        }
        
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info.update({
                "mean": float(df[col].mean()) if not df[col].empty else None,
                "min": float(df[col].min()) if not df[col].empty else None,
                "max": float(df[col].max()) if not df[col].empty else None
            })
        else:
            col_info.update({
                "unique_values": int(df[col].nunique())
            })
            
        profile["columns"].append(col_info)
        
    return profile

def detect_outliers(df: pd.DataFrame, contamination=0.05) -> list:
    """Detects outliers using Isolation Forest on numerical columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        return []
        
    # Impute missing values for Isolation Forest
    imputer = SimpleImputer(strategy='median')
    X = imputer.fit_transform(df[numeric_cols])
    
    clf = IsolationForest(contamination=contamination, random_state=42)
    preds = clf.fit_predict(X)
    
    # -1 means outlier, 1 means inlier
    outlier_indices = np.where(preds == -1)[0].tolist()
    return outlier_indices

def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Builds a scikit-learn preprocessing pipeline based on column types."""
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
        
    return preprocessor, numeric_features, categorical_features

def auto_train_model(df: pd.DataFrame, task_type: str, target_column: str = None, algorithm: str = 'auto'):
    """
    Trains an ML model based on the task type.
    Returns: pipeline, metrics, feature_importance
    """
    if task_type == 'CLUSTERING':
        # Remove target column if provided for clustering
        X = df.drop(columns=[target_column]) if target_column and target_column in df.columns else df.copy()
        preprocessor, num_cols, cat_cols = build_preprocessor(X)
        
        # Determine K if algorithm is KMeans
        model = KMeans(n_clusters=3, random_state=42) # default to 3 for now
        pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        
        # Fit
        pipeline.fit(X)
        
        # Get transformed data for silhouette score
        X_processed = preprocessor.transform(X)
        labels = pipeline.named_steps['model'].labels_
        
        # Ensure we have at least 2 clusters for silhouette
        n_clusters = len(np.unique(labels))
        metrics = {}
        if 1 < n_clusters < len(X):
            metrics['silhouette_score'] = float(silhouette_score(X_processed, labels))
            
        return pipeline, metrics, {}
        
    # Supervised Learning
    if not target_column or target_column not in df.columns:
        raise ValueError("Target column is missing for supervised task")
        
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    preprocessor, num_cols, cat_cols = build_preprocessor(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    metrics = {}
    model = None
    
    if task_type == 'CLASSIFICATION':
        # Auto-select algorithm
        if algorithm == 'auto' or not algorithm:
            algorithm = 'RandomForest'
            
        if algorithm == 'RandomForest':
            model = RandomForestClassifier(random_state=42)
        elif algorithm == 'XGBoost':
            model = xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')
        elif algorithm == 'LogisticRegression':
            model = LogisticRegression(random_state=42, max_iter=1000)
            
        pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        
        metrics = {
            'accuracy': float(accuracy_score(y_test, preds)),
            # Use macro average to handle multi-class
            'precision': float(precision_score(y_test, preds, average='macro', zero_division=0)),
            'recall': float(recall_score(y_test, preds, average='macro', zero_division=0)),
            'f1': float(f1_score(y_test, preds, average='macro', zero_division=0))
        }
        
    elif task_type == 'REGRESSION':
        if algorithm == 'auto' or not algorithm:
            algorithm = 'RandomForest'
            
        if algorithm == 'RandomForest':
            model = RandomForestRegressor(random_state=42)
        elif algorithm == 'XGBoost':
            model = xgb.XGBRegressor(random_state=42)
        elif algorithm == 'LinearRegression':
            model = LinearRegression()
            
        pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        
        metrics = {
            'rmse': float(np.sqrt(mean_squared_error(y_test, preds))),
            'r2': float(r2_score(y_test, preds))
        }
        
    # Extract Feature Importance
    feature_importance = {}
    if hasattr(pipeline.named_steps['model'], 'feature_importances_'):
        importances = pipeline.named_steps['model'].feature_importances_
        # Need to reconstruct feature names from ColumnTransformer
        cat_encoder = pipeline.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot']
        try:
            # works for newer scikit-learn
            cat_names = cat_encoder.get_feature_names_out(cat_cols)
        except AttributeError:
            cat_names = [f"cat_{i}" for i in range(len(importances) - len(num_cols))]
            
        all_features = num_cols + list(cat_names)
        
        # Match length in case something weird happens
        if len(all_features) == len(importances):
            for name, imp in zip(all_features, importances):
                feature_importance[name] = float(imp)
                
            # Sort dict
            feature_importance = dict(sorted(feature_importance.items(), key=lambda item: item[1], reverse=True)[:15])
            
    return pipeline, metrics, feature_importance
