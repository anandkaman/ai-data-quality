import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from .isolation_forest import IsolationForestDetector
from .lof_detector import LOFDetector
from .ocsvm_detector import OCSVMDetector

class AnomalyEnsemble:
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.models = {
            'isolation_forest': IsolationForestDetector(contamination=contamination),
            'lof': LOFDetector(contamination=contamination),
            'ocsvm': OCSVMDetector(nu=contamination)
        }
        self.weights = {
            'isolation_forest': 0.4,
            'lof': 0.3,
            'ocsvm': 0.3
        }
    
    def detect_anomalies(self, df: pd.DataFrame) -> Dict:
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {
                'ensemble_anomalies': [],
                'scores': np.array([]),
                'individual_results': {},
                'feature_importance': {}
            }
        
        all_predictions = {}
        all_scores = {}
        
        for name, model in self.models.items():
            try:
                anomalies, scores = model.detect(df)
                all_predictions[name] = anomalies
                all_scores[name] = scores
            except Exception as e:
                print(f"Error in {name}: {str(e)}")
                all_predictions[name] = np.zeros(len(df), dtype=bool)
                all_scores[name] = np.zeros(len(df))
        
        ensemble_scores = np.zeros(len(df))
        for name, weight in self.weights.items():
            if name in all_scores:
                normalized_scores = self._normalize_scores(all_scores[name])
                ensemble_scores += weight * normalized_scores
        
        threshold = np.percentile(ensemble_scores, (1 - self.contamination) * 100)
        ensemble_anomalies = ensemble_scores > threshold
        
        anomaly_indices = np.where(ensemble_anomalies)[0].tolist()
        
        feature_importance = {}
        if len(anomaly_indices) > 0:
            for name, model in self.models.items():
                try:
                    importance = model.get_feature_importance(df, np.array(anomaly_indices))
                    for feature, score in importance.items():
                        feature_importance[feature] = feature_importance.get(feature, 0) + score * self.weights[name]
                except:
                    pass
        
        return {
            'ensemble_anomalies': anomaly_indices,
            'scores': ensemble_scores,
            'individual_results': {
                name: np.where(pred)[0].tolist()
                for name, pred in all_predictions.items()
            },
            'feature_importance': feature_importance
        }
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        if len(scores) == 0:
            return scores
        
        scores = np.abs(scores)
        min_score = scores.min()
        max_score = scores.max()
        
        if max_score - min_score == 0:
            return np.zeros_like(scores)
        
        return (scores - min_score) / (max_score - min_score)
