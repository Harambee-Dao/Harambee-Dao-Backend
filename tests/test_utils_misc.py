from app.utils.ipfs import pin_cid
from app.utils.oracle import verify_attestation
from app.utils.celestia import anchor_hash


def test_ipfs_pin_cid():
    assert pin_cid("bafy123") is True


def test_oracle_verify_attestation_true():
    assert verify_attestation("0xabc") is True


def test_oracle_verify_attestation_false():
    assert verify_attestation("") is False


def test_celestia_anchor_hash():
    assert anchor_hash("0xdeadbeef") is True
