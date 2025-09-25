# DPR Feasibility Analysis Platform

A comprehensive AI-powered system for automated analysis of Detailed Project Reports (DPRs) with feasibility assessment, compliance validation, and interactive data visualization.

## Overview

The DPR Feasibility Analysis Platform is an enterprise-grade solution designed to automate the evaluation of government project proposals. It combines machine learning algorithms, document processing capabilities, and modern web technologies to provide accurate feasibility predictions and compliance assessments.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Frontend (React)                    │
│  - Interactive Dashboard with Chart.js Integration            │
│  - Real-time Analysis Visualization                           │
│  - Responsive UI with Professional Design                     │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Web Backend (Flask)                       │
│  - RESTful API Endpoints                                      │
│  - File Upload Management                                     │
│  - Process Orchestration                                      │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
          ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
          │Text         │  │AI/ML        │  │Compliance   │
          │Extractor    │  │Component    │  │Checker      │
          │             │  │             │  │             │
          │- PDF Parser │  │- XGBoost    │  │- MDONER     │
          │- OCR Engine │  │- TF-IDF     │  │- NEC Rules  │
          │- Text Clean │  │- Prediction │  │- Validation │
          └─────────────┘  └─────────────┘  └─────────────┘
```

## Technical Specifications

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Backend API** | Flask | 2.3.3 | RESTful API server |
| **CORS Handler** | Flask-CORS | 4.0.0 | Cross-origin resource sharing |
| **Frontend** | React | 18.2.0 | Single-page application |
| **Visualization** | Chart.js | 4.4.0 | Interactive data charts |
| **React Charts** | react-chartjs-2 | 3.3.0 | React Chart.js integration |
| **ML Framework** | XGBoost | 3.0.5 | Gradient boosting classifier |
| **Data Processing** | pandas | 2.3.0 | Data manipulation |
| **Text Vectorization** | scikit-learn | 1.7.2 | TF-IDF and ML utilities |
| **PDF Processing** | pdfminer.six | 20250506 | PDF text extraction |
| **OCR Engine** | pytesseract | 0.3.13 | Optical character recognition |

### Machine Learning Pipeline

#### Model Architecture
- **Algorithm**: XGBoost Classifier
- **Features**: TF-IDF vectors + engineered numerical features
- **Training Accuracy**: 91%
- **Validation Method**: Cross-validation with stratified sampling
- **Output**: Probability distributions with confidence scoring

#### Feature Engineering
```python
# Text Features
- TF-IDF vectors (max_features=5000)
- N-gram analysis (1-3 grams)
- Document length statistics
- Keyword density analysis

# Numerical Features
- Budget analysis (crores)
- Timeline estimation (months)
- Resource allocation metrics
- Compliance score computation
```

#### Model Configuration
```python
XGBClassifier(
    n_estimators=300,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method="gpu_hist",
    predictor="gpu_predictor",
    random_state=42
)
```

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

## Configuration

### Environment Variables

Create `.env` files in respective directories:

#### Backend Configuration (website/backend/.env)
```bash
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800  # 50MB
CORS_ORIGINS=http://localhost:3000
```

#### Frontend Configuration (website/frontend/.env)
```bash
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENVIRONMENT=development
```

## API Documentation

### Authentication
Currently, no authentication is required. For production deployment, implement JWT or OAuth2.

### Endpoints

#### Health Check
```http
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-25T10:30:00Z",
  "ai_predictor_available": true,
  "version": "1.0.0"
}
```

#### Document Analysis
```http
POST /api/extract
Content-Type: multipart/form-data
```
**Request Body:**
- `file`: PDF document (max 50MB)

**Response:**
```json
{
  "success": true,
  "data": {
    "text": "extracted_document_text",
    "prediction": "feasible|risky",
    "confidence": 0.87,
    "probability_feasible": 0.87,
    "probability_risky": 0.13,
    "feature_explanations": {
      "top_features": ["budget_analysis", "technical_feasibility"],
      "feature_importance": [0.35, 0.28, 0.22, 0.15],
      "interpretation": "Project shows strong financial planning..."
    },
    "compliance": {
      "mdoner_compliant": true,
      "nec_compliant": true,
      "issues": []
    }
  }
}
```

#### Direct Text Analysis
```http
POST /api/predict
Content-Type: application/json
```
**Request Body:**
```json
{
  "text": "Project description text for analysis..."
}
```

## Development Workflow

### Local Development

```bash
# Terminal 1: Start Backend
cd website/backend
python app.py

# Terminal 2: Start Frontend
cd website/frontend
npm start

# Access application at http://localhost:3000
```

### Code Quality

```bash
# Python code formatting
pip install black flake8
black ai/ text-extractor/
flake8 ai/ text-extractor/

# JavaScript code formatting
cd website/frontend
npm run lint
npm run format
```

### Testing

```bash
# Backend API tests
python test_enhanced_prediction.py

# Frontend tests
cd website/frontend
npm test

# Integration tests
python -m pytest tests/ -v
```

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

#### Using Docker (Recommended)

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

#### Manual Deployment

```bash
# Production environment setup
export FLASK_ENV=production
export NODE_ENV=production

# Install production dependencies
pip install -r requirements.txt --only-binary=all
npm ci --production

# Build frontend
cd website/frontend
npm run build

# Start services with process manager
pm2 start ecosystem.config.js
```

## Performance Optimization

### Backend Optimization
- **GPU Acceleration**: Enabled for ML inference
- **Caching**: TF-IDF vectorizer and model caching
- **Async Processing**: File upload and processing pipeline
- **Connection Pooling**: Database connection management

### Frontend Optimization
- **Code Splitting**: Dynamic imports for routes
- **Chart Performance**: Canvas rendering with data sampling
- **Bundle Optimization**: Webpack optimizations enabled
- **CDN Integration**: Static assets served via CDN

## Security Considerations

### Input Validation
- File type restriction (PDF only)
- File size limitations (50MB max)
- Input sanitization for text analysis
- Path traversal prevention

### API Security
- CORS configuration for specific origins
- Rate limiting on API endpoints
- Input validation and sanitization
- Error handling without data leakage

### Data Protection
- Temporary file cleanup
- No persistent storage of uploaded content
- Secure file handling procedures
- Privacy compliance measures

## Monitoring and Logging

### Application Monitoring
```python
# Logging configuration
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Metrics
- API response times
- Model prediction accuracy
- File processing throughput
- Error rates and exceptions

## Contributing

### Development Guidelines

1. **Code Standards**
   - Follow PEP 8 for Python code
   - Use ESLint configuration for JavaScript
   - Maintain consistent naming conventions
   - Include comprehensive docstrings

2. **Git Workflow**
   - Create feature branches from main
   - Use descriptive commit messages
   - Submit pull requests for review
   - Ensure CI/CD pipeline passes

3. **Testing Requirements**
   - Unit tests for new functionality
   - Integration tests for API endpoints
   - Frontend component testing
   - Performance regression testing

## Troubleshooting

### Common Issues

#### Backend Startup Failures
```bash
# Check Python environment
python --version
pip list

# Verify model files exist
ls -la ai/models/

# Check port availability
netstat -an | grep :5000
```

#### Frontend Build Errors
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version
npm --version
```

#### Model Prediction Errors
```bash
# Verify model integrity
python ai/src/test_model.py

# Check TF-IDF vectorizer
python -c "import joblib; print(joblib.load('ai/models/tfidf.pkl'))"

# Validate training data
python -c "import pandas as pd; print(pd.read_csv('ai/data/data.csv').head())"
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for detailed terms and conditions.

## Support and Contact

### Technical Support
- **Repository**: https://github.com/sjsreehari/Alt---F4
- **Issues**: Submit via GitHub Issues tracker
- **Documentation**: Available in `/docs` directory

### Development Team
- **Project Lead**: Sreehari S J
- **Institution**: Smart India Hackathon Participant
- **Last Updated**: September 25, 2025

### Acknowledgments
- Smart India Hackathon organizing committee
- Open source contributors and libraries
- Ministry of Development of North Eastern Region (MDONER)
- North Eastern Council (NEC)

---

**Version**: 1.0.0  
**Build Status**: Production Ready  
**Last Modified**: September 25, 2025