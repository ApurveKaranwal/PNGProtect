from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from app.services.hashing import sha256_bytes
from app.services.watermarking import (
    extract_watermark_lsb,
    load_image_from_bytes,
)
from app.storage.db import WatermarkStore
from app.models.schemas import VerifyResponse, PublicVerifyResponse, WatermarkDetectionResponse

router = APIRouter()
store = WatermarkStore.get_instance()


def validate_image_upload(file: UploadFile):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PNG or JPEG image.",
        )


@router.post(
    "",
    response_model=VerifyResponse,
    summary="Verify watermark from uploaded image",
)
async def verify_image(
    file: UploadFile = File(...),
):
    """
    Extracts watermark bits using LSB logic and compares with stored metadata.
    Returns watermark_found, owner_id, confidence and basic tamper status.
    """
    validate_image_upload(file)
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Empty image payload.")

    image_hash = sha256_bytes(raw_bytes)
    image = load_image_from_bytes(raw_bytes)

    # Try to extract watermark text and bit statistics
    extracted_text, match_ratio = extract_watermark_lsb(image)

    # If some text was reconstructed, try to match it with metadata
    record = store.get_by_owner_and_hash_prefix(extracted_text, image_hash)

    # Consider watermark found if:
    # 1. We found a stored record, OR
    # 2. LSB extraction matches pattern (>0.5 ratio) and extracted valid text
    watermark_found = record is not None or (match_ratio > 0.5 and extracted_text != "Unknown")
    owner_id = record.owner_id if record else (extracted_text if extracted_text != "Unknown" else None)

    # Confidence and tamper logic:
    # - match_ratio: fraction of bits matching expected pattern
    # - if we didn't find a metadata record but bits look structured, mark as modified
    if watermark_found:
        if match_ratio > 0.9:
            confidence = int(90 + (match_ratio - 0.9) * 100)
            tamper_status = "intact"
        elif match_ratio > 0.7:
            confidence = int(60 + (match_ratio - 0.7) * 100)
            tamper_status = "modified"
        else:
            confidence = int(40 + match_ratio * 100)
            tamper_status = "modified"
    else:
        # Watermark text could not be confidently mapped to known record
        if match_ratio > 0.4:
            confidence = int(20 + match_ratio * 80)
            tamper_status = "modified"
        else:
            confidence = int(match_ratio * 40)
            tamper_status = "no watermark"

    confidence = max(0, min(100, confidence))

    return VerifyResponse(
        watermark_found=watermark_found,
        owner_id=owner_id,
        confidence=confidence,
        tamper_status=tamper_status,
        extracted_text=extracted_text,
        match_ratio=match_ratio,
    )


@router.get(
    "/public/{watermark_id}",
    response_model=PublicVerifyResponse,
    summary="Public lookup by watermark ID",
)
async def public_lookup(watermark_id: str):
    """
    Simple public lookup of stored watermark metadata by watermark_id.
    Does not operate on image bytes, just returns stored ownership info.
    """
    record = store.get_by_watermark_id(watermark_id)
    if not record:
        raise HTTPException(status_code=404, detail="Watermark ID not found.")

    return PublicVerifyResponse(
        watermark_id=watermark_id,
        owner_id=record.owner_id,
        image_hash=record.image_hash,
        strength=record.strength,
        created_at=record.timestamp,
    )

@router.post(
    "/detect",
    response_model=WatermarkDetectionResponse,
    summary="Detect if image already has a watermark",
)
async def detect_watermark(file: UploadFile = File(...)):
    """
    Quick detection endpoint to check if an image already contains a watermark.
    Returns has_watermark flag and extracted text/ratio.
    Useful for preventing re-watermarking of already watermarked images.
    """
    validate_image_upload(file)
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Empty image payload.")

    try:
        image = load_image_from_bytes(raw_bytes)
        extracted_text, match_ratio = extract_watermark_lsb(image)
        
        # Get image hash to check watermark store
        image_hash = sha256_bytes(raw_bytes)
        
        # Check if image has watermark stored in the database
        stored_record = None
        if extracted_text != "Unknown":
            stored_record = store.get_by_owner_and_hash_prefix(extracted_text, image_hash)
        
        # Consider it a watermark if:
        # 1. LSB match_ratio is high (> 0.5) AND text extracted, OR
        # 2. Image found in watermark store
        has_watermark = (match_ratio > 0.5 and extracted_text != "Unknown") or (stored_record is not None)
        
        if has_watermark:
            owner_id = extracted_text if extracted_text != "Unknown" else (stored_record.owner_id if stored_record else "Unknown")
            message = f"Image already contains a watermark. Owner ID: {owner_id}. Cannot re-watermark."
        else:
            message = "Image is clean and ready to be watermarked."
        
        return WatermarkDetectionResponse(
            has_watermark=has_watermark,
            extracted_text=extracted_text if has_watermark else "",
            match_ratio=match_ratio,
            message=message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting watermark: {str(e)}",
        )