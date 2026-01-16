# PNGProtect

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com/ApurveKaranwal/PNGProtect)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> **Invisible Watermarking. Visible Ownership. Robust AI Protection.**

**PNGProtect** is a next-generation image security platform designed to empower creators in the age of generative AI. By combining steganography, cryptography, and adversarial machine learning, PNGProtect offers a multi-layered defense system for digital assets. Whether you are a digital artist, photographer, or platform, PNGProtect helps you assert ownership and protect your work from unauthorized AI training.

---

## 🌟 Key Features

### 🛡️ AI Shield (Adversarial Protection)
**Stop AI Scrapers in their tracks.**
- **Adversarial Noise Injection**: Injects imperceptible perturbations using Fast Gradient Sign Method (FGSM) that disrupt the feature extraction layers of computer vision models (e.g., ResNet, CLIP).
- **Unlearnable Data**: Makes images "unlearnable" for AI training pipelines without degrading visual quality for human viewers.
- **Robustness Scoring**: Real-time analysis providing a scored metric of how resistant your image is to AI interpretation.

### 🔐 Invisible Watermarking
**Ownership that stays with your content.**
- **LSB Steganography**: Embeds ownership identifiers directly into the pixel data (Least Significant Bits).
- **Imperceptible**: The watermark is invisible to the naked eye, preserving the artistic integrity of your work.
- **Machine-Readable**: Watermarks persist through standard file sharing and storage, allowing for automated verification.

### 🔍 Forensic Tamper Detection
**Verify authenticity with confidence.**
- **Integrity Analysis**: Automatically detects if an image has been modified, cropped, or compressed.
- **Confidence Scoring**: Provides a detailed confidence score indicating the likelihood of manipulation.
- **Artifact Detection**: Identifies potential removal attempts or post-processing artifacts.

### 🧹 Metadata Cleaning
**Privacy-first distribution.**
- **Strip Metadata**: Removes sensitive EXIF data, GPS coordinates, device information, and color profiles for clean, private sharing.

---

## 🏗️ Architecture & Tech Stack

PNGProtect is built as a modern full-stack application, ensuring high performance and scalability.

### Backend (Python/FastAPI)
The core logic resides in a high-performance Python backend.
- **API Framework**: `FastAPI` for asynchronous, high-speed API endpoints.
- **ML Engine**: `PyTorch` & `Torchvision` for adversarial attack generation (AI Shield).
- **Image Processing**: `OpenCV`, `Pillow (PIL)`, `NumPy` for matrix manipulation and steganography.
- **Security**: Cryptographic hashing and validation logic.

### Frontend (Static Web)
A lightweight, aesthetically pleasing interface using glassmorphism design principles.
- **Core**: Semantic `HTML5`, Modern `JavaScript (ES6+)`.
- **Styling**: Vanilla `CSS3` with custom animations and responsive layout.
- **Web3**: `Ethers.js` integration for optional blockchain wallet connectivity.

### Directory Structure
```
PNGProtect/
├── backend/                  # 🧠 Server-side Logic
│   ├── app/
│   │   ├── main.py           # Application Entry Point & Config
│   │   ├── routes/           # API Routers (Protection, Watermark, Verify)
│   │   └── services/         # Core Business Logic (Adversarial, Stego)
│   ├── requirements.txt      # Python Dependencies
│   └── venv/                 # Virtual Environment
├── frontend/                 # 🎨 Client-side Interface
│   ├── index.html            # Main UI
│   ├── script.js             # Interactivity & API Communication
│   └── style.css             # Glassmorphism Design System
└── README.md                 # 📖 Documentation
```

---

## 🚀 Getting Started

Follow these instructions to set up the project locally for development and testing.

### Prerequisites
- **Python**: Version 3.10 or higher.
- **Node.js**: (Optional) For serving the frontend via simple server.
- **Git**: For version control.

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/ApurveKaranwal/PNGProtect.git
cd PNGProtect
```

#### 2. Backend Setup
Set up the Python environment and install dependencies (including PyTorch).
```bash
cd backend
python -m venv venv
# Activate Virtual Environment:
source venv/bin/activate      # Linux/macOS
# .\venv\Scripts\activate     # Windows PowerShell

# Install Dependencies
pip install -r requirements.txt
```
> **Note:** PyTorch installation size is approx ~2GB if CUDA is enabled.

#### 3. Start the Backend Server
Run the FastAPI server with hot-reload enabled.
```bash
python -m uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can view the automatic API docs at `http://127.0.0.1:8000/docs`.

#### 4. Launch the Frontend
In a new terminal, navigate to the frontend directory and serve the static files.
```bash
cd ../frontend
# Using Python's built-in server
python -m http.server 3000
```
Open your browser and navigate to `http://localhost:3000`.

---

## � Usage Guide

### Using AI Shield
1.  Navigate to the **AI Shield** section in the web app.
2.  **Upload**: Drag & drop your artwork or photo.
3.  **Configure**: Adjust the "Protection Level" slider.
    *   **Standard (50%)**: Recommended balance between invisibility and protection.
    *   **High (80%+)**: Stronger perturbations, may introduce slight grain.
4.  **Apply**: Click "Apply AI Shield". The backend will process the image (first run may take a few seconds to load models).
5.  **Download**: Save your protected image.

### Verifying Ownership
1.  Go to the **Verify** tab.
2.  Upload an image you suspect contains a watermark.
3.  The system will decode the LSB data and recover the **Owner ID** if present.

---

## 🤝 Contributing

We welcome contributions from the community! Whether it's fixing bugs, improving documentation, or proposing new features.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Built with ❤️ by <strong>Apurve Karanwal</strong>
</p>
