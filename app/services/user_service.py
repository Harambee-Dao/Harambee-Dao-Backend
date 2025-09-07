import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

from app.models.schemas import (
    GroupIn, GroupOut, MemberIn, MemberOut, MemberUpdateIn,
    KYCStatus, MemberRole, VerificationStatus, MemberListOut,
    GroupMembershipOut
)

logger = logging.getLogger(__name__)

# In-memory storage for demo/development (replace with database in production)
_GROUPS: Dict[str, dict] = {}
_MEMBERS: Dict[str, dict] = {}
_GROUP_MEMBERS: Dict[str, List[str]] = defaultdict(list)  # group_id -> [member_ids]
_PHONE_TO_MEMBER: Dict[str, str] = {}  # phone_number -> member_id


def create_group(group_data: GroupIn) -> GroupOut:
    """Create a new community group and register the leader."""
    logger.info("Creating new group: %s", group_data.group_name)
    
    # Check if leader phone already exists
    if group_data.leader_phone in _PHONE_TO_MEMBER:
        raise ValueError(f"Phone number {group_data.leader_phone} is already registered")
    
    # Generate group ID
    group_id = str(uuid.uuid4())
    
    # Create group record
    group_record = {
        "group_id": group_id,
        "group_name": group_data.group_name,
        "description": group_data.description,
        "location": group_data.location,
        "leader_id": None,  # Will be set after creating leader
        "member_count": 0,
        "treasury_address": None,  # Will be set when Safe is deployed
        "treasury_threshold": group_data.treasury_threshold,
        "created_at": datetime.utcnow(),
        "kyc_status": KYCStatus.PENDING
    }
    
    # Create leader as first member
    leader_data = MemberIn(
        phone_number=group_data.leader_phone,
        full_name=group_data.leader_name,
        group_id=group_id,
        location=group_data.location,
        role=MemberRole.LEADER
    )
    
    leader = register_member(leader_data)
    group_record["leader_id"] = leader.member_id
    group_record["member_count"] = 1
    
    _GROUPS[group_id] = group_record
    
    logger.info("Created group %s with leader %s", group_id, leader.member_id)
    
    return GroupOut(**group_record)


def register_member(member_data: MemberIn) -> MemberOut:
    """Register a new member to a group."""
    logger.info("Registering member %s to group %s", member_data.phone_number, member_data.group_id)
    
    # Validate group exists
    if member_data.group_id not in _GROUPS:
        raise ValueError(f"Group {member_data.group_id} does not exist")
    
    # Check if phone already registered
    if member_data.phone_number in _PHONE_TO_MEMBER:
        raise ValueError(f"Phone number {member_data.phone_number} is already registered")
    
    # Generate member ID
    member_id = str(uuid.uuid4())
    
    # Create member record
    member_record = {
        "member_id": member_id,
        "phone_number": member_data.phone_number,
        "full_name": member_data.full_name,
        "group_id": member_data.group_id,
        "location": member_data.location,
        "role": member_data.role,
        "phone_verified": False,
        "kyc_status": KYCStatus.PENDING,
        "created_at": datetime.utcnow(),
        "last_active": None
    }
    
    # Store member
    _MEMBERS[member_id] = member_record
    _PHONE_TO_MEMBER[member_data.phone_number] = member_id
    _GROUP_MEMBERS[member_data.group_id].append(member_id)
    
    # Update group member count
    if member_data.group_id in _GROUPS:
        _GROUPS[member_data.group_id]["member_count"] += 1
    
    logger.info("Registered member %s", member_id)
    
    return MemberOut(**member_record)


def get_member_by_id(member_id: str) -> Optional[MemberOut]:
    """Get member by ID."""
    member_record = _MEMBERS.get(member_id)
    if member_record:
        return MemberOut(**member_record)
    return None


def get_member_by_phone(phone_number: str) -> Optional[MemberOut]:
    """Get member by phone number."""
    member_id = _PHONE_TO_MEMBER.get(phone_number)
    if member_id:
        return get_member_by_id(member_id)
    return None


def update_member(member_id: str, update_data: MemberUpdateIn) -> Optional[MemberOut]:
    """Update member information."""
    if member_id not in _MEMBERS:
        return None
    
    member_record = _MEMBERS[member_id]
    
    # Update fields if provided
    if update_data.full_name is not None:
        member_record["full_name"] = update_data.full_name
    if update_data.location is not None:
        member_record["location"] = update_data.location
    if update_data.role is not None:
        member_record["role"] = update_data.role
    
    logger.info("Updated member %s", member_id)
    
    return MemberOut(**member_record)


def get_group_members(group_id: str) -> MemberListOut:
    """Get all members of a group."""
    if group_id not in _GROUPS:
        raise ValueError(f"Group {group_id} does not exist")
    
    member_ids = _GROUP_MEMBERS.get(group_id, [])
    members = []
    verified_count = 0
    pending_kyc_count = 0
    
    for member_id in member_ids:
        if member_id in _MEMBERS:
            member = MemberOut(**_MEMBERS[member_id])
            members.append(member)
            
            if member.phone_verified and member.kyc_status == KYCStatus.VERIFIED:
                verified_count += 1
            elif member.kyc_status == KYCStatus.PENDING:
                pending_kyc_count += 1
    
    return MemberListOut(
        members=members,
        total_count=len(members),
        verified_count=verified_count,
        pending_kyc_count=pending_kyc_count
    )


def get_group_by_id(group_id: str) -> Optional[GroupOut]:
    """Get group by ID."""
    group_record = _GROUPS.get(group_id)
    if group_record:
        return GroupOut(**group_record)
    return None


def update_member_verification_status(member_id: str, phone_verified: bool = None, kyc_status: KYCStatus = None) -> Optional[MemberOut]:
    """Update member verification status."""
    if member_id not in _MEMBERS:
        return None
    
    member_record = _MEMBERS[member_id]
    
    if phone_verified is not None:
        member_record["phone_verified"] = phone_verified
        logger.info("Updated phone verification for member %s: %s", member_id, phone_verified)
    
    if kyc_status is not None:
        member_record["kyc_status"] = kyc_status
        logger.info("Updated KYC status for member %s: %s", member_id, kyc_status)
    
    # Update last active
    member_record["last_active"] = datetime.utcnow()
    
    return MemberOut(**member_record)


def get_all_groups() -> List[GroupOut]:
    """Get all groups."""
    return [GroupOut(**group_record) for group_record in _GROUPS.values()]


def update_group_treasury(group_id: str, treasury_address: str) -> Optional[GroupOut]:
    """Update group treasury address after Safe deployment."""
    if group_id not in _GROUPS:
        return None
    
    _GROUPS[group_id]["treasury_address"] = treasury_address
    logger.info("Updated treasury address for group %s: %s", group_id, treasury_address)
    
    return GroupOut(**_GROUPS[group_id])


def get_member_group_info(member_id: str) -> Optional[GroupMembershipOut]:
    """Get member's group membership information."""
    member = get_member_by_id(member_id)
    if not member:
        return None
    
    group = get_group_by_id(member.group_id)
    if not group:
        return None
    
    return GroupMembershipOut(
        group=group,
        member=member,
        joined_at=member.created_at,
        is_active=member.kyc_status == KYCStatus.VERIFIED and member.phone_verified
    )
