"""
AI Trap API Route

Exposes endpoints for generating data poisoning packages.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import Response, JSONResponse, StreamingResponse
import traceback
import io
import base64
import json
from app.services.adversarial_trap import AdversarialTrapGenerator

router = APIRouter()

# Global trap generator instance
trap_generator = None

def get_trap_generator():
    """Lazy-load trap generator on first use."""
    global trap_generator
    if trap_generator is None:
        trap_generator = AdversarialTrapGenerator()
    return trap_generator


@router.post("/generate")
async def generate_trap(
    file: UploadFile = File(...),
    variants: int = Form(default=20),
    intensity: int = Form(default=50),
    format: str = Form(default="json")
):
    """
    Generate AI Trap poisoned image package.
    
    This endpoint generates multiple adversarial variants that, if used in training,
    will degrade unauthorized AI model performance.
    
    Args:
        file: Input image file
        variants: Number of poisoned variants to generate (20-100, default 20)
        intensity: Poison intensity (1-100 scale, default 50)
        format: "json" (base64 encoded images) or "zip" (downloadable package)
    
    Returns:
        JSON with poisoned_images, poison_strength_score, and metadata
        OR
        ZIP file with all images and metadata
    """
    
    # Validate inputs
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if not (20 <= variants <= 100):
        raise HTTPException(status_code=400, detail="Variants must be between 20 and 100")
    
    if not (1 <= intensity <= 100):
        raise HTTPException(status_code=400, detail="Intensity must be between 1 and 100")
    
    if format not in ["json", "zip"]:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'zip'")
    
    try:
        # Read image bytes
        content = await file.read()
        
        # Get generator
        generator = get_trap_generator()
        
        # Generate trap package
        trap_package = generator.generate_trap_package(
            image_bytes=content,
            num_variants=variants,
            intensity=intensity,
            return_zip=(format == "zip")
        )
        
        # Return based on requested format
        if format == "zip":
            # Return as downloadable ZIP file
            zip_bytes = trap_package["zip_bytes"]
            return StreamingResponse(
                iter([zip_bytes]),
                media_type="application/zip",
                headers={
                    "Content-Disposition": f'attachment; filename="trap_{file.filename.split(".")[0]}.zip"'
                }
            )
        
        else:  # format == "json"
            # Encode images as base64 for JSON response
            response_data = {
                "poison_strength_score": trap_package["poison_strength_score"],
                "summary": trap_package["summary"],
                "metadata": trap_package["metadata"],
                "poisoned_images": [
                    base64.b64encode(img_bytes).decode('utf-8')
                    for img_bytes in trap_package["poisoned_images"]
                ]
            }
            
            return JSONResponse(content=response_data)
    
    except Exception as e:
        print(f"Trap generation failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_trap(
    file: UploadFile = File(...)
):
    """
    Analyze image poisoning potential without generating full package.
    
    Quick analysis to show:
    - Base embedding signature
    - Estimated poison strength if processed
    - Vulnerability to data poisoning
    
    Useful for determining optimal intensity before full generation.
    """
    
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        content = await file.read()
        generator = get_trap_generator()
        
        # Generate a small set of test variants for analysis
        _, metadata = generator.generate_variants(
            image_bytes=content,
            num_variants=5,  # Small set for quick analysis
            intensity=50.0,
            apply_trigger=True
        )
        
        poison_score = generator.calculate_poison_score(metadata)
        
        analysis = {
            "poisonable": bool(poison_score > 15.0),  # Explicitly convert to bool for JSON
            "poison_potential_score": float(round(poison_score, 2)),
            "avg_embedding_drift": float(round(
                sum(m["embedding_drift_percent"] for m in metadata) / len(metadata), 2
            )),
            "avg_confidence_drop": float(round(
                sum(m["confidence_drop_percent"] for m in metadata) / len(metadata), 2
            )),
            "recommendation": (
                "High poisoning potential - generate full trap" if poison_score > 40
                else "Moderate poisoning potential" if poison_score > 20
                else "Low poisoning potential - may need higher intensity"
            )
        }
        
        return JSONResponse(content=analysis)
    
    except Exception as e:
        print(f"Trap analysis failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def trap_info():
    """
    Get information about AI Trap system.
    
    Returns endpoint documentation and capability information.
    """
    return {
        "system": "AI Trap - Data Poisoning Defense",
        "description": "Generates adversarial image variants to degrade unauthorized AI model training",
        "version": "1.0.0",
        "capabilities": {
            "variant_generation": "20-100 poisoned variants with FGSM perturbations",
            "trigger_injection": "Imperceptible frequency-domain patterns",
            "embedding_analysis": "Drift measurement and confidence scoring",
            "output_formats": ["json (base64 encoded)", "zip (downloadable)"]
        },
        "parameters": {
            "variants": {
                "description": "Number of poisoned variants",
                "range": [20, 100],
                "default": 20
            },
            "intensity": {
                "description": "Poison intensity (1=subtle, 100=aggressive)",
                "range": [1, 100],
                "default": 50
            }
        },
        "performance": {
            "estimated_generation_time": "8-12 seconds for 20 variants",
            "cpu_only": True,
            "batch_processing": "Supported"
        }
    }
