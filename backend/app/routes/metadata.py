from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import io
from app.services.watermarking import (
    load_image_from_bytes,
    save_image_to_bytes,
    strip_metadata_from_image,
)

router = APIRouter()

def validate_image_upload(file: UploadFile):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PNG or JPEG image.",
        )


@router.post("/strip", summary="Remove metadata and encoding from image")
async def strip_metadata(file: UploadFile = File(...)):
    """
    Removes all metadata, EXIF data, and encoding information from an uploaded image.
    Returns a clean PNG image with only pixel data preserved.
    """
    validate_image_upload(file)
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Empty image payload.")

    try:
        # Load image from bytes
        image = load_image_from_bytes(raw_bytes)
        
        # Strip all metadata
        clean_image = strip_metadata_from_image(image)
        
        # Save as clean PNG
        clean_bytes = save_image_to_bytes(clean_image, "png")
        
        # Return the cleaned image as a file download
        return StreamingResponse(
            io.BytesIO(clean_bytes.getvalue()),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=cleaned_image.png"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}",
        )
