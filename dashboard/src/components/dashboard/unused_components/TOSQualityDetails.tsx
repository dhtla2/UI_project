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
import { TOSQualityDetailsData } from '../../services/apiService';

// Chart.js 컴포넌트 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface TOSQualityDetailsProps {
  data?: TOSQualityDetailsData | null;
}

const TOSQualityDetails: React.FC<TOSQualityDetailsProps> = ({ data }) => {
  const tosQualityDetails = data;

  if (!tosQualityDetails) {
    return (
      <div className="h-full p-4 bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">데이터를 불러올 수 없습니다.</div>
      </div>
    );
  }

  // 차트 데이터 준비
  const chartData = {
    labels: tosQualityDetails.completeness.field_groups?.map(item => item.name) || [],
    datasets: [
      {
        label: '완성도 (%)',
        data: tosQualityDetails.completeness.field_groups?.map(item => item.completion_rate) || [],
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
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
        text: 'TOS 필드별 품질 분석',
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
        <h3 className="text-lg font-semibold text-gray-800 mb-2">TOS 품질 상세 분석</h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-white p-3 rounded-lg shadow-sm">
            <div className="text-sm text-gray-600">전체 완성도</div>
            <div className="text-2xl font-bold text-blue-600">
              {tosQualityDetails.completeness.overall_rate?.toFixed(1)}%
            </div>
          </div>
          <div className="bg-white p-3 rounded-lg shadow-sm">
            <div className="text-sm text-gray-600">검사된 필드 수</div>
            <div className="text-2xl font-bold text-green-600">
              {tosQualityDetails.completeness.total_fields || 0}
            </div>
          </div>
        </div>
      </div>

      <div className="h-64">
        <Bar data={chartData} options={options} />
      </div>

      {/* 필드별 상세 정보 */}
      <div className="mt-4">
        <h4 className="text-md font-medium text-gray-700 mb-2">필드별 상세 정보</h4>
        <div className="space-y-2 max-h-32 overflow-y-auto">
          {tosQualityDetails.completeness.field_groups?.map((field, index) => (
            <div key={index} className="flex justify-between items-center bg-white p-2 rounded text-sm">
              <span className="font-medium">{field.name}</span>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs ${
                  field.completion_rate >= 95 ? 'bg-green-100 text-green-800' :
                  field.completion_rate >= 85 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {field.completion_rate.toFixed(1)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TOSQualityDetails;