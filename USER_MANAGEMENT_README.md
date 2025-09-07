# Harambee DAO User Management System

## Overview

This document describes the comprehensive user management system implemented for Harambee DAO, including user registration, KYC validation, phone verification, and SMS-based governance.

## Features Implemented

### 🏛️ **Group Management**
- Community group registration
- Multi-signature treasury setup
- Member roster management
- Group statistics and analytics

### 👥 **Member Management**
- Phone-based member registration
- Role-based access (Member, Leader, Treasurer)
- Member verification status tracking
- Group membership management

### 📱 **Phone Verification**
- SMS-based OTP verification
- Rate limiting and security controls
- Support for multiple verification types
- Automatic verification status updates

### 🔐 **KYC (Know Your Customer)**
- Document submission and verification
- Multiple document types support
- Automated and manual review processes
- Compliance tracking and reporting

### 💬 **SMS Integration**
- Twilio-based SMS sending
- SMS webhook handling for votes
- Proposal broadcasting via SMS
- Vote parsing and validation

### 🗳️ **Proposal Management**
- Proposal creation and management
- SMS voting integration
- Real-time vote tallying
- Deadline management

## API Endpoints

### Group Management
```
POST   /api/users/groups                    # Create new group
GET    /api/users/groups                    # List all groups
GET    /api/users/groups/{group_id}         # Get group details
GET    /api/users/groups/{group_id}/members # List group members
PATCH  /api/users/groups/{group_id}/treasury # Update treasury address
```

### Member Management
```
POST   /api/users/members                   # Register new member
GET    /api/users/members/{member_id}       # Get member details
GET    /api/users/members/phone/{phone}     # Get member by phone
PATCH  /api/users/members/{member_id}       # Update member info
GET    /api/users/members/{member_id}/group # Get member's group info
```

### Phone Verification
```
POST   /api/users/phone/request-otp         # Request OTP
POST   /api/users/phone/verify-otp          # Verify OTP
GET    /api/users/phone/{phone}/otp-status  # Get OTP status
```

### KYC Management
```
POST   /api/users/kyc/documents             # Submit KYC document
GET    /api/users/kyc/members/{id}/documents # Get member documents
POST   /api/users/kyc/review                # Review KYC status
GET    /api/users/kyc/members/{id}/reviews  # Get review history
GET    /api/users/kyc/pending-reviews       # Get pending reviews
PATCH  /api/users/kyc/documents/{id}/verify # Verify document
```

### Proposal Management
```
POST   /api/users/proposals                 # Create proposal
GET    /api/users/proposals/{proposal_id}   # Get proposal details
GET    /api/users/groups/{group_id}/proposals # List group proposals
GET    /api/users/proposals                 # List active proposals
POST   /api/users/proposals/{id}/start-sms-voting # Start SMS voting
GET    /api/users/proposals/{id}/sms-status # Get SMS voting status
```

### SMS Webhooks
```
POST   /api/users/webhooks/sms              # Handle Twilio SMS webhook
```

### Statistics
```
GET    /api/users/stats/phone-verification  # Phone verification stats
GET    /api/users/stats/kyc                 # KYC statistics
GET    /api/users/stats/sms                 # SMS interaction stats
GET    /api/users/stats/proposals           # Proposal statistics
```

## Data Models

### Group Schema
```python
class GroupIn(BaseModel):
    group_name: str
    description: Optional[str]
    location: str
    leader_phone: str
    leader_name: str
    expected_member_count: int
    treasury_threshold: int
```

### Member Schema
```python
class MemberIn(BaseModel):
    phone_number: str  # E.164 format
    full_name: str
    group_id: str
    location: Optional[str]
    role: MemberRole  # MEMBER, LEADER, TREASURER
```

### KYC Document Schema
```python
class KYCDocumentIn(BaseModel):
    member_id: str
    document_type: KYCDocumentType
    document_number: str
    document_image_cid: Optional[str]  # IPFS CID
    issuing_authority: Optional[str]
    expiry_date: Optional[datetime]
```

## User Journey

### 1. Group Registration
```
1. Community leader visits registration portal
2. Fills group information and leader details
3. System creates group and registers leader as first member
4. Leader receives SMS confirmation
5. Group treasury (Safe) can be deployed
```

### 2. Member Onboarding
```
1. Leader invites members via phone numbers
2. Member receives SMS invitation
3. Member registers via web portal or SMS
4. System sends OTP for phone verification
5. Member verifies phone number
6. Member submits KYC documents
7. Documents reviewed and approved
8. Member becomes active and can vote
```

### 3. SMS Voting Flow
```
1. Proposal created and SMS voting enabled
2. System broadcasts proposal SMS to all verified members
3. Members reply with YES### or NO### format
4. System validates vote and records it
5. Real-time tally updated
6. Confirmation SMS sent to voter
7. Results available when voting closes
```

## Security Features

### Phone Verification
- OTP rate limiting (max 5 per hour)
- OTP expiry (10 minutes)
- Maximum attempt limits (3 attempts)
- E.164 phone number validation

### KYC Security
- Document encryption before IPFS storage
- Multi-level verification process
- Audit trail for all KYC actions
- Privacy-preserving data handling

### SMS Security
- Twilio webhook signature verification
- Member phone number validation
- Duplicate vote prevention
- Rate limiting on SMS endpoints

## Configuration

### Environment Variables
```bash
# Twilio SMS Settings
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Security Settings
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
OTP_RATE_LIMIT_PER_HOUR=5
```

## Testing

### Run Tests
```bash
# Run all user management tests
pytest backend/tests/test_user_management.py -v

# Run specific test class
pytest backend/tests/test_user_management.py::TestGroupManagement -v

# Run with coverage
pytest backend/tests/test_user_management.py --cov=app.services --cov-report=html
```

### Test Coverage
- Group creation and management
- Member registration and verification
- Phone OTP verification flow
- KYC document submission and review
- SMS webhook processing
- Statistics and analytics

## Production Considerations

### Database Migration
- Replace in-memory storage with PostgreSQL
- Implement proper database migrations
- Add database indexing for performance

### Security Hardening
- Implement JWT authentication
- Add API rate limiting middleware
- Enable HTTPS and security headers
- Implement audit logging

### Scalability
- Add Redis for OTP storage
- Implement background job processing
- Add database connection pooling
- Implement caching strategies

### Monitoring
- Add application metrics
- Implement health checks
- Set up error tracking
- Monitor SMS delivery rates

## Integration Points

### Blockchain Integration
- Safe treasury deployment
- Oracle attestation verification
- On-chain vote anchoring
- Smart contract interactions

### External Services
- Twilio for SMS delivery
- IPFS for document storage
- Celestia for data availability
- AI services for document verification

## Future Enhancements

### Planned Features
- Biometric verification support
- Multi-language SMS support
- Advanced fraud detection
- Integration with local ID systems
- Mobile app for member management

### Roadmap
- Phase 1: Core functionality (✅ Complete)
- Phase 2: Production hardening
- Phase 3: Advanced features
- Phase 4: Scale and optimization

## Support

For technical support or questions about the user management system:
- Review the API documentation
- Check the test files for usage examples
- Refer to the main project README
- Contact the development team
