"""
Test Script: API Endpoints
==========================

Kiểm tra các API endpoints hoạt động không.
Gọi trực tiếp các endpoints (không dùng mock).

Chạy: python test_api_endpoints.py
      (Backend must be running on localhost:8000)
"""

import sys
import os
import time
import json
from pathlib import Path

# Detect backend URL
BACKEND_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health check endpoint"""
    print("\n" + "-"*80)
    print("[TEST 1/6] Health Check")
    print("-"*80)
    
    try:
        import requests
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   - Status: {data.get('status', 'unknown')}")
            print(f"   - Response: {response.status_code}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach backend: {e}")
        print(f"   - Make sure backend is running: python backend/main.py")
        return False

def test_get_dids():
    """Test get DIDs endpoint"""
    print("\n" + "-"*80)
    print("[TEST 2/6] Get DIDs List")
    print("-"*80)
    
    try:
        import requests
        response = requests.get(f"{BACKEND_URL}/dids", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get DIDs passed")
            print(f"   - Count: {data.get('count', 0)}")
            print(f"   - DIDs: {len(data.get('dids', []))}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_did():
    """Test create DID endpoint"""
    print("\n" + "-"*80)
    print("[TEST 3/6] Create DID via API")
    print("-"*80)
    
    try:
        import requests
        
        payload = {
            "did_id": f"api-test-{int(time.time())}",
            "face_embedding": "Qm" + "a" * 44
        }
        
        print(f"   - Creating: {payload['did_id']}")
        response = requests.post(
            f"{BACKEND_URL}/did/create",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Create DID passed")
            print(f"   - DID: {data.get('did', 'unknown')}")
            print(f"   - TX Hash: {data.get('tx_hash', 'unknown')}")
            return True, data.get('did')
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_get_did(did_id):
    """Test get DID endpoint"""
    print("\n" + "-"*80)
    print("[TEST 4/6] Get DID Document")
    print("-"*80)
    
    if not did_id:
        print(f"⚠️  Skipping (no DID from previous test)")
        return False
    
    try:
        import requests
        response = requests.get(f"{BACKEND_URL}/did/{did_id}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get DID passed")
            print(f"   - DID: {data.get('did', 'unknown')}")
            print(f"   - Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_register_did(did_id):
    """Test register DID endpoint"""
    print("\n" + "-"*80)
    print("[TEST 5/6] Register DID via API")
    print("-"*80)
    
    if not did_id:
        print(f"⚠️  Skipping (no DID from previous test)")
        return False
    
    try:
        import requests
        response = requests.post(
            f"{BACKEND_URL}/did/{did_id}/register",
            json={},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Register DID passed")
            print(f"   - DID: {did_id}")
            print(f"   - TX Hash: {data.get('tx_hash', 'unknown')}")
            print(f"   - Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_verify_did(did_id):
    """Test verify DID endpoint"""
    print("\n" + "-"*80)
    print("[TEST 6/6] Verify DID via API")
    print("-"*80)
    
    if not did_id:
        print(f"⚠️  Skipping (no DID from previous test)")
        return False
    
    try:
        import requests
        response = requests.post(
            f"{BACKEND_URL}/did/{did_id}/verify",
            json={},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Verify DID passed")
            print(f"   - DID: {did_id}")
            print(f"   - TX Hash: {data.get('tx_hash', 'unknown')}")
            print(f"   - Verified: {data.get('verified', False)}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_endpoints():
    """Run all API endpoint tests"""
    
    print("\n" + "="*80)
    print("API ENDPOINTS TEST")
    print("="*80)
    
    # Check if requests library is available
    try:
        import requests
    except ImportError:
        print("\n❌ ERROR: 'requests' library not found")
        print("   Install: pip install requests")
        return False
    
    results = []
    
    # Test 1: Health
    results.append(("Health", test_health()))
    
    if not results[-1][1]:
        print("\n" + "="*80)
        print("❌ Cannot connect to backend")
        print("="*80)
        print("\nMake sure backend is running:")
        print("  cd backend")
        print("  python main.py")
        return False
    
    # Test 2: Get DIDs
    results.append(("Get DIDs", test_get_dids()))
    
    # Test 3: Create DID
    success, did_id = test_create_did()
    results.append(("Create DID", success))
    
    # Test 4: Get DID
    results.append(("Get DID", test_get_did(did_id)))
    
    # Test 5: Register DID
    results.append(("Register DID", test_register_did(did_id)))
    
    # Test 6: Verify DID
    results.append(("Verify DID", test_verify_did(did_id)))
    
    # Summary
    print("\n" + "="*80)
    print("API ENDPOINTS TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nResults:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n✅ All API endpoints working correctly!")
        return True
    else:
        print(f"\n⚠️  Some tests failed")
        return False

if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)
