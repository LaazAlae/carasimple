import os
import hashlib
import mimetypes
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

@dataclass
class DetectionRecord:
    id: int
    filename: str
    kind: str
    sizeKB: float
    sha256: str
    found: bool
    confidence: Optional[float]
    createdAtISO: str

app = FastAPI(title="Cara Detect Simple")

# In-memory storage
records: List[DetectionRecord] = []
next_id = 1
MAX_RECORDS = 500

# Serve static files
app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/")
async def root():
    return FileResponse("public/index.html")

def validate_file_type(file: UploadFile) -> str:
    """Validate file type and return kind (image/audio)"""
    content_type = file.content_type or ""
    filename = file.filename or ""
    
    # Image types
    if content_type.startswith("image/") and any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
        return "image"
    
    # Audio types  
    if content_type.startswith("audio/") and any(filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.m4a']):
        return "audio"
    
    raise HTTPException(status_code=400, detail={"error": "Unsupported file type"})

def detect_content(sha256: str) -> tuple[bool, Optional[float]]:
    """Detection logic: even last hex digit = found"""
    last_digit = sha256[-1]
    digit_decimal = int(last_digit, 16)
    
    if digit_decimal % 2 == 0:  # Even
        confidence = 0.80 + (digit_decimal / 15) * 0.15
        return True, round(confidence, 3)
    else:
        return False, None

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    global next_id
    
    if not file.filename:
        raise HTTPException(status_code=400, detail={"error": "No file provided"})
    
    # Validate file type
    kind = validate_file_type(file)
    
    # Read file content
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    
    # Size limits
    if kind == "image" and size_mb > 5:
        raise HTTPException(status_code=400, detail={"error": "Image files must be ≤ 5MB"})
    if kind == "audio" and size_mb > 3:
        raise HTTPException(status_code=400, detail={"error": "Audio files must be ≤ 3MB"})
    
    # Compute SHA-256
    sha256 = hashlib.sha256(content).hexdigest()
    
    # Detection
    found, confidence = detect_content(sha256)
    
    # Create record
    record = DetectionRecord(
        id=next_id,
        filename=file.filename,
        kind=kind,
        sizeKB=round(len(content) / 1024, 1),
        sha256=sha256,
        found=found,
        confidence=confidence,
        createdAtISO=datetime.utcnow().isoformat() + 'Z'
    )
    
    # Add to storage (newest first, limit to MAX_RECORDS)
    records.insert(0, record)
    if len(records) > MAX_RECORDS:
        records.pop()
    
    next_id += 1
    
    return asdict(record)

@app.get("/api/assets")
async def get_assets():
    """Return all records, newest first"""
    return [asdict(record) for record in records]

@app.get("/api/stats")
async def get_stats():
    """Return detection statistics"""
    total = len(records)
    found = sum(1 for r in records if r.found)
    ratio = round(found / total, 3) if total > 0 else 0
    
    return {
        "total": total,
        "found": found, 
        "ratio": ratio
    }

@app.delete("/api/reset")
async def reset_data():
    """Clear all data"""
    global next_id
    records.clear()
    next_id = 1
    return {"cleared": True}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
