import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Columns, Sparkles, Loader, Download, CheckCircle, Info, TrendingUp, BarChart, Upload, Printer } from 'lucide-react';
import Plot from 'react-plotly.js';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import useAppStore from '@/store/useAppStore';
import { uploadDataset } from '@/services/api';

const AIDashboard = () => {
  const { currentDataset, setCurrentDataset, dashboardData, setDashboardData, reset } = useAppStore();
  const [numColumns, setNumColumns] = useState(2);
  const [prompt, setPrompt] = useState('');
  const [items, setItems] = useState([]);
  const [analysis, setAnalysis] = useState('');
  const [dashboardId, setDashboardId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [uploadingFile, setUploadingFile] = useState(false);
  const printRef = useRef(null);

  useEffect(() => {
    if (dashboardData) {
      setItems(dashboardData.items || []);
      setAnalysis(dashboardData.analysis || '');
      setDashboardId(dashboardData.dashboardId || null);
      setNumColumns(dashboardData.numColumns || 2);
      setPrompt(dashboardData.prompt || '');
    }
  }, [dashboardData]);

  const steps = [
    'Analyzing dataset structure',
    'Consulting Gemma 2:2b',
    'Calculating key metrics',
    'Generating visualizations',
    'Preparing dashboard'
  ];

  const examplePrompts = [
    "Show key metrics and distributions with blue colors",
    "Display sales trends and customer statistics",
    "Analyze correlations with metric summaries",
    "Compare categories and show totals"
  ];

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploadingFile(true);

    try {
      reset();
      setItems([]);
      setAnalysis('');
      setDashboardId(null);
      
      const response = await uploadDataset(file);
      setCurrentDataset(response);
      
      alert('Dataset uploaded successfully! You can now generate dashboard.');
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload dataset. Please try again.');
    } finally {
      setUploadingFile(false);
    }
  }, [setCurrentDataset, reset]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    multiple: false,
    noClick: true,
  });

  const generateDashboard = async () => {
    if (!currentDataset) {
      alert('Please upload a dataset first');
      return;
    }

    setLoading(true);
    setItems([]);
    setAnalysis('');
    
    try {
      for (let i = 0; i < steps.length; i++) {
        setProcessingStep(steps[i]);
        await new Promise(resolve => setTimeout(resolve, 600));
      }

      const response = await axios.post(
        'http://localhost:8000/api/v1/ai-dashboard/generate',
        {
          dataset_id: currentDataset.dataset_id,
          num_columns: numColumns,
          prompt: prompt || null
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      setItems(response.data.items);
      setAnalysis(response.data.analysis);
      setDashboardId(response.data.dashboard_id);
      setProcessingStep('Complete!');

      setDashboardData({
        items: response.data.items,
        analysis: response.data.analysis,
        dashboardId: response.data.dashboard_id,
        numColumns: numColumns,
        prompt: prompt,
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      console.error('Dashboard generation failed:', error);
      setProcessingStep('');
    } finally {
      setLoading(false);
      setTimeout(() => setProcessingStep(''), 2000);
    }
  };

  const handlePrintPDF = () => {
    window.print();
  };

  const renderMetricCard = (metric) => {
    const colors = {
      count: 'bg-blue-50 border-blue-200 text-blue-900',
      sum: 'bg-green-50 border-green-200 text-green-900',
      avg: 'bg-purple-50 border-purple-200 text-purple-900',
      min: 'bg-orange-50 border-orange-200 text-orange-900',
      max: 'bg-red-50 border-red-200 text-red-900',
      median: 'bg-indigo-50 border-indigo-200 text-indigo-900'
    };

    const icons = {
      count: BarChart,
      sum: TrendingUp,
      avg: TrendingUp,
      min: TrendingUp,
      max: TrendingUp,
      median: TrendingUp
    };

    const colorClass = colors[metric.metric_type] || 'bg-gray-50 border-gray-200 text-gray-900';
    const Icon = icons[metric.metric_type] || BarChart;

    return (
      <div className={`card ${colorClass} border-2 hover:shadow-lg transition-all print:shadow-none print:border print:break-inside-avoid`}>
        <div className="flex items-start justify-between mb-2">
          <Icon className="w-6 h-6 opacity-60" />
          <span className="text-xs uppercase font-semibold opacity-60">
            {metric.metric_type}
          </span>
        </div>
        <div className="text-4xl font-bold mb-2">{metric.value}</div>
        <div className="text-sm font-medium mb-1">{metric.title}</div>
        <div className="text-xs opacity-75">{metric.description}</div>
      </div>
    );
  };

  return (
    <>
      <style>{`
        @media print {
          /* Hide everything except printable content */
          body * {
            visibility: hidden;
          }
          
          #printable-dashboard,
          #printable-dashboard * {
            visibility: visible;
          }
          
          #printable-dashboard {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            padding: 20px;
          }
          
          /* A4 landscape or custom size */
          @page {
            size: A3 landscape;
            margin: 15mm;
          }
          
          /* Ensure proper page breaks */
          .print\\:break-inside-avoid {
            break-inside: avoid;
            page-break-inside: avoid;
          }
          
          /* Remove interactive elements */
          button, input, textarea {
            display: none !important;
          }
          
          /* Adjust card styling for print */
          .card {
            box-shadow: none !important;
            border: 1px solid #ccc !important;
            margin-bottom: 10px;
          }
          
          /* Ensure charts fit properly */
          .js-plotly-plot {
            max-width: 100% !important;
            height: auto !important;
          }
          
          /* Grid adjustments */
          .grid {
            display: grid !important;
          }
          
          /* Hide scrollbars */
          * {
            overflow: visible !important;
          }
          
          /* Ensure colors print */
          * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            color-adjust: exact !important;
          }
        }
      `}</style>

      <div className="space-y-6 print:hidden">
        {/* Dataset Info with Upload Button */}
        <div className="card bg-gradient-to-r from-gray-50 to-blue-50 border border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              {currentDataset ? (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Current Dataset</h3>
                  <p className="text-sm text-gray-600">
                    {currentDataset.filename} ({currentDataset.row_count} rows × {currentDataset.column_count} columns)
                  </p>
                </div>
              ) : (
                <div>
                  <h3 className="text-lg font-semibold text-gray-700">No Dataset Loaded</h3>
                  <p className="text-sm text-gray-500">Upload a dataset to get started</p>
                </div>
              )}
            </div>
            
            <div {...getRootProps()} className="ml-4">
              <input {...getInputProps()} />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  document.querySelector('input[type="file"]').click();
                }}
                disabled={uploadingFile || loading}
                className="btn bg-primary-600 text-white hover:bg-primary-700 flex items-center space-x-2"
                title={currentDataset ? "Replace dataset" : "Upload dataset"}
              >
                {uploadingFile ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    <span>Uploading...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5" />
                    <span>{currentDataset ? 'Replace' : 'Upload'}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-2xl font-semibold mb-4">AI-Powered Dashboard Generator</h2>
          <p className="text-gray-600 mb-6">
            Gemma 2:2b will analyze your data and create a comprehensive dashboard with key metrics and visualizations
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dashboard Columns
              </label>
              <div className="flex space-x-4">
                <button
                  onClick={() => setNumColumns(2)}
                  disabled={loading}
                  className={`flex items-center space-x-2 px-6 py-3 rounded-lg border transition-colors ${
                    numColumns === 2
                      ? 'border-primary-600 bg-primary-50 text-primary-700'
                      : 'border-gray-300 hover:bg-gray-50'
                  } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <Columns className="w-5 h-5" />
                  <span>2 Columns</span>
                </button>
                <button
                  onClick={() => setNumColumns(3)}
                  disabled={loading}
                  className={`flex items-center space-x-2 px-6 py-3 rounded-lg border transition-colors ${
                    numColumns === 3
                      ? 'border-primary-600 bg-primary-50 text-primary-700'
                      : 'border-gray-300 hover:bg-gray-50'
                  } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <Columns className="w-5 h-5" />
                  <span>3 Columns</span>
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                AI will generate as many items as needed. This controls column layout only.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
                <span>Analysis Preferences</span>
                <div className="group relative">
                  <Info className="w-4 h-4 text-gray-400 cursor-help" />
                  <div className="hidden group-hover:block absolute left-0 top-6 w-96 p-3 bg-gray-800 text-white text-xs rounded-lg shadow-lg z-10">
                    <p className="font-semibold mb-2">Gemma 2:2b will generate:</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Metric cards for simple stats (totals, averages, counts)</li>
                      <li>Charts for patterns and relationships</li>
                      <li>Mix based on your request and data characteristics</li>
                      <li>As many items as needed (not limited to fixed number)</li>
                    </ul>
                  </div>
                </div>
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g., Show key financial metrics and sales trends with blue colors"
                className="input resize-none"
                rows={3}
                disabled={loading}
              />
              <div className="mt-2 flex flex-wrap gap-2">
                <span className="text-xs text-gray-500">Examples:</span>
                {examplePrompts.map((example, idx) => (
                  <button
                    key={idx}
                    onClick={() => setPrompt(example)}
                    className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded"
                    disabled={loading}
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={generateDashboard}
                disabled={loading || !currentDataset}
                className="btn btn-primary flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Generate Dashboard</span>
                  </>
                )}
              </button>

              {items.length > 0 && dashboardId && (
                <button
                  onClick={handlePrintPDF}
                  className="btn bg-green-600 text-white hover:bg-green-700 flex items-center space-x-2"
                  title="Print dashboard to PDF (Ctrl+P)"
                >
                  <Printer className="w-5 h-5" />
                  <span>Print to PDF</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {loading && processingStep && (
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <Loader className="w-5 h-5 text-primary-600 animate-spin" />
              <h3 className="text-lg font-semibold">Processing Dashboard</h3>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>{processingStep}</span>
                <span>{Math.round(((steps.indexOf(processingStep) + 1) / steps.length) * 100)}%</span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-primary-600 h-2.5 rounded-full transition-all duration-300"
                  style={{ width: `${((steps.indexOf(processingStep) + 1) / steps.length) * 100}%` }}
                ></div>
              </div>

              <div className="mt-4 space-y-1">
                {steps.map((step, index) => {
                  const isCompleted = steps.indexOf(processingStep) >= index;
                  const isCurrent = processingStep === step;
                  return (
                    <div
                      key={index}
                      className={`flex items-center space-x-2 text-sm ${
                        isCompleted ? 'text-green-600' : isCurrent ? 'text-primary-600' : 'text-gray-400'
                      }`}
                    >
                      {isCompleted ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : (
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          isCurrent ? 'border-primary-600' : 'border-gray-300'
                        }`}></div>
                      )}
                      <span>{step}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Printable Dashboard Section */}
      <div id="printable-dashboard" ref={printRef}>
        {/* Print Header */}
        <div className="hidden print:block mb-6">
          <h1 className="text-3xl font-bold text-center text-primary-600 mb-2">
            AI Data Quality Guardian
          </h1>
          <h2 className="text-xl text-center text-gray-700 mb-4">Dashboard Report</h2>
          {currentDataset && (
            <div className="text-center text-sm text-gray-600 mb-4">
              <p><strong>Dataset:</strong> {currentDataset.filename}</p>
              <p><strong>Generated:</strong> {new Date().toLocaleString()}</p>
              {prompt && <p><strong>Analysis Request:</strong> {prompt}</p>}
            </div>
          )}
          <hr className="border-gray-300 mb-4" />
        </div>

        {analysis && !loading && (
          <div className="card bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 mb-6 print:break-inside-avoid">
            <h3 className="text-lg font-semibold mb-2 text-blue-900 flex items-center space-x-2">
              <Sparkles className="w-5 h-5 print:hidden" />
              <span>AI Analysis by Gemma 2:2b</span>
            </h3>
            <p className="text-blue-800 leading-relaxed">{analysis}</p>
          </div>
        )}

        {items.length > 0 && !loading && (
          <div className={`grid ${numColumns === 2 ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'} gap-4`}>
            {items.map((item, idx) => {
              if (item.type === 'metric_card' && item.metric_card) {
                return (
                  <div key={idx}>
                    {renderMetricCard(item.metric_card)}
                  </div>
                );
              } else if (item.plotly_json) {
                const plotData = JSON.parse(item.plotly_json);
                return (
                  <div key={idx} className="card hover:shadow-xl transition-all duration-300 group print:shadow-none print:border print:break-inside-avoid">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-lg font-semibold group-hover:text-primary-600 transition-colors print:text-gray-900">
                        {item.title}
                      </h3>
                      <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded print:bg-gray-200 print:text-gray-700">
                        {item.type}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{item.description}</p>
                    <div className="bg-gray-50 rounded-lg p-2 border border-gray-200 print:bg-white">
                      <Plot
                        data={plotData.data}
                        layout={{
                          ...plotData.layout,
                          autosize: true,
                          margin: { l: 50, r: 30, t: 40, b: 50 },
                        }}
                        config={{
                          responsive: true,
                          displayModeBar: true,
                          displaylogo: false,
                          modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                          staticPlot: window.matchMedia('print').matches, // Static for print
                        }}
                        style={{ width: '100%', height: '400px' }}
                      />
                    </div>
                  </div>
                );
              }
              return null;
            })}
          </div>
        )}

        {/* Print Footer */}
        <div className="hidden print:block mt-8 pt-4 border-t border-gray-300 text-center text-sm text-gray-600">
          <p>Generated by AI Data Quality Guardian - Powered by Gemma 2:2b</p>
          <p className="text-xs mt-1">Page generated on {new Date().toLocaleString()}</p>
        </div>
      </div>
    </>
  );
};

export default AIDashboard;
