/// Shared types for DID Management
///
/// DIDDatum: dữ liệu danh tính lưu on-chain
/// Action: redeemer actions cho validator

/// DID Datum — inline datum trên blockchain
pub type DIDDatum {
  /// Unique DID identifier (ví dụ: "did:cardano:abc123")
  did_id: ByteArray,
  /// IPFS CID chứa face embedding (từ Lesson 6)
  face_ipfs_hash: ByteArray,
  /// Public key hash của owner (28 bytes)
  owner: ByteArray,
  /// Thời điểm tạo (POSIX milliseconds)
  created_at: Int,
  /// Trạng thái xác minh (0 = chưa, 1 = đã xác minh)
  verified: Int,
}

/// Redeemer Actions — quyết định logic validation nào được chạy
pub type Action {
  /// Đăng ký DID mới trên blockchain
  Register
  /// Cập nhật dữ liệu DID (ví dụ: thay đổi face embedding)
  Update
  /// Xác minh danh tính (so khớp face embedding)
  Verify
  /// Thu hồi/vô hiệu hóa DID vĩnh viễn
  Revoke
}
