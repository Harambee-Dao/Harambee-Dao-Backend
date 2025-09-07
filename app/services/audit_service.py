import logging
from app.models.schemas import AuditResultIn, AuditResultOut
from app.utils.ipfs import pin_cid
from app.utils.oracle import verify_attestation

logger = logging.getLogger(__name__)


def process_audit_evidence(payload: AuditResultIn) -> AuditResultOut:
    logger.info("Processing audit evidence for proposal %s", payload.proposalId)

    verified = verify_attestation(payload.attestationSignature)
    if not verified:
        logger.warning("Attestation failed verification")

    pinned = pin_cid(payload.evidenceCID)
    logger.debug("Pinned CID %s => %s", payload.evidenceCID, pinned)

    return AuditResultOut(
        proposalId=payload.proposalId,
        decision=payload.decision,
        confidence=payload.confidence,
        evidenceCID=payload.evidenceCID,
        modelVersion=payload.modelVersion,
        attestationValid=verified,
    )
