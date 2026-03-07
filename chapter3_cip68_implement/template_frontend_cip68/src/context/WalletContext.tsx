'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { CardanoWalletAPI, CardanoWindow, SUPPORTED_WALLETS, WalletInfo } from '@/types/cardano';

interface WalletContextType {
  connected: boolean;
  connecting: boolean;
  walletName: string | null;
  walletAddress: string | null;
  walletApi: CardanoWalletAPI | null;
  error: string | null;
  connect: (walletId: keyof CardanoWindow) => Promise<void>;
  disconnect: () => void;
  getAvailableWallets: () => WalletInfo[];
  signTx: (txCbor: string, partialSign?: boolean) => Promise<string>;
}

const WalletContext = createContext<WalletContextType | null>(null);

export function useWallet() {
  const context = useContext(WalletContext);
  if (!context) {
    throw new Error('useWallet must be used within a WalletProvider');
  }
  return context;
}

export function WalletProvider({ children }: { children: ReactNode }) {
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [walletName, setWalletName] = useState<string | null>(null);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [walletApi, setWalletApi] = useState<CardanoWalletAPI | null>(null);
  const [error, setError] = useState<string | null>(null);

  /**
   * TODO 1: Implement getAvailableWallets
   * ====================================
   * Mục tiêu: Quét window.cardano tìm các ví đã cài đặt
   * 
   * Hướng dẫn:
   * 1. Check typeof window === 'undefined' → return []
   * 2. Check !window.cardano → return []
   * 3. Map qua SUPPORTED_WALLETS
   * 4. Với mỗi wallet, check window.cardano?.[wallet.id] có tồn tại không
   * 5. Return array wallets với property available: true/false
   * 6. Filter chỉ giữ các wallet available
   */

  const getAvailableWallets = useCallback((): WalletInfo[] => {
    // TODO: Implement logic here
    if(typeof window === 'undefined'||!window.cardano) {
    return [];
    }
    return SUPPORTED_WALLETS.map((wallet) => {
      const isAvailable = Boolean(window.cardano?.[wallet.id]);
      return {
        ...wallet,
        available: isAvailable,
      };
    }).filter(wallet => wallet.available);
  }, []);

  /**
   * TODO 2: Implement getAddress helper
   * ===================================
   * Mục tiêu: Lấy address từ wallet API (ưu tiên used → unused → change)
   * 
   * Hướng dẫn:
   * 1. Gọi api.getUsedAddresses() → nếu có addresses[0], return nó
   * 2. Nếu không, gọi api.getUnusedAddresses() → nếu có, return addresses[0]
   * 3. Nếu không, gọi api.getChangeAddress() và return
   */
  /**
   theo chuẩn CIP30 có 3 loại address:
  **Used addresses** — đã từng giao dịch (ưu tiên nhất)
  **Unused addresses** — chưa dùng (fallback)
  **Change address** — nhận tiền thừa (last resort)
  
   */
  const getAddress = async (api: CardanoWalletAPI): Promise<string> => {
    // TODO: Implement logic here
    const addresses = await api.getUsedAddresses();
    if(addresses && addresses.length > 0) {
      return addresses[0];
    }
    const unusedAddresses = await api.getUnusedAddresses();
    if(unusedAddresses && unusedAddresses.length > 0) {
      return unusedAddresses[0];
    }
    const changeAddress = await api.getChangeAddress();
    return changeAddress;
  };

  /**
   * TODO 3: Implement connect function
   * ==================================
   * Mục tiêu: Kết nối với ví Cardano qua CIP-30
   * 
   * Hướng dẫn:
   * 1. Check window và window.cardano tồn tại, nếu không → setError và return
   * 2. Lấy wallet object: window.cardano[walletId]
   * 3. Nếu wallet không tồn tại → setError và return
   * 4. setConnecting(true), setError(null)
   * 5. Try-catch:
   *    - Gọi wallet.enable() để lấy API
   *    - Gọi getAddress(api) để lấy address hex
   *    - setWalletApi(api)
   *    - setWalletName(wallet.name)
   *    - setWalletAddress(addressHex)
   *    - setConnected(true)
   *    - localStorage.setItem('connectedWallet', walletId)
   * 6. Catch error → setError
   * 7. Finally → setConnecting(false)
   */
  const connect = useCallback(async (walletId: keyof CardanoWindow) => {
    // TODO: Implement logic here
     if (typeof window === 'undefined' || !window.cardano){
    setError('Cardano wallet not found.');
    return;}

    const wallet = window.cardano[walletId];
    if (!wallet) {
    setError(`${walletId} wallet not found.`);
    return;
  }
    setConnecting(true);
    setError(null);
    try {
      const api = await wallet.enable();
      const addressHex = await getAddress(api);
      setWalletApi(api);
      setWalletName(wallet.name);
      setWalletAddress(addressHex);
      setConnected(true);
      localStorage.setItem('connectedWallet', walletId);
    } catch (err: any) {
       setError(err.message || 'Failed to connect wallet');
    } finally {
      setConnecting(false);
  }
  }, []);

  /**
   * TODO 4: Implement disconnect function
   * =====================================
   * Mục tiêu: Ngắt kết nối ví và xóa state
   * 
   * Hướng dẫn:
   * 1. setWalletApi(null)
   * 2. setWalletName(null)
   * 3. setWalletAddress(null)
   * 4. setConnected(false)
   * 5. setError(null)
   * 6. localStorage.removeItem('connectedWallet')
   */
  const disconnect = useCallback(() => {
    // TODO: Implement logic here
    setWalletApi(null);
    setWalletName(null);
    setWalletAddress(null);
    setConnected(false);
    setError(null);
    localStorage.removeItem('connectedWallet');
  }, []);

  /**
   * TODO 5: Implement signTx function
   * =================================
   * Mục tiêu: Ký transaction bằng wallet
   * 
   * Hướng dẫn:
   * 1. Check walletApi, nếu null → throw Error('Wallet not connected')
   * 2. Try-catch:
   *    - Gọi walletApi.signTx(txCbor, partialSign)
   *    - Return witness set CBOR
   * 3. Catch error → throw Error với message
   */
  const signTx = useCallback(async (txCbor: string, partialSign = false): Promise<string> => {
    // TODO: Implement logic here
    if (!walletApi) throw new Error('Wallet not connected');
    try {
      return await walletApi.signTx(txCbor, partialSign); 
    } catch (err: any) {
     throw new Error(err.message || 'Failed to sign transaction');
  }
  }, [walletApi]);

  /**
   * TODO 6: Implement auto-reconnect effect
   * =======================================
   * Mục tiêu: Tự động kết nối lại ví đã lưu khi reload trang
   * 
   * Hướng dẫn:
   * 1. Dùng React.useEffect
   * 2. Lấy savedWallet từ localStorage.getItem('connectedWallet')
   * 3. Nếu có savedWallet và window.cardano?.[savedWallet] tồn tại
   * 4. Gọi connect(savedWallet)
   * 5. Dependency array: [connect]
   */
  // TODO: Implement auto-reconnect effect here
  React.useEffect(() => {
  const savedWallet = localStorage.getItem('connectedWallet') as keyof CardanoWindow | null;
  if (savedWallet && typeof window !== 'undefined' && window.cardano?.[savedWallet]) {
    connect(savedWallet);
  }
}, [connect]);

  return (
    <WalletContext.Provider value={{
      connected, connecting, walletName, walletAddress, walletApi, error,
      connect, disconnect, getAvailableWallets, signTx,
    }}>
      {children}
    </WalletContext.Provider>
  );
}
