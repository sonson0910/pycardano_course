import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from app.blockchain.cardano_client import (
    CardanoClient,
    Register,
    Update,
    Verify,
    Revoke,
)


class TestCardanoClientInitialization:
    """Test CardanoClient initialization"""

    def test_init_without_blockfrost_key(self):
        """Should raise ValueError if BLOCKFROST_PROJECT_ID not set"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="BLOCKFROST_PROJECT_ID"):
                CardanoClient()

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_init_with_valid_blockfrost_key(self, mock_blockfrost):
        """Should initialize successfully with valid API key"""
        mock_client = MagicMock()
        mock_client.health.return_value = {"time": "2024-10-16"}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()
            assert client.client is not None
            mock_blockfrost.assert_called_once()

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_init_connection_failure(self, mock_blockfrost):
        """Should raise exception if connection fails"""
        mock_blockfrost.side_effect = Exception("Connection refused")

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            with pytest.raises(Exception):
                CardanoClient()


class TestWalletOperations:
    """Test wallet loading and operations"""

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    @patch("app.blockchain.cardano_client.PaymentSigningKey.load")
    def test_load_wallet_success(self, mock_load_key, mock_blockfrost):
        """Should load wallet successfully"""
        mock_blockfrost_instance = MagicMock()
        mock_blockfrost.return_value = mock_blockfrost_instance
        mock_blockfrost_instance.health.return_value = {}

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            mock_signing_key = MagicMock()
            mock_load_key.return_value = mock_signing_key

            mock_vk = MagicMock()
            mock_vk.hash.return_value = Mock()

            with patch(
                "app.blockchain.cardano_client.PaymentVerificationKey.from_signing_key",
                return_value=mock_vk,
            ):
                with patch(
                    "app.blockchain.cardano_client.Address",
                    return_value=Mock(spec=["__str__"]),
                ) as mock_address:
                    result = client.load_wallet("test.sk")
                    assert result is not None
                    assert client.signing_key is not None

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_load_wallet_file_not_found(self, mock_blockfrost):
        """Should raise error if signing key file not found"""
        mock_blockfrost_instance = MagicMock()
        mock_blockfrost.return_value = mock_blockfrost_instance
        mock_blockfrost_instance.health.return_value = {}

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            with patch(
                "app.blockchain.cardano_client.PaymentSigningKey.load",
                side_effect=FileNotFoundError("File not found"),
            ):
                with pytest.raises(FileNotFoundError):
                    client.load_wallet("nonexistent.sk")


class TestBalanceOperations:
    """Test balance query operations"""

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_get_balance_success(self, mock_blockfrost):
        """Should retrieve balance successfully"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_client.address.return_value = {"amount": {"coin": "5000000"}}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()
            mock_address = Mock()
            mock_address.__str__ = Mock(return_value="addr_test1...")

            balance = client.get_balance(mock_address)
            assert balance == 5000000

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_get_balance_zero(self, mock_blockfrost):
        """Should handle zero balance"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_client.address.return_value = {"amount": {"coin": "0"}}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()
            mock_address = Mock()
            mock_address.__str__ = Mock(return_value="addr_test1...")

            balance = client.get_balance(mock_address)
            assert balance == 0

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_get_balance_api_error(self, mock_blockfrost):
        """Should raise error if API call fails"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_client.address.side_effect = Exception("API Error")
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()
            mock_address = Mock()
            mock_address.__str__ = Mock(return_value="addr_test1...")

            with pytest.raises(Exception):
                client.get_balance(mock_address)


class TestUTxOOperations:
    """Test UTxO query operations"""

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_get_utxos_success(self, mock_blockfrost):
        """Should retrieve UTxOs successfully"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_client.address_utxos.return_value = [
            {"tx_hash": "abc123", "output_index": 0},
            {"tx_hash": "def456", "output_index": 1},
        ]
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()
            mock_address = Mock()
            mock_address.__str__ = Mock(return_value="addr_test1...")

            utxos = client.get_utxos(mock_address)
            assert len(utxos) == 2
            assert utxos[0]["tx_hash"] == "abc123"

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_get_utxos_empty(self, mock_blockfrost):
        """Should handle empty UTxO list"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_client.address_utxos.return_value = []
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()
            mock_address = Mock()
            mock_address.__str__ = Mock(return_value="addr_test1...")

            utxos = client.get_utxos(mock_address)
            assert utxos == []


class TestTransactionBuilding:
    """Test transaction building"""

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_build_transaction_success(self, mock_blockfrost):
        """Should build transaction with valid parameters"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()
            sender = Mock()
            receiver = Mock()
            sender.__str__ = Mock(return_value="addr_test1_sender")
            receiver.__str__ = Mock(return_value="addr_test1_receiver")

            tx = client.build_transaction(sender, receiver, 2000000)
            assert tx["type"] == "transaction"
            assert tx["amount"] == 2000000

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_build_transaction_zero_amount(self, mock_blockfrost):
        """Should allow zero amount transactions"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()
            sender = Mock()
            receiver = Mock()

            tx = client.build_transaction(sender, receiver, 0)
            assert tx["amount"] == 0


class TestActionValidation:
    """Test action validation"""

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_validate_register_valid(self, mock_blockfrost):
        """Should validate correct Register action"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            datum = Mock()
            datum.did_id = b"did_123"
            datum.face_ipfs_hash = b"QmHash"
            datum.created_at = 1696000000

            action = Register()
            result = client._validate_action(action, datum)
            assert result is True

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_validate_register_empty_did(self, mock_blockfrost):
        """Should reject Register with empty did_id"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            datum = Mock()
            datum.did_id = b""
            datum.face_ipfs_hash = b"QmHash"
            datum.created_at = 1696000000

            action = Register()
            with pytest.raises(ValueError):
                client._validate_action(action, datum)

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_validate_update_always_valid(self, mock_blockfrost):
        """Update should accept any datum"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            datum = Mock()
            datum.did_id = b""
            datum.face_ipfs_hash = b""
            datum.created_at = 0

            action = Update()
            result = client._validate_action(action, datum)
            assert result is True

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_validate_verify_valid(self, mock_blockfrost):
        """Should validate correct Verify action"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            datum = Mock()
            datum.did_id = b"did_123"
            datum.face_ipfs_hash = b"QmHash"

            action = Verify()
            result = client._validate_action(action, datum)
            assert result is True

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_validate_revoke_valid(self, mock_blockfrost):
        """Should validate correct Revoke action"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            datum = Mock()
            datum.did_id = b"did_123"

            action = Revoke()
            result = client._validate_action(action, datum)
            assert result is True


class TestValidatorFileOperations:
    """Test validator file reading"""

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_read_validator_file_not_found(self, mock_blockfrost):
        """Should raise FileNotFoundError if plutus.json not found"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            with patch("os.path.exists", return_value=False):
                with pytest.raises(FileNotFoundError):
                    client.read_validator_from_file()

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_read_validator_file_success(self, mock_blockfrost):
        """Should read validator from plutus.json successfully"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            validator_data = {
                "validators": [
                    {
                        "compiledCode": "code_bytes",
                        "hash": "script_hash_123",
                    }
                ]
            }

            with patch("os.path.exists", return_value=True):
                with patch("builtins.open", MagicMock()) as mock_open:
                    import json

                    mock_open.return_value.__enter__.return_value.read.return_value = (
                        json.dumps(validator_data)
                    )
                    with patch("json.load", return_value=validator_data):
                        result = client.read_validator_from_file()
                        assert result["type"] == "PlutusV3"
                        assert result["script_hash"] == "script_hash_123"


class TestScriptTransactions:
    """Test script transaction building"""

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_build_script_transaction_register(self, mock_blockfrost):
        """Should build script transaction for Register"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            datum = Mock()
            datum.did_id = b"did_123"
            datum.face_ipfs_hash = b"QmHash"
            datum.created_at = 1696000000

            action = Register()
            result = client.build_script_transaction(action, datum)

            assert result["type"] == "script_transaction"
            assert result["action"] == "Register"

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_build_script_transaction_invalid_action(self, mock_blockfrost):
        """Should raise error for invalid Register action"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            datum = Mock()
            datum.did_id = b""
            datum.face_ipfs_hash = b"QmHash"
            datum.created_at = 1696000000

            action = Register()
            with pytest.raises(ValueError):
                client.build_script_transaction(action, datum)


class TestQueryScriptUTxO:
    """Test script UTxO queries"""

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_query_script_utxo_not_found(self, mock_blockfrost):
        """Should return None if UTxO not found"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_client.address_utxos.return_value = []
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            result = client.query_script_utxo("did_123")
            assert result is None

    @patch("app.blockchain.cardano_client.BlockFrostApi")
    def test_query_script_utxo_with_utxos(self, mock_blockfrost):
        """Should handle query when UTxOs exist"""
        mock_client = MagicMock()
        mock_client.health.return_value = {}
        mock_client.address_utxos.return_value = [{"tx_hash": "abc", "output_index": 0}]
        mock_blockfrost.return_value = mock_client

        with patch.dict(os.environ, {"BLOCKFROST_PROJECT_ID": "preview_abc123"}):
            client = CardanoClient()

            result = client.query_script_utxo("did_123")
            # Currently returns None (not fully implemented)
            assert result is None
