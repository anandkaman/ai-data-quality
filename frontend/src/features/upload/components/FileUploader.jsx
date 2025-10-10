import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, CheckCircle, XCircle } from 'lucide-react';
import { uploadDataset } from '@/services/api';
import useAppStore from '@/store/useAppStore';

const FileUploader = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const { setCurrentDataset, setError, reset } = useAppStore();

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setUploadStatus(null);

    try {
      // Reset all previous data
      reset();
      
      const response = await uploadDataset(file);
      setCurrentDataset(response);
      setUploadStatus('success');
      onUploadSuccess?.(response);
    } catch (error) {
      setUploadStatus('error');
      setError(error.message);
    } finally {
      setUploading(false);
    }
  }, [setCurrentDataset, setError, reset, onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    multiple: false,
  });

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Upload Dataset</h2>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
        }`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          <Upload className="w-16 h-16 text-gray-400" />
          
          {uploading ? (
            <div>
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Uploading...</p>
            </div>
          ) : (
            <>
              <div>
                <p className="text-lg font-medium text-gray-700">
                  {isDragActive ? 'Drop your file here' : 'Drag and drop your dataset'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or click to browse
                </p>
              </div>
              <p className="text-xs text-gray-400">
                Supported formats: CSV, XLS, XLSX
              </p>
            </>
          )}
        </div>
      </div>

      {uploadStatus === 'success' && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <span className="text-green-800">File uploaded successfully!</span>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
          <XCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-800">Upload failed. Please try again.</span>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
