# 🏛️ Harambee DAO Backend

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)

**AI-audited, multi-signature governed community treasury with SMS governance**

A comprehensive FastAPI backend for managing community savings groups (Chamas/ROSCAs) with blockchain-based treasury management, AI-powered milestone verification, and accessible SMS voting.

## 🎯 **Mission**

Stop embezzlement in community savings groups by releasing funds only after verifiable, AI-verified project milestones — and let members vote via SMS.

## ✨ **Key Features**

### 🏗️ **Core Infrastructure**
- **FastAPI** application with modular architecture
- **Pydantic** data validation and settings management
- **100% test coverage** requirement with pytest
- **Comprehensive logging** and error handling

### 👥 **User Management System**
- **Group Registration**: Community group onboarding with leader setup
- **Member Management**: Phone-based registration with role-based access
- **Phone Verification**: SMS OTP with rate limiting and security controls
- **KYC Processing**: Document submission, verification, and compliance tracking

### 📱 **SMS Integration**
- **Twilio Integration**: Professional SMS delivery and webhook processing
- **Vote Processing**: Parse votes from SMS (YES001/NO001 format)
- **Proposal Broadcasting**: Automated SMS notifications to verified members
- **Real-time Tallying**: Live vote counts and proposal status updates

### 🗳️ **Governance Features**
- **Proposal Management**: Creation, voting, and deadline management
- **Multi-signature Treasury**: Gnosis Safe integration for secure fund management
- **AI Audit Pipeline**: Computer vision verification of project milestones
- **Evidence Anchoring**: IPFS and Celestia integration for immutable records

---

## Features

## 🏗️ **Architecture**

```
backend/
├── app/
│   ├── api/                    # FastAPI route handlers
│   │   ├── routes.py          # Main API router
│   │   └── user_routes.py     # User management endpoints
│   ├── services/              # Business logic layer
│   │   ├── user_service.py    # Group & member management
│   │   ├── kyc_service.py     # KYC processing
│   │   ├── phone_verification_service.py  # OTP verification
│   │   ├── sms_service.py     # SMS processing & voting
│   │   ├── proposal_service.py # Proposal management
│   │   ├── audit_service.py   # AI audit processing
│   │   └── vote_service.py    # Vote tallying
│   ├── models/                # Data models
│   │   └── schemas.py         # Pydantic schemas
│   ├── utils/                 # Utility functions
│   │   ├── sms.py            # Twilio integration
│   │   ├── ipfs.py           # IPFS utilities
│   │   ├── oracle.py         # Oracle verification
│   │   └── celestia.py       # Celestia integration
│   └── core/                  # Core configuration
│       ├── config.py         # Settings management
│       └── logging.py        # Logging setup
├── tests/                     # Test suite
├── docs/                      # Documentation
└── pyproject.toml            # Project configuration
```

## 🚀 **Quick Start**

### Prerequisites
- Python 3.9+
- pip or poetry
- Twilio account (for SMS features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Harambee-Dao/Harambee-Dao-Backend.git
cd Harambee-Dao-Backend
```

2. **Install dependencies**
```bash
pip install -e .
# or with development dependencies
pip install -e .[dev]
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the application**
```bash
uvicorn app.main:app --reload --port 8000
```

5. **Verify installation**
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/ping
```

---

## 📚 **API Documentation**

### **Core Endpoints**

#### Health & Status
```
GET  /health                    # Application health check
GET  /api/ping                  # API connectivity test
GET  /api/testall              # Smoke test all services
```

#### Group Management
```
POST /api/users/groups                    # Create new group
GET  /api/users/groups                    # List all groups
GET  /api/users/groups/{group_id}         # Get group details
GET  /api/users/groups/{group_id}/members # List group members
PATCH /api/users/groups/{group_id}/treasury # Update treasury address
```

#### Member Management
```
POST /api/users/members                   # Register new member
GET  /api/users/members/{member_id}       # Get member details
GET  /api/users/members/phone/{phone}     # Get member by phone
PATCH /api/users/members/{member_id}      # Update member info
GET  /api/users/members/{member_id}/group # Get member's group info
```

#### Phone Verification
```
POST /api/users/phone/request-otp         # Request OTP
POST /api/users/phone/verify-otp          # Verify OTP
GET  /api/users/phone/{phone}/otp-status  # Get OTP status
```

#### KYC Management
```
POST /api/users/kyc/documents             # Submit KYC document
GET  /api/users/kyc/members/{id}/documents # Get member documents
POST /api/users/kyc/review                # Review KYC status
GET  /api/users/kyc/pending-reviews       # Get pending reviews
```

#### Proposal & Voting
```
POST /api/users/proposals                 # Create proposal
GET  /api/users/proposals/{proposal_id}   # Get proposal details
POST /api/users/proposals/{id}/start-sms-voting # Start SMS voting
POST /api/users/webhooks/sms              # Handle Twilio SMS webhook
```

#### Statistics & Analytics
```
GET  /api/users/stats/phone-verification  # Phone verification stats
GET  /api/users/stats/kyc                 # KYC statistics
GET  /api/users/stats/sms                 # SMS interaction stats
GET  /api/users/stats/proposals           # Proposal statistics
```

**Total: 33 API endpoints**

## 🔄 **User Journey**

### 1. Group Registration
```
Community Leader → Web Registration → Group Creation → Treasury Setup → Member Invitation
```

### 2. Member Onboarding
```
Registration → Phone Verification (OTP) → KYC Submission → Document Review → Active Member
```

### 3. SMS Voting Flow
```
Proposal Creation → SMS Broadcast → Vote via SMS (YES001/NO001) → Real-time Tallying → Results
```

## ⚙️ **Configuration**

### Environment Setup

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -e .[dev]
```

3. **Configure environment variables**

```bash
# Application Settings
APP_ENV=dev
LOG_LEVEL=INFO

# Blockchain & Oracle Settings
IPFS_API_URL=http://localhost:5001
ORACLE_SIGNER=0x0000000000000000000000000000000000000000
CELESTIA_ENDPOINT=http://localhost:26658

# AI Settings (Groq OpenAI-compatible)
GROQ_API_KEY=your_groq_api_key_here
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions

# Twilio SMS Settings
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Security Settings
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
OTP_RATE_LIMIT_PER_HOUR=5
```

---

## Run the API

From repo root:

```bash
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

Check it’s alive:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/ping
```

Smoke everything:

```bash
# Using curl
curl -s http://127.0.0.1:8000/api/testall | jq

# Using demo script
python backend/api_demo.py --base-url http://127.0.0.1:8000
```

---

## 🧪 **Testing**

### Run Tests
```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_user_management.py -v

# Run with coverage
pytest --cov=app --cov-report term-missing --cov-report html

# Coverage HTML report in htmlcov/index.html
```

### Test Coverage
- **100% coverage requirement** enforced
- **Integration tests** for all API endpoints
- **Unit tests** for services and utilities
- **SMS webhook testing** with mock Twilio data
- **KYC workflow testing** with document verification

## 🔐 **Security Features**

### Phone Verification Security
- **Rate limiting**: 5 OTPs per hour, 1 per minute
- **OTP expiry**: 10 minutes with 3 attempt limit
- **E.164 validation**: International phone number format
- **Secure generation**: Cryptographically secure OTP codes

### KYC Security
- **Document encryption** before IPFS storage
- **Multi-level verification** with audit trails
- **Privacy preservation**: PII never on public chain
- **Compliance tracking** with review history

### SMS Security
- **Member validation** against verified phone numbers
- **Duplicate prevention**: One vote per member per proposal
- **Format validation**: Strict YES001/NO001 parsing
- **Rate limiting** on all SMS endpoints

## 🚀 **Deployment**

### Production Considerations
- **Database**: Replace in-memory storage with PostgreSQL
- **Caching**: Add Redis for OTP and session storage
- **Authentication**: Implement JWT token system
- **Monitoring**: Set up application metrics and alerting
- **Security**: Enable HTTPS, security headers, and audit logging

### Environment Setup
```bash
# Production environment variables
APP_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/harambee_dao
REDIS_URL=redis://localhost:6379
```

## 📈 **Roadmap**

### ✅ **Phase 1: Core Infrastructure (Complete)**
- User management system with group and member registration
- Phone verification with SMS OTP
- KYC document processing and verification
- SMS integration with Twilio webhooks
- Proposal management and voting system

### 🔄 **Phase 2: Production Hardening (In Progress)**
- Database migration from in-memory to PostgreSQL
- JWT authentication and authorization
- API rate limiting and security middleware
- Comprehensive monitoring and alerting
- Performance optimization and caching

### 🎯 **Phase 3: Advanced Features (Planned)**
- AI audit pipeline integration
- Gnosis Safe treasury management
- Oracle attestation verification
- IPFS and Celestia evidence anchoring
- Advanced fraud detection

### 🚀 **Phase 4: Scale & Deploy (Future)**
- Multi-language SMS support
- Mobile app integration
- Advanced analytics dashboard
- Multi-region deployment
- Enterprise features

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Maintain 100% test coverage
- Update documentation for API changes
- Use conventional commit messages

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: [User Management Guide](USER_MANAGEMENT_README.md)
- **API Reference**: Available at `/docs` when running the server
- **Issues**: [GitHub Issues](https://github.com/Harambee-Dao/Harambee-Dao-Backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Harambee-Dao/Harambee-Dao-Backend/discussions)

## 🙏 **Acknowledgments**

- **FastAPI** for the excellent web framework
- **Pydantic** for data validation and settings management
- **Twilio** for reliable SMS infrastructure
- **Gnosis Safe** for secure multi-signature treasury management
- **IPFS** for decentralized storage solutions

---

**Built with ❤️ for community empowerment and financial inclusion**
