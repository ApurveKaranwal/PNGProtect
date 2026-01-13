from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
import io
import uuid
import asyncio
from datetime import datetime

from app.models.user_schemas import (
    DashboardStats, WatermarkTemplate, BulkOperationRequest, 
    BulkOperationStatus, WatermarkHistory
)
from app.routes.auth import require_auth, get_current_user
from app.storage.user_db import UserStore, User, Template
from app.storage.db import WatermarkStore
from app.services.watermarking import load_image_from_bytes, embed_watermark_lsb, save_image_to_bytes
from app.services.hashing import sha256_bytes

router = APIRouter()
user_store = UserStore.get_instance()
watermark_store = WatermarkStore.get_instance()  # This will initialize the watermarks table

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: User = Depends(require_auth)):
    """Get user dashboard statistics and recent activity"""
    stats = user_store.get_user_stats(current_user.id)
    
    return DashboardStats(
        total_watermarks=stats["total_watermarks"],
        total_verifications=stats["total_verifications"],
        storage_used_mb=stats["storage_used_mb"],
        protection_score=stats["protection_score"],
        recent_activity=[
            WatermarkHistory(
                watermark_id=item["watermark_id"],
                original_filename=item["original_filename"],
                owner_id=item["owner_id"],
                strength=item["strength"],
                file_size_mb=item["file_size_mb"],
                created_at=datetime.fromisoformat(item["created_at"]),
                verification_count=item["verification_count"]
            ) for item in stats["recent_activity"]
        ]
    )

@router.get("/templates", response_model=List[WatermarkTemplate])
async def get_user_templates(current_user: User = Depends(require_auth)):
    """Get user's watermark templates including default ones"""
    templates = user_store.get_user_templates(current_user.id)
    
    return [
        WatermarkTemplate(
            id=t.id,
            name=t.name,
            strength=t.strength,
            description=t.description,
            is_default=t.is_default
        ) for t in templates
    ]

@router.post("/templates", response_model=dict)
async def create_template(
    name: str = Form(...),
    strength: int = Form(...),
    description: str = Form(""),
    current_user: User = Depends(require_auth)
):
    """Create a new watermark template"""
    if not (1 <= strength <= 10):
        raise HTTPException(status_code=400, detail="Strength must be between 1 and 10")
    
    if len(name.strip()) == 0:
        raise HTTPException(status_code=400, detail="Template name cannot be empty")
    
    template_id = user_store.create_template(
        user_id=current_user.id,
        name=name.strip(),
        strength=strength,
        description=description.strip()
    )
    
    return {
        "message": "Template created successfully",
        "template_id": template_id
    }

@router.get("/history", response_model=List[WatermarkHistory])
async def get_watermark_history(
    limit: int = 20,
    current_user: User = Depends(require_auth)
):
    """Get user's watermark history with pagination"""
    # This is a simplified version - in production you'd want proper pagination
    stats = user_store.get_user_stats(current_user.id)
    
    # Get more detailed history (this is a mock implementation)
    history = []
    for item in stats["recent_activity"][:limit]:
        history.append(WatermarkHistory(
            watermark_id=item["watermark_id"],
            original_filename=item["original_filename"],
            owner_id=item["owner_id"],
            strength=item["strength"],
            file_size_mb=item["file_size_mb"],
            created_at=datetime.fromisoformat(item["created_at"]),
            verification_count=item["verification_count"]
        ))
    
    return history

# Bulk operations (simplified implementation)
bulk_operations = {}  # In production, use Redis or database

@router.post("/bulk/watermark", response_model=dict)
async def start_bulk_watermark(
    files: List[UploadFile] = File(...),
    owner_id: str = Form(...),
    strength: int = Form(5),
    template_id: Optional[str] = Form(None),
    current_user: User = Depends(require_auth)
):
    """Start bulk watermarking operation"""
    if len(files) > 50:  # Limit for demo
        raise HTTPException(status_code=400, detail="Maximum 50 files allowed")
    
    if not (1 <= strength <= 10):
        raise HTTPException(status_code=400, detail="Strength must be between 1 and 10")
    
    operation_id = str(uuid.uuid4())
    
    # Store operation status
    bulk_operations[operation_id] = {
        "status": "pending",
        "total_files": len(files),
        "processed_files": 0,
        "failed_files": 0,
        "created_at": datetime.utcnow(),
        "user_id": current_user.id,
        "results": []
    }
    
    # Start background processing (simplified)
    asyncio.create_task(process_bulk_watermark(operation_id, files, owner_id, strength))
    
    return {
        "message": "Bulk operation started",
        "operation_id": operation_id,
        "total_files": len(files)
    }

async def process_bulk_watermark(operation_id: str, files: List[UploadFile], owner_id: str, strength: int):
    """Background task to process bulk watermarking"""
    operation = bulk_operations[operation_id]
    operation["status"] = "processing"
    
    for i, file in enumerate(files):
        try:
            # Read file
            raw_bytes = await file.read()
            if not raw_bytes:
                operation["failed_files"] += 1
                continue
            
            # Process watermark
            image = load_image_from_bytes(raw_bytes)
            watermarked_image, binary_data = embed_watermark_lsb(image, owner_id, strength)
            watermarked_bytes = save_image_to_bytes(watermarked_image, "png")
            
            # Store metadata
            watermarked_image_hash = sha256_bytes(watermarked_bytes.getvalue())
            watermark_id = str(uuid.uuid4())
            watermark_store.save_record(
                watermark_id=watermark_id,
                image_hash=watermarked_image_hash,
                owner_id=owner_id,
                strength=strength,
                total_bits=len(binary_data)
            )
            
            operation["results"].append({
                "filename": file.filename,
                "watermark_id": watermark_id,
                "status": "success"
            })
            operation["processed_files"] += 1
            
        except Exception as e:
            operation["failed_files"] += 1
            operation["results"].append({
                "filename": file.filename,
                "error": str(e),
                "status": "failed"
            })
        
        # Reset file position for next iteration
        await file.seek(0)
    
    operation["status"] = "completed"

@router.get("/bulk/{operation_id}", response_model=BulkOperationStatus)
async def get_bulk_operation_status(
    operation_id: str,
    current_user: User = Depends(require_auth)
):
    """Get status of bulk operation"""
    if operation_id not in bulk_operations:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    operation = bulk_operations[operation_id]
    
    # Check if user owns this operation
    if operation["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return BulkOperationStatus(
        operation_id=operation_id,
        status=operation["status"],
        total_files=operation["total_files"],
        processed_files=operation["processed_files"],
        failed_files=operation["failed_files"],
        created_at=operation["created_at"]
    )

@router.get("/analytics", response_model=dict)
async def get_analytics(current_user: User = Depends(require_auth)):
    """Get user analytics and protection reports"""
    stats = user_store.get_user_stats(current_user.id)
    
    # Mock analytics data
    analytics = {
        "protection_trends": {
            "last_7_days": [12, 15, 8, 22, 18, 25, 20],
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        },
        "strength_distribution": {
            "light": 30,
            "medium": 45,
            "strong": 25
        },
        "verification_success_rate": 94.5,
        "most_used_template": "Medium Protection",
        "total_protected_assets": stats["total_watermarks"],
        "estimated_protection_value": stats["total_watermarks"] * 15.50  # Mock value
    }
    
    return analytics