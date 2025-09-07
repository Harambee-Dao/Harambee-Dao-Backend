import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.models.schemas import (
    KYCDocumentIn, KYCDocumentOut, KYCReviewIn, KYCReviewOut,
    KYCStatus, KYCDocumentType, VerificationStatus
)
from app.services.user_service import get_member_by_id, update_member_verification_status
from app.utils.ipfs import pin_cid

logger = logging.getLogger(__name__)

# In-memory storage for demo/development (replace with database in production)
_KYC_DOCUMENTS: Dict[str, dict] = {}
_MEMBER_DOCUMENTS: Dict[str, List[str]] = {}  # member_id -> [document_ids]
_KYC_REVIEWS: Dict[str, List[dict]] = {}  # member_id -> [review_records]


def submit_kyc_document(document_data: KYCDocumentIn) -> KYCDocumentOut:
    """Submit a KYC document for verification."""
    logger.info("Submitting KYC document for member %s", document_data.member_id)
    
    # Validate member exists
    member = get_member_by_id(document_data.member_id)
    if not member:
        raise ValueError(f"Member {document_data.member_id} does not exist")
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    # Pin document image to IPFS if provided
    if document_data.document_image_cid:
        try:
            pin_cid(document_data.document_image_cid)
            logger.info("Pinned document image CID: %s", document_data.document_image_cid)
        except Exception as e:
            logger.warning("Failed to pin document image: %s", e)
    
    # Create document record
    document_record = {
        "document_id": document_id,
        "member_id": document_data.member_id,
        "document_type": document_data.document_type,
        "document_number": document_data.document_number,
        "document_image_cid": document_data.document_image_cid,
        "issuing_authority": document_data.issuing_authority,
        "expiry_date": document_data.expiry_date,
        "verification_status": VerificationStatus.PENDING,
        "created_at": datetime.utcnow(),
        "verified_at": None
    }
    
    # Store document
    _KYC_DOCUMENTS[document_id] = document_record
    
    # Add to member's documents
    if document_data.member_id not in _MEMBER_DOCUMENTS:
        _MEMBER_DOCUMENTS[document_data.member_id] = []
    _MEMBER_DOCUMENTS[document_data.member_id].append(document_id)
    
    # Auto-approve community attestations for now (in production, require manual review)
    if document_data.document_type == KYCDocumentType.COMMUNITY_ATTESTATION:
        document_record["verification_status"] = VerificationStatus.VERIFIED
        document_record["verified_at"] = datetime.utcnow()
        logger.info("Auto-approved community attestation for member %s", document_data.member_id)
    
    logger.info("Submitted KYC document %s for member %s", document_id, document_data.member_id)
    
    return KYCDocumentOut(**document_record)


def get_member_documents(member_id: str) -> List[KYCDocumentOut]:
    """Get all KYC documents for a member."""
    document_ids = _MEMBER_DOCUMENTS.get(member_id, [])
    documents = []
    
    for document_id in document_ids:
        if document_id in _KYC_DOCUMENTS:
            documents.append(KYCDocumentOut(**_KYC_DOCUMENTS[document_id]))
    
    return documents


def review_kyc_documents(review_data: KYCReviewIn) -> KYCReviewOut:
    """Review and update KYC status for a member."""
    logger.info("Reviewing KYC for member %s", review_data.member_id)
    
    # Validate member exists
    member = get_member_by_id(review_data.member_id)
    if not member:
        raise ValueError(f"Member {review_data.member_id} does not exist")
    
    previous_status = member.kyc_status
    
    # Create review record
    review_record = {
        "member_id": review_data.member_id,
        "previous_status": previous_status,
        "new_status": review_data.status,
        "reviewer_notes": review_data.reviewer_notes,
        "reviewed_at": datetime.utcnow(),
        "required_documents": review_data.required_documents
    }
    
    # Store review
    if review_data.member_id not in _KYC_REVIEWS:
        _KYC_REVIEWS[review_data.member_id] = []
    _KYC_REVIEWS[review_data.member_id].append(review_record)
    
    # Update member KYC status
    update_member_verification_status(review_data.member_id, kyc_status=review_data.status)
    
    logger.info("Updated KYC status for member %s: %s -> %s", 
                review_data.member_id, previous_status, review_data.status)
    
    return KYCReviewOut(**review_record)


def get_kyc_review_history(member_id: str) -> List[KYCReviewOut]:
    """Get KYC review history for a member."""
    reviews = _KYC_REVIEWS.get(member_id, [])
    return [KYCReviewOut(**review) for review in reviews]


def auto_verify_basic_kyc(member_id: str) -> bool:
    """Automatically verify basic KYC if conditions are met."""
    logger.info("Attempting auto-verification for member %s", member_id)
    
    member = get_member_by_id(member_id)
    if not member:
        return False
    
    # Check if member has phone verified
    if not member.phone_verified:
        logger.info("Member %s phone not verified, cannot auto-verify KYC", member_id)
        return False
    
    # Get member documents
    documents = get_member_documents(member_id)
    
    # Check for valid documents
    has_valid_id = False
    has_community_attestation = False
    
    for doc in documents:
        if doc.verification_status == VerificationStatus.VERIFIED:
            if doc.document_type in [KYCDocumentType.NATIONAL_ID, KYCDocumentType.PASSPORT, 
                                   KYCDocumentType.DRIVERS_LICENSE, KYCDocumentType.VOTER_ID]:
                has_valid_id = True
            elif doc.document_type == KYCDocumentType.COMMUNITY_ATTESTATION:
                has_community_attestation = True
    
    # Auto-approve if has community attestation (for pilot phase)
    if has_community_attestation:
        review_data = KYCReviewIn(
            member_id=member_id,
            status=KYCStatus.VERIFIED,
            reviewer_notes="Auto-approved with community attestation"
        )
        review_kyc_documents(review_data)
        logger.info("Auto-verified KYC for member %s with community attestation", member_id)
        return True
    
    # Auto-approve if has valid government ID (in production, require manual review)
    if has_valid_id:
        review_data = KYCReviewIn(
            member_id=member_id,
            status=KYCStatus.VERIFIED,
            reviewer_notes="Auto-approved with valid government ID"
        )
        review_kyc_documents(review_data)
        logger.info("Auto-verified KYC for member %s with government ID", member_id)
        return True
    
    logger.info("Could not auto-verify KYC for member %s", member_id)
    return False


def get_pending_kyc_reviews() -> List[dict]:
    """Get all members with pending KYC reviews."""
    pending_reviews = []
    
    for member_id, documents in _MEMBER_DOCUMENTS.items():
        member = get_member_by_id(member_id)
        if member and member.kyc_status == KYCStatus.PENDING:
            member_documents = get_member_documents(member_id)
            pending_reviews.append({
                "member": member,
                "documents": member_documents,
                "submitted_at": min(doc.created_at for doc in member_documents) if member_documents else member.created_at
            })
    
    # Sort by submission date
    pending_reviews.sort(key=lambda x: x["submitted_at"])
    
    return pending_reviews


def verify_document(document_id: str, verification_status: VerificationStatus, notes: Optional[str] = None) -> Optional[KYCDocumentOut]:
    """Verify or reject a specific KYC document."""
    if document_id not in _KYC_DOCUMENTS:
        return None
    
    document_record = _KYC_DOCUMENTS[document_id]
    document_record["verification_status"] = verification_status
    
    if verification_status == VerificationStatus.VERIFIED:
        document_record["verified_at"] = datetime.utcnow()
    
    logger.info("Updated document %s verification status: %s", document_id, verification_status)
    
    # Try auto-verification after document update
    if verification_status == VerificationStatus.VERIFIED:
        auto_verify_basic_kyc(document_record["member_id"])
    
    return KYCDocumentOut(**document_record)


def get_kyc_statistics() -> dict:
    """Get KYC statistics across all members."""
    total_members = len(_MEMBER_DOCUMENTS)
    verified_count = 0
    pending_count = 0
    rejected_count = 0
    
    for member_id in _MEMBER_DOCUMENTS.keys():
        member = get_member_by_id(member_id)
        if member:
            if member.kyc_status == KYCStatus.VERIFIED:
                verified_count += 1
            elif member.kyc_status == KYCStatus.PENDING:
                pending_count += 1
            elif member.kyc_status == KYCStatus.REJECTED:
                rejected_count += 1
    
    return {
        "total_members": total_members,
        "verified_count": verified_count,
        "pending_count": pending_count,
        "rejected_count": rejected_count,
        "verification_rate": verified_count / total_members if total_members > 0 else 0
    }
