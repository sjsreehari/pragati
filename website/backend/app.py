from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import subprocess
import tempfile
import json
from werkzeug.utils import secure_filename
import shutil
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Path to the text extractor - from backend/ to project root to text-extractor/
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BACKEND_DIR))
TEXT_EXTRACTOR_PATH = os.path.join(PROJECT_ROOT, 'text-extractor')
PYTHON_VENV_PATH = os.path.join(PROJECT_ROOT, '.venv', 'Scripts', 'python.exe')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    """API documentation endpoint"""
    return jsonify({
        'name': 'PDF Text Extractor API',
        'version': '1.0.0',
        'description': 'Flask backend for PDF text extraction',
        'endpoints': {
            'POST /api/extract': 'Upload PDF and extract text',
            'GET /api/health': 'Health check endpoint',
            'GET /': 'This documentation'
        },
        'status': 'running'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask server is running',
        'text_extractor_available': os.path.exists(os.path.join(TEXT_EXTRACTOR_PATH, 'main.py')),
        'python_venv_available': os.path.exists(PYTHON_VENV_PATH)
    })

@app.route('/api/extract', methods=['POST'])
def extract_text():
    """Extract text from uploaded PDF"""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Only PDF files are supported.'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file
            input_path = os.path.join(temp_dir, filename)
            file.save(input_path)
            
            # Prepare output paths
            base_name = os.path.splitext(filename)[0]
            output_txt_path = os.path.join(temp_dir, f"{base_name}.txt")
            output_json_path = os.path.join(temp_dir, f"{base_name}.json")
            
            # Run the text extractor
            try:
                # Copy file to text-extractor input directory
                input_dir = os.path.join(TEXT_EXTRACTOR_PATH, 'input')
                output_dir = os.path.join(TEXT_EXTRACTOR_PATH, 'output')
                
                # Ensure directories exist
                os.makedirs(input_dir, exist_ok=True)
                os.makedirs(output_dir, exist_ok=True)
                
                # Copy file to input directory
                extractor_input_path = os.path.join(input_dir, filename)
                shutil.copy2(input_path, extractor_input_path)
                
                # Change to text-extractor directory and run the script
                original_cwd = os.getcwd()
                os.chdir(TEXT_EXTRACTOR_PATH)
                
                cmd = [
                    PYTHON_VENV_PATH,
                    'main.py',
                    filename,
                    '--format', 'both'
                ]
                
                print(f"Running command: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=TEXT_EXTRACTOR_PATH)
                print(f"Command output: {result.stdout}")
                
                # Restore original working directory
                os.chdir(original_cwd)
                
                # Update output paths to point to text-extractor output
                output_txt_path = os.path.join(output_dir, f"{base_name}.txt")
                output_json_path = os.path.join(output_dir, f"{base_name}.json")
                
            except subprocess.CalledProcessError as e:
                os.chdir(original_cwd) if 'original_cwd' in locals() else None
                print(f"Error running text extractor: {e}")
                print(f"Stderr: {e.stderr}")
                return jsonify({
                    'error': 'Failed to process PDF',
                    'details': str(e),
                    'stderr': e.stderr
                }), 500
            
            # Read the extracted content
            extracted_data = {}
            
            # Read text content
            if os.path.exists(output_txt_path):
                with open(output_txt_path, 'r', encoding='utf-8') as f:
                    txt_content = f.read()
                    extracted_data['txtContent'] = txt_content
                    extracted_data['txtFilename'] = f"{base_name}.txt"
            else:
                extracted_data['txtContent'] = 'Text extraction failed'
                extracted_data['txtFilename'] = f"{base_name}.txt"
            
            # Read JSON content
            if os.path.exists(output_json_path):
                with open(output_json_path, 'r', encoding='utf-8') as f:
                    try:
                        json_content = json.load(f)
                        extracted_data['jsonContent'] = json_content
                        extracted_data['jsonFilename'] = f"{base_name}.json"
                    except json.JSONDecodeError:
                        extracted_data['jsonContent'] = {'error': 'Invalid JSON format'}
                        extracted_data['jsonFilename'] = f"{base_name}.json"
            else:
                extracted_data['jsonContent'] = {'error': 'JSON extraction failed'}
                extracted_data['jsonFilename'] = f"{base_name}.json"
            
            # Return the results in the format expected by frontend
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'PDF processed successfully',
                **extracted_data
            })
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/api/download/<format_type>/<filename>')
def download_file(format_type, filename):
    """Download extracted content as file"""
    try:
        # This endpoint would be used for downloading files
        # For now, we'll return the content directly in the extract endpoint
        return jsonify({'error': 'Download endpoint not implemented yet'}), 501
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Flask server starting...")
    print(f"📁 Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"🐍 Text extractor path: {os.path.abspath(TEXT_EXTRACTOR_PATH)}")
    print(f"🐍 Python venv path: {PYTHON_VENV_PATH}")
    print(f"📊 Text extractor main.py exists: {os.path.exists(os.path.join(TEXT_EXTRACTOR_PATH, 'main.py'))}")
    print(f"🐍 Python venv exists: {os.path.exists(PYTHON_VENV_PATH)}")
    print("📖 API Documentation: http://localhost:5000/")
    print("💚 Health Check: http://localhost:5000/api/health")
    print("🔄 File Upload: POST http://localhost:5000/api/extract")
    
    app.run(host='0.0.0.0', port=5000, debug=True)