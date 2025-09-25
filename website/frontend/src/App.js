import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid PDF file');
      setFile(null);
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
      const response = await axios.post('http://localhost:5000/api/extract', formData, {
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

  return (
    <div className="app">
      <div className="container">
        {/* Header */}
        <header className="header">
          <h1>DPR Analysis</h1>
          <p>AI-powered feasibility analysis for project reports</p>
        </header>

        {/* Upload Section */}
        <div className="upload-section">
          <div className="upload-area">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="file-input"
              id="fileInput"
            />
            <label htmlFor="fileInput" className="file-label">
              <div className="upload-icon">📄</div>
              <span>{file ? file.name : 'Choose PDF file'}</span>
            </label>
            
            <button 
              onClick={handleUpload} 
              disabled={!file || loading}
              className="analyze-btn"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
          
          {error && <div className="error">{error}</div>}
        </div>

        {/* Results Section */}
        {results && (
          <div className="results">
            {/* AI Prediction Card */}
            {results.prediction && results.prediction.ai_analysis_available && (
              <div className="card prediction-card">
                <h3>AI Analysis</h3>
                <div className="prediction-result">
                  <div className={`status ${results.prediction.feasibility.toLowerCase()}`}>
                    {results.prediction.feasibility === 'feasible' ? '✓' : '⚠'} 
                    {results.prediction.feasibility.toUpperCase()}
                  </div>
                  <div className="confidence">
                    Confidence: {Math.round(results.prediction.confidence * 100)}%
                  </div>
                </div>
                
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ 
                      width: `${results.prediction.confidence * 100}%`,
                      backgroundColor: results.prediction.feasibility === 'feasible' ? '#10b981' : '#ef4444'
                    }}
                  ></div>
                </div>

                {results.prediction.explanation && results.prediction.explanation.top_features && (
                  <div className="explanations">
                    <h4>Key Factors</h4>
                    <div className="features">
                      {results.prediction.explanation.top_features.slice(0, 3).map((feature, idx) => (
                        <span key={idx} className="feature-tag">
                          {feature.feature.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Text Content Card */}
            <div className="card content-card">
              <h3>Extracted Content</h3>
              <div className="content-preview">
                {results.txtContent ? results.txtContent.substring(0, 200) + '...' : 'No text extracted'}
              </div>
              <div className="stats">
                <span>Characters: {results.txtContent ? results.txtContent.length : 0}</span>
              </div>
            </div>

            {/* Download Section */}
            <div className="card download-card">
              <h3>Download Results</h3>
              <div className="download-buttons">
                {results.txtContent && (
                  <button 
                    onClick={() => downloadFile(results.txtContent, results.txtFilename || 'analysis.txt', 'text/plain')}
                    className="download-btn"
                  >
                    Text File
                  </button>
                )}
                {results.jsonContent && (
                  <button 
                    onClick={() => downloadFile(JSON.stringify(results.jsonContent, null, 2), results.jsonFilename || 'analysis.json', 'application/json')}
                    className="download-btn"
                  >
                    JSON Data
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;