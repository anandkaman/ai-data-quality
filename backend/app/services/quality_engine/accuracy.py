import pandas as pd
import numpy as np
from typing import Dict, List

class AccuracyAnalyzer:
    def analyze(self, df: pd.DataFrame) -> Dict:
        results = {
            'range_violations': self._check_range_violations(df),
            'referential_integrity': self._check_referential_integrity(df),
            'statistical_outliers': self._detect_statistical_outliers(df),
            'recommendations': []
        }
        results['recommendations'] = self._generate_recommendations(results)
        return results
    
    def _check_range_violations(self, df: pd.DataFrame) -> Dict:
        violations = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 3 * iqr
                upper_bound = q3 + 3 * iqr
                
                below_range = (col_data < lower_bound).sum()
                above_range = (col_data > upper_bound).sum()
                
                if below_range > 0 or above_range > 0:
                    violations[col] = {
                        'below_range_count': int(below_range),
                        'above_range_count': int(above_range),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound),
                        'min_value': float(col_data.min()),
                        'max_value': float(col_data.max())
                    }
        return violations
    
    def _check_referential_integrity(self, df: pd.DataFrame) -> Dict:
        integrity_checks = {}
        columns = df.columns.tolist()
        
        for i, col1 in enumerate(columns):
            for col2 in columns[i+1:]:
                if '_id' in col1.lower() and col2.lower().startswith(col1.replace('_id', '')):
                    unique_ids = set(df[col1].dropna())
                    referenced_ids = set(df[col2].dropna())
                    orphaned = referenced_ids - unique_ids
                    
                    if orphaned:
                        integrity_checks[f"{col2}_to_{col1}"] = {
                            'orphaned_count': len(orphaned),
                            'orphaned_sample': list(orphaned)[:5]
                        }
        return integrity_checks
    
    def _detect_statistical_outliers(self, df: pd.DataFrame) -> Dict:
        outliers = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                mean = col_data.mean()
                std = col_data.std()
                z_scores = np.abs((col_data - mean) / std) if std > 0 else np.zeros(len(col_data))
                outlier_count = (z_scores > 3).sum()
                
                if outlier_count > 0:
                    outliers[col] = {
                        'count': int(outlier_count),
                        'percentage': round((outlier_count / len(col_data)) * 100, 2),
                        'mean': float(mean),
                        'std': float(std)
                    }
        return outliers
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        recommendations = []
        if results['range_violations']:
            recommendations.append(f"Found range violations in {len(results['range_violations'])} columns. Review extreme values.")
        if results['referential_integrity']:
            recommendations.append(f"Found referential integrity issues. Check foreign key relationships.")
        if results['statistical_outliers']:
            recommendations.append(f"Found statistical outliers in {len(results['statistical_outliers'])} columns. Investigate extreme values.")
        return recommendations
