import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/layout/Layout';
import Login from './features/auth/Login';
import Register from './features/auth/Register';
import FileUploader from './features/upload/components/FileUploader';
import DataPreview from './features/upload/components/DataPreview';
import QualityMetricsCard from './features/dashboard/components/QualityMetricsCard';
import AnomalyVisualization from './features/dashboard/components/AnomalyVisualization';
import StrategyList from './features/recommendations/components/StrategyList';
import ChatInterface from './features/chat/ChatInterface';
import ProgressTracker from './features/dashboard/components/ProgressTracker';
import useAppStore from './store/useAppStore';
import { assessQuality, detectAnomalies, generateRecommendations } from './services/api';
import { Play, Loader } from 'lucide-react';
import AIDashboard from './features/dashboard/AIDashboard';

const queryClient = new QueryClient();

const AppContent = ({ activeTab, setActiveTab, onLogout }) => {
  const {
    currentDataset,
    qualityMetrics,
    anomalyResults,
    recommendations,
    setQualityMetrics,
    setAnomalyResults,
    setRecommendations,
    loading,
    setLoading,
  } = useAppStore();

  const [processing, setProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');

  const handleUploadSuccess = (dataset) => {
    setActiveTab('assessment');
  };

  const runQualityAssessment = async () => {
    if (!currentDataset) return;
    setProcessing(true);
    setLoading(true);
    
    const steps = [
      'Loading dataset',
      'Analyzing completeness',
      'Checking consistency',
      'Validating accuracy',
      'Computing uniqueness',
      'Finalizing report'
    ];
    
    try {
      for (const step of steps) {
        setProcessingStep(step);
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      const metrics = await assessQuality(currentDataset.dataset_id);
      setQualityMetrics(metrics);
    } catch (error) {
      console.error('Assessment failed:', error);
    } finally {
      setProcessing(false);
      setLoading(false);
      setProcessingStep('');
    }
  };

  const runAnomalyDetection = async () => {
    if (!currentDataset) return;
    setProcessing(true);
    setLoading(true);
    try {
      const results = await detectAnomalies(currentDataset.dataset_id);
      setAnomalyResults(results);
      setActiveTab('anomaly');
    } catch (error) {
      console.error('Anomaly detection failed:', error);
    } finally {
      setProcessing(false);
      setLoading(false);
    }
  };

  const runRecommendations = async () => {
    if (!currentDataset) return;
    setProcessing(true);
    setLoading(true);
    try {
      const recs = await generateRecommendations(currentDataset.dataset_id);
      setRecommendations(recs);
      setActiveTab('recommendations');
    } catch (error) {
      console.error('Recommendations failed:', error);
    } finally {
      setProcessing(false);
      setLoading(false);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <div className="space-y-6">
            {/* Chat Interface First */}
            <ChatInterface />
            
            {/* Welcome Card Below */}
            <div className="card">
              <h2 className="text-2xl font-bold mb-4">Welcome to AI Data Quality Guardian</h2>
              <p className="text-gray-600 mb-4">
                An intelligent system for comprehensive data quality assessment, anomaly detection, 
                and automated cleaning recommendations powered by local AI models.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-900 mb-2">Quality Assessment</h3>
                  <p className="text-sm text-blue-700">
                    Analyze completeness, consistency, accuracy, and uniqueness metrics
                  </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h3 className="font-semibold text-purple-900 mb-2">Anomaly Detection</h3>
                  <p className="text-sm text-purple-700">
                    ML ensemble models detect outliers and data quality issues
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <h3 className="font-semibold text-green-900 mb-2">AI Recommendations</h3>
                  <p className="text-sm text-green-700">
                    Get actionable cleaning strategies powered by AI 
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'dashboard':
        return <AIDashboard />;

      case 'upload':
        return (
          <div className="space-y-6">
            <FileUploader onUploadSuccess={handleUploadSuccess} />
            <DataPreview dataset={currentDataset} />
          </div>
        );

      case 'assessment':
        return (
          <div className="space-y-6">
            {currentDataset && !qualityMetrics && (
              <div className="card">
                <button
                  onClick={runQualityAssessment}
                  disabled={processing}
                  className="btn btn-primary flex items-center space-x-2"
                >
                  {processing ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>Run Quality Assessment</span>
                    </>
                  )}
                </button>
              </div>
            )}
            
            {processing && (
              <ProgressTracker 
                isActive={processing} 
                currentStep={processingStep}
              />
            )}
            
            {qualityMetrics && <QualityMetricsCard metrics={qualityMetrics} />}
            {qualityMetrics && !anomalyResults && (
              <div className="card">
                <button
                  onClick={runAnomalyDetection}
                  disabled={processing}
                  className="btn btn-primary flex items-center space-x-2"
                >
                  {processing ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      <span>Detecting...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>Run Anomaly Detection</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        );

      case 'anomaly':
        return (
          <div className="space-y-6">
            {anomalyResults && <AnomalyVisualization anomalyResults={anomalyResults} />}
            {anomalyResults && !recommendations && (
              <div className="card">
                <button
                  onClick={runRecommendations}
                  disabled={processing}
                  className="btn btn-primary flex items-center space-x-2"
                >
                  {processing ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>Generate Recommendations</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        );

      case 'recommendations':
        return (
          <div className="space-y-6">
            {recommendations && <StrategyList recommendations={recommendations} />}
          </div>
        );

      default:
        return null;
    }
  };

  return <div>{renderContent()}</div>;
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleRegisterSuccess = () => {
    setShowRegister(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    if (showRegister) {
      return (
        <Register
          onRegisterSuccess={handleRegisterSuccess}
          onSwitchToLogin={() => setShowRegister(false)}
        />
      );
    }
    return (
      <Login
        onLoginSuccess={handleLoginSuccess}
        onSwitchToRegister={() => setShowRegister(true)}
      />
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Layout onLogout={handleLogout}>
        <AppContent />
      </Layout>
    </QueryClientProvider>
  );
}

export default App;