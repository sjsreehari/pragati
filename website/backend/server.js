const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs-extra');
const { exec } = require('child_process');
const util = require('util');

const app = express();
const PORT = process.env.PORT || 5000;
const execPromise = util.promisify(exec);

app.use(cors());
app.use(express.json());

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/');
  },
  filename: function (req, file, cb) {
    const timestamp = Date.now();
    const originalName = file.originalname;
    const extension = path.extname(originalName);
    const baseName = path.basename(originalName, extension);
    cb(null, `${baseName}_${timestamp}${extension}`);
  }
});

const upload = multer({
  storage: storage,
  fileFilter: function (req, file, cb) {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed!'), false);
    }
  },
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB limit
  }
});

async function runPythonExtractor(pdfPath, outputDir) {
  try {
    const textExtractorPath = path.join(__dirname, '..', '..', 'text-extractor');
    const pythonScript = path.join(textExtractorPath, 'main.py');
    
    const command = `cd "${textExtractorPath}" && python "${pythonScript}" "${pdfPath}" --format both --output "${outputDir}"`;
    
    console.log('Executing command:', command);
    
    const { stdout, stderr } = await execPromise(command);
    
    if (stderr) {
      console.warn('Python stderr:', stderr);
    }
    
    console.log('Python stdout:', stdout);
    return true;
  } catch (error) {
    console.error('Error running Python extractor:', error);
    throw error;
  }
}

app.post('/api/extract', upload.single('pdf'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No PDF file uploaded' });
    }

    console.log('Uploaded file:', req.file.filename);
    
    const pdfPath = req.file.path;
    const outputDir = path.join(__dirname, 'output');
    
    await fs.ensureDir(outputDir);
    
    await runPythonExtractor(pdfPath, outputDir);
    
    const baseName = path.basename(req.file.filename, '.pdf');
    const txtFile = path.join(outputDir, `${baseName}.txt`);
    const jsonFile = path.join(outputDir, `${baseName}.json`);
    
    if (!await fs.exists(txtFile) || !await fs.exists(jsonFile)) {
      const alternateBaseName = path.basename(req.file.originalname, '.pdf');
      const alternateTxtFile = path.join(outputDir, `${alternateBaseName}.txt`);
      const alternateJsonFile = path.join(outputDir, `${alternateBaseName}.json`);
      
      if (await fs.exists(alternateTxtFile) && await fs.exists(alternateJsonFile)) {
        txtFile = alternateTxtFile;
        jsonFile = alternateJsonFile;
      } else {
        const files = await fs.readdir(outputDir);
        const txtFiles = files.filter(f => f.endsWith('.txt'));
        const jsonFiles = files.filter(f => f.endsWith('.json'));
        
        if (txtFiles.length > 0 && jsonFiles.length > 0) {
          txtFile = path.join(outputDir, txtFiles[txtFiles.length - 1]);
          jsonFile = path.join(outputDir, jsonFiles[jsonFiles.length - 1]);
        } else {
          throw new Error('Output files not found after extraction');
        }
      }
    }
    
    const txtContent = await fs.readFile(txtFile, 'utf8');
    const jsonContent = JSON.parse(await fs.readFile(jsonFile, 'utf8'));
    
    await fs.remove(pdfPath);
    
    const response = {
      success: true,
      txtContent: txtContent,
      txtFilename: `${path.basename(req.file.originalname, '.pdf')}.txt`,
      jsonContent: jsonContent,
      jsonFilename: `${path.basename(req.file.originalname, '.pdf')}.json`,
      metadata: {
        originalFilename: req.file.originalname,
        extractedAt: new Date().toISOString(),
        fileSize: req.file.size
      }
    };
    
    res.json(response);
    
  } catch (error) {
    console.error('Extraction error:', error);
    
    if (req.file) {
      try {
        await fs.remove(req.file.path);
      } catch (cleanupError) {
        console.error('Cleanup error:', cleanupError);
      }
    }
    
    res.status(500).json({ 
      error: 'Failed to process PDF file', 
      details: error.message 
    });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'PDF Text Extractor Backend'
  });
});

app.get('/', (req, res) => {
  res.json({ 
    message: 'PDF Text Extractor Backend API',
    version: '1.0.0',
    endpoints: {
      'POST /api/extract': 'Upload and extract text from PDF',
      'GET /api/health': 'Health check endpoint'
    }
  });
});

app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'File too large (max 50MB)' });
    }
    if (error.code === 'LIMIT_FILE_COUNT') {
      return res.status(400).json({ error: 'Too many files' });
    }
  }
  
  if (error.message === 'Only PDF files are allowed!') {
    return res.status(400).json({ error: 'Only PDF files are allowed' });
  }
  
  console.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📖 API Documentation: http://localhost:${PORT}/`);
  console.log(`💚 Health Check: http://localhost:${PORT}/api/health`);
});