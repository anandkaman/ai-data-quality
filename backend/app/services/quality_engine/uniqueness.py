import pandas as pd
import numpy as np
from typing import Dict, List
from collections import Counter

class UniquenessAnalyzer:
    def analyze(self, df: pd.DataFrame) -> Dict:
        results = {
            'duplicate_rows': self._check_duplicate_rows(df),
            'duplicate_values': self._check_duplicate_values(df),
            'uniqueness_scores': self._calculate_uniqueness_scores(df),
            'recommendations': []
        }
        results['recommendations'] = self._generate_recommendations(results)
        return results
    
    def _check_duplicate_rows(self, df: pd.DataFrame) -> Dict:
        total_rows = len(df)
        duplicate_rows = df.duplicated().sum()
        unique_rows = total_rows - duplicate_rows
        
        return {
            'total_rows': total_rows,
            'duplicate_count': int(duplicate_rows),
            'unique_count': int(unique_rows),
            'duplicate_percentage': round((duplicate_rows / total_rows) * 100, 2) if total_rows > 0 else 0.0,
            'uniqueness_score': round((unique_rows / total_rows) * 100, 2) if total_rows > 0 else 0.0
        }
    
    def _check_duplicate_values(self, df: pd.DataFrame) -> Dict:
        duplicate_info = {}
        for col in df.columns:
            value_counts = df[col].value_counts()
            duplicates = value_counts[value_counts > 1]
            
            if len(duplicates) > 0:
                duplicate_info[col] = {
                    'duplicate_value_count': len(duplicates),
                    'total_duplicate_occurrences': int(duplicates.sum()),
                    'most_common': duplicates.head(5).to_dict(),
                    'unique_percentage': round((df[col].nunique() / len(df)) * 100, 2)
                }
        return duplicate_info
    
    def _calculate_uniqueness_scores(self, df: pd.DataFrame) -> Dict:
        scores = {}
        for col in df.columns:
            total_values = len(df[col].dropna())
            unique_values = df[col].nunique()
            
            scores[col] = {
                'total_values': total_values,
                'unique_values': unique_values,
                'uniqueness_score': round((unique_values / total_values) * 100, 2) if total_values > 0 else 0.0,
                'cardinality': 'high' if unique_values > total_values * 0.9 else 'medium' if unique_values > total_values * 0.5 else 'low'
            }
        return scores
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        recommendations = []
        dup_rows = results['duplicate_rows']
        if dup_rows['duplicate_count'] > 0:
            recommendations.append(f"Found {dup_rows['duplicate_count']} duplicate rows ({dup_rows['duplicate_percentage']}%). Consider deduplication.")
        
        for col, info in results['duplicate_values'].items():
            if info['unique_percentage'] < 50:
                recommendations.append(f"Column '{col}' has low uniqueness ({info['unique_percentage']}%). May indicate data quality issue.")
        
        return recommendations
