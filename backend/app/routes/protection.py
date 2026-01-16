from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import Response, JSONResponse
from app.services.adversarial import AdversarialProtector
import io

router = APIRouter()
protector = AdversarialProtector()

@router.post("/process")
async def process_protection(
    file: UploadFile = File(...),
    strength: float = Form(0.01)
):
    """
    Apply adversarial noise to the image to protect against AI scraping.
    strength: Protection level (0.001 to 0.05).
    """
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        content = await file.read()
        
        # Ensure strength is within reasonable bounds
        # Front end sends 1-100, we probably want to map or expect raw epsilon?
        # Let's assume input is raw epsilon for now, or we define mapping here.
        # If frontend sends 0-100 slider value, we should normalize.
        # But `AdversarialProtector` default is 0.01 (imperceptible). 
        # Max 0.05 is visible noise.
        # We'll treat the input `strength` as the raw epsilon directly if small.
        # If > 1, treating as 1-100 scale -> map to 0.0-0.05
        
        epsilon = strength
        if strength > 1.0:
            epsilon = (strength / 100.0) * 0.05
        
        protected_bytes, robustness = protector.protect_image(content, strength=epsilon)

        return Response(
            content=protected_bytes,
            media_type="image/png",
            headers={
                "X-Robustness-Score": str(round(robustness, 2)),
                "Content-Disposition": f'attachment; filename="protected_{file.filename}"'
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
