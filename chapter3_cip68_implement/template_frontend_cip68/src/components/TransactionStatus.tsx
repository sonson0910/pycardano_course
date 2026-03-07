'use client';

interface TransactionStatusProps {
  status: {
    status: 'idle' | 'building' | 'signing' | 'submitting' | 'success' | 'error';
    message?: string;
    txHash?: string;
  };
}

/**
 * TransactionStatus Component
 * ===========================
 * Hiển thị trạng thái transaction - HOÀN CHỈNH, không cần chỉnh sửa.
 */
export default function TransactionStatus({ status }: TransactionStatusProps) {
  if (status.status === 'idle') return null;

  const getStatusConfig = () => {
    switch (status.status) {
      case 'building':
        return {
          icon: '🔧',
          color: 'bg-blue-100 text-blue-800 border-blue-300',
          title: 'Đang xây dựng transaction...',
        };
      case 'signing':
        return {
          icon: '✍️',
          color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
          title: 'Chờ ký transaction...',
        };
      case 'submitting':
        return {
          icon: '📤',
          color: 'bg-purple-100 text-purple-800 border-purple-300',
          title: 'Đang gửi lên blockchain...',
        };
      case 'success':
        return {
          icon: '✅',
          color: 'bg-green-100 text-green-800 border-green-300',
          title: 'Thành công!',
        };
      case 'error':
        return {
          icon: '❌',
          color: 'bg-red-100 text-red-800 border-red-300',
          title: 'Lỗi',
        };
      default:
        return {
          icon: '⏳',
          color: 'bg-gray-100 text-gray-800 border-gray-300',
          title: 'Đang xử lý...',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={`p-4 rounded-lg border-2 ${config.color}`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl">{config.icon}</span>
        <div className="flex-1">
          <h3 className="font-semibold mb-1">{config.title}</h3>
          {status.message && (
            <p className="text-sm opacity-90">{status.message}</p>
          )}
          {status.txHash && (
            <a
              href={`https://preprod.cardanoscan.io/transaction/${status.txHash}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm underline hover:opacity-80 mt-2 inline-block"
            >
              Xem transaction trên CardanoScan →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
