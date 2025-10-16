"""
Unit tests for face tracking model
"""

import pytest
import numpy as np
from app.models import FaceTracker


@pytest.fixture
def tracker():
    """Create face tracker instance"""
    return FaceTracker()


def test_tracker_initialization(tracker):
    """Test tracker initialization"""
    assert tracker is not None
    assert tracker.next_face_id == 0


def test_face_embedding_extraction(tracker):
    """Test face embedding extraction"""
    # Create dummy frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Extract embedding
    bbox = (100, 100, 50, 50)
    embedding = tracker.extract_face_embedding(frame, bbox)

    # Check embedding shape and type
    assert embedding is not None
    assert embedding.dtype == np.float32
    assert len(embedding) > 0


def test_draw_faces(tracker):
    """Test drawing faces on frame"""
    from app.models.face_tracker import FaceData

    # Create frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Create test face
    face = FaceData(face_id=1, bbox=(100, 100, 50, 50), confidence=0.95)

    # Draw
    output = tracker.draw_faces(frame, [face])

    assert output is not None
    assert output.shape == frame.shape


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
