"""
Example usage of the Computer Vision + Blockchain DApp
"""

import cv2
from app.models import FaceTracker
from app.blockchain import CardanoClient, DIDManager
from app.ipfs import IPFSClient
import numpy as np


def example_face_tracking():
    """Example: Detect faces in a webcam stream"""

    print("🎯 Starting Face Tracking Example...")

    # Initialize face tracker
    tracker = FaceTracker(min_detection_confidence=0.5)

    # Open webcam
    cap = cv2.VideoCapture(0)

    print("Press 'q' to quit, 's' to save face")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Track faces
        faces = tracker.track_faces(frame)

        # Draw faces
        output_frame = tracker.draw_faces(frame, faces)

        # Display
        cv2.imshow("Face Tracking", output_frame)

        # Handle key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("s") and faces:
            print(f"✅ Found {len(faces)} face(s)")
            for face in faces:
                print(f"  Face ID: {face.face_id}, Confidence: {face.confidence:.2f}")

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
    tracker.release()
    print(f"🏁 Face tracking ended. Processed {frame_count} frames")


def example_did_creation():
    """Example: Create DIDs for faces"""

    print("\n🔐 Starting DID Creation Example...")

    # Initialize clients
    try:
        cardano = CardanoClient(network="testnet")
        did_manager = DIDManager(cardano)

        # Create sample DIDs
        for i in range(3):
            face_id = f"face_{i:03d}"
            metadata = {
                "name": f"Person {i}",
                "email": f"person{i}@example.com",
                "created_at": "2025-01-01T00:00:00Z",
            }

            # Create DID
            did = did_manager.create_did(f"QmSample{i}", metadata)
            print(f"✅ DID created: {did}")

        # List all DIDs
        all_dids = did_manager.list_dids()
        print(f"\n📋 Total DIDs: {len(all_dids)}")
        for did in all_dids:
            doc = did_manager.get_did_document(did)
            print(f"  - {did}: {doc['metadata']['name']}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_ipfs_upload():
    """Example: Upload face embedding to IPFS"""

    print("\n💾 Starting IPFS Upload Example...")

    try:
        ipfs = IPFSClient()

        # Sample face embedding data
        face_data = {
            "face_id": "face_001",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "confidence": 0.95,
            "timestamp": "2025-01-01T00:00:00Z",
        }

        # Upload to IPFS
        cid = ipfs.add_json(face_data)
        print(f"✅ Uploaded to IPFS: {cid}")

        # Retrieve from IPFS
        retrieved = ipfs.get_json(cid)
        print(f"✅ Retrieved from IPFS: {retrieved}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Ensure IPFS node is running: ipfs daemon")


if __name__ == "__main__":
    print("=" * 50)
    print("Computer Vision + Blockchain DApp Examples")
    print("=" * 50)

    # Uncomment to run examples
    # example_face_tracking()
    # example_did_creation()
    # example_ipfs_upload()

    print("\n✨ Examples are ready! Uncomment in main.py to run them")
