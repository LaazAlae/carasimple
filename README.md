# Cara Detect (Simple)

A minimal content detection demo built with FastAPI and vanilla JavaScript. Upload images or audio files to test a simple detection algorithm based on file hash patterns.

## Features

- **Drag & Drop Upload**: Intuitive file upload with visual feedback
- **Multi-format Support**: Images (PNG, JPG, JPEG, WEBP) and Audio (MP3, WAV, M4A)
- **Real-time Detection**: Instant results with confidence scoring
- **File Validation**: Client and server-side size/type checking
- **Live Statistics**: Upload count, detection rate, and success metrics
- **Modern UI**: Glassmorphism design with Tailwind CSS
- **In-memory Storage**: No database required, capped at 500 records

## Quick Start

1. **Run the bootstrap script**:
   ```bash
   chmod +x bootstrap_carasimple.sh
   ./bootstrap_carasimple.sh
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Start the server**:
   ```bash
   python server.py
   ```

Visit http://localhost:8000 to use the application.

## API Endpoints

### Upload File
```bash
curl -X POST "http://localhost:8000/api/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@example.jpg"
```

### Get All Assets
```bash
curl "http://localhost:8000/api/assets"
```

### Get Statistics
```bash
curl "http://localhost:8000/api/stats"
```

### Reset Data
```bash
curl -X DELETE "http://localhost:8000/api/reset"
```

## Detection Logic Explanation

The detection algorithm uses a simple but deterministic approach:

1. **Hash Calculation**: Compute SHA-256 of uploaded file
2. **Pattern Analysis**: Extract the last hexadecimal digit
3. **Detection Rule**: Even digits (0,2,4,6,8,A,C,E) = "Found"
4. **Confidence Scoring**: For detected content, confidence = 0.80 + (digit_value/15) * 0.15

This creates a ~50% detection rate with confidence scores ranging from 0.800 to 0.950.

## Extending

To integrate real detection services:

• **Reverse Image Search**: Replace detection logic with TinEye API calls
• **Audio Fingerprinting**: Use ACRCloud or AudioTag for music identification  
• **Content Moderation**: Add Azure Content Moderator or AWS Rekognition
• **Database Storage**: Replace in-memory list with PostgreSQL/MongoDB
• **Authentication**: Add user accounts and API keys
• **Batch Processing**: Queue large files for background processing

## Limits / Next Steps

**Current Limitations**:
- In-memory storage (lost on restart)
- No user authentication or rate limiting
- Simplified file validation
- Single-server deployment only

**Production Considerations**:
- Add persistent database storage
- Implement proper logging and monitoring
- Add file virus scanning
- Use cloud storage for uploaded files
- Add comprehensive error handling

### Security Notes

This demo is intended for local development only. Before production deployment:

- Add authentication and authorization
- Implement rate limiting and CORS policies  
- Validate all file uploads against malware
- Use HTTPS and secure headers
- Sanitize all user inputs and filenames
- Consider implementing file quarantine procedures
