import React from 'react';

interface TCDataQualityStatusProps {
  status?: {
    workEfficiency: { status: string; rate: number; lastCheck: string };
    terminalUtilization: { status: string; rate: number; lastCheck: string };
    overall: { status: string; score: number; lastUpdate: string };
    alerts: Array<{ type: string; message: string; timestamp: string }>;
  };
  alerts?: Array<{ type: string; message: string; timestamp: string }>;
}

const TCDataQualityStatus: React.FC<TCDataQualityStatusProps> = ({ status, alerts = [] }) => {
  const mockStatus = status || {
    workEfficiency: { status: 'PASS', rate: 85.2, lastCheck: '2024-09-08 10:30' },
    terminalUtilization: { status: 'PASS', rate: 78.5, lastCheck: '2024-09-08 10:30' },
    overall: { status: 'PASS', score: 81.8, lastUpdate: '2024-09-08 10:30' },
    alerts: []
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PASS': return 'text-green-600 bg-green-100';
      case 'WARNING': return 'text-yellow-600 bg-yellow-100';
      case 'FAIL': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PASS': return '✓';
      case 'WARNING': return '⚠';
      case 'FAIL': return '✗';
      default: return '?';
    }
  };

  return (
    <div className="h-full p-4 bg-white">
      {/* 데이터 품질 상태 */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">데이터 품질 상태</h2>
        
        <div className="grid grid-cols-3 gap-6 mb-6">
          {/* 작업 효율성 */}
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">작업 효율성</h3>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(mockStatus.workEfficiency.status)}`}>
                {getStatusIcon(mockStatus.workEfficiency.status)} {mockStatus.workEfficiency.status}
              </div>
            </div>
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {mockStatus.workEfficiency.rate}%
            </div>
            <div className="text-sm text-gray-500">
              {mockStatus.workEfficiency.lastCheck}
            </div>
          </div>

          {/* 터미널 활용도 */}
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">터미널 활용도</h3>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(mockStatus.terminalUtilization.status)}`}>
                {getStatusIcon(mockStatus.terminalUtilization.status)} {mockStatus.terminalUtilization.status}
              </div>
            </div>
            <div className="text-3xl font-bold text-green-600 mb-2">
              {mockStatus.terminalUtilization.rate}%
            </div>
            <div className="text-sm text-gray-500">
              {mockStatus.terminalUtilization.lastCheck}
            </div>
          </div>

          {/* 전체 점수 */}
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">전체 점수</h3>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(mockStatus.overall.status)}`}>
                {getStatusIcon(mockStatus.overall.status)} {mockStatus.overall.status}
              </div>
            </div>
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {mockStatus.overall.score}%
            </div>
            <div className="text-sm text-gray-500">
              {mockStatus.overall.lastUpdate}
            </div>
          </div>
        </div>
      </div>

      {/* 검사 결과 알림 */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">검사 결과 알림</h3>
        <div className="bg-white p-4 rounded-lg shadow-sm">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center mr-3">
              <span className="text-yellow-600 text-lg">⚠</span>
            </div>
            <div className="flex-1">
              <p className="text-gray-800">
                {mockStatus.workEfficiency.rate < 90 ? 
                  `작업 효율성 검사에서 ${(100 - mockStatus.workEfficiency.rate).toFixed(1)}% 실패했습니다. 일부 데이터 누락이 있습니다.` :
                  `작업 효율성 검사에서 ${mockStatus.workEfficiency.rate}% 통과했습니다.`
                }
              </p>
              <p className="text-sm text-gray-500 mt-1">{mockStatus.workEfficiency.lastCheck}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 권장사항 */}
      <div className="bg-blue-100 p-4 rounded-lg">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-yellow-200 rounded-full flex items-center justify-center mr-3">
            <span className="text-yellow-700 text-lg">💡</span>
          </div>
          <div>
            <h4 className="font-semibold text-gray-800 mb-1">권장사항</h4>
            <p className="text-gray-700 text-sm">
              TC 작업 데이터의 품질을 향상시키기 위해 누락된 데이터를 보완하고, 
              데이터 입력 시 필수 필드의 완전성을 확인해주세요.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TCDataQualityStatus;
