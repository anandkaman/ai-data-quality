import shap
import pandas as pd
import numpy as np
from typing import Dict, List
import json

class SHAPExplainer:
    def __init__(self):
        self.explainer = None
        self.shap_values = None
    
    def explain_anomalies(self, df: pd.DataFrame, model, anomaly_indices: List[int]) -> Dict:
        numeric_df = df.select_dtypes(include=[np.number]).fillna(0)
        
        if numeric_df.empty:
            return {'error': 'No numeric features for explanation'}
        
        try:
            self.explainer = shap.Explainer(model.predict, numeric_df)
            self.shap_values = self.explainer(numeric_df)
            
            explanations = {}
            for idx in anomaly_indices[:10]:
                if idx < len(numeric_df):
                    feature_contributions = {}
                    for i, col in enumerate(numeric_df.columns):
                        feature_contributions[col] = float(self.shap_values.values[idx][i])
                    
                    explanations[int(idx)] = {
                        'feature_contributions': dict(sorted(
                            feature_contributions.items(),
                            key=lambda x: abs(x[1]),
                            reverse=True
                        )),
                        'base_value': float(self.shap_values.base_values[idx]) if hasattr(self.shap_values, 'base_values') else 0.0
                    }
            
            global_importance = self._calculate_global_importance(numeric_df.columns)
            
            return {
                'individual_explanations': explanations,
                'global_feature_importance': global_importance,
                'explanation_type': 'SHAP'
            }
        
        except Exception as e:
            return {'error': f'SHAP explanation failed: {str(e)}'}
    
    def _calculate_global_importance(self, columns: List[str]) -> Dict:
        if self.shap_values is None:
            return {}
        
        importance = {}
        for i, col in enumerate(columns):
            importance[col] = float(np.abs(self.shap_values.values[:, i]).mean())
        
        total = sum(importance.values())
        if total > 0:
            importance = {k: v/total for k, v in importance.items()}
        
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))