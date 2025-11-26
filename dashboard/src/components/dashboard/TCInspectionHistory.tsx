import React from 'react';
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

interface TCInspectionRecord {
  date: string;
  score: number;
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  completenessRate: number;
  validityRate: number;
}

interface TCInspectionHistoryData {
  inspectionId: string;
  inspectionDatetime: string;
  totalChecks: number;
  passCount: number;
  failCount: number;
  passRate: number;
  completenessRate?: number;
  validityRate?: number;
}

interface TCInspectionHistoryProps {
  history?: TCInspectionHistoryData[];
}

const TCInspectionHistory: React.FC<TCInspectionHistoryProps> = ({ history }) => {
  // TCInspectionHistoryData를 TCInspectionRecord로 변환
  const convertToTCInspectionRecord = (data: TCInspectionHistoryData): TCInspectionRecord => ({
    date: data.inspectionDatetime,
    score: data.passRate,
    totalChecks: data.totalChecks,
    passedChecks: data.passCount,
    failedChecks: data.totalChecks - data.passCount,
    completenessRate: data.completenessRate || data.passRate,
    validityRate: data.validityRate || 100.0
  });

  // TC 데이터로 변환된 히스토리
  const tcHistory = history && history.length > 0 ? history.map(convertToTCInspectionRecord) : [];

  const data = {
    labels: tcHistory.map(h => h.date),
    datasets: [
      {
        label: '전체 품질 점수 (%)',
        data: tcHistory.map(h => h.score),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: '완전성 검사 (%)',
        data: tcHistory.map(h => h.completenessRate),
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: false,
        tension: 0.4
      },
      {
        label: '유효성 검사 (%)',
        data: tcHistory.map(h => h.validityRate),
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
            const record = tcHistory[index];
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

  const latestRecord = tcHistory[tcHistory.length - 1]; // 가장 최근 검사 (배열의 마지막 요소)
  const previousRecord = tcHistory[tcHistory.length - 2]; // 이전 검사 (배열의 마지막에서 두 번째 요소)
  const scoreChange = latestRecord && previousRecord ? latestRecord.score - previousRecord.score : 0;

  return (
    <div className="h-full p-4 bg-gray-50">
      <h3 className="text-lg font-bold text-center text-gray-800 mb-4">
        검사 히스토리 추이
      </h3>
      
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
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  날짜
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  품질 점수
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  완전성
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  유효성
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  통과/총계
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tcHistory.slice(-5).reverse().map((record, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">
                    {record.date}
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm">
                    <span className={`font-semibold ${
                      record.score >= 90 ? 'text-green-600' : 
                      record.score >= 70 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {record.score.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                    {record.completenessRate.toFixed(1)}%
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                    {record.validityRate.toFixed(1)}%
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
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

export default TCInspectionHistory;
