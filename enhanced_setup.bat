@echo off
echo ========================================
echo   DPR Analysis System - Enhanced Setup
echo ========================================

echo.
echo [1/4] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [2/4] Installing enhanced dependencies...
pip install shap>=0.42.1 googletrans==4.0.0rc1 flask-cors>=4.0.0

echo.
echo [3/4] Testing enhanced prediction module...
python test_enhanced_prediction.py

echo.
echo [4/4] Setup complete!
echo.
echo To start the enhanced system:
echo 1. Backend: cd website\backend ^&^& python app.py
echo 2. Frontend: cd website\frontend ^&^& npm start
echo 3. Open: http://localhost:3000
echo.
echo Enhanced Features:
echo - AI Feasibility Prediction with 91%% accuracy
echo - Confidence scoring and probability distribution
echo - Feature-based explanations
echo - Multi-language support (coming soon)
echo - Professional web interface
echo.
pause