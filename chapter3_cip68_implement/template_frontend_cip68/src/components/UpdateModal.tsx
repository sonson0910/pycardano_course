'use client';

import { useState } from 'react';
import { useWallet } from '@/context/WalletContext';
import Modal from './Modal';

interface UpdateModalProps {
  isOpen: boolean;
  onClose: () => void;
  tokenName: string;
  currentDescription: string;
  walletAddress: string;
  setTxStatus: (status: any) => void;
  onUpdateSuccess?: () => void;
}

/**
 * UpdateModal Component
 * ====================
 * Modal để cập nhật metadata CIP-68 NFT
 * 
 * PHẦN ĐÃ HOÀN THIỆN:
 * - UI modal
 * - State management
 * 
 * CẦN BỔ SUNG:
 * - Logic update (3 bước tương tự mint)
 */
export default function UpdateModal({
  isOpen, onClose, tokenName, currentDescription, walletAddress, setTxStatus, onUpdateSuccess
}: UpdateModalProps) {
  const { signTx } = useWallet();
  const [newDescription, setNewDescription] = useState(currentDescription);
  const [isLoading, setIsLoading] = useState(false);

  /**
   * TODO 9: Implement handleUpdate function
   * =======================================
   * Mục tiêu: Cập nhật metadata NFT (tương tự mint - 3 bước)
   * 
   * Hướng dẫn:
   * 1. setIsLoading(true)
   * 2. setTxStatus({ status: 'building', ... })
   * 3. POST /api/update với body: { wallet_address, token_name, new_description }
   * 4. Sign: await signTx(data.tx_cbor, true)
   * 5. Submit: POST /api/submit
   * 6. Success: setTxStatus success, onClose(), sau 2s gọi onUpdateSuccess()
   * 7. Catch error
   * 8. Finally setIsLoading(false)
   */
  const handleUpdate = async (e: React.FormEvent) => {
    // TODO: Implement logic here
    e.preventDefault();
    try {
    setIsLoading(true);
    setTxStatus({ status: 'building', message: 'Đang tạo burn transaction...' });
    const response =await fetch('http://localhost:8000/api/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            wallet_address: walletAddress,
            token_name: tokenName,
            new_description: newDescription,
          }),
        });

    const data = await response.json();
    if (!data.success) throw new Error(data.message);
    setTxStatus({ status: 'signing', message: 'Vui lòng ký transaction...' });

     const witnessSet = await signTx(data.tx_cbor, true);
     
     setTxStatus({ status: 'submitting', message: 'Đang gửi...' });
     const submitResponse = await fetch('http://localhost:8000/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tx_cbor: data.tx_cbor, witness_set_cbor: witnessSet }),
    });
    const submitData = await submitResponse.json();
    if (!submitData.success) throw new Error(submitData.message);
    setTxStatus({ status: 'success', message: 'Metadata đã được cập nhật!', txHash: submitData.tx_hash });
    onClose();
       if (onUpdateSuccess) {
      setTimeout(() => onUpdateSuccess(), 2000);
    }
    }
    catch (error: any) {
    setTxStatus({ status: 'error', message: error.message });
  } finally {
    setIsLoading(false);
  }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="🔄 Cập nhật Metadata">
      <form onSubmit={handleUpdate} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Token: <span className="font-semibold">{tokenName}</span>
          </label>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Mô tả hiện tại
          </label>
          <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
            {currentDescription}
          </p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Mô tả mới
          </label>
          <textarea
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            placeholder="Nhập mô tả mới..."
            className="input min-h-[100px]"
            required
            maxLength={256}
            disabled={isLoading}
          />
        </div>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg transition-colors"
            disabled={isLoading}
          >
            Hủy
          </button>
          <button
            type="submit"
            className="flex-1 btn-primary"
            disabled={isLoading || newDescription === currentDescription}
          >
            {isLoading ? '⏳ Đang cập nhật...' : '🔄 Cập nhật'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
