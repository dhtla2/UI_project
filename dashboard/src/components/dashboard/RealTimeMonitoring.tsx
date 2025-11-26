import React, { useState, useEffect } from 'react';
import { fetchDataQualityStatus, DataQualityStatusData, TOSDataQualityStatusData } from '../../services/apiService';

interface DataQualityStatusProps {
  status?: TOSDataQualityStatusData | DataQualityStatusData | null;
  alerts?: Array<{
    id: string;
    type: 'error' | 'warning' | 'info';
    message: string;
    timestamp: string;
  }>;
}

const DataQualityStatus: React.FC<DataQualityStatusProps> = ({ status: propStatus, alerts: propAlerts }) => {
  const [status, setStatus] = useState<DataQualityStatusData | TOSDataQualityStatusData | null>(propStatus || null);
  const [loading, setLoading] = useState(!propStatus);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // props로 데이터가 전달된 경우 내부 로딩을 하지 않음
    if (propStatus) {
      setStatus(propStatus);
      setLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchDataQualityStatus();
        setStatus(data);
      } catch (err) {
        console.error('데이터 품질 상태 로드 실패:', err);
        setError('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [propStatus]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PASS':
        return 'text-green-600 bg-green-100';
      case 'WARNING':
        return 'text-yellow-600 bg-yellow-100';
      case 'FAIL':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PASS':
        return '✅';
      case 'WARNING':
        return '⚠️';
      case 'FAIL':
        return '❌';
      default:
        return '❓';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error':
        return '🔴';
      case 'warning':
        return '🟡';
      case 'info':
        return '🔵';
      default:
        return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="h-full p-4 bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">로딩 중...</div>
      </div>
    );
  }

  if (error || !status) {
    return (
      <div className="h-full p-4 bg-gray-50 flex items-center justify-center">
        <div className="text-red-500 text-sm">{error || '데이터를 불러올 수 없습니다.'}</div>
      </div>
    );
  }

  return (
    <div className="h-full p-4 bg-gray-50">
      <h3 className="text-lg font-bold text-center text-gray-800 mb-4">
        데이터 품질 상태
      </h3>

      {/* 상태 카드들 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">완전성</span>
            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(status.completeness.status)}`}>
              {getStatusIcon(status.completeness.status)} {status.completeness.status}
            </span>
          </div>
          <div className="text-2xl font-bold text-blue-600">
            {status.completeness.rate.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">
            {status.completeness.lastCheck}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">유효성</span>
            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(status.validity.status)}`}>
              {getStatusIcon(status.validity.status)} {status.validity.status}
            </span>
          </div>
          <div className="text-2xl font-bold text-purple-600">
            {status.validity.rate.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">
            {status.validity.lastCheck}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">전체</span>
            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(status.overall.status)}`}>
              {getStatusIcon(status.overall.status)} {status.overall.status}
            </span>
          </div>
          <div className="text-2xl font-bold text-green-600">
            {status.overall.score.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">
            {status.overall.lastUpdate}
          </div>
        </div>
      </div>

      {/* 알림 섹션 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-4 py-3 bg-gray-50 border-b">
          <h4 className="font-semibold text-gray-800">검사 결과 알림</h4>
        </div>
        <div className="max-h-48 overflow-y-auto">
          {(propAlerts || status.alerts || []).map((alert) => (
            <div key={alert.id} className="p-3 border-b border-gray-100 hover:bg-gray-50">
              <div className="flex items-start">
                <div className="text-lg mr-3">{getAlertIcon(alert.type)}</div>
                <div className="flex-1">
                  <div className="text-sm text-gray-800">{alert.message}</div>
                  <div className="text-xs text-gray-500 mt-1">{alert.timestamp}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 권장사항 */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
        <div className="flex items-center">
          <div className="text-blue-600 mr-2">💡</div>
          <div>
            <div className="font-semibold text-blue-800">권장사항</div>
            <div className="text-sm text-blue-700">
              GRID 검사 실패는 정상적인 결과입니다. 바다 위 선박 위치는 유효한 데이터입니다.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataQualityStatus;
