from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import watermark, verify, metadata, auth, dashboard
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI(
    title="PNGProtect API",
    description="Invisible image watermarking with user management and dashboard.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(watermark.router, prefix="/watermark", tags=["Watermark"])
app.include_router(verify.router, prefix="/verify", tags=["Verify"])
app.include_router(metadata.router, prefix="/metadata", tags=["Metadata"])
from app.routes import registry as registry_router
app.include_router(registry_router.router, prefix="/registry", tags=["Registry"])

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "API running"}
