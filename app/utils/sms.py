import logging
from typing import Optional
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_sms(to_phone: str, message: str) -> bool:
    """
    Send SMS using Twilio API.
    
    Args:
        to_phone: Recipient phone number in E.164 format
        message: SMS message content
        
    Returns:
        bool: True if SMS sent successfully, False otherwise
    """
    # Check if Twilio credentials are configured
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio credentials not configured, simulating SMS send")
        logger.info("SIMULATED SMS to %s: %s", to_phone, message)
        return True  # Return True for development/testing
    
    try:
        # Twilio API endpoint
        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        
        # Request payload
        data = {
            "From": settings.TWILIO_PHONE_NUMBER,
            "To": to_phone,
            "Body": message
        }
        
        # Make request with basic auth
        response = requests.post(
            url,
            data=data,
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            timeout=10
        )
        
        if response.status_code == 201:
            response_data = response.json()
            message_sid = response_data.get("sid")
            logger.info("SMS sent successfully to %s, SID: %s", to_phone, message_sid)
            return True
        else:
            logger.error("Failed to send SMS to %s: %s %s", to_phone, response.status_code, response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error("Network error sending SMS to %s: %s", to_phone, e)
        return False
    except Exception as e:
        logger.error("Unexpected error sending SMS to %s: %s", to_phone, e)
        return False


def send_bulk_sms(phone_numbers: list, message: str) -> dict:
    """
    Send SMS to multiple recipients.
    
    Args:
        phone_numbers: List of phone numbers in E.164 format
        message: SMS message content
        
    Returns:
        dict: Summary of send results
    """
    results = {
        "total": len(phone_numbers),
        "sent": 0,
        "failed": 0,
        "failed_numbers": []
    }
    
    for phone in phone_numbers:
        if send_sms(phone, message):
            results["sent"] += 1
        else:
            results["failed"] += 1
            results["failed_numbers"].append(phone)
    
    logger.info("Bulk SMS completed: %d sent, %d failed out of %d total", 
                results["sent"], results["failed"], results["total"])
    
    return results


def validate_phone_number(phone_number: str) -> bool:
    """
    Validate phone number format (E.164).
    
    Args:
        phone_number: Phone number to validate
        
    Returns:
        bool: True if valid E.164 format
    """
    import re
    
    # E.164 format: +[country code][number] (max 15 digits total)
    pattern = r'^\+[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone_number))


def format_phone_number(phone_number: str, default_country_code: str = "+254") -> Optional[str]:
    """
    Format phone number to E.164 format.
    
    Args:
        phone_number: Raw phone number
        default_country_code: Default country code if not provided
        
    Returns:
        str: Formatted phone number or None if invalid
    """
    # Remove all non-digit characters except +
    cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    
    # If already starts with +, validate and return
    if cleaned.startswith('+'):
        return cleaned if validate_phone_number(cleaned) else None
    
    # If starts with country code without +, add +
    if cleaned.startswith('254') and len(cleaned) >= 10:  # Kenya example
        formatted = '+' + cleaned
        return formatted if validate_phone_number(formatted) else None
    
    # If local number, add default country code
    if len(cleaned) >= 9:  # Minimum local number length
        # Remove leading 0 if present (common in local formats)
        if cleaned.startswith('0'):
            cleaned = cleaned[1:]
        
        formatted = default_country_code + cleaned
        return formatted if validate_phone_number(formatted) else None
    
    return None


def get_sms_delivery_status(message_sid: str) -> Optional[dict]:
    """
    Get SMS delivery status from Twilio.
    
    Args:
        message_sid: Twilio message SID
        
    Returns:
        dict: Message status information or None if error
    """
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio credentials not configured")
        return None
    
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages/{message_sid}.json"
        
        response = requests.get(
            url,
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "sid": data.get("sid"),
                "status": data.get("status"),
                "to": data.get("to"),
                "from": data.get("from"),
                "date_sent": data.get("date_sent"),
                "date_updated": data.get("date_updated"),
                "error_code": data.get("error_code"),
                "error_message": data.get("error_message")
            }
        else:
            logger.error("Failed to get message status: %s %s", response.status_code, response.text)
            return None
            
    except Exception as e:
        logger.error("Error getting message status for %s: %s", message_sid, e)
        return None


def send_otp_sms(phone_number: str, otp_code: str, expiry_minutes: int = 10) -> bool:
    """
    Send OTP verification SMS.
    
    Args:
        phone_number: Recipient phone number
        otp_code: OTP code to send
        expiry_minutes: OTP expiry time in minutes
        
    Returns:
        bool: True if sent successfully
    """
    message = (
        f"Your Harambee DAO verification code is: {otp_code}\n"
        f"Valid for {expiry_minutes} minutes.\n"
        f"Do not share this code with anyone."
    )
    
    return send_sms(phone_number, message)


def send_vote_confirmation_sms(phone_number: str, proposal_title: str, vote: str, tally: dict) -> bool:
    """
    Send vote confirmation SMS.
    
    Args:
        phone_number: Recipient phone number
        proposal_title: Title of the proposal
        vote: Vote cast (YES/NO)
        tally: Current vote tally
        
    Returns:
        bool: True if sent successfully
    """
    message = (
        f"✅ Vote recorded: {vote}\n"
        f"Proposal: {proposal_title[:50]}{'...' if len(proposal_title) > 50 else ''}\n"
        f"Current tally: {tally.get('yes', 0)} YES, {tally.get('no', 0)} NO"
    )
    
    return send_sms(phone_number, message)


def send_proposal_notification_sms(phone_number: str, proposal_title: str, short_code: str, deadline: str) -> bool:
    """
    Send proposal notification SMS.
    
    Args:
        phone_number: Recipient phone number
        proposal_title: Title of the proposal
        short_code: Short code for voting
        deadline: Voting deadline
        
    Returns:
        bool: True if sent successfully
    """
    message = (
        f"🗳️ HARAMBEE DAO VOTE\n"
        f"Proposal: {proposal_title[:60]}{'...' if len(proposal_title) > 60 else ''}\n"
        f"Vote by {deadline}\n"
        f"Reply: YES{short_code} or NO{short_code}"
    )
    
    return send_sms(phone_number, message)


def send_welcome_sms(phone_number: str, group_name: str) -> bool:
    """
    Send welcome SMS to new member.
    
    Args:
        phone_number: New member's phone number
        group_name: Name of the group they joined
        
    Returns:
        bool: True if sent successfully
    """
    message = (
        f"Welcome to Harambee DAO! 🎉\n"
        f"You've joined: {group_name}\n"
        f"You'll receive SMS notifications for proposals and votes.\n"
        f"Visit harambeedao.com for more info."
    )
    
    return send_sms(phone_number, message)
