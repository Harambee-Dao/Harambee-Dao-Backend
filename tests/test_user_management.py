import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.models.schemas import KYCStatus, MemberRole, KYCDocumentType

client = TestClient(app)


class TestGroupManagement:
    """Test group creation and management."""
    
    def test_create_group(self):
        """Test creating a new group."""
        group_data = {
            "group_name": "Test Farmers Group",
            "description": "A test farming community",
            "location": "Nairobi, Kenya",
            "leader_phone": "+254700000001",
            "leader_name": "John Doe",
            "expected_member_count": 10,
            "treasury_threshold": 3
        }
        
        response = client.post("/api/users/groups", json=group_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["group_name"] == group_data["group_name"]
        assert data["location"] == group_data["location"]
        assert data["member_count"] == 1  # Leader is automatically added
        assert data["kyc_status"] == KYCStatus.PENDING
        
        return data["group_id"]
    
    def test_list_groups(self):
        """Test listing all groups."""
        response = client.get("/api/users/groups")
        assert response.status_code == 200
        
        groups = response.json()
        assert isinstance(groups, list)
    
    def test_get_group_by_id(self):
        """Test getting a specific group."""
        group_id = self.test_create_group()
        
        response = client.get(f"/api/users/groups/{group_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["group_id"] == group_id
    
    def test_create_group_duplicate_phone(self):
        """Test creating group with duplicate leader phone."""
        group_data = {
            "group_name": "Test Group 1",
            "location": "Nairobi, Kenya",
            "leader_phone": "+254700000002",
            "leader_name": "Jane Doe",
            "expected_member_count": 5,
            "treasury_threshold": 2
        }
        
        # Create first group
        response1 = client.post("/api/users/groups", json=group_data)
        assert response1.status_code == 201
        
        # Try to create second group with same phone
        group_data["group_name"] = "Test Group 2"
        response2 = client.post("/api/users/groups", json=group_data)
        assert response2.status_code == 400


class TestMemberManagement:
    """Test member registration and management."""
    
    def setup_method(self):
        """Set up test group for member tests."""
        group_data = {
            "group_name": "Member Test Group",
            "location": "Mombasa, Kenya",
            "leader_phone": "+254700000003",
            "leader_name": "Leader Test",
            "expected_member_count": 5,
            "treasury_threshold": 2
        }
        
        response = client.post("/api/users/groups", json=group_data)
        self.group_id = response.json()["group_id"]
    
    def test_register_member(self):
        """Test registering a new member."""
        member_data = {
            "phone_number": "+254700000004",
            "full_name": "Test Member",
            "group_id": self.group_id,
            "location": "Mombasa, Kenya",
            "role": MemberRole.MEMBER
        }
        
        response = client.post("/api/users/members", json=member_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["phone_number"] == member_data["phone_number"]
        assert data["full_name"] == member_data["full_name"]
        assert data["group_id"] == self.group_id
        assert data["phone_verified"] == False
        assert data["kyc_status"] == KYCStatus.PENDING
        
        return data["member_id"]
    
    def test_get_member_by_phone(self):
        """Test getting member by phone number."""
        member_id = self.test_register_member()
        
        response = client.get("/api/users/members/phone/+254700000004")
        assert response.status_code == 200
        
        data = response.json()
        assert data["member_id"] == member_id
    
    def test_get_group_members(self):
        """Test getting all members of a group."""
        self.test_register_member()
        
        response = client.get(f"/api/users/groups/{self.group_id}/members")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_count"] >= 2  # Leader + new member
        assert len(data["members"]) >= 2


class TestPhoneVerification:
    """Test phone verification functionality."""
    
    def test_request_otp(self):
        """Test requesting OTP for phone verification."""
        otp_request = {
            "phone_number": "+254700000005",
            "verification_type": "registration"
        }
        
        response = client.post("/api/users/phone/request-otp", json=otp_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["phone_number"] == otp_request["phone_number"]
        assert data["otp_sent"] == True
    
    def test_verify_otp_invalid(self):
        """Test verifying invalid OTP."""
        # First request OTP
        otp_request = {
            "phone_number": "+254700000006",
            "verification_type": "registration"
        }
        client.post("/api/users/phone/request-otp", json=otp_request)
        
        # Try to verify with wrong OTP
        verification_data = {
            "phone_number": "+254700000006",
            "otp_code": "000000",
            "verification_type": "registration"
        }
        
        response = client.post("/api/users/phone/verify-otp", json=verification_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["verified"] == False
    
    def test_otp_rate_limiting(self):
        """Test OTP rate limiting."""
        otp_request = {
            "phone_number": "+254700000007",
            "verification_type": "registration"
        }
        
        # First request should succeed
        response1 = client.post("/api/users/phone/request-otp", json=otp_request)
        assert response1.status_code == 200
        assert response1.json()["otp_sent"] == True
        
        # Second immediate request should be rate limited
        response2 = client.post("/api/users/phone/request-otp", json=otp_request)
        assert response2.status_code == 200
        assert response2.json()["otp_sent"] == False


class TestKYCManagement:
    """Test KYC document submission and verification."""
    
    def setup_method(self):
        """Set up test member for KYC tests."""
        # Create group and member
        group_data = {
            "group_name": "KYC Test Group",
            "location": "Kisumu, Kenya",
            "leader_phone": "+254700000008",
            "leader_name": "KYC Leader",
            "expected_member_count": 5,
            "treasury_threshold": 2
        }
        
        group_response = client.post("/api/users/groups", json=group_data)
        self.group_id = group_response.json()["group_id"]
        
        member_data = {
            "phone_number": "+254700000009",
            "full_name": "KYC Test Member",
            "group_id": self.group_id,
            "role": MemberRole.MEMBER
        }
        
        member_response = client.post("/api/users/members", json=member_data)
        self.member_id = member_response.json()["member_id"]
    
    def test_submit_kyc_document(self):
        """Test submitting KYC document."""
        document_data = {
            "member_id": self.member_id,
            "document_type": KYCDocumentType.NATIONAL_ID,
            "document_number": "12345678",
            "issuing_authority": "Government of Kenya"
        }
        
        response = client.post("/api/users/kyc/documents", json=document_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["member_id"] == self.member_id
        assert data["document_type"] == KYCDocumentType.NATIONAL_ID
        assert data["document_number"] == document_data["document_number"]
    
    def test_get_member_documents(self):
        """Test getting member's KYC documents."""
        self.test_submit_kyc_document()
        
        response = client.get(f"/api/users/kyc/members/{self.member_id}/documents")
        assert response.status_code == 200
        
        documents = response.json()
        assert isinstance(documents, list)
        assert len(documents) >= 1
    
    def test_kyc_review(self):
        """Test KYC review process."""
        self.test_submit_kyc_document()
        
        review_data = {
            "member_id": self.member_id,
            "status": KYCStatus.VERIFIED,
            "reviewer_notes": "Documents verified successfully"
        }
        
        response = client.post("/api/users/kyc/review", json=review_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["member_id"] == self.member_id
        assert data["new_status"] == KYCStatus.VERIFIED


class TestSMSWebhook:
    """Test SMS webhook functionality."""
    
    def test_sms_webhook_unregistered_phone(self):
        """Test SMS webhook with unregistered phone number."""
        webhook_data = {
            "From": "+254700000999",
            "To": "+254700000000",
            "Body": "YES001",
            "MessageSid": "SM123456789"
        }
        
        response = client.post("/api/users/webhooks/sms", json=webhook_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["processed"] == False
        assert "not registered" in data["error_message"]
    
    def test_sms_webhook_invalid_format(self):
        """Test SMS webhook with invalid vote format."""
        # First create a member
        group_data = {
            "group_name": "SMS Test Group",
            "location": "Eldoret, Kenya",
            "leader_phone": "+254700000010",
            "leader_name": "SMS Leader",
            "expected_member_count": 5,
            "treasury_threshold": 2
        }
        
        group_response = client.post("/api/users/groups", json=group_data)
        group_id = group_response.json()["group_id"]
        
        member_data = {
            "phone_number": "+254700000011",
            "full_name": "SMS Test Member",
            "group_id": group_id,
            "role": MemberRole.MEMBER
        }
        
        client.post("/api/users/members", json=member_data)
        
        # Test invalid SMS format
        webhook_data = {
            "From": "+254700000011",
            "To": "+254700000000",
            "Body": "INVALID MESSAGE",
            "MessageSid": "SM123456790"
        }
        
        response = client.post("/api/users/webhooks/sms", json=webhook_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["processed"] == False
        assert "Invalid vote format" in data["error_message"]


class TestStatistics:
    """Test statistics endpoints."""
    
    def test_phone_verification_stats(self):
        """Test phone verification statistics."""
        response = client.get("/api/users/stats/phone-verification")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_members" in data
        assert "verified_phones" in data
        assert "verification_rate" in data
    
    def test_kyc_stats(self):
        """Test KYC statistics."""
        response = client.get("/api/users/stats/kyc")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_members" in data
        assert "verified_count" in data
        assert "pending_count" in data
    
    def test_sms_stats(self):
        """Test SMS statistics."""
        response = client.get("/api/users/stats/sms")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_interactions" in data
        assert "successful_votes" in data
        assert "success_rate" in data
