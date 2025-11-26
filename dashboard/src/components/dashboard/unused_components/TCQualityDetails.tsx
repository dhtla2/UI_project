import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Chart.js 컴포넌트 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface TCQualityDetailsProps {
  historyData?: Array<{
    date: string;
    totalWork: number;
    terminals: number;
    ships: number;
    containers: number;
  }>;
}

const TCQualityDetails: React.FC<TCQualityDetailsProps> = ({ historyData }) => {
  const mockHistoryData = historyData || [
    { date: '2024-09-01', totalWork: 45000, terminals: 1, ships: 12, containers: 3500 },
    { date: '2024-09-02', totalWork: 52000, terminals: 1, ships: 15, containers: 4200 },
    { date: '2024-09-03', totalWork: 48000, terminals: 1, ships: 13, containers: 3800 },
    { date: '2024-09-04', totalWork: 55000, terminals: 1, ships: 16, containers: 4500 },
    { date: '2024-09-05', totalWork: 51000, terminals: 1, ships: 14, containers: 4100 },
    { date: '2024-09-06', totalWork: 47000, terminals: 1, ships: 12, containers: 3700 },
    { date: '2024-09-07', totalWork: 49000, terminals: 1, ships: 13, containers: 3900 }
  ];

  // 실제 DB 검사 결과 기반 데이터 (tc_work_info_inspection_1757565578_f5ef42)
  const tcColumns = [
    // 완전성 100%, 유효성 검사 없음, 사용성 100%
    { name: 'tmnlId', completion_rate: 100.0, validity_rate: 0.0, usage_rate: 100.0 },
    { name: 'shpCd', completion_rate: 100.0, validity_rate: 0.0, usage_rate: 100.0 },
    { name: 'tcNo', completion_rate: 100.0, validity_rate: 0.0, usage_rate: 100.0 },
    { name: 'cntrNo', completion_rate: 100.0, validity_rate: 0.0, usage_rate: 100.0 },
    { name: 'tmnlNm', completion_rate: 100.0, validity_rate: 0.0, usage_rate: 100.0 },
    { name: 'wkId', completion_rate: 100.0, validity_rate: 100.0, usage_rate: 100.0 },
    { name: 'szTp', completion_rate: 100.0, validity_rate: 0.0, usage_rate: 100.0 },
    { name: 'block', completion_rate: 100.0, validity_rate: 0.0, usage_rate: 100.0 },
    { name: 'bay', completion_rate: 100.0, validity_rate: 0.0, usage_rate: 100.0 },
    { name: 'roww', completion_rate: 100.0, validity_rate: 0.0, usage_rate: 100.0 },
    { name: 'wkTime', completion_rate: 100.0, validity_rate: 100.0, usage_rate: 100.0 },
    
    // 완전성 100%, 유효성 100%, 사용성 100%
    { name: 'callYr', completion_rate: 100.0, validity_rate: 100.0, usage_rate: 100.0 },
    { name: 'serNo', completion_rate: 100.0, validity_rate: 100.0, usage_rate: 100.0 },
    
    // 완전성 100%, 유효성 검사 없음, 사용성 99.999% (1개 누락)
    { name: 'shpNm', completion_rate: 100.0, validity_rate: 0.0, usage_rate: 99.999 },
    
    // 완전성 0%, 유효성 검사 없음, 사용성 0% (모든 값이 NULL)
    { name: 'jobNo', completion_rate: 0.0, validity_rate: 0.0, usage_rate: 0.0 },
    { name: 'ytNo', completion_rate: 0.0, validity_rate: 0.0, usage_rate: 0.0 },
    { name: 'rtNo', completion_rate: 0.0, validity_rate: 0.0, usage_rate: 0.0 },
    { name: 'ordTime', completion_rate: 0.0, validity_rate: 0.0, usage_rate: 0.0 },
    { name: 'jobState', completion_rate: 0.0, validity_rate: 0.0, usage_rate: 0.0 },
    { name: 'evntTime', completion_rate: 0.0, validity_rate: 0.0, usage_rate: 0.0 }
  ];

  // 전체 완성도, 유효성, 사용성 계산
  const overallCompletion = tcColumns.reduce((sum, col) => sum + col.completion_rate, 0) / tcColumns.length;
  const validityCheckedColumns = tcColumns.filter(col => col.validity_rate > 0);
  const overallValidity = validityCheckedColumns.length > 0 
    ? validityCheckedColumns.reduce((sum, col) => sum + col.validity_rate, 0) / validityCheckedColumns.length
    : 0;
  const overallUsage = tcColumns.reduce((sum, col) => sum + col.usage_rate, 0) / tcColumns.length;

  // 차트 데이터 준비 (완전성, 유효성, 사용성)
  const chartData = {
    labels: tcColumns.map(item => item.name),
    datasets: [
      {
        label: '완전성 (%)',
        data: tcColumns.map(item => item.completion_rate),
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
      {
        label: '유효성 (%)',
        data: tcColumns.map(item => item.validity_rate > 0 ? item.validity_rate : null),
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1,
      },
      {
        label: '사용성 (%)',
        data: tcColumns.map(item => item.usage_rate),
        backgroundColor: 'rgba(245, 158, 11, 0.5)',
        borderColor: 'rgba(245, 158, 11, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'TC 컬럼별 품질 분석',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
      },
    },
  };

  return (
    <div className="h-full p-4 bg-gray-50">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">TC 품질 상세 분석</h3>
        <div className="grid grid-cols-4 gap-4 mb-4">
          <div className="bg-white p-3 rounded-lg shadow-sm">
            <div className="text-sm text-gray-600">완전성</div>
            <div className="text-2xl font-bold text-blue-600">
              {overallCompletion.toFixed(1)}%
            </div>
          </div>
          <div className="bg-white p-3 rounded-lg shadow-sm">
            <div className="text-sm text-gray-600">유효성</div>
            <div className="text-2xl font-bold text-green-600">
              {overallValidity.toFixed(1)}%
            </div>
          </div>
          <div className="bg-white p-3 rounded-lg shadow-sm">
            <div className="text-sm text-gray-600">사용성</div>
            <div className="text-2xl font-bold text-orange-600">
              {overallUsage.toFixed(1)}%
            </div>
          </div>
          <div className="bg-white p-3 rounded-lg shadow-sm">
            <div className="text-sm text-gray-600">검사된 컬럼</div>
            <div className="text-2xl font-bold text-purple-600">
              {tcColumns.length}개
            </div>
          </div>
        </div>
      </div>

      <div className="h-64">
        <Bar data={chartData} options={options} />
      </div>

      {/* 컬럼별 상세 정보 */}
      <div className="mt-4">
        <h4 className="text-md font-medium text-gray-700 mb-2">컬럼별 상세 정보</h4>
        <div className="space-y-2 max-h-32 overflow-y-auto">
          {tcColumns.map((column, index) => (
            <div key={index} className="flex justify-between items-center bg-white p-2 rounded text-sm">
              <span className="font-medium">{column.name}</span>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs ${
                  column.completion_rate >= 95 ? 'bg-green-100 text-green-800' :
                  column.completion_rate >= 85 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  완전성: {column.completion_rate.toFixed(1)}%
                </span>
                {column.validity_rate > 0 && (
                  <span className={`px-2 py-1 rounded text-xs ${
                    column.validity_rate >= 95 ? 'bg-green-100 text-green-800' :
                    column.validity_rate >= 85 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    유효성: {column.validity_rate.toFixed(1)}%
                  </span>
                )}
                <span className={`px-2 py-1 rounded text-xs ${
                  column.usage_rate >= 95 ? 'bg-green-100 text-green-800' :
                  column.usage_rate >= 85 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  사용성: {column.usage_rate.toFixed(1)}%
                </span>
                <span className="text-gray-400">▼</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TCQualityDetails;
