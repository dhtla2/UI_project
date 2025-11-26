import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
import { Pie } from 'react-chartjs-2';
import { fetchAISChartsData, AISChartsData } from '../../services/apiService';

ChartJS.register(ArcElement, Tooltip, Legend);

const GridDistributionChart: React.FC = () => {
  const [aisChartsData, setAisChartsData] = useState<AISChartsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // AIS 차트 데이터 로드
  useEffect(() => {
    const loadAISChartsData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchAISChartsData();
        setAisChartsData(data);
      } catch (err) {
        console.error('AIS 차트 데이터 로드 실패:', err);
        setError('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };
    
    loadAISChartsData();
  }, []);

  if (loading) return <div className="flex items-center justify-center h-full">로딩 중...</div>;
  if (error) return <div className="text-red-500 text-center">오류: {error}</div>;

  const landCount = aisChartsData?.grid_distribution.find(item => item.type === '육지')?.count || 0;
  const seaCount = aisChartsData?.grid_distribution.find(item => item.type === '바다')?.count || 0;
  const total = landCount + seaCount;
  const landPercentage = ((landCount / total) * 100).toFixed(1);
  const seaPercentage = ((seaCount / total) * 100).toFixed(1);

  const data = {
    labels: ['육지 위 선박', '바다 위 선박'],
    datasets: [{
      data: [landCount, seaCount],
      backgroundColor: [
        '#22c55e', // 녹색 - 육지
        '#3b82f6'  // 파란색 - 바다
      ],
      borderColor: [
        '#16a34a',
        '#2563eb'
      ],
      borderWidth: 2
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || '';
            const value = context.parsed;
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value}개 (${percentage}%)`;
          }
        }
      }
    },
    elements: {
      arc: {
        borderWidth: 2
      }
    }
  };

  return (
    <div className="h-full p-3 bg-gray-50">
      <h3 className="text-sm font-bold text-center text-gray-800 mb-3">
        지리적 위치 분포
      </h3>
      
      <div className="flex items-center justify-center gap-4">
        {/* 왼쪽: 파이 차트 */}
        <div className="w-32 h-32">
          <Pie data={data} options={options} />
        </div>

        {/* 오른쪽: 범례 */}
        <div className="flex flex-col gap-2">
          <div className="bg-green-50 p-2 rounded-lg border-l-4 border-green-400">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              <div>
                <div className="text-sm font-semibold text-green-800">육지 위</div>
                <div className="text-xs text-green-600">
                  {landCount}개 ({landPercentage}%)
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-blue-50 p-2 rounded-lg border-l-4 border-blue-400">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
              <div>
                <div className="text-sm font-semibold text-blue-800">바다 위</div>
                <div className="text-xs text-blue-600">
                  {seaCount}개 ({seaPercentage}%)
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-3 p-2 bg-yellow-50 rounded-lg border-l-4 border-yellow-400">
        <div className="flex items-center">
          <div className="text-yellow-600 mr-2 text-sm">ℹ️</div>
          <div className="text-xs text-yellow-800">
            바다 위 선박은 정상적인 위치입니다. 육지 위 선박만 검사 실패로 분류됩니다.
          </div>
        </div>
      </div>
    </div>
  );
};

export default GridDistributionChart;
