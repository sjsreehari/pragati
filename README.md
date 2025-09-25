# PRAGATI
**Project Review and Governance AI-based Transparency Interface**

An enterprise-grade AI platform for automated Detailed Project Report (DPR) analysis with ML-driven feasibility assessment and governance compliance validation.

## System Architecture

```
Frontend (React 18.2 + Chart.js 4.4) ← REST API → Flask 2.3.3 Backend
                                                          ↓
                                    ┌─────────────────────┼─────────────────────┐
                                    ▼                     ▼                     ▼
                            Text Extraction        XGBoost ML Engine    Compliance Checker
                           (pdfminer + OCR)        (91% accuracy)       (MDONER/NEC)
```

## Core Technologies

| Component | Stack | Purpose |
|-----------|-------|---------|
| **ML Engine** | XGBoost 3.0.5 + scikit-learn 1.7.2 | Feasibility classification (91% accuracy) |
| **NLP Pipeline** | TF-IDF + pandas 2.3.0 | Feature extraction & text vectorization |
| **Document Processing** | pdfminer.six + pytesseract | PDF parsing & OCR processing |
| **Backend API** | Flask 2.3.3 + Flask-CORS 4.0.0 | RESTful services & CORS handling |
| **Frontend** | React 18.2.0 + Chart.js 4.4.0 | Interactive dashboard with real-time viz |
| **Charts Integration** | react-chartjs-2 3.3.0 | Doughnut, Bar, Line charts for insights |

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

## Installation Guide

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/sjsreehari/Alt---F4.git
cd "Hackathon SIH"

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

### 2. Backend Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr
```

### 3. Frontend Dependencies

```bash
# Navigate to frontend directory
cd website/frontend

# Install Node.js dependencies
npm install

# Return to project root
cd ../..
```

### 4. Model Initialization

```bash
# Navigate to AI directory
cd ai

# Train initial models (if not pre-trained)
python src/train.py

# Test model functionality
python src/test_model.py

# Return to project root
cd ..
```

## Quick Setup

### Prerequisites
- Python 3.11+ with GPU support (optional)
- Node.js 18+ and npm
- Git for repository management

### Installation & Deployment
```bash
# Clone and setup
git clone https://github.com/sjsreehari/Alt---F4.git
cd "Hackathon SIH" && .\enhanced_setup.bat

# Frontend (port 3000)
cd website/frontend && npm install && npm start

# Backend API (port 5000)
cd website/backend && pip install -r requirements.txt && python app.py
```

## Development Workflow

## Performance Metrics

| Metric | Value | Context |
|--------|--------|---------|
| **ML Accuracy** | 91% | Cross-validated on 110 DPRs |
| **Processing Speed** | <2s | Average PDF analysis time |
| **API Response** | <500ms | Prediction endpoint latency |
| **Model Size** | 15.2 MB | Optimized for deployment |

## Key Features

- **Real-time Visualization**: Interactive Chart.js dashboards
- **Confidence Scoring**: ML uncertainty quantification  
- **Compliance Automation**: MDONER guideline validation
- **Multi-format Support**: PDF + OCR for scanned documents
- **Enterprise Ready**: Production-grade CI/CD pipeline

## Deployment

### CI/CD Pipeline

The project includes a comprehensive GitHub Actions workflow:

```yaml
# Automated pipeline includes:
- Frontend build validation
- Backend API testing  
- AI model verification
- Code quality assessment
- Automatic approval (75%+ success rate)
- Staging deployment
```

### Production Deployment

### Production Deployment
- **CI/CD**: GitHub Actions with auto-approval (75% success threshold)
- **Monitoring**: Comprehensive logging with performance metrics
- **Security**: CORS configuration, input validation, sanitization
- **Scaling**: Multi-worker deployment ready

Built for **Smart India Hackathon 2024** | Transforming governance through AI