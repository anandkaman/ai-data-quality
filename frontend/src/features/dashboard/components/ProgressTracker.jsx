import React, { useEffect, useState } from 'react';
import { Loader, CheckCircle } from 'lucide-react';

const ProgressTracker = ({ isActive, currentStep }) => {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('Initializing...');

  const steps = [
    'Loading dataset',
    'Analyzing completeness',
    'Checking consistency',
    'Validating accuracy',
    'Computing uniqueness',
    'Finalizing report'
  ];

  useEffect(() => {
    if (isActive && currentStep) {
      const stepIndex = steps.indexOf(currentStep);
      const newProgress = ((stepIndex + 1) / steps.length) * 100;
      setProgress(newProgress);
      setMessage(currentStep);
    }
  }, [isActive, currentStep]);

  if (!isActive) return null;

  return (
    <div className="card">
      <div className="flex items-center space-x-3 mb-4">
        <Loader className="w-5 h-5 text-primary-600 animate-spin" />
        <h3 className="text-lg font-semibold">Processing...</h3>
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>{message}</span>
          <span>{Math.round(progress)}%</span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-primary-600 h-2.5 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>

        <div className="mt-4 space-y-1">
          {steps.map((step, index) => {
            const stepProgress = ((index + 1) / steps.length) * 100;
            const isCompleted = progress >= stepProgress;
            const isCurrent = message === step;

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
  );
};

export default ProgressTracker;
