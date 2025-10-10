import React from 'react';
import { CheckCircle, AlertCircle, Info } from 'lucide-react';

const QualityMetricsCard = ({ metrics }) => {
  if (!metrics) return null;

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score) => {
    if (score >= 80) return 'bg-green-50';
    if (score >= 60) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  const metricItems = [
    { label: 'Completeness', value: metrics.completeness_score },
    { label: 'Consistency', value: metrics.consistency_score },
    { label: 'Accuracy', value: metrics.accuracy_score },
    { label: 'Uniqueness', value: metrics.uniqueness_score },
  ];

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-6">Quality Metrics</h2>
      
      <div className="mb-6 p-6 bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg border border-primary-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">Overall Quality Score</p>
            <p className="text-4xl font-bold text-primary-700">
              {metrics.overall_score.toFixed(1)}%
            </p>
          </div>
          <div className={`p-3 rounded-full ${getScoreBg(metrics.overall_score)}`}>
            {metrics.overall_score >= 80 ? (
              <CheckCircle className="w-12 h-12 text-green-600" />
            ) : (
              <AlertCircle className="w-12 h-12 text-yellow-600" />
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {metricItems.map((item) => (
          <div key={item.label} className={`p-4 rounded-lg border ${getScoreBg(item.value)}`}>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">{item.label}</span>
              <span className={`text-2xl font-bold ${getScoreColor(item.value)}`}>
                {item.value.toFixed(1)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default QualityMetricsCard;
