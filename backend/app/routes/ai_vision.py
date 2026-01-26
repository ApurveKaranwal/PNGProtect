from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.ai_vision_service import AIVisionAnalyzer
import traceback

router = APIRouter()

# Initialize service globally to load model once (or lazy load if preferred)
# For MVP, eager load or lazy load on first request is fine.
# Let's do lazy loading to check if servers starts fast, 
# but simply instantiating here is easier for now.
analyzer = None

def get_analyzer():
    global analyzer
    if analyzer is None:
        analyzer = AIVisionAnalyzer()
    return analyzer

@router.post("/ai-vision")
async def analyze_ai_vision(file: UploadFile = File(...)):
    """
    Analyze image for AI confusion.
    Returns prediction stats and a visual heatmap of adversarial noise.
    """
    try:
        # Validate file type
        if not file.content_type and not file.filename:
             raise HTTPException(status_code=400, detail="Invalid file")
        
        # Read file
        contents = await file.read()
        
        # Get Analyzer instance
        service = get_analyzer()
        
        # Analyze
        result = service.analyze_image(contents)
        
        return result

    except Exception as e:
        print(f"Error processing image: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
