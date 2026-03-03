'use client';

import { useEffect, useState } from 'react';
import { useWallet } from '@/context/WalletContext';
import WalletConnect from '@/components/WalletConnect';
import MintForm from '@/components/MintForm';
import NFTList from '@/components/NFTList';
import TransactionStatus from '@/components/TransactionStatus';

/**
 * HomeContent Component
 * ====================
 * Trang chính của ứng dụng
 * 
 * PHẦN ĐÃ HOÀN THIỆN:
 * - UI layout
 * - Transaction status display
 * - Connected/disconnected states
 * 
 * CẦN BỔ SUNG:
 * - convertAddress: Convert hex address → bech32
 * - fetchScriptInfo: Lấy policy ID, store address từ backend
 */
export default function HomeContent() {
  const { connected, walletAddress } = useWallet();
  const [bech32Address, setBech32Address] = useState<string>('');
  const [scriptInfo, setScriptInfo] = useState<any>(null);
  const [txStatus, setTxStatus] = useState({ status: 'idle' as const });
  const [refreshNFTList, setRefreshNFTList] = useState(0);

  /**
   * TODO 14: Implement convertAddress function
   * ==========================================
   * Mục tiêu: Convert hex address (từ wallet) sang bech32 (cho backend)
   * 
   * Hướng dẫn:
   * 1. Nếu không có walletAddress → setBech32Address(''), return
   * 2. Try-catch:
   *    - Gọi GET http://localhost:8000/api/convert-address?hex_address=${walletAddress}
   *    - Parse response
   *    - Nếu data.success: setBech32Address(data.bech32_address)
   * 3. Catch error: console.error
   */
  const convertAddress = async () => {
    // TODO: Implement logic here
      if (!walletAddress) {
      setBech32Address('');
      return;
      }
      try {
         const response = await fetch(
      `http://localhost:8000/api/convert-address?hex_address=${walletAddress}`
    );
    const data = await response.json();
     if (data.success) {
      setBech32Address(data.bech32_address);
    }
      }
      catch (error) {
    console.error('Error converting address:', error);
  }


  };

  /**
   * TODO 15: Implement fetchScriptInfo function
   * ===========================================
   * Mục tiêu: Lấy thông tin script (policy ID, store address) từ backend
   * 
   * Hướng dẫn:
   * 1. Try-catch:
   *    - Gọi GET http://localhost:8000/api/script-info
   *    - Parse response
   *    - setScriptInfo(data)
   * 2. Catch error: console.error
   */
  const fetchScriptInfo = async () => {
    // TODO: Implement logic here
    try{
      const response = await fetch('http://localhost:8000/api/script-info');
      const data = await response.json();
      setScriptInfo(data);
    }
    catch (error) {
    console.error('Error fetching script info:', error);
  }

  };

  /**
   * TODO 16: Implement useEffect for initialization
   * ===============================================
   * Mục tiêu: Chạy convert address và fetch script info khi mount
   * 
   * Hướng dẫn:
   * 1. useEffect(() => { convertAddress(); fetchScriptInfo(); }, [walletAddress])
   */
  // TODO: Implement useEffect here
  useEffect(() => {
    convertAddress();
    fetchScriptInfo();
  }, [walletAddress]);

  const handleMintSuccess = () => {
    setRefreshNFTList(prev => prev + 1);
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🎨 CIP-68 Dynamic Asset Demo
          </h1>
          <p className="text-gray-600">
            Mint, Update và Burn NFT với metadata động trên Cardano
          </p>
          {scriptInfo && (
            <div className="mt-4 text-sm text-gray-500">
              <p>Policy ID: <code className="bg-gray-100 px-2 py-1 rounded">{scriptInfo.policy_id}</code></p>
              <p>Network: <span className="font-semibold">{scriptInfo.network}</span></p>
            </div>
          )}
        </div>

        {/* Wallet Connect */}
        <div className="flex justify-center mb-8">
          <WalletConnect />
        </div>

        {/* Main Content */}
        {connected ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column: Mint Form + Status */}
            <div className="lg:col-span-2 space-y-6">
              <div className="card">
                <MintForm
                  walletAddress={bech32Address}
                  setTxStatus={setTxStatus}
                  scriptInfo={scriptInfo}
                  onMintSuccess={handleMintSuccess}
                />
              </div>
              
              <TransactionStatus status={txStatus} />
            </div>

            {/* Right Column: NFT List */}
            <div className="lg:col-span-1">
              <div className="card">
                <NFTList
                  walletAddress={bech32Address}
                  scriptInfo={scriptInfo}
                  setTxStatus={setTxStatus}
                  refreshTrigger={refreshNFTList}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="card text-center">
            <div className="py-12">
              <div className="text-6xl mb-4">🔗</div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                Kết nối ví để bắt đầu
              </h2>
              <p className="text-gray-600">
                Vui lòng kết nối ví Cardano (Nami, Eternl, hoặc Lace) để sử dụng ứng dụng.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
