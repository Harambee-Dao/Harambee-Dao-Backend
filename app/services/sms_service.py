import logging
import re
from datetime import datetime
from typing import Optional, Dict, List

from app.models.schemas import (
    TwilioWebhookIn, SMSVoteIn, SMSVoteOut, VoteIn
)
from app.services.user_service import get_member_by_phone
from app.services.vote_service import record_vote, get_vote_tally
from app.utils.sms import send_sms

logger = logging.getLogger(__name__)

# In-memory storage for demo/development
_ACTIVE_PROPOSALS: Dict[str, dict] = {}  # proposal_id -> proposal_info
_SMS_LOGS: List[dict] = []  # SMS interaction logs


def register_proposal_for_sms_voting(proposal_id: str, proposal_title: str, group_id: str, voting_deadline: datetime) -> str:
    """Register a proposal for SMS voting and generate a short code."""
    # Generate a short code (3-4 digits)
    short_code = str(len(_ACTIVE_PROPOSALS) + 1).zfill(3)
    
    proposal_info = {
        "proposal_id": proposal_id,
        "short_code": short_code,
        "title": proposal_title,
        "group_id": group_id,
        "voting_deadline": voting_deadline,
        "created_at": datetime.utcnow()
    }
    
    _ACTIVE_PROPOSALS[proposal_id] = proposal_info
    
    logger.info("Registered proposal %s for SMS voting with code %s", proposal_id, short_code)
    return short_code


def broadcast_proposal_sms(proposal_id: str, member_phones: List[str]) -> dict:
    """Broadcast proposal SMS to all group members."""
    if proposal_id not in _ACTIVE_PROPOSALS:
        raise ValueError(f"Proposal {proposal_id} not registered for SMS voting")
    
    proposal = _ACTIVE_PROPOSALS[proposal_id]
    short_code = proposal["short_code"]
    title = proposal["title"]
    deadline = proposal["voting_deadline"]
    
    # Create SMS message
    message = (
        f"🗳️ HARAMBEE DAO VOTE\n"
        f"Proposal: {title}\n"
        f"Vote by {deadline.strftime('%Y-%m-%d %H:%M')}\n"
        f"Reply: YES{short_code} or NO{short_code}\n"
        f"Example: YES{short_code}"
    )
    
    sent_count = 0
    failed_count = 0
    
    for phone in member_phones:
        try:
            if send_sms(phone, message):
                sent_count += 1
                logger.debug("Sent proposal SMS to %s", phone)
            else:
                failed_count += 1
                logger.warning("Failed to send proposal SMS to %s", phone)
        except Exception as e:
            failed_count += 1
            logger.error("Error sending proposal SMS to %s: %s", phone, e)
    
    # Log broadcast
    _SMS_LOGS.append({
        "type": "proposal_broadcast",
        "proposal_id": proposal_id,
        "sent_count": sent_count,
        "failed_count": failed_count,
        "timestamp": datetime.utcnow()
    })
    
    logger.info("Broadcast proposal %s: %d sent, %d failed", proposal_id, sent_count, failed_count)
    
    return {
        "proposal_id": proposal_id,
        "sent_count": sent_count,
        "failed_count": failed_count,
        "total_recipients": len(member_phones)
    }


def process_sms_webhook(webhook_data: TwilioWebhookIn) -> SMSVoteOut:
    """Process incoming SMS webhook from Twilio."""
    logger.info("Processing SMS from %s: %s", webhook_data.From, webhook_data.Body)
    
    sms_vote = SMSVoteIn(
        phone_number=webhook_data.From,
        message_body=webhook_data.Body.strip().upper(),
        message_sid=webhook_data.MessageSid
    )
    
    return process_sms_vote(sms_vote)


def process_sms_vote(sms_data: SMSVoteIn) -> SMSVoteOut:
    """Process an SMS vote message."""
    phone_number = sms_data.phone_number
    message_body = sms_data.message_body.strip().upper()
    
    # Get member by phone
    member = get_member_by_phone(phone_number)
    if not member:
        response_msg = "❌ Phone number not registered. Please register first at harambeedao.com"
        _log_sms_interaction(phone_number, message_body, "unregistered_phone", response_msg)
        return SMSVoteOut(
            phone_number=phone_number,
            member_id=None,
            proposal_id=None,
            vote=None,
            processed=False,
            error_message="Phone number not registered",
            response_message=response_msg
        )
    
    # Check if member is verified
    if not member.phone_verified:
        response_msg = "❌ Phone number not verified. Please complete verification first."
        _log_sms_interaction(phone_number, message_body, "unverified_phone", response_msg)
        return SMSVoteOut(
            phone_number=phone_number,
            member_id=member.member_id,
            proposal_id=None,
            vote=None,
            processed=False,
            error_message="Phone number not verified",
            response_message=response_msg
        )
    
    # Parse vote from message
    vote_result = _parse_vote_message(message_body)
    
    if not vote_result:
        response_msg = "❌ Invalid vote format. Use YES### or NO### (e.g., YES001)"
        _log_sms_interaction(phone_number, message_body, "invalid_format", response_msg)
        return SMSVoteOut(
            phone_number=phone_number,
            member_id=member.member_id,
            proposal_id=None,
            vote=None,
            processed=False,
            error_message="Invalid vote format",
            response_message=response_msg
        )
    
    vote_value, short_code = vote_result
    
    # Find proposal by short code
    proposal_id = _find_proposal_by_short_code(short_code)
    if not proposal_id:
        response_msg = f"❌ Invalid proposal code: {short_code}"
        _log_sms_interaction(phone_number, message_body, "invalid_proposal", response_msg)
        return SMSVoteOut(
            phone_number=phone_number,
            member_id=member.member_id,
            proposal_id=None,
            vote=None,
            processed=False,
            error_message="Invalid proposal code",
            response_message=response_msg
        )
    
    # Check if proposal is still active
    proposal = _ACTIVE_PROPOSALS[proposal_id]
    if datetime.utcnow() > proposal["voting_deadline"]:
        response_msg = f"❌ Voting deadline passed for proposal {short_code}"
        _log_sms_interaction(phone_number, message_body, "deadline_passed", response_msg)
        return SMSVoteOut(
            phone_number=phone_number,
            member_id=member.member_id,
            proposal_id=proposal_id,
            vote=None,
            processed=False,
            error_message="Voting deadline passed",
            response_message=response_msg
        )
    
    # Record the vote
    try:
        vote_in = VoteIn(
            memberId=member.member_id,
            proposalId=proposal_id,
            vote=vote_value
        )
        
        vote_result = record_vote(vote_in)
        
        # Get current tally
        tally = get_vote_tally(proposal_id)
        
        vote_text = "YES" if vote_value else "NO"
        response_msg = (
            f"✅ Vote recorded: {vote_text} for {proposal['title'][:30]}...\n"
            f"Current tally: {tally['yes']} YES, {tally['no']} NO"
        )
        
        _log_sms_interaction(phone_number, message_body, "vote_recorded", response_msg)
        
        # Send confirmation SMS
        try:
            send_sms(phone_number, response_msg)
        except Exception as e:
            logger.warning("Failed to send confirmation SMS to %s: %s", phone_number, e)
        
        return SMSVoteOut(
            phone_number=phone_number,
            member_id=member.member_id,
            proposal_id=proposal_id,
            vote=vote_value,
            processed=True,
            error_message=None,
            response_message=response_msg
        )
    
    except Exception as e:
        error_msg = str(e)
        if "already voted" in error_msg.lower():
            response_msg = f"❌ You already voted on proposal {short_code}"
        else:
            response_msg = "❌ Error recording vote. Please try again."
        
        _log_sms_interaction(phone_number, message_body, "vote_error", response_msg)
        
        return SMSVoteOut(
            phone_number=phone_number,
            member_id=member.member_id,
            proposal_id=proposal_id,
            vote=None,
            processed=False,
            error_message=error_msg,
            response_message=response_msg
        )


def _parse_vote_message(message: str) -> Optional[tuple]:
    """Parse vote message to extract vote and proposal code."""
    # Pattern: YES### or NO### where ### is 3-4 digits
    pattern = r'^(YES|NO)(\d{3,4})$'
    match = re.match(pattern, message)
    
    if match:
        vote_text, code = match.groups()
        vote_value = vote_text == "YES"
        return vote_value, code
    
    return None


def _find_proposal_by_short_code(short_code: str) -> Optional[str]:
    """Find proposal ID by short code."""
    for proposal_id, proposal_info in _ACTIVE_PROPOSALS.items():
        if proposal_info["short_code"] == short_code:
            return proposal_id
    return None


def _log_sms_interaction(phone_number: str, message: str, interaction_type: str, response: str):
    """Log SMS interaction for debugging and analytics."""
    _SMS_LOGS.append({
        "phone_number": phone_number,
        "message": message,
        "interaction_type": interaction_type,
        "response": response,
        "timestamp": datetime.utcnow()
    })


def get_sms_statistics() -> dict:
    """Get SMS interaction statistics."""
    total_interactions = len(_SMS_LOGS)
    
    # Count by interaction type
    type_counts = {}
    for log in _SMS_LOGS:
        interaction_type = log["interaction_type"]
        type_counts[interaction_type] = type_counts.get(interaction_type, 0) + 1
    
    successful_votes = type_counts.get("vote_recorded", 0)
    
    return {
        "total_interactions": total_interactions,
        "successful_votes": successful_votes,
        "active_proposals": len(_ACTIVE_PROPOSALS),
        "interaction_breakdown": type_counts,
        "success_rate": successful_votes / total_interactions if total_interactions > 0 else 0
    }


def get_proposal_voting_status(proposal_id: str) -> Optional[dict]:
    """Get voting status for a proposal."""
    if proposal_id not in _ACTIVE_PROPOSALS:
        return None
    
    proposal = _ACTIVE_PROPOSALS[proposal_id]
    tally = get_vote_tally(proposal_id)
    
    return {
        "proposal_id": proposal_id,
        "short_code": proposal["short_code"],
        "title": proposal["title"],
        "voting_deadline": proposal["voting_deadline"],
        "is_active": datetime.utcnow() <= proposal["voting_deadline"],
        "vote_tally": tally
    }


def close_proposal_voting(proposal_id: str) -> bool:
    """Close voting for a proposal."""
    if proposal_id in _ACTIVE_PROPOSALS:
        del _ACTIVE_PROPOSALS[proposal_id]
        logger.info("Closed voting for proposal %s", proposal_id)
        return True
    return False
