import React, { useState, useEffect } from 'react';
import { mqttDataService } from '../../services/mqttDataService';

interface RecentInspection {
  inspection_id: string;
  table_name: string;
  data_source: string;
  total_rows: number;
  total_columns: number;
  inspection_status: string;
  start_time: string;
  end_time: string;
  processing_time_ms: number;
  pass_rate: number;
  data_quality_score: number;
}

const MqttRealtimeMonitor: React.FC = () => {
  const [recentInspections, setRecentInspections] = useState<RecentInspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // 안전한 데이터 검증 함수
  const validateInspectionData = (data: any[]): RecentInspection[] => {
    if (!Array.isArray(data)) return [];
    
    return data.filter(item => item && typeof item === 'object').map(item => ({
      inspection_id: item.inspection_id || `insp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      table_name: item.table_name || 'Unknown',
      data_source: item.data_source || 'Unknown',
      total_rows: item.total_rows || 0,
      total_columns: item.total_columns || 0,
      inspection_status: item.inspection_status || 'Unknown',
      start_time: item.start_time || new Date().toISOString(),
      end_time: item.end_time || new Date().toISOString(),
      processing_time_ms: item.processing_time_ms || 0,
      pass_rate: item.pass_rate || 0,
      data_quality_score: item.data_quality_score || 0
    }));
  };

  useEffect(() => {
    fetchRecentData();
    
    // 실시간 업데이트 시작
    const cleanup = mqttDataService.startRealtimeUpdates((data) => {
      const validatedData = validateInspectionData(data);
      setRecentInspections(validatedData);
      setLastUpdate(new Date());
    }, 3000); // 3초마다 업데이트

    return cleanup;
  }, []);

  const fetchRecentData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await mqttDataService.getRecentInspections(8);
      const validatedData = validateInspectionData(data);
      setRecentInspections(validatedData);
      setLastUpdate(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : '데이터를 가져오는데 실패했습니다.');
      // 에러 발생 시 빈 배열로 설정
      setRecentInspections([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-blue-600 bg-blue-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatTime = (timeString: string) => {
    if (!timeString) return '-';
    const date = new Date(timeString);
    return date.toLocaleString('ko-KR', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading && recentInspections.length === 0) {
    return <div className="flex items-center justify-center h-full">로딩 중...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center">오류: {error}</div>;
  }

  return (
    <div className="dash mqtt-realtime-monitor" style={{ 
      background: 'transparent', 
      padding: '15px',
      height: '100%',
      position: 'relative'
    }}>
      <div className="flex justify-between items-center mb-4">
        <h2 style={{ color: '#333', fontSize: '18px', fontWeight: 'bold' }}>
          실시간 MQTT 데이터 모니터링
        </h2>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-gray-600">
            마지막 업데이트: {lastUpdate.toLocaleTimeString('ko-KR')}
          </span>
        </div>
      </div>

      {/* 새로고침 버튼 */}
      <button
        onClick={fetchRecentData}
        className="absolute top-5 right-5 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-xs transition-colors"
      >
        새로고침
      </button>

      {/* 실시간 데이터 테이블 */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden" style={{ height: 'calc(100% - 60px)' }}>
        <div className="overflow-x-auto h-full">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  검사 ID
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  소스
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  상태
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  품질점수
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  데이터
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  처리시간
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  시작시간
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentInspections.map((inspection, index) => (
                <tr key={inspection.inspection_id || `inspection-${index}`} className="hover:bg-gray-50">
                  <td className="px-3 py-2">
                    <div className="text-xs font-mono text-gray-900">
                      {inspection.inspection_id ? `${inspection.inspection_id.slice(-8)}...` : 'N/A'}
                    </div>
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex items-center">
                      <span className="text-xs font-medium text-gray-900">
                        {inspection.data_source || 'Unknown'}
                      </span>
                      <span className="ml-1 text-xs text-gray-500">
                        ({inspection.table_name || 'N/A'})
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-2">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(inspection.inspection_status)}`}>
                      {inspection.inspection_status || 'Unknown'}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex items-center">
                      <span className={`text-xs font-bold ${getQualityColor(inspection.data_quality_score || 0)}`}>
                        {inspection.data_quality_score || 0}
                      </span>
                      <span className="ml-1 text-xs text-gray-500">
                        ({inspection.pass_rate || 0}%)
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-2">
                    <div className="text-xs text-gray-900">
                      {inspection.total_rows ? inspection.total_rows.toLocaleString() : 0}행 × {inspection.total_columns || 0}열
                    </div>
                  </td>
                  <td className="px-3 py-2">
                    <span className="text-xs text-gray-900">
                      {inspection.processing_time_ms ? inspection.processing_time_ms.toFixed(0) : 0}ms
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <span className="text-xs text-gray-500">
                      {formatTime(inspection.start_time)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 데이터가 없을 때 */}
      {recentInspections.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          아직 MQTT 데이터가 수집되지 않았습니다.
          <br />
          <span className="text-sm">API 호출 후 데이터가 여기에 표시됩니다.</span>
        </div>
      )}
    </div>
  );
};

export default MqttRealtimeMonitor;
