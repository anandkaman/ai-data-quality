import React from 'react';
import { Database, Activity, LogOut } from 'lucide-react';

const Header = ({ onLogout }) => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-3">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                AI Data Quality Asistant 
              </h1>
              <p className="text-sm text-gray-500">
                Intelligent Data Quality Assessment & Anomaly Detection
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm">
              <Activity className="w-4 h-4 text-green-500" />
              <span className="text-gray-600">System Online</span>
            </div>
            
            {onLogout && (
              <button
                onClick={onLogout}
                className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
