
import React, { useState, useEffect, useRef } from 'react';
import { RefreshCw, Download, Check, Loader, ChevronDown, Terminal, X } from 'lucide-react';
import axios from 'axios';

const ModelSwitcher = ({ onModelChange }) => {
  const [models, setModels] = useState([]);
  const [currentModel, setCurrentModel] = useState('gemma2:2b');
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showTerminal, setShowTerminal] = useState(false);
  const [terminalLogs, setTerminalLogs] = useState([]);
  const [pullingModel, setPullingModel] = useState(null);
  const terminalRef = useRef(null);
  const dropdownRef = useRef(null);

  const API_BASE = 'http://localhost:8000/api/v1/models';

  useEffect(() => {
    loadAvailableModels();
  }, []);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalLogs]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadAvailableModels = async () => {
    try {
      const response = await axios.get(`${API_BASE}/available`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setModels(response.data.models);
      setCurrentModel(response.data.current_model);
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const addLog = (content, type = 'info') => {
    setTerminalLogs(prev => [...prev, {
      content,
      type,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  const pullModel = async (modelName) => {
    setPullingModel(modelName);
    setShowTerminal(true);
    setTerminalLogs([]);
    addLog(`Starting to pull ${modelName}...`, 'info');

    try {
      const eventSource = new EventSource(
        `${API_BASE}/pull/${encodeURIComponent(modelName)}`
      );

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'log') {
          addLog(data.content, 'info');
        } else if (data.type === 'success') {
          addLog(data.content, 'success');
          setPullingModel(null);
          loadAvailableModels();
          eventSource.close();
        } else if (data.type === 'error') {
          addLog(data.content, 'error');
          setPullingModel(null);
          eventSource.close();
        }
      };

      eventSource.onerror = () => {
        addLog('Connection error', 'error');
        setPullingModel(null);
        eventSource.close();
      };

    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
      setPullingModel(null);
    }
  };

  const switchModel = async (modelName) => {
    setLoading(true);
    addLog(`Switching to ${modelName}...`, 'info');

    try {
      const response = await axios.post(
        `${API_BASE}/switch`,
        { model_name: modelName },
        { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }
      );

      if (response.data.requires_pull) {
        addLog(response.data.message, 'warning');
        await pullModel(modelName);
      } else if (response.data.success) {
        setCurrentModel(modelName);
        addLog(response.data.message, 'success');
        onModelChange?.(modelName);
        setShowDropdown(false);
      }
    } catch (error) {
      addLog(`Failed to switch model: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const popularModels = [
    { name: 'gemma2:2b', description: 'Gemma 2 - 2B params (Fast, Good for general use)' },
    { name: 'llama3.2', description: 'Llama 3.2 - Latest from Meta' },
    { name: 'mistral', description: 'Mistral 7B - Balanced performance' },
    { name: 'phi3', description: 'Phi-3 - Microsoft\'s small model' },
    { name: 'qwen2.5', description: 'Qwen 2.5 - Strong multilingual' },
  ];

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Model Selector Button */}
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        disabled={loading}
      >
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        <span className="text-sm font-medium">{currentModel}</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${showDropdown ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {showDropdown && (
        <div className="absolute top-full mt-2 right-0 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-hidden flex flex-col">
          <div className="p-3 border-b border-gray-200 bg-gray-50">
            <h3 className="font-semibold text-sm">Select Model</h3>
            <p className="text-xs text-gray-600 mt-1">Switch between different LLM models</p>
          </div>

          <div className="flex-1 overflow-y-auto">
            {/* Current Models */}
            {models.length > 0 && (
              <div className="p-2">
                <p className="text-xs font-semibold text-gray-500 px-2 py-1">INSTALLED MODELS</p>
                {models.map((model) => (
                  <button
                    key={model.name}
                    onClick={() => switchModel(model.name)}
                    disabled={loading || currentModel === model.name}
                    className={`w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors ${
                      currentModel === model.name ? 'bg-primary-50 border border-primary-200' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-sm">{model.name}</div>
                        <div className="text-xs text-gray-500">
                          {(model.size / 1e9).toFixed(2)} GB
                        </div>
                      </div>
                      {currentModel === model.name && (
                        <Check className="w-4 h-4 text-primary-600" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Popular Models to Install */}
            <div className="p-2 border-t border-gray-200">
              <p className="text-xs font-semibold text-gray-500 px-2 py-1">POPULAR MODELS</p>
              {popularModels.map((model) => {
                const isInstalled = models.some(m => m.name === model.name);
                const isPulling = pullingModel === model.name;

                return (
                  <div
                    key={model.name}
                    className="px-3 py-2 rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-sm">{model.name}</div>
                        <div className="text-xs text-gray-500">{model.description}</div>
                      </div>
                      {!isInstalled && !isPulling && (
                        <button
                          onClick={() => pullModel(model.name)}
                          className="p-1 hover:bg-blue-100 rounded text-blue-600"
                          title="Pull this model"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      )}
                      {isPulling && (
                        <Loader className="w-4 h-4 text-blue-600 animate-spin" />
                      )}
                      {isInstalled && (
                        <Check className="w-4 h-4 text-green-600" />
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Terminal Toggle */}
          <div className="border-t border-gray-200 p-2">
            <button
              onClick={() => setShowTerminal(!showTerminal)}
              className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <div className="flex items-center space-x-2">
                <Terminal className="w-4 h-4" />
                <span className="text-sm font-medium">Terminal Logs</span>
              </div>
              <ChevronDown className={`w-4 h-4 transition-transform ${showTerminal ? 'rotate-180' : ''}`} />
            </button>
          </div>
        </div>
      )}

      {/* Terminal Window */}
      {showTerminal && (
        <div className="fixed bottom-4 right-4 w-[600px] h-[400px] bg-gray-900 rounded-lg shadow-2xl z-50 flex flex-col">
          <div className="flex items-center justify-between px-4 py-2 bg-gray-800 rounded-t-lg">
            <div className="flex items-center space-x-2">
              <Terminal className="w-4 h-4 text-green-400" />
              <span className="text-sm font-medium text-white">Ollama Terminal</span>
            </div>
            <button
              onClick={() => setShowTerminal(false)}
              className="p-1 hover:bg-gray-700 rounded text-gray-400"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div
            ref={terminalRef}
            className="flex-1 overflow-y-auto p-4 font-mono text-xs text-green-400 space-y-1"
          >
            {terminalLogs.length === 0 ? (
              <div className="text-gray-500">No logs yet...</div>
            ) : (
              terminalLogs.map((log, idx) => (
                <div
                  key={idx}
                  className={`${
                    log.type === 'error' ? 'text-red-400' :
                    log.type === 'success' ? 'text-green-400' :
                    log.type === 'warning' ? 'text-yellow-400' :
                    'text-gray-300'
                  }`}
                >
                  <span className="text-gray-500">[{log.timestamp}]</span> {log.content}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelSwitcher;
