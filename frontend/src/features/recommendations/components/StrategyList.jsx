import React from 'react';
import { Lightbulb, AlertTriangle, TrendingUp, CheckSquare } from 'lucide-react';

const StrategyList = ({ recommendations }) => {
  if (!recommendations) return null;

  const { priority_ranking = [], strategies = [], implementation_order = [] } = recommendations;

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-6">Cleaning Recommendations</h2>

      {priority_ranking.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-3 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-orange-600" />
            Priority Issues
          </h3>
          <div className="space-y-2">
            {priority_ranking.map((item, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${
                  item.severity === 'high'
                    ? 'bg-red-50 border-red-200'
                    : item.severity === 'medium'
                    ? 'bg-yellow-50 border-yellow-200'
                    : 'bg-blue-50 border-blue-200'
                }`}
              >
                <div className="flex justify-between items-start">
                  <span className="font-medium">{item.issue}</span>
                  <span
                    className={`px-2 py-1 text-xs rounded ${
                      item.severity === 'high'
                        ? 'bg-red-600 text-white'
                        : item.severity === 'medium'
                        ? 'bg-yellow-600 text-white'
                        : 'bg-blue-600 text-white'
                    }`}
                  >
                    {item.severity}
                  </span>
                </div>
                {item.impact && (
                  <p className="text-sm text-gray-600 mt-1">{item.impact}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {strategies.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-3 flex items-center">
            <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
            Recommended Strategies
          </h3>
          <div className="space-y-4">
            {strategies.map((strategy, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-2">
                  {strategy.issue_type}
                </h4>
                
                {strategy.affected_columns && (
                  <div className="mb-2">
                    <span className="text-sm font-medium text-gray-700">Affected Columns: </span>
                    <span className="text-sm text-gray-600">
                      {strategy.affected_columns.join(', ')}
                    </span>
                  </div>
                )}
                
                {strategy.root_cause && (
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Root Cause:</strong> {strategy.root_cause}
                  </p>
                )}
                
                {strategy.recommended_approach && (
                  <div className="mb-2">
                    <p className="text-sm font-medium text-gray-700 mb-1">Approach:</p>
                    <p className="text-sm text-gray-600">
                      {strategy.recommended_approach.method || JSON.stringify(strategy.recommended_approach)}
                    </p>
                  </div>
                )}
                
                {strategy.expected_improvement && (
                  <div className="flex items-center text-sm text-green-600 mb-2">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    {strategy.expected_improvement}
                  </div>
                )}
                
                {strategy.risks && strategy.risks.length > 0 && (
                  <div className="mt-2 p-2 bg-yellow-50 rounded border border-yellow-200">
                    <p className="text-xs font-medium text-yellow-800 mb-1">Risks:</p>
                    <ul className="text-xs text-yellow-700 list-disc list-inside">
                      {strategy.risks.map((risk, idx) => (
                        <li key={idx}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {implementation_order.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-3 flex items-center">
            <CheckSquare className="w-5 h-5 mr-2 text-green-600" />
            Implementation Order
          </h3>
          <ol className="list-decimal list-inside space-y-1">
            {implementation_order.map((step, index) => (
              <li key={index} className="text-gray-700">
                {step}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
};

export default StrategyList;
