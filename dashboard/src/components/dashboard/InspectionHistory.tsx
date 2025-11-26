import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface InspectionRecord {
  date: string;
  score: number;
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  completenessRate: number;
  validityRate: number;
}

interface InspectionHistoryProps {
  history: InspectionRecord[];
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  onPeriodChange?: (period: 'daily' | 'weekly' | 'monthly' | 'custom', startDate?: string, endDate?: string) => void;
}

// 공통 버튼 스타일 정의 - 사용자 활동 추이와 동일한 스타일
const buttonBaseStyle: React.CSSProperties = {
  padding: '2px 6px',
  border: '1px solid #ccc',
  borderRadius: '3px',
  backgroundColor: 'white',
  color: '#333',
  cursor: 'pointer',
  fontSize: '10px',
  transition: 'all 0.2s ease',
  marginLeft: '2px',
  position: 'relative',
  zIndex: 1001,
  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
};

// 활성화된 버튼에 적용할 스타일
const activeButtonStyle: React.CSSProperties = {
  ...buttonBaseStyle,
  background: '#007bff',
  color: 'white',
  border: '1px solid #007bff',
  fontWeight: 'bold',
  boxShadow: '0 2px 4px rgba(0,123,255,0.3)'
};

const InspectionHistory: React.FC<InspectionHistoryProps> = ({ history, currentPage, onPeriodChange }) => {
  const [timePeriod, setTimePeriod] = useState<'daily' | 'weekly' | 'monthly' | 'custom'>('daily');
  const [customDateRange, setCustomDateRange] = useState({
    startDate: '',
    endDate: ''
  });
  const [showDatePicker, setShowDatePicker] = useState(false);

  // 오늘 날짜 기본값 설정
  const getTodayString = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const getWeekAgoString = () => {
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return weekAgo.toISOString().split('T')[0];
  };

  // 기간 변경 핸들러
  const handlePeriodChange = (period: 'daily' | 'weekly' | 'monthly' | 'custom') => {
    setTimePeriod(period);
    if (period !== 'custom' && onPeriodChange) {
      onPeriodChange(period);
    }
  };

  // 사용자 정의 날짜 범위 적용
  const applyCustomDateRange = () => {
    if (customDateRange.startDate && customDateRange.endDate) {
      setTimePeriod('custom');
      setShowDatePicker(false);
      if (onPeriodChange) {
        onPeriodChange('custom', customDateRange.startDate, customDateRange.endDate);
      }
    } else {
      alert('시작 날짜와 종료 날짜를 모두 선택해주세요.');
    }
  };
  const data = {
    labels: history.map(h => h.date),
    datasets: [
      {
        label: '전체 품질 점수 (%)',
        data: history.map(h => h.score),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: '완전성 검사 (%)',
        data: history.map(h => h.completenessRate),
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: false,
        tension: 0.4
      },
      {
        label: '유효성 검사 (%)',
        data: history.map(h => h.validityRate),
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: false,
        tension: 0.4
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20
        }
      },
      tooltip: {
        callbacks: {
          afterLabel: function(context: any) {
            const index = context.dataIndex;
            const record = history[index];
            return [
              `총 검사: ${record.totalChecks}개`,
              `통과: ${record.passedChecks}개`,
              `실패: ${record.failedChecks}개`
            ];
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value: any) {
            return value + '%';
          }
        }
      }
    }
  };

  const latestRecord = history[history.length - 1]; // 가장 최근 검사 (배열의 마지막 요소)
  const previousRecord = history[history.length - 2]; // 이전 검사 (배열의 마지막에서 두 번째 요소)
  const scoreChange = latestRecord && previousRecord ? latestRecord.score - previousRecord.score : 0;

  return (
    <div className="h-full p-4 bg-gray-50" style={{ position: 'relative', overflow: 'visible' }}>
      <h3 className="text-lg font-bold text-center text-gray-800 mb-4">
        검사 히스토리 추이
      </h3>
      
      {/* 기간 선택 버튼들 - 오른쪽 위에 작게 배치 */}
      <div style={{ 
        position: 'absolute',
        top: '8px',
        right: '8px',
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        gap: '2px'
      }}>
        <button
          onClick={() => handlePeriodChange('daily')}
          style={timePeriod === 'daily' ? activeButtonStyle : buttonBaseStyle}
        >
          일간
        </button>
        <button
          onClick={() => handlePeriodChange('weekly')}
          style={timePeriod === 'weekly' ? activeButtonStyle : buttonBaseStyle}
        >
          주간
        </button>
        <button
          onClick={() => handlePeriodChange('monthly')}
          style={timePeriod === 'monthly' ? activeButtonStyle : buttonBaseStyle}
        >
          월간
        </button>
        <button
          onClick={() => setShowDatePicker(!showDatePicker)}
          style={timePeriod === 'custom' ? activeButtonStyle : buttonBaseStyle}
        >
          사용자 설정
        </button>
      </div>

      {/* 사용자 정의 날짜 선택기 */}
      {showDatePicker && (
        <div style={{
          position: 'absolute',
          top: '40px',
          right: '8px',
          background: 'white',
          border: '1px solid #ccc',
          borderRadius: '8px',
          padding: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          zIndex: 10000,
          minWidth: '280px'
        }}>
          <div style={{ marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>
            날짜 범위 선택
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div>
              <label style={{ fontSize: '12px', color: '#666', display: 'block', marginBottom: '4px' }}>
                시작 날짜:
              </label>
              <input
                type="date"
                value={customDateRange.startDate || getWeekAgoString()}
                onChange={(e) => setCustomDateRange(prev => ({ ...prev, startDate: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '4px 8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '12px'
                }}
              />
            </div>
            
            <div>
              <label style={{ fontSize: '12px', color: '#666', display: 'block', marginBottom: '4px' }}>
                종료 날짜:
              </label>
              <input
                type="date"
                value={customDateRange.endDate || getTodayString()}
                onChange={(e) => setCustomDateRange(prev => ({ ...prev, endDate: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '4px 8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '12px'
                }}
              />
            </div>
            
            <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
              <button
                onClick={applyCustomDateRange}
                style={{
                  ...buttonBaseStyle,
                  background: '#28a745',
                  color: 'white',
                  border: '1px solid #28a745',
                  flex: 1
                }}
              >
                적용
              </button>
              <button
                onClick={() => setShowDatePicker(false)}
                style={{
                  ...buttonBaseStyle,
                  background: '#6c757d',
                  color: 'white',
                  border: '1px solid #6c757d',
                  flex: 1
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* 최신 결과 요약 */}
      {latestRecord && (
        <div className="mb-4 grid grid-cols-2 gap-4">
          <div className="bg-white p-3 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600">현재 품질 점수</div>
                <div className="text-2xl font-bold text-blue-600">
                  {latestRecord.score.toFixed(1)}%
                </div>
              </div>
              <div className={`text-sm font-semibold ${
                scoreChange > 0 ? 'text-green-600' : 
                scoreChange < 0 ? 'text-red-600' : 'text-gray-600'
              }`}>
                {scoreChange > 0 ? '↗' : scoreChange < 0 ? '↘' : '→'} 
                {Math.abs(scoreChange).toFixed(1)}%
              </div>
            </div>
          </div>
          <div className="bg-white p-3 rounded-lg shadow">
            <div className="text-sm text-gray-600">최근 검사</div>
            <div className="text-lg font-semibold text-gray-800">
              {latestRecord.date}
            </div>
            <div className="text-sm text-gray-500">
              {latestRecord.passedChecks}/{latestRecord.totalChecks} 통과
            </div>
          </div>
        </div>
      )}

      {/* 라인 차트 */}
      <div className="h-64 mb-4">
        <Line data={data} options={options} />
      </div>

      {/* 검사 기록 테이블 */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-4 py-3 bg-gray-50 border-b">
          <h4 className="font-semibold text-gray-800">최근 검사 기록</h4>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                  날짜
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                  통과율
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                  완전성
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                  유효성
                </th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                  양호/총계
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history.slice(-5).reverse().map((record, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 text-center">
                    {record.date}
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-center">
                    <span className={`font-semibold ${
                      record.score >= 90 ? 'text-green-600' : 
                      record.score >= 70 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {record.score.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500 text-center">
                    {record.completenessRate.toFixed(1)}%
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500 text-center">
                    {record.validityRate.toFixed(1)}%
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500 text-center">
                    {record.passedChecks}/{record.totalChecks}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default InspectionHistory;
