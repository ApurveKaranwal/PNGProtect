from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user_schemas import UserCreate, UserLogin, UserResponse
from app.storage.user_db import UserStore, User
from typing import Optional

router = APIRouter()
security = HTTPBearer(auto_error=False)
user_store = UserStore.get_instance()

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    if not credentials:
        return None
    
    user = user_store.get_user_by_token(credentials.credentials)
    return user

async def require_auth(current_user: Optional[User] = Depends(get_current_user)) -> User:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """Register a new user account"""
    try:
        user_id = user_store.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role
        )
        
        # Create session token
        token = user_store.create_session(user_id)
        
        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "token": token
        }
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=dict)
async def login(login_data: UserLogin):
    """Login user and return session token"""
    user = user_store.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = user_store.create_session(user.id)
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(require_auth)):
    """Get current user information"""
    stats = user_store.get_user_stats(current_user.id)
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        created_at=current_user.created_at,
        watermarks_count=stats["total_watermarks"],
        storage_used_mb=stats["storage_used_mb"]
    )

@router.post("/logout")
async def logout(current_user: User = Depends(require_auth)):
    """Logout user (in a real app, you'd invalidate the token)"""
    return {"message": "Logged out successfully"}