import React from 'react';
import { FileText, Database, Columns } from 'lucide-react';

const DataPreview = ({ dataset }) => {
  if (!dataset) return null;

  return (
    <div className="card mt-6">
      <h3 className="text-lg font-semibold mb-4">Dataset Preview</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg">
          <FileText className="w-8 h-8 text-blue-600" />
          <div>
            <p className="text-sm text-gray-600">Filename</p>
            <p className="font-medium text-gray-900">{dataset.filename}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3 p-4 bg-green-50 rounded-lg">
          <Database className="w-8 h-8 text-green-600" />
          <div>
            <p className="text-sm text-gray-600">Total Rows</p>
            <p className="font-medium text-gray-900">{dataset.row_count.toLocaleString()}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3 p-4 bg-purple-50 rounded-lg">
          <Columns className="w-8 h-8 text-purple-600" />
          <div>
            <p className="text-sm text-gray-600">Columns</p>
            <p className="font-medium text-gray-900">{dataset.column_count}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataPreview;
