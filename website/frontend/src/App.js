import React, { useState } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import './App.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [currentPage, setCurrentPage] = useState('analyze');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [showWizard, setShowWizard] = useState(false);
  const [wizardStep, setWizardStep] = useState(1);
  const [jobQueue, setJobQueue] = useState([]);

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

  const startWizard = () => {
    setShowWizard(true);
    setWizardStep(1);
  };

  const closeWizard = () => {
    setShowWizard(false);
    setWizardStep(1);
  };

  const nextStep = () => {
    if (wizardStep < 4) setWizardStep(wizardStep + 1);
  };

  const prevStep = () => {
    if (wizardStep > 1) setWizardStep(wizardStep - 1);
  };

  const sidebarItems = [
    { id: 'analyze', label: 'Analyze', icon: '🔍' },
    { id: 'projects', label: 'Projects', icon: '📁' },
    { id: 'compliance', label: 'Compliance', icon: '✅' },
    { id: 'benchmarks', label: 'Benchmarks', icon: '📊' },
    { id: 'workflows', label: 'Workflows', icon: '⚡' },
    { id: 'audit', label: 'Audit', icon: '🔍' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  const renderAnalyzePage = () => (
    <div className="analyze-page">
      {/* Hero Panel */}
      <div className="hero-panel">
        <div className="hero-content">
          <h2>DPR Analysis Dashboard</h2>
          <p>Upload and analyze your Detailed Project Reports with AI-powered insights</p>
        </div>
        
        <div className="upload-hero-area" onClick={startWizard}>
          <div className="upload-icon-large">📄</div>
          <div className="upload-content">
            <h3>Start New Analysis</h3>
            <p>Click to upload your DPR document</p>
            <div className="file-types">
              <span className="file-type">PDF</span>
              <span className="file-type">DOC</span>
              <span className="file-type">DOCX</span>
            </div>
            <p className="size-limit">Maximum file size: 16MB</p>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="quick-stats">
        <div className="stat-card">
          <div className="stat-value">127</div>
          <div className="stat-label">Analyses Completed</div>
          <div className="stat-trend positive">↗ +12%</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">89%</div>
          <div className="stat-label">Avg. Confidence</div>
          <div className="stat-trend positive">↗ +3%</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">3.2s</div>
          <div className="stat-label">Avg. Processing Time</div>
          <div className="stat-trend negative">↘ -0.5s</div>
        </div>
      </div>

      {/* Job Queue */}
      <div className="job-queue">
        <h3>Analysis Queue</h3>
        {jobQueue.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <p>No active analyses</p>
            <button className="start-btn" onClick={startWizard}>Start Analysis</button>
          </div>
        ) : (
          <div className="job-list">
            {jobQueue.map(job => (
              <div key={job.id} className="job-item">
                <div className="job-info">
                  <span className="job-name">{job.name}</span>
                  <div className="job-progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${(job.stage / 6) * 100}%` }}
                      ></div>
                    </div>
                    <span className="progress-text">{Math.round((job.stage / 6) * 100)}%</span>
                  </div>
                </div>
                <div className="stage-indicators">
                  {['Ingest', 'OCR/Layout', 'Extract', 'Feasibility', 'Compliance', 'Export'].map((stage, idx) => (
                    <span key={idx} className={`stage ${job.stage > idx ? 'completed' : job.stage === idx + 1 ? 'active' : 'pending'}`}>
                      {stage}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Results Dashboard */}
      {results && (
        <div className="results-dashboard">
          {/* Header Strip */}
          <div className="results-header">
            <div className="result-info">
              <h2>Analysis Results</h2>
              <div className="result-meta">
                <span>Completed: {new Date().toLocaleDateString()}</span>
                <span>Model: DPR-AI v2.1.0</span>
              </div>
            </div>
            <div className="header-actions">
              <button className="action-btn primary" onClick={() => downloadFile(JSON.stringify(results, null, 2), 'analysis-results.json', 'application/json')}>
                Download Results
              </button>
              <button className="action-btn secondary">View Report</button>
            </div>
          </div>

          {/* Key Metrics Row */}
          <div className="metrics-row">
            <div className="metric-card feasibility">
              <div className="metric-header">
                <h3>Feasibility Score</h3>
                <div className={`status-badge ${results.prediction?.feasibility.toLowerCase()}`}>
                  {results.prediction?.feasibility === 'feasible' ? '✓ FEASIBLE' : '⚠ AT RISK'}
                </div>
              </div>
              <div className="metric-chart">
                <Doughnut
                  data={{
                    datasets: [{
                      data: [
                        (results.prediction?.confidence || 0) * 100, 
                        100 - ((results.prediction?.confidence || 0) * 100)
                      ],
                      backgroundColor: [
                        results.prediction?.feasibility === 'feasible' ? '#10b981' : '#f59e0b',
                        '#f3f4f6'
                      ],
                      borderWidth: 0,
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                      legend: { display: false },
                      tooltip: { enabled: false }
                    }
                  }}
                />
                <div className="chart-center">
                  <div className="confidence-score">
                    {Math.round((results.prediction?.confidence || 0) * 100)}%
                  </div>
                  <div className="confidence-label">Confidence</div>
                </div>
              </div>
            </div>

            <div className="metric-card kpis">
              <h3>Key Performance Indicators</h3>
              <div className="kpi-chart">
                <Bar
                  data={{
                    labels: ['DSCR', 'IRR', 'NPV', 'Payback'],
                    datasets: [{
                      label: 'Performance',
                      data: [1.25, 14.5, 2.5, 8.2],
                      backgroundColor: '#3b82f6',
                      borderRadius: 4,
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: { beginAtZero: true, grid: { display: false } },
                      x: { grid: { display: false } }
                    },
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const labels = ['1.25x', '14.5%', '₹2.5Cr', '8.2 yrs'];
                            return labels[context.dataIndex];
                          }
                        }
                      }
                    }
                  }}
                />
              </div>
            </div>

            <div className="metric-card trends">
              <h3>Analysis Trends</h3>
              <div className="trend-chart">
                <Line
                  data={{
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                      label: 'Feasibility Score',
                      data: [85, 89, 87, 92, 90, Math.round((results.prediction?.confidence || 0) * 100)],
                      borderColor: '#10b981',
                      backgroundColor: 'rgba(16, 185, 129, 0.1)',
                      tension: 0.4,
                      fill: true,
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: { beginAtZero: false, min: 80, max: 100, grid: { display: false } },
                      x: { grid: { display: false } }
                    },
                    plugins: {
                      legend: { display: false }
                    },
                    elements: {
                      point: { radius: 3 }
                    }
                  }}
                />
              </div>
            </div>
          </div>

          {/* Analysis Details */}
          <div className="analysis-details">
            <div className="detail-card key-factors">
              <h3>Key Success Factors</h3>
              <div className="factors-list">
                {results.prediction?.explanation?.top_features?.slice(0, 5).map((feature, idx) => (
                  <div key={idx} className="factor-item">
                    <div className="factor-info">
                      <span className="factor-name">{feature.feature?.replace(/_/g, ' ')}</span>
                      <div className="factor-impact">
                        <div 
                          className="impact-bar"
                          style={{ width: `${(feature.importance || 0) * 100}%` }}
                        ></div>
                        <span className="impact-value">{Math.round((feature.importance || 0) * 100)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="detail-card section-coverage">
              <h3>Document Coverage</h3>
              <div className="coverage-grid">
                {['Executive Summary', 'Technical Specs', 'Market Analysis', 'Financial Projections', 'Timeline', 'Risk Assessment'].map(section => (
                  <div key={section} className="coverage-item">
                    <div className="coverage-header">
                      <span className="section-name">{section}</span>
                      <span className="coverage-percent">{Math.floor(Math.random() * 20) + 80}%</span>
                    </div>
                    <div className="coverage-bar">
                      <div 
                        className="coverage-fill" 
                        style={{ width: `${Math.floor(Math.random() * 20) + 80}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Extracted Content Preview */}
          <div className="content-preview-card">
            <h3>Extracted Content Summary</h3>
            <div className="content-tabs">
              <button className="tab active">Key Highlights</button>
              <button className="tab">Financial Data</button>
              <button className="tab">Risk Factors</button>
            </div>
            <div className="content-area">
              <p>{results.extracted_text?.substring(0, 300)}...</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderProjectsPage = () => (
    <div className="projects-page">
      <h2>Projects</h2>
      <p>Project management and tracking</p>
    </div>
  );

  const renderWizard = () => (
    <div className="wizard-overlay">
      <div className="wizard-modal">
        <div className="wizard-header">
          <h2>Analysis Wizard</h2>
          <button className="close-btn" onClick={closeWizard}>×</button>
        </div>
        
        <div className="wizard-steps">
          <div className={`step ${wizardStep >= 1 ? 'active' : ''}`}>1. Upload</div>
          <div className={`step ${wizardStep >= 2 ? 'active' : ''}`}>2. Metadata</div>
          <div className={`step ${wizardStep >= 3 ? 'active' : ''}`}>3. Options</div>
          <div className={`step ${wizardStep >= 4 ? 'active' : ''}`}>4. Review & Run</div>
        </div>

        <div className="wizard-content">
          {wizardStep === 1 && (
            <div className="wizard-step">
              <h3>Upload Files</h3>
              <div className="file-upload-area">
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                  className="file-input"
                  id="wizardFileInput"
                />
                <label htmlFor="wizardFileInput" className="file-drop-zone">
                  <div className="upload-icon">📁</div>
                  <p>Drop files here or click to browse</p>
                  <div className="validation-chips">
                    <span className="chip success">PDF supported</span>
                    <span className="chip warning">OCR needed for scanned docs</span>
                  </div>
                </label>
                {file && (
                  <div className="file-list">
                    <div className="file-item">
                      <span>{file.name}</span>
                      <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {wizardStep === 2 && (
            <div className="wizard-step">
              <h3>Project Metadata</h3>
              <div className="metadata-form">
                <div className="form-group">
                  <label>Sector</label>
                  <select>
                    <option>Healthcare</option>
                    <option>Infrastructure</option>
                    <option>Education</option>
                    <option>Tourism</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>State/District</label>
                  <input type="text" placeholder="Enter location" />
                </div>
                <div className="form-group">
                  <label>Capex (₹ Crores)</label>
                  <input type="number" placeholder="Project cost" />
                </div>
                <div className="form-group">
                  <label>Sponsor</label>
                  <input type="text" placeholder="Sponsoring organization" />
                </div>
                <div className="toggles">
                  <label className="toggle">
                    <input type="checkbox" />
                    <span>Enable OCR</span>
                  </label>
                  <label className="toggle">
                    <input type="checkbox" />
                    <span>Auto-translate</span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {wizardStep === 3 && (
            <div className="wizard-step">
              <h3>Analysis Options</h3>
              <div className="options-form">
                <div className="slider-group">
                  <label>Confidence Threshold</label>
                  <input type="range" min="50" max="95" defaultValue="80" />
                  <span>80%</span>
                </div>
                <div className="format-options">
                  <label>Output Formats</label>
                  <div className="checkbox-group">
                    <label><input type="checkbox" defaultChecked /> JSON Report</label>
                    <label><input type="checkbox" /> CSV Data</label>
                    <label><input type="checkbox" /> Brief Summary</label>
                    <label><input type="checkbox" /> Compliance Appendix</label>
                  </div>
                </div>
                <div className="webhook-option">
                  <label className="toggle">
                    <input type="checkbox" />
                    <span>Enable webhook notifications</span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {wizardStep === 4 && (
            <div className="wizard-step">
              <h3>Review & Run</h3>
              <div className="summary-table">
                <div className="summary-row">
                  <span>File:</span>
                  <span>{file?.name || 'No file selected'}</span>
                </div>
                <div className="summary-row">
                  <span>Sector:</span>
                  <span>Healthcare</span>
                </div>
                <div className="summary-row">
                  <span>Confidence:</span>
                  <span>80%</span>
                </div>
                <div className="summary-row">
                  <span>Formats:</span>
                  <span>JSON, Brief</span>
                </div>
              </div>
              <button 
                className="start-analysis-btn"
                onClick={async () => {
                  closeWizard();
                  const jobId = Date.now();
                  const newJob = {
                    id: jobId,
                    name: file?.name || 'Analysis Job',
                    stage: 1
                  };
                  setJobQueue([...jobQueue, newJob]);
                  
                  // Simulate job progression
                  for (let stage = 1; stage <= 6; stage++) {
                    setTimeout(() => {
                      setJobQueue(prev => prev.map(job => 
                        job.id === jobId ? { ...job, stage } : job
                      ));
                    }, stage * 2000);
                  }
                  
                  // Run actual analysis
                  await handleUpload();
                }}
                disabled={!file}
              >
                Start Analysis
              </button>
            </div>
          )}
        </div>

        <div className="wizard-footer">
          {wizardStep > 1 && (
            <button className="btn-secondary" onClick={prevStep}>Previous</button>
          )}
          {wizardStep < 4 && (
            <button className="btn-primary" onClick={nextStep}>Next</button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="app-enterprise">
      {/* Top Bar */}
      <header className="top-bar">
        <div className="top-bar-left">
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          >
            ☰
          </button>
          <h1 className="product-name">DPR Analysis Platform</h1>
          <div className="global-search">
            <input type="text" placeholder="Search projects, runs, rules..." />
            <span className="search-icon">🔍</span>
          </div>
        </div>
        <div className="top-bar-right">
          <button className="notification-btn">🔔</button>
          <button className="help-btn">❓</button>
          <div className="profile-menu">
            <div className="profile-avatar">👤</div>
            <div className="profile-info">
              <span className="username">Analyst</span>
              <span className="role">MDONER</span>
            </div>
          </div>
        </div>
      </header>

      <div className="main-layout">
        {/* Left Sidebar */}
        <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
          <nav className="sidebar-nav">
            {sidebarItems.map(item => (
              <button
                key={item.id}
                className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
                onClick={() => setCurrentPage(item.id)}
              >
                <span className="nav-icon">{item.icon}</span>
                {!sidebarCollapsed && <span className="nav-label">{item.label}</span>}
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          {currentPage === 'analyze' && renderAnalyzePage()}
          {currentPage === 'projects' && renderProjectsPage()}
          {currentPage === 'compliance' && (
            <div><h2>Compliance Center</h2><p>MDONER/NEC compliance checking</p></div>
          )}
          {currentPage === 'benchmarks' && (
            <div><h2>Benchmarks</h2><p>Sector presets and custom benchmarks</p></div>
          )}
          {currentPage === 'workflows' && (
            <div><h2>Workflows</h2><p>Task management and approval flows</p></div>
          )}
          {currentPage === 'audit' && (
            <div><h2>Audit Trail</h2><p>Activity timeline and change tracking</p></div>
          )}
          {currentPage === 'settings' && (
            <div><h2>Settings</h2><p>System configuration and preferences</p></div>
          )}
        </main>
      </div>

      {/* Wizard Modal */}
      {showWizard && renderWizard()}

      {/* Error Toast */}
      {error && (
        <div className="toast error-toast">
          <span>{error}</span>
          <button onClick={() => setError('')}>×</button>
        </div>
      )}
    </div>
  );
}

export default App;