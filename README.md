# PRAGATI

![DPR Analysis](https://img.shields.io/badge/DPR%20Analysis-AI%20Platform-blue)
![ML Accuracy](https://img.shields.io/badge/ML%20Accuracy-91%25-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18.2.0-61dafb)
![XGBoost](https://img.shields.io/badge/XGBoost-3.0.5-orange)

**Project Review and Governance AI-based Transparency Interface**

An enterprise-grade AI platform for automated Detailed Project Report (DPR) analysis with ML-driven feasibility assessment and governance compliance validation.

## Core Technologies

| Component | Stack | Purpose |
|-----------|-------|---------|
| **ML Engine** | XGBoost 3.0.5 + scikit-learn 1.7.2 | Feasibility classification (91% accuracy) |
| **NLP Pipeline** | TF-IDF + pandas 2.3.0 | Feature extraction & text vectorization |
| **Document Processing** | pdfminer.six + pytesseract | PDF parsing & OCR processing |
| **Backend API** | Flask 2.3.3 | RESTful services & CORS handling |
| **Frontend** | React 18.2.0 + Chart.js 4.4.0 | Interactive dashboard with real-time viz |
| **Charts Integration** | react-chartjs-2 3.3.0 | Doughnut, Bar, Line charts for insights |


## System Architecture

<img src="./assets/Mermaid%20Chart%20-%20Create%20complex%2C%20visual%20diagrams%20with%20text.%20A%20smarter%20way%20of%20creating%20diagrams.-2025-09-25-105253.png" alt="System Architecture Diagram" width="800">


## Machine Learning Pipeline

### Algorithm Configuration
```python
XGBClassifier(
    n_estimators=300,      # Ensemble size
    learning_rate=0.1,     # Gradient step size
    max_depth=6,           # Tree complexity
    tree_method="gpu_hist", # GPU acceleration
    predictor="gpu_predictor"
)
```

### Feature Engineering
- **Text Features**: TF-IDF vectors (5K features, 1-3 grams)
- **Numerical Features**: Budget analysis, timeline estimation
- **Domain Features**: MDONER compliance score, technical feasibility
- **Output**: Probability distributions + confidence scoring (0-100%)

### Training Dataset
- **Size**: 110 DPR entries with ground truth labels
- **Classes**: Feasible (60%) vs Risky (40%) projects
- **Domains**: Infrastructure, Healthcare, Education, Tourism, Technology
- **Geography**: Northeast India (rural + urban projects)

## System Requirements

### Hardware Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores, 2.4 GHz | 4+ cores, 3.0 GHz |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 5 GB available space | 10 GB SSD |
| **GPU** | Not required | NVIDIA CUDA-compatible |

### Software Dependencies
| Software | Version | Required For |
|----------|---------|-------------|
| **Python** | 3.11+ | Backend, AI, Text Processing |
| **Node.js** | 18+ | Frontend development |
| **Git** | Latest | Version control |
| **Visual C++ Build Tools** | Latest | Python package compilation |



### Production Deployment

### Production Deployment
- **CI/CD**: GitHub Actions with auto-approval (75% success threshold)
- **Monitoring**: Comprehensive logging with performance metrics
- **Security**: CORS configuration, input validation, sanitization
- **Scaling**: Multi-worker deployment ready

Built for **Smart India Hackathon 2024** | Transforming governance through AI
