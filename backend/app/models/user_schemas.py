from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.FREE

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    created_at: datetime
    watermarks_count: int
    storage_used_mb: float

class WatermarkTemplate(BaseModel):
    id: str
    name: str
    strength: int
    description: str
    is_default: bool = False

class WatermarkHistory(BaseModel):
    watermark_id: str
    original_filename: str
    owner_id: str
    strength: int
    file_size_mb: float
    created_at: datetime
    verification_count: int

class DashboardStats(BaseModel):
    total_watermarks: int
    total_verifications: int
    storage_used_mb: float
    protection_score: int
    recent_activity: List[WatermarkHistory]

class BulkOperationRequest(BaseModel):
    owner_id: str
    strength: int
    template_id: Optional[str] = None

class BulkOperationStatus(BaseModel):
    operation_id: str
    status: str  # "pending", "processing", "completed", "failed"
    total_files: int
    processed_files: int
    failed_files: int
    created_at: datetime