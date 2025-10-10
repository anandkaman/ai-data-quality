from sklearn.svm import OneClassSVM
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class OCSVMDetector:
    def __init__(self, nu: float = 0.1, kernel: str = 'rbf'):
        self.model = OneClassSVM(nu=nu, kernel=kernel, gamma='auto')
        self.nu = nu
    
    def detect(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return np.array([]), np.array([])
        
        numeric_df = numeric_df.fillna(numeric_df.mean())
        predictions = self.model.fit_predict(numeric_df)
        scores = self.model.decision_function(numeric_df)
        
        anomalies = predictions == -1
        return anomalies, scores
    
    def get_feature_importance(self, df: pd.DataFrame, anomaly_indices: np.ndarray) -> Dict:
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty or len(anomaly_indices) == 0:
            return {}
        
        importance = {}
        for col in numeric_df.columns:
            anomaly_mean = numeric_df.loc[anomaly_indices, col].mean()
            normal_mean = numeric_df.loc[~anomaly_indices, col].mean()
            importance[col] = abs(anomaly_mean - normal_mean)
        
        total = sum(importance.values())
        if total > 0:
            importance = {k: v/total for k, v in importance.items()}
        
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
