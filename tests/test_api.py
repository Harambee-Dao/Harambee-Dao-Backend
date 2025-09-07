from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import AuditDecision

client = TestClient(app)


def test_ping():
    r = client.get("/api/ping")
    assert r.status_code == 200
    assert r.json()["message"] == "pong"


def test_vote_and_tally():
    # vote yes
    r1 = client.post("/api/vote", json={"memberId": "m1", "proposalId": "p1", "vote": True})
    assert r1.status_code == 200
    # vote no
    r2 = client.post("/api/vote", json={"memberId": "m2", "proposalId": "p1", "vote": False})
    assert r2.status_code == 200

    # tally
    rt = client.get("/api/tally/p1")
    assert rt.status_code == 200
    data = rt.json()
    assert data["yes"] == 1
    assert data["no"] == 1
    assert data["total"] == 2


def test_audit_result():
    payload = {
        "proposalId": "p2",
        "decision": AuditDecision.PASS.value,
        "confidence": 0.9,
        "evidenceCID": "bafy...",
        "modelVersion": "resnet50-v1.0",
        "attestationSignature": "0xabc",
    }
    r = client.post("/api/audit-result", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["proposalId"] == "p2"
    assert data["decision"] == "PASS"
    assert data["attestationValid"] is True


def test_audit_result_attestation_invalid():
    # empty signature ensures verify_attestation returns False
    payload = {
        "proposalId": "p3",
        "decision": AuditDecision.FAIL.value,
        "confidence": 0.1,
        "evidenceCID": "bafy...",
        "modelVersion": "resnet50-v1.0",
        "attestationSignature": "",
    }
    r = client.post("/api/audit-result", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["proposalId"] == "p3"
    assert data["decision"] == "FAIL"
    assert data["attestationValid"] is False


def test_testall_smoke():
    r = client.get("/api/testall")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "tally" in data
