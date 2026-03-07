'use client';

import { ReactNode, useState, useEffect } from 'react';
import { WalletProvider } from '@/context/WalletContext';

export default function Providers({ children }: { children: ReactNode }) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) return <>{children}</>;

  return <WalletProvider>{children}</WalletProvider>;
}
