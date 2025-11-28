from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import uuid
from data_handler import DataHandler
from pdf_generator import PDFGenerator

app = FastAPI(title="NutriGuide API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_handler = DataHandler()
pdf_generator = PDFGenerator()

class MedicalData(BaseModel):
    name: str
    age: int
    height: float
    weight: float
    blood_group: str
    sugar_level: Optional[float] = None
    # Add other fields as needed

class Feedback(BaseModel):
    user_name: str
    message: str
    contact_info: str

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
def predict_disease(data: MedicalData):
    # Simple rule-based prediction for demonstration
    # In a real app, this would use a ML model
    prediction = "Healthy"
    if data.sugar_level and data.sugar_level > 140:
        prediction = "Diabetes Type 2"
    elif data.age > 50: # Very simple heuristic
        prediction = "Hypertension"
    
    return {"prediction": prediction}

@app.get("/search")
def search_diseases(q: str):
    results = data_handler.search_diseases(q)
    return {"results": results}

@app.post("/recommend")
def recommend_food(disease: str):
    disease_info = data_handler.get_disease_info(disease)
    if not disease_info:
        # Default recommendation if disease not found
        return {
            "recommendations": ["Balanced diet", "Fruits", "Vegetables"], 
            "avoid": ["Processed foods", "Excess sugar"],
            "reason": "General healthy eating guidelines."
        }
    
    return disease_info["recommendations"]

@app.post("/feedback")
def submit_feedback(feedback: Feedback):
    data_handler.save_feedback(feedback.dict())
    return {"status": "success", "message": "Feedback received"}

@app.post("/report")
def generate_report(data: MedicalData, prediction: str, background_tasks: BackgroundTasks):
    # Get recommendations
    disease_info = data_handler.get_disease_info(prediction)
    recommendations = disease_info["recommendations"] if disease_info else {
        "eat": ["Balanced diet"], "avoid": ["Junk food"], "reason": "General health"
    }
    
    # Generate PDF
    filename = f"report_{uuid.uuid4()}.pdf"
    filepath = os.path.join("data", filename)
    
    pdf_generator.generate_report(data.dict(), prediction, recommendations, filepath)
    
    # Clean up file after sending (optional, here we keep it for simplicity or add a cleanup task)
    return FileResponse(filepath, media_type='application/pdf', filename="MedicalReport.pdf")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
