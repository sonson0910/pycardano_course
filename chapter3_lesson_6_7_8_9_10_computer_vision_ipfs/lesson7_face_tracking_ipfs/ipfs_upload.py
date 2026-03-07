"""
Lesson 6 — Upload Face Embedding lên IPFS (Pinata)

Đọc file embedding JSON từ face_detect.py và upload lên Pinata IPFS.
Trả về CID (Content Identifier) để dùng trong các bài tiếp theo.

Usage:
    python ipfs_upload.py --file face_embedding.json
    python ipfs_upload.py --file face_embedding.json --name "my_face"
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env từ thư mục gốc repo
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

PINATA_API_URL = "https://api.pinata.cloud"


class PinataIPFS:
    """
    Client upload dữ liệu lên Pinata IPFS

    Pinata cung cấp:
    - Upload file/JSON lên IPFS
    - Pin (giữ) dữ liệu trên mạng IPFS
    - Gateway để truy cập dữ liệu qua HTTP
    """

    def __init__(self, jwt_token: str):
        self.jwt = jwt_token
        self.headers = {"Authorization": f"Bearer {jwt_token}"}
        self._verify_auth()

    def _verify_auth(self):
        """Kiểm tra JWT token hợp lệ"""
        resp = requests.get(
            f"{PINATA_API_URL}/data/testAuthentication",
            headers=self.headers,
            timeout=10,
        )
        if resp.status_code != 200:
            raise ValueError(f"❌ Pinata JWT không hợp lệ: {resp.text}")
        print("✅ Pinata authentication OK")

    def upload_json(self, data: dict, name: str = "face_embedding") -> dict:
        """
        Upload JSON data lên Pinata IPFS

        Args:
            data: Dictionary chứa dữ liệu
            name: Tên cho pin (hiển thị trên Pinata dashboard)

        Returns:
            {
                "cid": "QmXxx...",
                "size": 1234,
                "url": "https://gateway.pinata.cloud/ipfs/QmXxx..."
            }
        """
        payload = {
            "pinataContent": data,
            "pinataMetadata": {"name": name},
            "pinataOptions": {"cidVersion": 0},
        }

        print(f"📤 Uploading JSON to Pinata IPFS...")
        resp = requests.post(
            f"{PINATA_API_URL}/pinning/pinJSONToIPFS",
            json=payload,
            headers={**self.headers, "Content-Type": "application/json"},
            timeout=30,
        )

        if resp.status_code != 200:
            raise Exception(f"Upload failed: {resp.text}")

        result = resp.json()
        cid = result["IpfsHash"]
        size = result.get("PinSize", 0)

        print(f"✅ Upload successful!")
        print(f"   CID: {cid}")
        print(f"   Size: {size} bytes")
        print(f"   URL: https://gateway.pinata.cloud/ipfs/{cid}")

        return {
            "cid": cid,
            "size": size,
            "url": f"https://gateway.pinata.cloud/ipfs/{cid}",
        }

    def upload_file(self, file_path: str, name: str = None) -> dict:
        """
        Upload file lên Pinata IPFS

        Args:
            file_path: Đường dẫn file
            name: Tên cho pin (mặc định = tên file)

        Returns:
            {"cid": "...", "size": ..., "url": "..."}
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        pin_name = name or path.name

        print(f"📤 Uploading file to Pinata IPFS: {path.name}")
        with open(file_path, "rb") as f:
            resp = requests.post(
                f"{PINATA_API_URL}/pinning/pinFileToIPFS",
                files={"file": (path.name, f)},
                data={"pinataMetadata": json.dumps({"name": pin_name})},
                headers=self.headers,
                timeout=60,
            )

        if resp.status_code != 200:
            raise Exception(f"Upload failed: {resp.text}")

        result = resp.json()
        cid = result["IpfsHash"]
        size = result.get("PinSize", 0)

        print(f"✅ Upload successful!")
        print(f"   CID: {cid}")
        print(f"   Size: {size} bytes")
        print(f"   URL: https://gateway.pinata.cloud/ipfs/{cid}")

        return {
            "cid": cid,
            "size": size,
            "url": f"https://gateway.pinata.cloud/ipfs/{cid}",
        }

    def get_json(self, cid: str) -> dict:
        """
        Đọc JSON từ IPFS qua public gateway

        Args:
            cid: IPFS CID

        Returns:
            Parsed JSON data
        """
        print(f"📥 Fetching from IPFS: {cid}")
        resp = requests.get(
            f"https://gateway.pinata.cloud/ipfs/{cid}",
            timeout=30,
        )

        if resp.status_code != 200:
            raise Exception(f"Fetch failed: {resp.status_code}")

        data = resp.json()
        print(f"✅ Retrieved data ({len(json.dumps(data))} chars)")
        return data


def main():
    parser = argparse.ArgumentParser(description="Upload Face Embedding to IPFS")
    parser.add_argument("--file", type=str, required=True, help="File embedding JSON")
    parser.add_argument("--name", type=str, default="face_embedding", help="Tên pin")
    args = parser.parse_args()

    # Kiểm tra JWT
    jwt = os.getenv("PINATA_JWT")
    if not jwt:
        print("❌ PINATA_JWT chưa được cấu hình trong file .env")
        print("   1. Đăng ký tại https://pinata.cloud")
        print("   2. Tạo API Key → copy JWT")
        print("   3. Thêm vào .env: PINATA_JWT=your_jwt_here")
        sys.exit(1)

    # Đọc file embedding
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ File không tồn tại: {args.file}")
        print(f"   Chạy face_detect.py trước: python face_detect.py --image face.jpg")
        sys.exit(1)

    with open(file_path) as f:
        embedding_data = json.load(f)

    print(f"📄 Loaded: {file_path.name}")
    print(f"   Faces: {embedding_data.get('faces_detected', 0)}")

    # Upload lên Pinata
    ipfs = PinataIPFS(jwt)
    result = ipfs.upload_json(embedding_data, name=args.name)

    # Lưu CID ra file để dùng cho bài sau
    cid_file = file_path.with_suffix(".cid")
    with open(cid_file, "w") as f:
        f.write(result["cid"])

    print(f"\n💡 CID đã lưu vào: {cid_file}")
    print(f"   Dùng CID này cho Lesson 8 (off-chain code)")


if __name__ == "__main__":
    main()
