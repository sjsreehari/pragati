# PDF Text Extractor Website

A full-stack web application for extracting text and structured data from PDF documents.

## Features

- 🔄 **Dual Output**: Generates both TXT (plain text) and JSON (structured data) formats
- 🎯 **Smart Extraction**: Automatically extracts table of contents and metadata
- 🎨 **Modern UI**: Beautiful, responsive React frontend with drag-and-drop functionality
- 🚀 **Fast Processing**: Node.js backend with Python text extraction engine
- 📱 **Mobile Friendly**: Responsive design that works on all devices
- 🔒 **File Validation**: Only accepts PDF files with size limits
- 💾 **Easy Downloads**: Direct download buttons for both TXT and JSON outputs

## Tech Stack

### Frontend
- React 18
- Axios for API calls
- Modern CSS with gradient backgrounds
- Drag & drop file upload

### Backend
- Node.js + Express.js
- Multer for file uploads
- Python integration for text extraction
- CORS enabled for cross-origin requests

### Text Extraction Engine
- Python with multiple PDF processing libraries
- OCR support for scanned documents
- Index and metadata extraction
- AI compliance checking (MDONER/NEC DPR)

## Quick Start

### Prerequisites
- Node.js 16+ installed
- Python 3.8+ installed
- Git (optional)

### Installation & Setup

1. **Install Dependencies**
   ```bash
   # Install backend dependencies
   cd backend
   npm install
   
   # Install frontend dependencies  
   cd ../frontend
   npm install
   
   # Install Python dependencies
   cd ../../text-extractor
   pip install -r requirements.txt
   ```

2. **Start the Application**
   
   Option 1 - Use the setup script:
   ```bash
   # From the website directory
   ./setup_and_run.bat    # Windows
   ./setup_and_run.sh     # Linux/Mac
   ```
   
   Option 2 - Manual startup:
   ```bash
   # Terminal 1: Start Backend (from website/backend)
   npm start
   
   # Terminal 2: Start Frontend (from website/frontend)  
   npm start
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Usage

1. **Upload PDF**: Drag and drop or click to select a PDF file
2. **Process**: Click "Extract Text" to process the document
3. **Download Results**: Get both TXT and JSON outputs
4. **View Metadata**: See extracted document information

## API Endpoints

### POST /api/extract
Upload a PDF file for text extraction.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: PDF file in 'pdf' field

**Response:**
```json
{
  "success": true,
  "txtContent": "Full extracted text...",
  "txtFilename": "document.txt", 
  "jsonContent": {
    "metadata": {...},
    "content": {"full_text": "...", "raw_text": "..."},
    "index": [...]
  },
  "jsonFilename": "document.json"
}
```

### GET /api/health
Health check endpoint.

## File Structure

```
website/
├── frontend/          # React frontend
│   ├── public/       # Static assets
│   ├── src/          # React components
│   └── package.json  # Frontend dependencies
├── backend/          # Node.js backend  
│   ├── uploads/      # Temporary PDF storage
│   ├── output/       # Processed files
│   ├── server.js     # Main server file
│   └── package.json  # Backend dependencies
├── setup_and_run.*  # Setup scripts
└── README.md         # This file
```

## Configuration

### Backend Configuration
- Port: 5000 (configurable via PORT environment variable)
- Upload limit: 50MB
- Supported formats: PDF only
- Temporary file cleanup: Automatic

### Frontend Configuration  
- Port: 3000 (React default)
- API Proxy: Configured to backend on port 5000
- File size display: Automatic calculation

## Troubleshooting

### Common Issues

1. **Python not found**
   - Ensure Python is installed and in PATH
   - Try `python --version` or `python3 --version`

2. **Port already in use**
   - Backend: Change PORT in backend/.env or environment
   - Frontend: React will prompt for alternative port

3. **Upload fails**
   - Check file is valid PDF
   - Verify file size is under 50MB
   - Check backend logs for detailed error

4. **Missing dependencies**
   - Run `npm install` in both frontend and backend directories
   - Run `pip install -r requirements.txt` in text-extractor directory

### Log Locations
- Backend logs: Console output where server is running
- Frontend logs: Browser console (F12)
- Python extraction logs: Backend console

## Development

### Adding New Features
1. Backend changes: Modify `backend/server.js`
2. Frontend changes: Modify `frontend/src/App.js`
3. Text extraction: Modify `../text-extractor/main.py`

### Testing
- Frontend: `npm test` in frontend directory
- Backend: Test API endpoints with curl or Postman
- Integration: Upload test PDFs through the web interface

## Security Notes

- Files are temporarily stored and automatically cleaned up
- Only PDF files are accepted
- File size limits prevent abuse
- No persistent storage of uploaded content
- CORS is enabled for development (configure for production)

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review console logs for error details
3. Ensure all dependencies are properly installed
4. Verify Python text extractor works independently