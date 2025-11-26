import React, { useState, useEffect } from 'react';
import { fetchDataQualityStatus } from '../../services/apiService';

interface Alert {
  id: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  timestamp: string;
}

const KeyAlerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const data = await fetchDataQualityStatus();
        setAlerts(data.alerts || []);
      } catch (error) {
        console.error('알림 데이터 로드 실패:', error);
        setAlerts([]);
      } finally {
        setLoading(false);
      }
    };

    loadAlerts();
  }, []);

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error':
        return '🔴';
      case 'warning':
        return '🟡';
      case 'info':
        return '🔵';
      default:
        return '🔔';
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'error':
        return 'border-l-red-500 bg-red-50';
      case 'warning':
        return 'border-l-yellow-500 bg-yellow-50';
      case 'info':
        return 'border-l-blue-500 bg-blue-50';
      default:
        return 'border-l-gray-500 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 h-full">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-2">🔔</span>
          <h3 className="text-lg font-semibold text-gray-800">주요 알림</h3>
        </div>
        <div className="text-gray-500 text-sm text-center py-8">
          로딩 중...
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4 h-full">
      <div className="flex items-center mb-4">
        <span className="text-2xl mr-2">🔔</span>
        <h3 className="text-lg font-semibold text-gray-800">주요 알림</h3>
      </div>
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {alerts.length > 0 ? (
          alerts.slice(0, 5).map((alert) => (
            <div key={alert.id} className={`p-3 rounded border-l-4 ${getAlertColor(alert.type)}`}>
              <div className="flex items-start">
                <span className="text-lg mr-2">{getAlertIcon(alert.type)}</span>
                <div className="flex-1">
                  <div className="text-sm text-gray-800">{alert.message}</div>
                  <div className="text-xs text-gray-500 mt-1">{alert.timestamp}</div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-gray-500 text-sm text-center py-8">
            현재 알림이 없습니다
          </div>
        )}
      </div>
    </div>
  );
};

export default KeyAlerts;
