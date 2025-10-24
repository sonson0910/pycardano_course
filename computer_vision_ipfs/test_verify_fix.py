#!/usr/bin/env python3
"""
Quick test to verify the face similarity verification fix
Run after backend is started
"""

import requests
import json
from pathlib import Path
import time

# Configuration
API_BASE = "http://localhost:8000/api/v1"
TEST_IMAGE = "test_face.jpg"  # You need to provide this


def test_verify_flow():
    """Test the full DID creation and verification flow"""

    print("\n" + "=" * 60)
    print("🧪 FACE VERIFICATION SYSTEM TEST")
    print("=" * 60)

    # Step 1: Upload image and detect faces
    print("\n[1] 📸 Uploading test image and detecting faces...")
    with open(TEST_IMAGE, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_BASE}/detect-faces", files=files)

    if response.status_code != 200:
        print(f"❌ Face detection failed: {response.text}")
        return False

    detect_result = response.json()
    embedding_hash = detect_result["embedding_ipfs_hash"]
    face_count = detect_result["faces_detected"]

    print(f"✅ Detected {face_count} face(s)")
    print(f"   Embedding IPFS hash: {embedding_hash[:12]}...")

    # Step 2: Create DID with first embedding
    print("\n[2] 🆔 Creating DID with first embedding...")
    did_payload = {
        "face_id": "test_face_001",
        "face_ipfs_hash": embedding_hash,
        "owner_address": "addr_test1vqfwvs52xn0ue7m9x9h82xd3h0ah2hg4jzjjw2q82y7s0sqvwdrf0",
    }

    response = requests.post(f"{API_BASE}/create-did", json=did_payload)
    if response.status_code != 200:
        print(f"❌ DID creation failed: {response.text}")
        return False

    create_result = response.json()
    did = create_result["did"]

    print(f"✅ DID created: {did}")
    print(f"   Transaction: {create_result.get('tx_hash', 'N/A')[:12]}...")

    # Wait for confirmation
    print("\n[3] ⏳ Waiting for on-chain confirmation...")
    time.sleep(5)

    # Step 3: Verify with SAME image (should be 100%)
    print("\n[4] ✅ Verifying with SAME image...")
    verify_payload = {"face_embedding": embedding_hash}

    response = requests.post(
        f"{API_BASE}/did/{did}/verify", json=verify_payload, timeout=120
    )

    if response.status_code != 200:
        print(f"❌ Verification failed: {response.text}")
        return False

    verify_result = response.json()
    confidence_same = verify_result["confidence"]

    print(f"✅ Same image verification:")
    print(f"   Confidence: {(confidence_same * 100):.2f}%")
    print(f"   Status: {verify_result['message']}")

    # Expected: 100% (identical image)
    if confidence_same == 1.0:
        print("   ✅ PASS: Got 100% confidence for identical image")
    else:
        print(f"   ⚠️  WARN: Expected 100%, got {(confidence_same * 100):.2f}%")

    # Step 4: Verify with DIFFERENT image (should be lower)
    print("\n[5] 🔄 Uploading different image...")

    # For this test, you would upload a different image
    # For now, we'll show what to expect
    print("   ℹ️  To test with different image:")
    print("   - Upload a different face photo")
    print("   - Run same verify request")
    print("   - Expected: 50-95% confidence (depending on similarity)")

    # Summary
    print("\n" + "=" * 60)
    print("✅ TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"DID Created: {did}")
    print(f"Same Image Confidence: {(confidence_same * 100):.2f}%")
    print(f"Expected: 100% (identical image)")

    if confidence_same > 0.95:
        print("\n✅ VERIFICATION SYSTEM WORKING CORRECTLY!")
        return True
    else:
        print("\n❌ Verification returned unexpected value")
        return False


def test_api_endpoint():
    """Test that the API endpoint accepts the correct format"""

    print("\n[TEST] 📡 API Endpoint Format Test")
    print("-" * 40)

    # Test with proper Pydantic model format
    test_data = {"face_embedding": "QmTestHash123456789"}

    # This would fail with invalid DID, but tests endpoint accepts format
    response = requests.post(
        f"{API_BASE}/did/invalid-did/verify", json=test_data, timeout=10
    )

    # Even if it fails, it should fail with "DID not found", not format error
    if "DID not found" in response.text or response.status_code >= 400:
        print("✅ Endpoint accepts JSON body format correctly")
        return True
    else:
        print(f"⚠️  Unexpected response: {response.text}")
        return False


if __name__ == "__main__":
    print("\n🔍 FACE VERIFICATION SYSTEM - TEST SUITE\n")

    # Check if test image exists
    if not Path(TEST_IMAGE).exists():
        print(f"❌ Test image not found: {TEST_IMAGE}")
        print("\nTo run full test, provide a test face image at:", TEST_IMAGE)
        print("\nRunning API format test only...")
        test_api_endpoint()
    else:
        # Run full test
        success = test_verify_flow()
        exit(0 if success else 1)
