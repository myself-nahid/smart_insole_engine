from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from app.services.input_handler import InputHandler
from app.services.vision_engine import VisionEngine
from app.services.morphing import MorphingEngine
from app.services.manufacturing import calculate_infill
import shutil
import os
import uuid
from app.config import TEMP_DIR

app = FastAPI(title="Smart 2D to 3D Engine")

input_handler = InputHandler()
vision_engine = VisionEngine()
morphing_engine = MorphingEngine()

@app.post("/upload/pdf")
async def process_pdf(file: UploadFile = File(...)):
    """
    Path A: Automated Workflow (Text + Visuals + 3D Gen)
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type")

    content = await file.read()
    
    # 1. Parse PDF (Metadata + Image)
    metadata = input_handler.parse_pdf(content)
    
    # Validation Fallback
    if not metadata['weight'] or not metadata['size']:
        return JSONResponse(status_code=206, content={
            "message": "Partial Data. Manual Input Required.", 
            "extracted": metadata
        })

    # 2. Vision Analysis (Using the image rendered from PDF)
    if metadata['image_bytes']:
        # Pass the extracted bytes to the Vision Engine
        vision_results = vision_engine.process_image(metadata['image_bytes'])
        foot_data = vision_results['left'] # Defaulting to left for demo
    else:
        # Fallback if image extraction failed completely: Use default values
        foot_data = {"arch_type": "Normal", "csi": 35.0}

    # 3. 3D Generation
    # Use the extracted Size (44) and Vision Data
    job_id = str(uuid.uuid4())
    output_filename = f"{job_id}_from_pdf.stl"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    mesh = morphing_engine.generate_3d_model(metadata['size'], foot_data)
    
    # Apply Diagnosis Modifiers (e.g., Supination found in text)
    # (Optional: Logic to add wedge if metadata['diagnosis'] == 'Supination')
    
    morphing_engine.export_mesh(mesh, output_path)
    
    # 4. Manufacturing Calculation
    infill = calculate_infill(metadata['weight'])
    
    return {
        "status": "success",
        "job_id": job_id,
        "patient": {
            "weight": metadata['weight'],
            "size": metadata['size'],
            "diagnosis": metadata['diagnosis']
        },
        "vision_analysis": {
            "arch_type": foot_data.get('arch_type', 'Unknown'),
            "source": "PDF Extraction"
        },
        "manufacturing": {
            "recommended_infill": infill
        },
        "download_url": f"/download/{output_filename}"
    }

@app.post("/upload/image")
async def process_image(
    file: UploadFile = File(...),
    weight: float = Form(...),
    size: int = Form(...),
    diagnosis: str = Form("Normal")
):
    """
    Path B: Raw Image + Manual Data
    """
    content = await file.read()
    
    # 1. Vision Analysis
    vision_results = vision_engine.process_image(content)
    
    # 2. 3D Generation
    job_id = str(uuid.uuid4())
    output_filename = f"{job_id}_left.stl"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    # --- CHANGE IS HERE: Passing 'weight' to the function ---
    mesh = morphing_engine.generate_3d_model(
        target_size=size, 
        weight=weight, 
        foot_data=vision_results['left']
    )
    # --------------------------------------------------------
    
    morphing_engine.export_mesh(mesh, output_path)
    
    # 3. Manufacturing Data
    infill = calculate_infill(weight)

    return {
        "job_id": job_id,
        "vision_analysis": {
            "arch_type": vision_results['left']['arch_type'],
            "csi_estimated": vision_results['left']['csi']
        },
        "manufacturing": {
            "infill_percentage": infill,
            "visual_thickness_factor": weight / 75.0
        },
        "download_url": f"/download/{output_filename}"
    }

@app.get("/download/{filename}")
async def download_stl(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)