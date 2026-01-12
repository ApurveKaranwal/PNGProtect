# 🛡️ PNGProtect

**Professional invisible watermarking system with user authentication, dashboard management, and blockchain integration.**

## ✨ Features

- **🔐 User Authentication** - JWT-like token system with role-based access
- **🖼️ Invisible Watermarking** - Advanced steganography with adjustable strength (1-10 levels)
- **📊 Dashboard Analytics** - User statistics, watermark history, and usage tracking
- **🔍 Verification System** - Watermark detection with confidence scoring
- **🧹 Metadata Stripping** - Privacy protection tool for removing image metadata
- **⚡ Bulk Operations** - Process multiple images efficiently with templates
- **🌐 Blockchain Integration** - MetaMask wallet connection for on-chain ownership registry
- **📜 Smart Contracts** - Ethereum-based ownership registration system

## 🚀 Quick Start

### Backend Setup
```bash
cd PNGProtect/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Access
Open `PNGProtect/frontend/index.html` in your browser or serve with any HTTP server.

### Demo Login
- **Email**: `demo@pngprotect.com`
- **Password**: `demo123`

### Wallet Connection
- Install **MetaMask** browser extension
- Click **"Connect Wallet"** to link your Ethereum wallet
- Register watermark ownership on-chain after verification

## 📁 Project Structure

```
PNGProtect/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Data schemas
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── storage/        # Database layer
│   │   └── main.py         # FastAPI app
│   ├── contracts/          # Smart contracts (Solidity)
│   └── requirements.txt    # Dependencies
├── frontend/               # Web interface
│   ├── index.html         # Home page with wallet integration
│   ├── login.html         # Authentication
│   ├── dashboard.html     # User dashboard
│   ├── *.js              # JavaScript modules
│   └── *.css             # Styling
└── README.md             # This file
```

## 🔧 API Endpoints

- **Authentication**: `/auth/login`, `/auth/register`, `/auth/me`
- **Watermarking**: `/watermark/embed`, `/watermark/{id}`
- **Verification**: `/verify/detect`, `/verify/extract`
- **Dashboard**: `/dashboard/stats`, `/dashboard/analytics`
- **Metadata**: `/metadata/strip`
- **Blockchain Registry**: `/registry/abi` (smart contract integration)

## � Blockchain Features

### Wallet Integration
- **MetaMask Connection** - Seamless wallet linking
- **Account Management** - Automatic account switching detection
- **Network Support** - Ethereum mainnet and testnets

### On-Chain Registration
- **Ownership Registry** - Register watermark ownership on blockchain
- **Smart Contract** - Ethereum-based ownership verification
- **Immutable Records** - Permanent ownership proof

### Usage Flow
1. **Watermark** your image using the invisible watermarking system
2. **Verify** the watermark is properly embedded
3. **Connect Wallet** using MetaMask
4. **Register Ownership** on-chain for permanent proof

## 🎨 Tech Stack

- **Backend**: FastAPI, SQLite, Python
- **Frontend**: Vanilla JavaScript, CSS Grid, HTML5
- **Authentication**: JWT-like tokens, password hashing
- **Blockchain**: ethers.js, MetaMask integration, Solidity smart contracts
- **Styling**: Glassmorphism design, responsive layout

## 🔒 Security Features

- **Password Hashing** with SHA-256
- **Session Management** with secure tokens
- **CORS Protection** properly configured
- **Input Validation** on all endpoints
- **Blockchain Security** - Immutable ownership records

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built for digital content protection with blockchain-verified ownership** 🛡️⛓️