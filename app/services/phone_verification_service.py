import logging
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional

from app.models.schemas import (
    OTPRequestIn, OTPRequestOut, OTPVerificationIn, OTPVerificationOut
)
from app.services.user_service import get_member_by_phone, update_member_verification_status
from app.services.kyc_service import auto_verify_basic_kyc
from app.utils.sms import send_sms

logger = logging.getLogger(__name__)

# In-memory storage for demo/development (replace with Redis in production)
_OTP_STORE: Dict[str, dict] = {}  # phone_number -> {otp, expires_at, verification_type, attempts}

# Configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 3
RATE_LIMIT_MINUTES = 1  # Minimum time between OTP requests


def generate_otp(length: int = OTP_LENGTH) -> str:
    """Generate a random OTP code."""
    return ''.join(random.choices(string.digits, k=length))


def request_otp(request_data: OTPRequestIn) -> OTPRequestOut:
    """Request an OTP for phone verification."""
    logger.info("OTP requested for %s, type: %s", request_data.phone_number, request_data.verification_type)
    
    phone_number = request_data.phone_number
    verification_type = request_data.verification_type
    
    # Check rate limiting
    if phone_number in _OTP_STORE:
        last_request = _OTP_STORE[phone_number].get("last_request")
        if last_request and datetime.utcnow() - last_request < timedelta(minutes=RATE_LIMIT_MINUTES):
            remaining_time = RATE_LIMIT_MINUTES - (datetime.utcnow() - last_request).total_seconds() / 60
            return OTPRequestOut(
                phone_number=phone_number,
                otp_sent=False,
                expires_at=datetime.utcnow(),
                message=f"Please wait {remaining_time:.1f} minutes before requesting another OTP"
            )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    # Store OTP
    _OTP_STORE[phone_number] = {
        "otp": otp_code,
        "expires_at": expires_at,
        "verification_type": verification_type,
        "attempts": 0,
        "last_request": datetime.utcnow()
    }
    
    # Send SMS
    try:
        message = f"Your Harambee DAO verification code is: {otp_code}. Valid for {OTP_EXPIRY_MINUTES} minutes. Do not share this code."
        sms_sent = send_sms(phone_number, message)
        
        if sms_sent:
            logger.info("OTP sent successfully to %s", phone_number)
            return OTPRequestOut(
                phone_number=phone_number,
                otp_sent=True,
                expires_at=expires_at,
                message="OTP sent successfully"
            )
        else:
            logger.error("Failed to send OTP to %s", phone_number)
            return OTPRequestOut(
                phone_number=phone_number,
                otp_sent=False,
                expires_at=expires_at,
                message="Failed to send OTP. Please try again."
            )
    
    except Exception as e:
        logger.error("Error sending OTP to %s: %s", phone_number, e)
        return OTPRequestOut(
            phone_number=phone_number,
            otp_sent=False,
            expires_at=expires_at,
            message="Error sending OTP. Please try again."
        )


def verify_otp(verification_data: OTPVerificationIn) -> OTPVerificationOut:
    """Verify an OTP code."""
    logger.info("OTP verification attempt for %s", verification_data.phone_number)
    
    phone_number = verification_data.phone_number
    provided_otp = verification_data.otp_code.strip()
    verification_type = verification_data.verification_type
    
    # Check if OTP exists
    if phone_number not in _OTP_STORE:
        logger.warning("No OTP found for %s", phone_number)
        return OTPVerificationOut(
            phone_number=phone_number,
            verified=False,
            verification_type=verification_type,
            expires_at=None
        )
    
    otp_data = _OTP_STORE[phone_number]
    
    # Check if OTP expired
    if datetime.utcnow() > otp_data["expires_at"]:
        logger.warning("Expired OTP for %s", phone_number)
        del _OTP_STORE[phone_number]
        return OTPVerificationOut(
            phone_number=phone_number,
            verified=False,
            verification_type=verification_type,
            expires_at=otp_data["expires_at"]
        )
    
    # Check verification type matches
    if otp_data["verification_type"] != verification_type:
        logger.warning("Verification type mismatch for %s: expected %s, got %s", 
                      phone_number, otp_data["verification_type"], verification_type)
        return OTPVerificationOut(
            phone_number=phone_number,
            verified=False,
            verification_type=verification_type,
            expires_at=otp_data["expires_at"]
        )
    
    # Increment attempts
    otp_data["attempts"] += 1
    
    # Check max attempts
    if otp_data["attempts"] > MAX_OTP_ATTEMPTS:
        logger.warning("Max OTP attempts exceeded for %s", phone_number)
        del _OTP_STORE[phone_number]
        return OTPVerificationOut(
            phone_number=phone_number,
            verified=False,
            verification_type=verification_type,
            expires_at=None
        )
    
    # Verify OTP
    if provided_otp == otp_data["otp"]:
        logger.info("OTP verified successfully for %s", phone_number)
        
        # Remove OTP from store
        expires_at = otp_data["expires_at"]
        del _OTP_STORE[phone_number]
        
        # Update member verification status if this is registration verification
        if verification_type == "registration":
            member = get_member_by_phone(phone_number)
            if member:
                update_member_verification_status(member.member_id, phone_verified=True)
                logger.info("Updated phone verification status for member %s", member.member_id)
                
                # Try auto-KYC verification
                auto_verify_basic_kyc(member.member_id)
        
        return OTPVerificationOut(
            phone_number=phone_number,
            verified=True,
            verification_type=verification_type,
            expires_at=expires_at
        )
    
    else:
        logger.warning("Invalid OTP for %s (attempt %d/%d)", phone_number, otp_data["attempts"], MAX_OTP_ATTEMPTS)
        return OTPVerificationOut(
            phone_number=phone_number,
            verified=False,
            verification_type=verification_type,
            expires_at=otp_data["expires_at"]
        )


def is_phone_verified(phone_number: str) -> bool:
    """Check if a phone number is verified."""
    member = get_member_by_phone(phone_number)
    return member.phone_verified if member else False


def get_otp_status(phone_number: str) -> Optional[dict]:
    """Get current OTP status for a phone number."""
    if phone_number not in _OTP_STORE:
        return None
    
    otp_data = _OTP_STORE[phone_number]
    
    # Check if expired
    if datetime.utcnow() > otp_data["expires_at"]:
        del _OTP_STORE[phone_number]
        return None
    
    return {
        "phone_number": phone_number,
        "verification_type": otp_data["verification_type"],
        "expires_at": otp_data["expires_at"],
        "attempts_remaining": MAX_OTP_ATTEMPTS - otp_data["attempts"],
        "can_request_new": datetime.utcnow() - otp_data["last_request"] >= timedelta(minutes=RATE_LIMIT_MINUTES)
    }


def cleanup_expired_otps():
    """Clean up expired OTPs from storage."""
    current_time = datetime.utcnow()
    expired_phones = []
    
    for phone_number, otp_data in _OTP_STORE.items():
        if current_time > otp_data["expires_at"]:
            expired_phones.append(phone_number)
    
    for phone_number in expired_phones:
        del _OTP_STORE[phone_number]
        logger.debug("Cleaned up expired OTP for %s", phone_number)
    
    if expired_phones:
        logger.info("Cleaned up %d expired OTPs", len(expired_phones))


def get_verification_statistics() -> dict:
    """Get phone verification statistics."""
    active_otps = len(_OTP_STORE)
    
    # Count verified phones (this would be more efficient with a database)
    verified_count = 0
    total_members = 0
    
    # This is a simplified count - in production, query the database directly
    from app.services.user_service import _MEMBERS
    for member_data in _MEMBERS.values():
        total_members += 1
        if member_data.get("phone_verified", False):
            verified_count += 1
    
    return {
        "total_members": total_members,
        "verified_phones": verified_count,
        "active_otps": active_otps,
        "verification_rate": verified_count / total_members if total_members > 0 else 0
    }
