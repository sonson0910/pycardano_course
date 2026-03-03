'use client';

import { useState } from 'react';
import { useWallet } from '@/context/WalletContext';

interface MintFormProps {
  walletAddress: string;
  setTxStatus: (status: any) => void;
  scriptInfo: any;
  onMintSuccess?: () => void;
}

/**
 * MintForm Component
 * ==================
 * Form để mint CIP-68 NFT
 * 
 * PHẦN ĐÃ HOÀN THIỆN:
 * - UI form (input token name, description)
 * - State management
 * - Button loading states
 * 
 * CẦN BỔ SUNG:
 * - Logic 3 bước: build → sign → submit transaction
 */
export default function MintForm({ walletAddress, setTxStatus, scriptInfo, onMintSuccess }: MintFormProps) {
  const { signTx, connected } = useWallet();
  const [tokenName, setTokenName] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  /**
   * TODO 8: Implement handleMint function
   * ====================================
   * Mục tiêu: Xử lý submit form mint NFT (3 bước: build → sign → submit)
   * 
   * Hướng dẫn:
   * 1. Check connected và walletAddress, nếu không → setTxStatus error
   * 2. setIsLoading(true)
   * 3. setTxStatus({ status: 'building', message: 'Đang tạo transaction...' })
   * 
   * 4. BƯỚC 1 - BUILD TRANSACTION:
   *    - Gọi POST http://localhost:8000/api/mint
   *    - Body: { wallet_address: walletAddress, token_name: tokenName, description: description }
   *    - Parse response JSON
   *    - Nếu !data.success → throw Error(data.message)
   * 
   * 5. BƯỚC 2 - SIGN TRANSACTION:
   *    - setTxStatus({ status: 'signing', message: 'Vui lòng ký transaction trong ví...' })
   *    - Gọi await signTx(data.tx_cbor, true) → lấy witnessSet
   * 
   * 6. BƯỚC 3 - SUBMIT TRANSACTION:
   *    - setTxStatus({ status: 'submitting', message: 'Đang gửi transaction...' })
   *    - Gọi POST http://localhost:8000/api/submit
   *    - Body: { tx_cbor: data.tx_cbor, witness_set_cbor: witnessSet }
   *    - Parse response
   *    - Nếu !submitData.success → throw Error
   * 
   * 7. SUCCESS:
   *    - setTxStatus({ status: 'success', message: `...`, txHash: submitData.tx_hash })
   *    - Reset form: setTokenName(''), setDescription('')
   *    - Sau 2s gọi onMintSuccess() để refresh NFT list
   * 
   * 8. CATCH ERROR:
   *    - setTxStatus({ status: 'error', message: error.message })
   * 
   * 9. FINALLY:
   *    - setIsLoading(false)
   */
  const handleMint = async (e: React.FormEvent) => {
        // TODO: Implement logic here
    e.preventDefault();
    if (!connected || !walletAddress) {
    setTxStatus({ status: 'error', message: 'Vui lòng kết nối ví trước!' });
    return;
  }

try {
    setIsLoading(true);
    setTxStatus({ status: 'building', message: 'Đang tạo transaction...' });
     // BƯỚC 1: BUILD TRANSACTION
     const response = await fetch('http://localhost:8000/api/mint', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body :  JSON.stringify({
        wallet_address: walletAddress,
        token_name: tokenName,
        description: description,
      }),
    });
      const data =  await response.json();
      if (!data.success) throw new Error(data.message);
      // BƯỚC 2: SIGN TRANSACTION
      setTxStatus({ status: 'signing', message: 'Vui lòng ký transaction trong ví...' });
       const witnessSet = await signTx(data.tx_cbor, true);
        // BƯỚC 3: SUBMIT TRANSACTION
        setTxStatus({ status: 'submitting', message: 'Đang gửi transaction...' });
      const submitResponse = await fetch('http://localhost:8000/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tx_cbor: data.tx_cbor, witness_set_cbor: witnessSet }),
    });
     const submitData = await submitResponse.json();
    if (!submitData.success) throw new Error(submitData.message);

    // SUCCESS
    setTxStatus({
      status: 'success',
      message: `NFT "${tokenName}" đã được mint thành công!`,
      txHash: submitData.tx_hash,
    });
    setTokenName('');
    setDescription('');
     if (onMintSuccess) {
      setTimeout(() => onMintSuccess(), 2000);
    }
  } catch (error: any) {
    setTxStatus({ status: 'error', message: error.message || 'Lỗi khi mint' });
  } finally {
    setIsLoading(false);
  }

  };

  return (
    <div>
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">🎨 Mint CIP-68 Dynamic NFT</h2>
      <p className="text-gray-600 mb-6">
        Tạo NFT mới với metadata có thể cập nhật. Gồm Reference Token (metadata) và User Token.
      </p>
      <form onSubmit={handleMint} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tên Token
          </label>
          <input
            type="text"
            value={tokenName}
            onChange={(e) => setTokenName(e.target.value)}
            placeholder="MyAwesomeNFT"
            className="input"
            required
            maxLength={32}
            disabled={isLoading}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Mô tả
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Mô tả về NFT..."
            className="input min-h-[100px]"
            required
            maxLength={256}
            disabled={isLoading}
          />
        </div>
        <button
          type="submit"
          className="btn-primary w-full"
          disabled={isLoading || !tokenName || !description}
        >
          {isLoading ? '⏳ Đang xử lý...' : '🚀 Mint NFT'}
        </button>
      </form>
    </div>
  );
}
