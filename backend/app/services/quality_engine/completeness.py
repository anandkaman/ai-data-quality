import pandas as pd
import numpy as np
from typing import Dict, List

class CompletenessAnalyzer:
    def analyze(self, df: pd.DataFrame) -> Dict:
        results = {
            'overall_completeness': self._calculate_overall_completeness(df),
            'column_completeness': self._analyze_columns(df),
            'missing_patterns': self._detect_missing_patterns(df),
            'recommendations': []
        }
        results['recommendations'] = self._generate_recommendations(results)
        return results
    
    def _calculate_overall_completeness(self, df: pd.DataFrame) -> float:
        total_cells = df.size
        non_null_cells = df.count().sum()
        return (non_null_cells / total_cells) * 100 if total_cells > 0 else 0.0
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict:
        column_stats = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            missing_pct = (missing_count / len(df)) * 100 if len(df) > 0 else 0.0
            column_stats[col] = {
                'missing_count': int(missing_count),
                'missing_percentage': round(missing_pct, 2),
                'completeness_score': round(100 - missing_pct, 2),
                'data_type': str(df[col].dtype),
                'unique_values': int(df[col].nunique())
            }
        return column_stats
    
    def _detect_missing_patterns(self, df: pd.DataFrame) -> List[Dict]:
        patterns = []
        missing_matrix = df.isnull().astype(int)
        for i, col1 in enumerate(df.columns):
            for col2 in df.columns[i+1:]:
                overlap = (missing_matrix[col1] & missing_matrix[col2]).sum()
                if overlap > 0:
                    total_missing = missing_matrix[col1].sum() + missing_matrix[col2].sum()
                    jaccard = overlap / (total_missing - overlap) if total_missing > overlap else 0
                    if jaccard > 0.5:
                        patterns.append({
                            'columns': [col1, col2],
                            'overlap_count': int(overlap),
                            'similarity_score': round(jaccard, 3),
                            'pattern_type': 'correlated_missing'
                        })
        return patterns
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        recommendations = []
        overall = results['overall_completeness']
        if overall < 90:
            recommendations.append(f"Overall completeness is {overall:.2f}%. Consider data source quality improvement.")
        for col, stats in results['column_completeness'].items():
            if stats['missing_percentage'] > 50:
                recommendations.append(f"Column '{col}' has {stats['missing_percentage']:.2f}% missing. Consider dropping or imputing.")
            elif stats['missing_percentage'] > 20:
                recommendations.append(f"Column '{col}' has {stats['missing_percentage']:.2f}% missing. Imputation recommended.")
        return recommendations
