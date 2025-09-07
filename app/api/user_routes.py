from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.schemas import (
    GroupIn, GroupOut, MemberIn, MemberOut, MemberUpdateIn, MemberListOut,
    OTPRequestIn, OTPRequestOut, OTPVerificationIn, OTPVerificationOut,
    KYCDocumentIn, KYCDocumentOut, KYCReviewIn, KYCReviewOut,
    TwilioWebhookIn, SMSVoteOut, GroupMembershipOut,
    ProposalIn, ProposalOut
)
from app.services.user_service import (
    create_group, register_member, get_member_by_id, get_member_by_phone,
    update_member, get_group_members, get_group_by_id, get_all_groups,
    update_group_treasury, get_member_group_info
)
from app.services.phone_verification_service import (
    request_otp, verify_otp, get_otp_status, get_verification_statistics
)
from app.services.kyc_service import (
    submit_kyc_document, get_member_documents, review_kyc_documents,
    get_kyc_review_history, get_pending_kyc_reviews, verify_document,
    get_kyc_statistics
)
from app.services.sms_service import (
    process_sms_webhook, get_sms_statistics, get_proposal_voting_status
)
from app.services.proposal_service import (
    create_proposal, get_proposal_by_id, get_group_proposals,
    start_sms_voting, get_active_proposals, get_proposals_by_status,
    get_proposal_statistics, get_member_voting_history
)

router = APIRouter()


# Group Management Endpoints
@router.post("/groups", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_new_group(group_data: GroupIn):
    """Create a new community group and register the leader."""
    try:
        return create_group(group_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create group")


@router.get("/groups", response_model=List[GroupOut])
def list_groups():
    """Get all groups."""
    return get_all_groups()


@router.get("/groups/{group_id}", response_model=GroupOut)
def get_group(group_id: str):
    """Get group by ID."""
    group = get_group_by_id(group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


@router.get("/groups/{group_id}/members", response_model=MemberListOut)
def list_group_members(group_id: str):
    """Get all members of a group."""
    try:
        return get_group_members(group_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/groups/{group_id}/treasury")
def update_treasury_address(group_id: str, treasury_address: str):
    """Update group treasury address after Safe deployment."""
    group = update_group_treasury(group_id, treasury_address)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return {"message": "Treasury address updated", "group": group}


# Member Management Endpoints
@router.post("/members", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def register_new_member(member_data: MemberIn):
    """Register a new member to a group."""
    try:
        return register_member(member_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register member")


@router.get("/members/{member_id}", response_model=MemberOut)
def get_member(member_id: str):
    """Get member by ID."""
    member = get_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@router.get("/members/phone/{phone_number}", response_model=MemberOut)
def get_member_by_phone_number(phone_number: str):
    """Get member by phone number."""
    member = get_member_by_phone(phone_number)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@router.patch("/members/{member_id}", response_model=MemberOut)
def update_member_info(member_id: str, update_data: MemberUpdateIn):
    """Update member information."""
    member = update_member(member_id, update_data)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@router.get("/members/{member_id}/group", response_model=GroupMembershipOut)
def get_member_group(member_id: str):
    """Get member's group membership information."""
    membership = get_member_group_info(member_id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member or group not found")
    return membership


# Phone Verification Endpoints
@router.post("/phone/request-otp", response_model=OTPRequestOut)
def request_phone_otp(request_data: OTPRequestIn):
    """Request OTP for phone verification."""
    return request_otp(request_data)


@router.post("/phone/verify-otp", response_model=OTPVerificationOut)
def verify_phone_otp(verification_data: OTPVerificationIn):
    """Verify OTP code."""
    return verify_otp(verification_data)


@router.get("/phone/{phone_number}/otp-status")
def get_phone_otp_status(phone_number: str):
    """Get current OTP status for a phone number."""
    status_info = get_otp_status(phone_number)
    if not status_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active OTP found")
    return status_info


# KYC Endpoints
@router.post("/kyc/documents", response_model=KYCDocumentOut, status_code=status.HTTP_201_CREATED)
def submit_kyc_doc(document_data: KYCDocumentIn):
    """Submit a KYC document for verification."""
    try:
        return submit_kyc_document(document_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/kyc/members/{member_id}/documents", response_model=List[KYCDocumentOut])
def get_member_kyc_documents(member_id: str):
    """Get all KYC documents for a member."""
    return get_member_documents(member_id)


@router.post("/kyc/review", response_model=KYCReviewOut)
def review_member_kyc(review_data: KYCReviewIn):
    """Review and update KYC status for a member."""
    try:
        return review_kyc_documents(review_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/kyc/members/{member_id}/reviews", response_model=List[KYCReviewOut])
def get_member_kyc_reviews(member_id: str):
    """Get KYC review history for a member."""
    return get_kyc_review_history(member_id)


@router.get("/kyc/pending-reviews")
def get_pending_reviews():
    """Get all members with pending KYC reviews."""
    return get_pending_kyc_reviews()


@router.patch("/kyc/documents/{document_id}/verify")
def verify_kyc_document(document_id: str, verification_status: str, notes: str = None):
    """Verify or reject a specific KYC document."""
    from app.models.schemas import VerificationStatus
    
    try:
        status_enum = VerificationStatus(verification_status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification status")
    
    document = verify_document(document_id, status_enum, notes)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    return {"message": "Document verification updated", "document": document}


# SMS Webhook Endpoint
@router.post("/webhooks/sms", response_model=SMSVoteOut)
def handle_sms_webhook(webhook_data: TwilioWebhookIn):
    """Handle incoming SMS webhook from Twilio."""
    return process_sms_webhook(webhook_data)


# Statistics Endpoints
@router.get("/stats/phone-verification")
def get_phone_verification_stats():
    """Get phone verification statistics."""
    return get_verification_statistics()


@router.get("/stats/kyc")
def get_kyc_stats():
    """Get KYC statistics."""
    return get_kyc_statistics()


@router.get("/stats/sms")
def get_sms_stats():
    """Get SMS interaction statistics."""
    return get_sms_statistics()


# Proposal Management Endpoints
@router.post("/proposals", response_model=ProposalOut, status_code=status.HTTP_201_CREATED)
def create_new_proposal(proposal_data: ProposalIn):
    """Create a new proposal for group voting."""
    try:
        return create_proposal(proposal_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/proposals/{proposal_id}", response_model=ProposalOut)
def get_proposal(proposal_id: str):
    """Get proposal by ID."""
    proposal = get_proposal_by_id(proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return proposal


@router.get("/groups/{group_id}/proposals", response_model=List[ProposalOut])
def list_group_proposals(group_id: str):
    """Get all proposals for a group."""
    return get_group_proposals(group_id)


@router.get("/proposals", response_model=List[ProposalOut])
def list_active_proposals():
    """Get all active proposals."""
    return get_active_proposals()


@router.get("/proposals/status/{status}", response_model=List[ProposalOut])
def list_proposals_by_status(status: str):
    """Get proposals by status."""
    return get_proposals_by_status(status)


@router.post("/proposals/{proposal_id}/start-sms-voting")
def start_proposal_sms_voting(proposal_id: str):
    """Start SMS voting for a proposal."""
    try:
        return start_sms_voting(proposal_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/proposals/{proposal_id}/sms-status")
def get_proposal_sms_status(proposal_id: str):
    """Get SMS voting status for a proposal."""
    status_info = get_proposal_voting_status(proposal_id)
    if not status_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found or not configured for SMS voting")
    return status_info


@router.get("/members/{member_id}/voting-history")
def get_member_votes(member_id: str):
    """Get voting history for a member."""
    return get_member_voting_history(member_id)


# Additional Statistics Endpoints
@router.get("/stats/proposals")
def get_proposal_stats():
    """Get proposal statistics."""
    return get_proposal_statistics()
