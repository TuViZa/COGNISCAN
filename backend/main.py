from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
import asyncio
from typing import Dict, List
import os
from datetime import datetime
import uuid

app = FastAPI(title="Cogniscan API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split(".")[-1]
        filename = f"{file_id}.{file_extension}"
        file_path = f"uploads/{filename}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the video (placeholder for now)
        result = await process_video(file_path)
        
        return JSONResponse(content={
            "success": True,
            "file_id": file_id,
            "cognitive_score": result["score"],
            "analysis": result["analysis"],
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_video(file_path: str) -> Dict:
    """
    Placeholder for video processing pipeline
    In real implementation, this would:
    1. Split audio and video
    2. Process with MediaPipe for facial analysis
    3. Extract audio features with Librosa
    4. Analyze speech with BERT
    5. Calculate cognitive score
    """
    
    # Mock processing for demonstration
    await asyncio.sleep(2)  # Simulate processing time
    
    # Mock cognitive score (0-100, higher is better)
    import random
    score = random.uniform(60, 95)
    
    # Mock analysis results
    analysis = {
        "facial_analysis": {
            "micro_expressions": "normal",
            "eye_contact": "stable",
            "facial_symmetry": "balanced"
        },
        "speech_analysis": {
            "pitch_variance": "normal",
            "speech_rate": "moderate",
            "pause_frequency": "acceptable"
        },
        "language_analysis": {
            "coherence": "good",
            "vocabulary_richness": "adequate",
            "sentence_complexity": "normal"
        }
    }
    
    # Check if high risk (score < 70)
    if score < 70:
        await manager.broadcast(json.dumps({
            "type": "alert",
            "severity": "high",
            "message": f"High risk detected! Cognitive score: {score:.1f}",
            "timestamp": datetime.now().isoformat()
        }))
    
    return {
        "score": score,
        "analysis": analysis
    }

@app.get("/api/patient-history/{patient_id}")
async def get_patient_history(patient_id: str):
    """
    Mock patient history data
    In real implementation, this would fetch from MongoDB
    """
    import random
    
    # Generate mock historical data
    history = []
    for i in range(30):
        date = datetime.now().replace(day=1).replace(month=1).replace(day=i+1)
        score = random.uniform(65, 95)
        history.append({
            "date": date.isoformat(),
            "score": score,
            "assessment_type": "daily_checkin"
        })
    
    return JSONResponse(content={
        "patient_id": patient_id,
        "history": history
    })

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
