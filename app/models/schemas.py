from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import re


class AuditDecision(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class AuditResultIn(BaseModel):
    proposalId: str
    decision: AuditDecision
    confidence: float = Field(ge=0.0, le=1.0)
    evidenceCID: str
    modelVersion: str
    attestationSignature: str


class AuditResultOut(BaseModel):
    proposalId: str
    decision: AuditDecision
    confidence: float
    evidenceCID: str
    modelVersion: str
    attestationValid: bool


class VoteIn(BaseModel):
    memberId: str
    proposalId: str
    vote: bool


class VoteOut(BaseModel):
    memberId: str
    proposalId: str
    vote: bool
    tally: dict


# User Management Schemas
class KYCStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class MemberRole(str, Enum):
    MEMBER = "MEMBER"
    LEADER = "LEADER"
    TREASURER = "TREASURER"


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class GroupIn(BaseModel):
    group_name: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(max_length=500)
    location: str = Field(min_length=2, max_length=100)
    leader_phone: str = Field(regex=r'^\+[1-9]\d{8,14}$')
    leader_name: str = Field(min_length=2, max_length=100)
    expected_member_count: int = Field(ge=5, le=1000)
    treasury_threshold: int = Field(ge=2, le=10)  # Multi-sig threshold


class GroupOut(BaseModel):
    group_id: str
    group_name: str
    description: Optional[str]
    location: str
    leader_id: str
    member_count: int
    treasury_address: Optional[str]
    treasury_threshold: int
    created_at: datetime
    kyc_status: KYCStatus


class MemberIn(BaseModel):
    phone_number: str = Field(regex=r'^\+[1-9]\d{8,14}$')
    full_name: str = Field(min_length=2, max_length=100)
    group_id: str
    location: Optional[str] = Field(max_length=100)
    role: MemberRole = MemberRole.MEMBER

    @validator('full_name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', v):
            raise ValueError('Name can only contain letters, spaces, hyphens, apostrophes, and periods')
        return v.strip()


class MemberOut(BaseModel):
    member_id: str
    phone_number: str
    full_name: str
    group_id: str
    location: Optional[str]
    role: MemberRole
    phone_verified: bool
    kyc_status: KYCStatus
    created_at: datetime
    last_active: Optional[datetime]


class OTPVerificationIn(BaseModel):
    phone_number: str = Field(regex=r'^\+[1-9]\d{8,14}$')
    otp_code: str = Field(min_length=4, max_length=8)
    verification_type: str = Field(regex=r'^(registration|voting|password_reset)$')


class OTPVerificationOut(BaseModel):
    phone_number: str
    verified: bool
    verification_type: str
    expires_at: Optional[datetime]


class OTPRequestIn(BaseModel):
    phone_number: str = Field(regex=r'^\+[1-9]\d{8,14}$')
    verification_type: str = Field(regex=r'^(registration|voting|password_reset)$')


class OTPRequestOut(BaseModel):
    phone_number: str
    otp_sent: bool
    expires_at: datetime
    message: str


# SMS Webhook Schemas
class TwilioWebhookIn(BaseModel):
    From: str = Field(alias="From")  # Phone number
    To: str = Field(alias="To")      # Twilio number
    Body: str = Field(alias="Body")  # SMS content
    MessageSid: str = Field(alias="MessageSid")
    AccountSid: Optional[str] = Field(alias="AccountSid", default=None)

    class Config:
        allow_population_by_field_name = True


class SMSVoteIn(BaseModel):
    phone_number: str
    message_body: str
    message_sid: str


class SMSVoteOut(BaseModel):
    phone_number: str
    member_id: Optional[str]
    proposal_id: Optional[str]
    vote: Optional[bool]
    processed: bool
    error_message: Optional[str]
    response_message: str


# KYC Schemas
class KYCDocumentType(str, Enum):
    NATIONAL_ID = "NATIONAL_ID"
    PASSPORT = "PASSPORT"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    VOTER_ID = "VOTER_ID"
    COMMUNITY_ATTESTATION = "COMMUNITY_ATTESTATION"


class KYCDocumentIn(BaseModel):
    member_id: str
    document_type: KYCDocumentType
    document_number: str = Field(min_length=3, max_length=50)
    document_image_cid: Optional[str]  # IPFS CID
    issuing_authority: Optional[str] = Field(max_length=100)
    expiry_date: Optional[datetime]


class KYCDocumentOut(BaseModel):
    document_id: str
    member_id: str
    document_type: KYCDocumentType
    document_number: str
    document_image_cid: Optional[str]
    issuing_authority: Optional[str]
    expiry_date: Optional[datetime]
    verification_status: VerificationStatus
    created_at: datetime
    verified_at: Optional[datetime]


class KYCReviewIn(BaseModel):
    member_id: str
    status: KYCStatus
    reviewer_notes: Optional[str] = Field(max_length=500)
    required_documents: Optional[List[KYCDocumentType]]


class KYCReviewOut(BaseModel):
    member_id: str
    previous_status: KYCStatus
    new_status: KYCStatus
    reviewer_notes: Optional[str]
    reviewed_at: datetime
    required_documents: Optional[List[KYCDocumentType]]


# Proposal Schemas
class ProposalIn(BaseModel):
    group_id: str
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10, max_length=1000)
    amount_requested: float = Field(gt=0)
    milestone_description: str = Field(min_length=10, max_length=500)
    deadline: datetime
    created_by: str  # member_id


class ProposalOut(BaseModel):
    proposal_id: str
    group_id: str
    title: str
    description: str
    amount_requested: float
    milestone_description: str
    deadline: datetime
    created_by: str
    created_at: datetime
    voting_deadline: datetime
    status: str  # DRAFT, VOTING, PASSED, FAILED, EXECUTED
    vote_count: dict  # {"yes": 0, "no": 0, "total": 0}


# Member Management Schemas
class MemberUpdateIn(BaseModel):
    full_name: Optional[str] = Field(min_length=2, max_length=100)
    location: Optional[str] = Field(max_length=100)
    role: Optional[MemberRole]


class MemberListOut(BaseModel):
    members: List[MemberOut]
    total_count: int
    verified_count: int
    pending_kyc_count: int


class GroupMembershipOut(BaseModel):
    group: GroupOut
    member: MemberOut
    joined_at: datetime
    is_active: bool
