import pandas as pd
import numpy as np
from typing import Dict, List
import re

class ConsistencyAnalyzer:
    def analyze(self, df: pd.DataFrame) -> Dict:
        results = {
            'format_consistency': self._check_format_consistency(df),
            'value_consistency': self._check_value_consistency(df),
            'type_consistency': self._check_type_consistency(df),
            'recommendations': []
        }
        results['recommendations'] = self._generate_recommendations(results)
        return results
    
    def _check_format_consistency(self, df: pd.DataFrame) -> Dict:
        format_issues = {}
        for col in df.select_dtypes(include=['object']).columns:
            patterns = {}
            for val in df[col].dropna().unique():
                val_str = str(val)
                pattern = self._extract_pattern(val_str)
                patterns[pattern] = patterns.get(pattern, 0) + 1
            
            if len(patterns) > 1:
                format_issues[col] = {
                    'pattern_count': len(patterns),
                    'patterns': patterns,
                    'consistency_score': round((max(patterns.values()) / sum(patterns.values())) * 100, 2)
                }
        return format_issues
    
    def _extract_pattern(self, value: str) -> str:
        pattern = re.sub(r'\d', 'N', value)
        pattern = re.sub(r'[a-zA-Z]', 'A', pattern)
        return pattern
    
    def _check_value_consistency(self, df: pd.DataFrame) -> Dict:
        inconsistencies = {}
        for col in df.select_dtypes(include=['object']).columns:
            unique_vals = df[col].dropna().unique()
            normalized_vals = {}
            for val in unique_vals:
                normalized = str(val).strip().lower()
                if normalized in normalized_vals:
                    inconsistencies.setdefault(col, []).append({
                        'original_values': [normalized_vals[normalized], val],
                        'issue': 'case_or_whitespace_difference'
                    })
                else:
                    normalized_vals[normalized] = val
        return inconsistencies
    
    def _check_type_consistency(self, df: pd.DataFrame) -> Dict:
        type_issues = {}
        for col in df.columns:
            if df[col].dtype == 'object':
                type_distribution = {}
                for val in df[col].dropna():
                    val_type = self._infer_type(val)
                    type_distribution[val_type] = type_distribution.get(val_type, 0) + 1
                
                if len(type_distribution) > 1:
                    type_issues[col] = {
                        'mixed_types': type_distribution,
                        'dominant_type': max(type_distribution, key=type_distribution.get)
                    }
        return type_issues
    
    def _infer_type(self, value):
        try:
            float(value)
            return 'numeric'
        except:
            if re.match(r'^\d{4}-\d{2}-\d{2}', str(value)):
                return 'date'
            return 'text'
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        recommendations = []
        if results['format_consistency']:
            recommendations.append(f"Found format inconsistencies in {len(results['format_consistency'])} columns. Standardize formats.")
        if results['value_consistency']:
            recommendations.append(f"Found value inconsistencies in {len(results['value_consistency'])} columns. Normalize values.")
        if results['type_consistency']:
            recommendations.append(f"Found type inconsistencies in {len(results['type_consistency'])} columns. Convert to consistent types.")
        return recommendations
