import React from 'react';
import { Upload, BarChart3, AlertTriangle, Lightbulb, Home, LineChart } from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'assessment', label: 'Assessment', icon: BarChart3 },
    { id: 'anomaly', label: 'Anomalies', icon: AlertTriangle },
    { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
    { id: 'dashboard', label: 'AI Dashboard', icon: LineChart },
  ];

  const handleTabClick = (tabId) => {
    // Change tab first
    setActiveTab(tabId);
    
    // Force immediate scroll reset
    requestAnimationFrame(() => {
      const mainContent = document.querySelector('main');
      if (mainContent) {
        mainContent.scrollTo(0, 0);
        mainContent.scrollTop = 0;
      }
      
      window.scrollTo(0, 0);
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    });
  };

  return (
    <aside className="w-64 bg-white shadow-sm border-r border-gray-200 h-full overflow-y-auto">
      <nav className="p-4 space-y-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-primary-50 text-primary-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar;
