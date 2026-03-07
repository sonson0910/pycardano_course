'use client';

import { useState } from 'react';
import { useWallet } from '@/context/WalletContext';
import { CardanoWindow } from '@/types/cardano';

/**
 * WalletConnect Component
 * =======================
 * UI để kết nối/ngắt kết nối ví Cardano
 * 
 * PHẦN ĐÃ HOÀN THIỆN:
 * - UI hiển thị trạng thái connected/disconnected
 * - Dropdown chọn ví
 * - Format address
 * 
 * CẦN BỔ SUNG:
 * - Logic xử lý kết nối ví (handleConnect)
 */
export default function WalletConnect() {
  const { connected, connecting, walletName, walletAddress, error,
    connect, disconnect, getAvailableWallets } = useWallet();
  const [showDropdown, setShowDropdown] = useState(false);

  const availableWallets = getAvailableWallets();

  /**
   * TODO 7: Implement handleConnect
   * ===============================
   * Mục tiêu: Xử lý khi user click chọn ví trong dropdown
   * 
   * Hướng dẫn:
   * 1. Gọi await connect(walletId)
   * 2. setShowDropdown(false) để đóng dropdown
   */
  const handleConnect = async (walletId: keyof CardanoWindow) => {
    // TODO: Implement logic here
     await connect(walletId);
     setShowDropdown(false);
  };

  const formatAddress = (address: string): string => {
    if (address.length <= 20) return address;
    return `${address.slice(0, 8)}...${address.slice(-8)}`;
  };

  // UI khi đã kết nối
  if (connected) {
    return (
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 bg-green-100 text-green-800 px-4 py-2 rounded-lg">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          <span className="font-medium">{walletName}</span>
          {walletAddress && (
            <span className="text-xs text-green-600 hidden sm:inline">
              ({formatAddress(walletAddress)})
            </span>
          )}
        </div>
        <button
          onClick={disconnect}
          className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors text-sm font-medium"
        >
          Ngắt kết nối
        </button>
      </div>
    );
  }

  // UI khi chưa kết nối
  return (
    <div className="relative">
      {availableWallets.length === 0 ? (
        <div className="px-4 py-2 bg-yellow-100 text-yellow-800 rounded-lg text-sm">
          Không tìm thấy ví Cardano. Vui lòng cài đặt Nami, Eternl, hoặc Lace.
        </div>
      ) : (
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            disabled={connecting}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2
              ${connecting ? 'bg-gray-300 text-gray-500 cursor-wait' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
          >
            {connecting ? (
              <>
                <span className="animate-spin">⏳</span>
                Đang kết nối...
              </>
            ) : (
              <>
                <span>🔗</span>
                Kết nối ví
              </>
            )}
          </button>
          
          {showDropdown && !connecting && (
            <div className="absolute top-full left-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-[200px]">
              {availableWallets.map(wallet => (
                <button
                  key={wallet.id}
                  onClick={() => handleConnect(wallet.id)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-100 flex items-center gap-3 first:rounded-t-lg last:rounded-b-lg transition-colors"
                >
                  <span className="text-xl">{wallet.icon}</span>
                  <span className="font-medium text-gray-800">{wallet.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
      
      {showDropdown && (
        <div className="fixed inset-0 z-40" onClick={() => setShowDropdown(false)} />
      )}
      
      {error && (
        <div className="absolute top-full left-0 mt-2 px-4 py-2 bg-red-100 text-red-800 rounded-lg text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
