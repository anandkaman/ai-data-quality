import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const AnomalyVisualization = ({ anomalyResults }) => {
  if (!anomalyResults) return null;

  const data = Object.entries(anomalyResults.feature_importance || {})
    .slice(0, 10)
    .map(([feature, importance]) => ({
      feature: feature.length > 15 ? feature.substring(0, 15) + '...' : feature,
      importance: (importance * 100).toFixed(2),
    }));

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-6">Anomaly Detection Results</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-red-50 rounded-lg border border-red-200">
          <p className="text-sm text-gray-600 mb-1">Anomalies Detected</p>
          <p className="text-3xl font-bold text-red-600">
            {anomalyResults.anomaly_count}
          </p>
        </div>
        
        <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
          <p className="text-sm text-gray-600 mb-1">Anomaly Rate</p>
          <p className="text-3xl font-bold text-orange-600">
            {anomalyResults.anomaly_percentage.toFixed(2)}%
          </p>
        </div>
        
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-gray-600 mb-1">Detection Method</p>
          <p className="text-lg font-bold text-blue-600">
            ML Ensemble
          </p>
        </div>
      </div>

      {data.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-4">Feature Importance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="feature" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="importance" fill="#0ea5e9" name="Importance (%)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default AnomalyVisualization;
