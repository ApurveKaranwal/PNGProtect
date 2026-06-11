# PNGProtect

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com/ApurveKaranwal/PNGProtect)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> **Invisible Watermarking. Visible Ownership. Robust AI Protection.**

**PNGProtect** is an enterprise-grade image security and protection platform designed to empower digital creators, photographers, and enterprises in the age of generative AI and large-scale model training. By combining advanced steganography, cryptographic hashing, forensic analysis, and adversarial machine learning, PNGProtect delivers a comprehensive, multi-layered defense system for protecting digital intellectual property.

### Mission
To provide creators with a seamless, robust, and non-intrusive solution for asserting ownership, preventing unauthorized AI training on their work, and detecting tampering or malicious modifications of their digital assets.

---

## Live Demo

**Frontend**: [https://pngprotect.apurve.xyz](https://pngprotect.apurve.xyz)
**Backend API**: [https://pngprotect-h6f4.onrender.com](https://pngprotect-h6f4.onrender.com)

---

##  Core Features

### ️ AI Shield – Adversarial Protection
**Prevent unauthorized AI training on your artwork.**

The AI Shield module implements cutting-edge adversarial attack techniques to make images resistant to machine learning model training:

- **FGSM-Based Perturbation**: Uses Fast Gradient Sign Method to inject imperceptible adversarial noise that disrupts feature extraction in popular CV models (ResNet, CLIP, ViT, etc.)
- **Model-Agnostic Defense**: Attacks are crafted to be effective against multiple architectures, not just specific models
- **Unlearnable Data Generation**: Creates images that "teach wrong" to AI models, making them ineffective for training without affecting human perception
- **Scalable Protection Levels**: Adjust noise intensity from subtle (minimal perceptual impact) to aggressive (maximum robustness)
- **Real-time Robustness Scoring**: Quantifies how resistant an image is to adversarial attacks and model interpretation
- **Zero Visual Quality Loss**: Protected images appear identical to the naked eye—artistic integrity is preserved

### ️ AI Confusion Visualizer
**See exactly what the AI sees.**

A powerful educational and diagnostic tool that visualizes how computer vision models perceive your images before and after protection:

- **Adversarial Noise Heatmaps**: Visualize the exact pixels that are confusing the AI using Jet color maps
- **Real-time Confusion Scoring**: rigorous metric calculating the divergence between the model's original prediction and its prediction on the protected image
- **Perception Comparison**: Side-by-side view of how a standard ResNet50 model classifies the original vs. protected image
- **Interactive Analysis**: Upload any image to see how "robust" it naturally is against AI recognition

###  Invisible Watermarking
**Assert ownership with stealth and precision.**

The watermarking module embeds cryptographic proof of ownership directly into image data:

- **LSB Steganography**: Encodes ownership identifiers in the Least Significant Bits of pixel data
- **Cryptographic Hashing**: Uses SHA-256 and Blake2 for tamper-proof identity verification
- **Imperceptible Embedding**: Watermarks remain invisible to human eyes while being machine-readable
- **Robust Persistence**: Survives JPEG compression, format conversion, and minor image editing
- **Fast Verification**: Watermark extraction takes milliseconds, enabling real-time authenticity checks
- **Metadata Integration**: Watermarks encode timestamp, creator info, and license metadata

###  Forensic Tamper Detection
**Detect manipulation with forensic precision.**

Advanced forensic analysis tools to verify image authenticity and detect unauthorized modifications:

- **Binary Similarity Analysis**: Compares pixel-level data to detect even minor alterations
- **Compression Artifact Detection**: Identifies JPEG and PNG compression signatures
- **Manipulation Scoring**: Returns a confidence score (0-100%) indicating likelihood of tampering
- **Layer Analysis**: Detects cropping, resizing, and content-aware fill artifacts
- **Statistical Anomaly Detection**: Uses ML classifiers to identify unnatural pixel patterns
- **Temporal Integrity**: Tracks creation time and modification history when metadata is available

###  Metadata Management
**Privacy-first image distribution.**

Comprehensive metadata handling for secure sharing:

- **EXIF Stripping**: Removes camera model, serial numbers, and device fingerprints
- **GPS Sanitization**: Eliminates geolocation data to protect creator privacy
- **Color Profile Removal**: Strips ICC profiles and color management metadata
- **Device Anonymization**: Removes software/firmware information that could identify you
- **Selective Preservation**: Option to keep essential color space info while removing sensitive data

###  Registry Management
**On-chain ownership records (Blockchain Integration).**

Optional Web3 integration for decentralized ownership verification:

- **Ethereum Integration**: Register ownership claims on-chain using Smart Contracts
- **Immutable Records**: Create permanent, auditable proof of ownership and timestamps
- **Web3 Wallet Support**: Connect via MetaMask, WalletConnect, or other Web3 providers
- **Multi-Chain Support**: Extensible architecture for Polygon, Arbitrum, and other L2s
- **Registry Verification**: Public verification of ownership claims

###  Detection & Classification
**ML-powered image analysis.**

Advanced machine learning capabilities for content analysis:

- **Content Classification**: Categorizes images (artwork, photography, generated, etc.)
- **Model Training**: Framework for custom model training on protected image datasets
- **Batch Processing**: Support for processing multiple images at scale
- **Performance Metrics**: Accuracy, precision, recall, and F1 scores for all classifiers

###  Authentication & Security
**Enterprise-grade access control.**

Robust security infrastructure for protecting API endpoints:

- **JWT-Based Authentication**: Secure token-based API access
- **Role-Based Access Control**: Admin, creator, and viewer roles with granular permissions
- **Rate Limiting**: DDoS protection and fair-use enforcement
- **HTTPS/TLS Support**: Encrypted communication for all data in transit
- **Environment Configuration**: Secure handling of API keys and secrets via .env files

---

## ️ Architecture & Technical Stack

PNGProtect is engineered as a modern, production-ready full-stack application with separated concerns, asynchronous processing, and enterprise-grade security.

### Technology Stack Overview

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Framework** | FastAPI 0.95+ | High-performance async REST API with automatic documentation |
| **ML Engine** | PyTorch 2.0+, Torchvision | Deep learning framework for adversarial attacks and model training |
| **Image Processing** | OpenCV, Pillow, NumPy, SciPy | Matrix operations, steganography, compression analysis |
| **Security** | PyJWT, Passlib, Bcrypt | Authentication tokens, password hashing, cryptographic operations |
| **Web3** | Ethers.js, Web3.py | Blockchain integration for ownership registry |
| **Frontend** | HTML5, CSS3, ES6+ JavaScript | Responsive, accessible user interface with glassmorphism design |

### Backend Architecture (Python/FastAPI)

The backend implements a modular, service-oriented architecture:

```
app/
├── main.py                 # FastAPI app initialization, CORS, middleware config
├── models/
│   └── schemas.py          # Pydantic request/response schemas for API contracts
├── routes/                 # API endpoint definitions (organized by feature)
│   ├── protection.py       # POST /protect - AI Shield protection endpoint
│   ├── watermark.py        # POST /watermark/embed, GET /watermark/verify - Watermarking
│   ├── verify.py           # POST /verify - Verify watermark presence
│   ├── detection.py        # POST /detect - Forensic analysis & tampering detection
│   ├── metadata.py         # POST /metadata/clean - EXIF/GPS removal
│   ├── registry.py         # POST /registry/register - Blockchain ownership
│   └── auth.py             # POST /auth/login - Authentication (JWT)
├── services/               # Core business logic & algorithms
│   ├── adversarial.py      # FGSM attack generation, robustness scoring
│   ├── watermarking.py     # LSB embedding/extraction, hashing
│   ├── detection.py        # ML-based tampering detection, classification
│   ├── forensics.py        # Binary analysis, artifact detection
│   ├── ml_classifier.py    # Model training & inference
│   ├── hashing.py          # Cryptographic hashing utilities
│   └── <feature>.py        # Additional service modules
├── storage/
│   └── db.py               # Database models & ORM configuration (if applicable)
└── utils/                  # Helper functions, validators, error handlers
```

**Design Patterns Used:**
- **Service Layer Pattern**: Business logic isolated from API routes
- **Dependency Injection**: FastAPI dependency system for testability
- **Factory Pattern**: Model and detector instantiation
- **Strategy Pattern**: Multiple watermarking/detection algorithms

### Frontend Architecture (Web)

A modern, multi-page application (MPA) built with vanilla web technologies for maximum performance and separation of concerns:

```
frontend/
├── index.html              # Landing Page & Feature Overview
├── ai-shield.html          # AI Shield Interface (Adversarial Protection)
├── ai-vision.html          # AI Confusion Visualizer (Heatmaps & Analysis)
├── watermark.html          # Watermarking Interface (Embed/Extract)
├── verify.html             # Verification Interface
├── detect.html             # Tampering Detection Interface
├── cleanup.html            # Metadata Cleaning Interface
├── script.js               # Shared Client-side logic & API Communication
└── style.css               # Shared Design System (Glassmorphism)
```

### Complete Directory Structure

```
PNGProtect/
│
├── backend/                           #  Server-side Core Logic
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point, routes registration
│   │   ├── models/
│   │   │   └── schemas.py            # Pydantic models for request/response validation
│   │   ├── routes/                   # API Endpoint Handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Authentication & JWT tokens
│   │   │   ├── protection.py         # AI Shield protection endpoint
│   │   │   ├── watermark.py          # Watermarking embed/verify endpoints
│   │   │   ├── verify.py             # Quick watermark verification
│   │   │   ├── detection.py          # Tampering detection endpoint
│   │   │   ├── metadata.py           # Metadata cleaning endpoint
│   │   │   ├── registry.py           # Blockchain registry endpoints
│   │   │   └── __pycache__/
│   │   ├── services/                 # Business Logic Layer
│   │   │   ├── __init__.py
│   │   │   ├── adversarial.py        # FGSM attacks, robustness scoring
│   │   │   ├── watermarking.py       # LSB steganography, embedding/extraction
│   │   │   ├── detection.py          # ML-based tampering detection
│   │   │   ├── forensics.py          # Forensic analysis, artifact detection
│   │   │   ├── ml_classifier.py      # Model training & inference
│   │   │   ├── hashing.py            # SHA-256, Blake2, cryptographic utilities
│   │   │   └── __pycache__/
│   │   ├── storage/                  # Data Persistence
│   │   │   ├── __init__.py
│   │   │   ├── db.py                 # Database models & ORM
│   │   │   └── __pycache__/
│   │   └── __pycache__/
│   │
│   ├── contracts/                    #  Smart Contracts (Blockchain)
│   │   └── OwnershipRegistry.sol     # Solidity contract for on-chain ownership
│   │
│   ├── requirements.txt              # Python package dependencies
│   ├── .env.example                  # Environment variables template
│   └── venv/                         # Python virtual environment (auto-created)
│
├── frontend/                         #  Client-side Interface
│   ├── index.html                   # Landing page
│   ├── ai-shield.html               # Protection tool
│   ├── ai-vision.html               # Confusion visualizer
│   ├── watermark.html               # Watermarking tool
│   ├── verify.html                  # Verification tool
│   ├── detect.html                  # Forensics tool
│   ├── cleanup.html                 # Metadata tool
│   ├── script.js                    # Application logic
│   ├── style.css                    # Glassmorphism styles
│   └── assets/                      # Images & icons
│
├── .gitignore                       # Git ignore rules
├── LICENSE                          # MIT License
└── README.md                        # This file

```

### API Endpoints Reference

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| **GET** | `/` | Health check | `{"status": "ok"}` |
| **POST** | `/ai-vision` | Visualise AI Confusion | Heatmap + confusion score |
| **POST** | `/protect` | Apply AI Shield protection | Protected image + robustness score |
| **POST** | `/watermark/embed` | Embed watermark | Watermarked image |
| **POST** | `/watermark/extract` | Extract watermark | Owner ID, metadata |
| **POST** | `/verify` | Quick watermark check | Boolean + confidence score |
| **POST** | `/detect` | Tampering detection | Detection results + confidence |
| **POST** | `/metadata/clean` | Remove EXIF/GPS | Cleaned image |
| **POST** | `/registry/register` | Blockchain registration | TX hash, owner proof |
| **POST** | `/auth/login` | User authentication | JWT token |

---

##  Getting Started

Comprehensive setup instructions for local development and production deployment.

### System Requirements

- **Python**: 3.10 or higher (for async/await support and type hints)
- **Node.js**: 14+ (optional, for advanced frontend tooling)
- **RAM**: Minimum 8GB recommended (PyTorch models require significant memory)
- **GPU**: Optional but recommended for faster adversarial attack generation (NVIDIA CUDA 11.8+)
- **Disk Space**: ~5GB (includes PyTorch model downloads)
- **OS**: Windows, macOS, or Linux

### Prerequisites

- Git (for cloning the repository)
- A code editor (VS Code, PyCharm, etc.)
- pip (Python package manager)
- Virtual environment tool (venv, conda, or poetry)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/ApurveKaranwal/PNGProtect.git
cd PNGProtect
```

#### 2. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate Virtual Environment:
# On Linux/macOS:
source venv/bin/activate

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.\venv\Scripts/activate.bat

# Install Dependencies
pip install -r requirements.txt
```

> **Note:** PyTorch installation can be large (~2-3GB) depending on your system configuration. If you have a CUDA-enabled GPU, you can optionally install a GPU-accelerated version for faster processing.

#### 3. Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration (API keys, database URLs, etc.):

```dotenv
# Server Config
SERVER_HOST=127.0.0.1
SERVER_PORT=8000

# Database
DATABASE_URL=sqlite:///./pngprotect.db

# JWT Security
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Web3 (Optional)
WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
REGISTRY_CONTRACT_ADDRESS=0x...

# ML Models
MODEL_CACHE_DIR=./models
DEVICE=cuda  # or 'cpu' if GPU not available
```

#### 4. Start the Backend Server

```bash
# From the backend directory (with venv activated)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`

**API Documentation:**
- Swagger UI (Interactive): `http://127.0.0.1:8000/docs`
- ReDoc (Alternative): `http://127.0.0.1:8000/redoc`

#### 5. Launch the Frontend

In a **new terminal**, navigate to the frontend directory:

```bash
cd frontend

# Option A: Using Python's built-in HTTP server
python -m http.server 3000

# Option B: Using Node.js (if installed)
npx http-server -p 3000

# Option C: Using any other simple server
```

Open your browser and navigate to: **`http://localhost:3000`**

---

##  Usage Guide

### Complete Workflow Examples

#### Scenario 1: Protecting Original Artwork

1. **Access the App**: Open `http://localhost:3000` in your browser
2. **Navigate to AI Shield**: Click the "️ AI Shield" tab
3. **Upload Your Image**: Drag & drop or select your artwork (JPEG, PNG, BMP)
4. **Configure Protection**:
   - **Protection Level**: Slider from 1-100%
     - 30%: Minimal, imperceptible perturbations
     - 50%: Recommended balance (standard setting)
     - 80%+: Aggressive, maximum protection (may introduce slight grain)
5. **Apply Protection**: Click "Protect Image" and wait for processing
6. **Download**: Right-click the result and "Save Image As..." to download
7. **Verify**: Test in any reverse image search to confirm reduced AI visibility

#### Scenario 1.5: Visualizing AI Confusion
1. **Navigate to AI Vision**: Click the "️ AI Vision" tab
2. **Upload Image**: Select an image to analyze
3. **Run Analysis**: Click "Run Visual Analysis"
4. **View Results**:
    - **Confusion Score**: See a numerical score of how confused the AI is
    - **Heatmap**: View the colorful overlay showing where the adversarial noise is most effective
    - **Prediction Change**: See how the model's top guess (e.g., "Tabby Cat") changes after protection (e.g., "Dishwasher")

#### Scenario 2: Embedding & Verifying Ownership

1. **Embed Watermark**:
   - Go to " Watermark" tab
   - Upload your original image
   - Enter your Owner ID (email, hash, or identifier)
   - Add optional metadata (title, copyright year)
   - Click "Embed Watermark"
   - Download the watermarked image

2. **Verify Ownership**:
   - Go to " Verify" tab
   - Upload any image (original or modified)
   - Click "Check Watermark"
   - System displays:
     -  Watermark found /  No watermark
     - Owner ID (if present)
     - Confidence score
     - Extraction timestamp

#### Scenario 3: Forensic Analysis

1. **Upload Suspect Image**: Go to " Detection" tab
2. **Run Analysis**: Click "Analyze for Tampering"
3. **Review Results**:
   - **Manipulation Score**: 0-100% likelihood of modification
   - **Detected Artifacts**: List of suspicious patterns
   - **Compression History**: Original vs current compression
   - **Modification Timeline**: Estimated edit points
4. **Export Report**: Download detailed forensic report (PDF)

#### Scenario 4: Privacy-Safe Sharing

1. **Upload Image**: Go to " Metadata" tab
2. **Review Metadata**: See current EXIF, GPS, device info
3. **Clean Image**: Click "Remove All Metadata"
4. **Download**: Save cleaned image without personal information
5. **Share Safely**: Distribute without exposing location or device details

---

##  API Integration Examples

### Using the REST API Directly

#### Example: Protect an Image with AI Shield

```bash
curl -X POST http://127.0.0.1:8000/protect \
  -F "file=@/path/to/image.jpg" \
  -F "protection_level=50" \
  --output protected_image.jpg
```

Response includes header: `X-Robustness-Score: 78` (robustness percentage)

#### Example: Embed a Watermark

```bash
curl -X POST http://127.0.0.1:8000/watermark/embed \
  -F "file=@/path/to/image.jpg" \
  -F "owner_id=artist@example.com" \
  -F "metadata={\"title\":\"My Artwork\",\"year\":2024}" \
  --output watermarked.jpg
```

#### Example: Verify Watermark

```bash
curl -X POST http://127.0.0.1:8000/verify \
  -F "file=@/path/to/image.jpg" \
  | jq .
```

Response:
```json
{
  "watermark_detected": true,
  "owner_id": "artist@example.com",
  "confidence": 0.95,
  "metadata": {
    "title": "My Artwork",
    "year": 2024,
    "embedded_at": "2024-01-19T10:30:00Z"
  }
}
```

### Python Client Example

```python
import requests
from pathlib import Path

API_URL = "http://127.0.0.1:8000"

def protect_image(image_path, protection_level=50):
    """Apply AI Shield protection to an image."""
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'protection_level': protection_level}
        response = requests.post(
            f"{API_URL}/protect",
            files=files,
            data=data
        )
    
    robustness_score = response.headers.get('X-Robustness-Score')
    return response.content, robustness_score

def verify_watermark(image_path):
    """Check if an image contains a watermark."""
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_URL}/verify", files=files)
    
    return response.json()

# Usage
protected, score = protect_image('artwork.jpg', protection_level=60)
with open('artwork_protected.jpg', 'wb') as f:
    f.write(protected)
print(f"Robustness Score: {score}%")

# Verify
result = verify_watermark('artwork_protected.jpg')
print(f"Watermark found: {result['watermark_detected']}")
```

---

##  Testing & Validation

### Manual Testing Checklist

- [ ] Backend server starts without errors
- [ ] API docs accessible at `/docs`
- [ ] Frontend loads without JS errors
- [ ] Image upload works for PNG, JPG, BMP formats
- [ ] AI Shield protection generates different output on repeated runs
- [ ] Watermarking embeds owner ID successfully
- [ ] Watermark extraction returns correct owner ID
- [ ] Metadata cleaning removes EXIF/GPS
- [ ] Forensic analysis detects synthetic images vs originals
- [ ] Download functionality preserves image quality

### Performance Benchmarks

(Run on typical hardware: 8GB RAM, CPU-only)

| Operation | Time | Notes |
|-----------|------|-------|
| AI Shield (single image) | 3-8s | Depends on protection level |
| Watermark Embed | 0.5-1s | Fast LSB encoding |
| Watermark Extract | 0.1-0.3s | Sub-second verification |
| Tampering Detection | 1-2s | ML model inference |
| Metadata Cleaning | 0.1s | EXIF stripping |

---

##  Security Considerations

### Best Practices

1. **Never commit `.env` files** to version control
2. **Rotate JWT secrets** regularly in production
3. **Use HTTPS/TLS** in production deployments
4. **Implement rate limiting** to prevent abuse
5. **Validate all file uploads** for size and format
6. **Sanitize file names** to prevent directory traversal
7. **Store processed images** securely or delete after serving
8. **Monitor API logs** for suspicious activity

### Data Privacy

- Images are **not stored** on the server by default
- All processing happens in memory
- Optional: Configure image retention policies
- GDPR/CCPA compliant (no data persistence without consent)

---

##  Contributing

We welcome contributions from the community! Contributions can take many forms:

- **Bug Reports**: Found an issue? Open a GitHub Issue with reproduction steps
- **Feature Requests**: Have an idea? Discuss in Issues before submitting code
- **Code Contributions**: Fix bugs or implement features
- **Documentation**: Improve README, API docs, or code comments
- **Testing**: Add tests for new functionality

### Contributing Workflow

1. **Fork** the repository on GitHub
2. **Clone** your fork locally: `git clone https://github.com/YOUR_USERNAME/PNGProtect.git`
3. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
4. **Make your changes**: Commit with clear, descriptive messages
5. **Test thoroughly**: Ensure no regressions
6. **Push to your fork**: `git push origin feature/AmazingFeature`
7. **Open a Pull Request**: Submit PR with detailed description of changes
8. **Code Review**: Address feedback and iterate

### Development Guidelines

- Follow PEP 8 for Python code
- Add docstrings to functions and classes
- Include unit tests for new functionality
- Update README for user-facing changes
- Test both frontend and backend

---

##  Additional Resources

### Documentation
- **[API Documentation](http://localhost:8000/docs)**: Interactive Swagger UI (when server is running)
- **[PyTorch Docs](https://pytorch.org/docs/)**: Deep learning framework reference
- **[FastAPI Guide](https://fastapi.tiangolo.com/)**: Backend framework documentation
- **[Web3.py Docs](https://web3py.readthedocs.io/)**: Blockchain integration

### Research & References
- "Adversarial Examples Against Deep Neural Networks" - Goodfellow et al.
- "Invisible Watermarking for Image Authentication" - Research Papers
- "CLIP: Learning Transferable Models for Computer Vision Tasks" - Radford et al.
- "Unlearnable Examples: Making Personal Data Unexploitable" - Huang et al.

### Community & Support
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions and share ideas
- **Pull Requests**: Contribute improvements

---

##  License

Distributed under the **MIT License**. See the [LICENSE](LICENSE) file for complete details.

This means you are free to:
-  Use commercially
-  Modify and distribute
-  Use privately
- ️ Must include license and copyright notice

---

##  Roadmap

### Upcoming Features (v0.4+)
- [ ] Batch processing API for enterprise users
- [ ] GPU acceleration for faster processing
- [ ] Additional blockchain networks (Polygon, Arbitrum)
- [ ] Advanced ML model fine-tuning interface
- [ ] REST API key management dashboard
- [ ] Audit logs and compliance reporting
- [ ] Video protection (frame-by-frame watermarking)
- [ ] Mobile app (React Native)
- [ ] CLI tool for batch operations

### Long-term Vision
- Become the industry standard for digital asset protection
- Support multimedia (video, audio, 3D models)
- Integrate with major platforms (OpenSea, ArtStation, etc.)
- Enterprise deployment options (on-premise)
- AI-powered rights management system

---

<p align="center">
  <strong>Built with ️ by Apurve Karanwal</strong>
  <br>
  <a href="https://github.com/ApurveKaranwal/PNGProtect">GitHub</a> • 
  <a href="LICENSE">License</a> • 
  <a href="https://github.com/ApurveKaranwal/PNGProtect/issues">Report Issue</a>
</p>
