import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.models.schemas import ProposalIn, ProposalOut
from app.services.user_service import get_group_by_id, get_group_members
from app.services.sms_service import register_proposal_for_sms_voting, broadcast_proposal_sms

logger = logging.getLogger(__name__)

# In-memory storage for demo/development (replace with database in production)
_PROPOSALS: Dict[str, dict] = {}
_GROUP_PROPOSALS: Dict[str, List[str]] = {}  # group_id -> [proposal_ids]


def create_proposal(proposal_data: ProposalIn) -> ProposalOut:
    """Create a new proposal for group voting."""
    logger.info("Creating proposal for group %s: %s", proposal_data.group_id, proposal_data.title)
    
    # Validate group exists
    group = get_group_by_id(proposal_data.group_id)
    if not group:
        raise ValueError(f"Group {proposal_data.group_id} does not exist")
    
    # Generate proposal ID
    proposal_id = str(uuid.uuid4())
    
    # Calculate voting deadline (default 7 days from now if not specified)
    voting_deadline = proposal_data.deadline if proposal_data.deadline > datetime.utcnow() else datetime.utcnow() + timedelta(days=7)
    
    # Create proposal record
    proposal_record = {
        "proposal_id": proposal_id,
        "group_id": proposal_data.group_id,
        "title": proposal_data.title,
        "description": proposal_data.description,
        "amount_requested": proposal_data.amount_requested,
        "milestone_description": proposal_data.milestone_description,
        "deadline": proposal_data.deadline,
        "created_by": proposal_data.created_by,
        "created_at": datetime.utcnow(),
        "voting_deadline": voting_deadline,
        "status": "VOTING",  # DRAFT, VOTING, PASSED, FAILED, EXECUTED
        "vote_count": {"yes": 0, "no": 0, "total": 0}
    }
    
    # Store proposal
    _PROPOSALS[proposal_id] = proposal_record
    
    # Add to group proposals
    if proposal_data.group_id not in _GROUP_PROPOSALS:
        _GROUP_PROPOSALS[proposal_data.group_id] = []
    _GROUP_PROPOSALS[proposal_data.group_id].append(proposal_id)
    
    logger.info("Created proposal %s", proposal_id)
    
    return ProposalOut(**proposal_record)


def get_proposal_by_id(proposal_id: str) -> Optional[ProposalOut]:
    """Get proposal by ID."""
    proposal_record = _PROPOSALS.get(proposal_id)
    if proposal_record:
        return ProposalOut(**proposal_record)
    return None


def get_group_proposals(group_id: str) -> List[ProposalOut]:
    """Get all proposals for a group."""
    proposal_ids = _GROUP_PROPOSALS.get(group_id, [])
    proposals = []
    
    for proposal_id in proposal_ids:
        if proposal_id in _PROPOSALS:
            proposals.append(ProposalOut(**_PROPOSALS[proposal_id]))
    
    # Sort by creation date (newest first)
    proposals.sort(key=lambda p: p.created_at, reverse=True)
    
    return proposals


def update_proposal_status(proposal_id: str, status: str) -> Optional[ProposalOut]:
    """Update proposal status."""
    if proposal_id not in _PROPOSALS:
        return None
    
    _PROPOSALS[proposal_id]["status"] = status
    logger.info("Updated proposal %s status to %s", proposal_id, status)
    
    return ProposalOut(**_PROPOSALS[proposal_id])


def update_proposal_vote_count(proposal_id: str, vote_count: dict) -> Optional[ProposalOut]:
    """Update proposal vote count."""
    if proposal_id not in _PROPOSALS:
        return None
    
    _PROPOSALS[proposal_id]["vote_count"] = vote_count
    
    # Auto-update status based on vote count and deadline
    proposal = _PROPOSALS[proposal_id]
    if datetime.utcnow() > proposal["voting_deadline"]:
        total_votes = vote_count.get("total", 0)
        yes_votes = vote_count.get("yes", 0)
        
        # Simple majority rule (can be customized per group)
        if total_votes > 0 and yes_votes > total_votes / 2:
            proposal["status"] = "PASSED"
        else:
            proposal["status"] = "FAILED"
        
        logger.info("Auto-updated proposal %s status to %s based on votes", proposal_id, proposal["status"])
    
    return ProposalOut(**_PROPOSALS[proposal_id])


def start_sms_voting(proposal_id: str) -> dict:
    """Start SMS voting for a proposal."""
    proposal = get_proposal_by_id(proposal_id)
    if not proposal:
        raise ValueError(f"Proposal {proposal_id} not found")
    
    # Register proposal for SMS voting
    short_code = register_proposal_for_sms_voting(
        proposal_id=proposal_id,
        proposal_title=proposal.title,
        group_id=proposal.group_id,
        voting_deadline=proposal.voting_deadline
    )
    
    # Get group members
    members_list = get_group_members(proposal.group_id)
    verified_members = [m for m in members_list.members if m.phone_verified]
    
    if not verified_members:
        raise ValueError("No verified members found in group")
    
    # Extract phone numbers
    phone_numbers = [member.phone_number for member in verified_members]
    
    # Broadcast SMS
    broadcast_result = broadcast_proposal_sms(proposal_id, phone_numbers)
    
    logger.info("Started SMS voting for proposal %s with code %s", proposal_id, short_code)
    
    return {
        "proposal_id": proposal_id,
        "short_code": short_code,
        "broadcast_result": broadcast_result,
        "eligible_voters": len(verified_members)
    }


def get_active_proposals() -> List[ProposalOut]:
    """Get all active proposals (status = VOTING)."""
    active_proposals = []
    
    for proposal_record in _PROPOSALS.values():
        if proposal_record["status"] == "VOTING":
            active_proposals.append(ProposalOut(**proposal_record))
    
    # Sort by voting deadline (soonest first)
    active_proposals.sort(key=lambda p: p.voting_deadline)
    
    return active_proposals


def get_proposals_by_status(status: str) -> List[ProposalOut]:
    """Get proposals by status."""
    proposals = []
    
    for proposal_record in _PROPOSALS.values():
        if proposal_record["status"] == status:
            proposals.append(ProposalOut(**proposal_record))
    
    # Sort by creation date (newest first)
    proposals.sort(key=lambda p: p.created_at, reverse=True)
    
    return proposals


def check_voting_deadlines():
    """Check and update proposals that have passed their voting deadline."""
    current_time = datetime.utcnow()
    updated_count = 0
    
    for proposal_id, proposal_record in _PROPOSALS.items():
        if (proposal_record["status"] == "VOTING" and 
            current_time > proposal_record["voting_deadline"]):
            
            # Get current vote tally
            from app.services.vote_service import get_vote_tally
            vote_tally = get_vote_tally(proposal_id)
            
            # Update vote count and status
            update_proposal_vote_count(proposal_id, vote_tally)
            updated_count += 1
    
    if updated_count > 0:
        logger.info("Updated %d proposals that passed voting deadline", updated_count)
    
    return updated_count


def get_proposal_statistics() -> dict:
    """Get proposal statistics."""
    total_proposals = len(_PROPOSALS)
    status_counts = {}
    
    for proposal_record in _PROPOSALS.values():
        status = proposal_record["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total_proposals": total_proposals,
        "status_breakdown": status_counts,
        "active_voting": status_counts.get("VOTING", 0),
        "passed_proposals": status_counts.get("PASSED", 0),
        "failed_proposals": status_counts.get("FAILED", 0)
    }


def delete_proposal(proposal_id: str) -> bool:
    """Delete a proposal (admin only)."""
    if proposal_id not in _PROPOSALS:
        return False
    
    proposal = _PROPOSALS[proposal_id]
    group_id = proposal["group_id"]
    
    # Remove from proposals
    del _PROPOSALS[proposal_id]
    
    # Remove from group proposals
    if group_id in _GROUP_PROPOSALS:
        _GROUP_PROPOSALS[group_id] = [pid for pid in _GROUP_PROPOSALS[group_id] if pid != proposal_id]
    
    logger.info("Deleted proposal %s", proposal_id)
    return True


def get_member_voting_history(member_id: str) -> List[dict]:
    """Get voting history for a member."""
    from app.services.vote_service import _VOTES
    
    voting_history = []
    
    for proposal_id, votes in _VOTES.items():
        if member_id in votes:
            proposal = get_proposal_by_id(proposal_id)
            if proposal:
                voting_history.append({
                    "proposal": proposal,
                    "vote": votes[member_id],
                    "voted_at": proposal.created_at  # In production, store actual vote timestamp
                })
    
    # Sort by vote date (newest first)
    voting_history.sort(key=lambda v: v["voted_at"], reverse=True)
    
    return voting_history
