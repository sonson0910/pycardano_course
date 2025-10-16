"""
Unit tests for blockchain integration
"""

import pytest
from app.blockchain import DIDManager, CardanoClient


@pytest.fixture
def mock_cardano():
    """Mock Cardano client"""
    # Return mock for testing
    return None


@pytest.fixture
def did_manager(mock_cardano):
    """Create DID manager with mock client"""
    # Create with mock client
    client = CardanoClient(network="testnet")
    return DIDManager(client)


def test_did_creation(did_manager):
    """Test DID creation"""
    did = did_manager.create_did("QmTest", {"name": "Test"})

    assert did is not None
    assert did.startswith("did:cardano:")


def test_did_retrieval(did_manager):
    """Test DID document retrieval"""
    # Create DID
    did = did_manager.create_did("QmTest", {"name": "Test"})

    # Retrieve
    doc = did_manager.get_did_document(did)

    assert doc is not None
    assert doc["did"] == did
    assert doc["face_ipfs_hash"] == "QmTest"


def test_list_dids(did_manager):
    """Test listing DIDs"""
    # Create multiple DIDs
    for i in range(3):
        did_manager.create_did(f"QmTest{i}", {"name": f"Test {i}"})

    # List
    dids = did_manager.list_dids()

    assert len(dids) == 3


def test_face_verification(did_manager):
    """Test face verification"""
    # Create DID
    did = did_manager.create_did("QmTest123", {"name": "Test"})

    # Verify with matching hash
    result = did_manager.verify_face_identity(did, "QmTest123")
    assert result is True

    # Verify with non-matching hash
    result = did_manager.verify_face_identity(did, "QmWrong")
    assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
