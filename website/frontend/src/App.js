import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
      setResults(null);
    } else {
      setError('Please select a valid PDF file');
      setFile(null);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    handleFileSelect(selectedFile);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a PDF file first');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/extract', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResults(response.data);
    } catch (error) {
      console.error('Error uploading file:', error);
      setError(error.response?.data?.error || 'Error processing file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (content, filename, type) => {
    const blob = new Blob([content], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const formatJSON = (jsonData) => {
    return JSON.stringify(jsonData, null, 2);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>PDF Text Extractor</h1>
        <p>Upload a PDF file to extract text and structured data</p>
      </header>

      <main className="main-content">
        <div className="upload-section">
          <div
            className={`upload-area ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="upload-content">
              <div className="upload-icon">📄</div>
              <p>Drag and drop your PDF file here, or</p>
              <label className="file-input-label">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="file-input"
                />
                Choose File
              </label>
            </div>
          </div>

          {file && (
            <div className="file-info">
              <p><strong>Selected file:</strong> {file.name}</p>
              <p><strong>Size:</strong> {(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="extract-button"
          >
            {loading ? 'Processing...' : 'Extract Text'}
          </button>
        </div>

        {results && (
          <div className="results-section">
            <h2>Extraction Results</h2>
            
            <div className="results-grid">
              <div className="result-card">
                <div className="result-header">
                  <h3>📝 Text Output</h3>
                  <button
                    onClick={() => downloadFile(results.txtContent, results.txtFilename, 'text/plain')}
                    className="download-button"
                  >
                    Download TXT
                  </button>
                </div>
                <div className="result-content">
                  <pre className="text-preview">
                    {results.txtContent.substring(0, 500)}
                    {results.txtContent.length > 500 ? '...' : ''}
                  </pre>
                </div>
                <p className="result-info">
                  Length: {results.txtContent.length} characters
                </p>
              </div>

              <div className="result-card">
                <div className="result-header">
                  <h3>🔧 JSON Output</h3>
                  <button
                    onClick={() => downloadFile(
                      formatJSON(results.jsonContent),
                      results.jsonFilename,
                      'application/json'
                    )}
                    className="download-button"
                  >
                    Download JSON
                  </button>
                </div>
                <div className="result-content">
                  <pre className="json-preview">
                    {formatJSON(results.jsonContent).substring(0, 500)}
                    {formatJSON(results.jsonContent).length > 500 ? '...' : ''}
                  </pre>
                </div>
                <p className="result-info">
                  Metadata: {Object.keys(results.jsonContent.metadata || {}).length} fields
                  {results.jsonContent.index && ` | Index: ${results.jsonContent.index.length} items`}
                </p>
              </div>
            </div>

            {results.jsonContent.metadata && (
              <div className="metadata-section">
                <h3>📋 Document Metadata</h3>
                <div className="metadata-grid">
                  {Object.entries(results.jsonContent.metadata).map(([key, value]) => (
                    <div key={key} className="metadata-item">
                      <strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                      <span>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Processing your PDF file...</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;