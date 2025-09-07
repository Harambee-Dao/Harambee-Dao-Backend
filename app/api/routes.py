from fastapi import APIRouter

from app.models.schemas import (
    AuditDecision,
    AuditResultIn,
    AuditResultOut,
    VoteIn,
    VoteOut,
)
from app.services.audit_service import process_audit_evidence
from app.services.vote_service import record_vote, get_vote_tally
from app.api.user_routes import router as user_router

router = APIRouter()

# Include user management routes
router.include_router(user_router, prefix="/users", tags=["User Management"])


@router.get("/ping")
def ping():
    return {"message": "pong"}


@router.post("/audit-result", response_model=AuditResultOut)
def audit_result(payload: AuditResultIn):
    """Webhook endpoint for AI/Oracle to post audit result evidence bundle."""
    result = process_audit_evidence(payload)
    return result


@router.post("/vote", response_model=VoteOut)
def vote(payload: VoteIn):
    result = record_vote(payload)
    return result


@router.get("/tally/{proposal_id}")
def tally(proposal_id: str):
    return get_vote_tally(proposal_id)


@router.get("/testall")
def test_all():
    # basic smoke touching main services
    _ = process_audit_evidence(
        AuditResultIn(
            proposalId="prop-123",
            decision=AuditDecision.PASS,
            confidence=0.94,
            evidenceCID="bafy...",
            modelVersion="resnet50-v1.3",
            attestationSignature="0xabc",
        )
    )
    record_vote(VoteIn(memberId="m1", proposalId="prop-123", vote=True))
    record_vote(VoteIn(memberId="m2", proposalId="prop-123", vote=False))
    tally_res = get_vote_tally("prop-123")
    return {"ok": True, "tally": tally_res}
