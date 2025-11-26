import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { fetchAISChartsData, AISChartsData } from '../../services/apiService';

ChartJS.register(ArcElement, Tooltip, Legend);

const QualityScoreGauge: React.FC = () => {
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

  const score = aisChartsData?.quality_score || 0;
  const total = aisChartsData?.check_type_results.reduce((sum, item) => sum + item.total_checks, 0) || 0;
  const passed = aisChartsData?.check_type_results.reduce((sum, item) => sum + item.pass_count, 0) || 0;
  const failed = total - passed;
  const data = {
    datasets: [{
      data: [score, 100 - score],
      backgroundColor: [
        score >= 90 ? '#22c55e' : score >= 70 ? '#f59e0b' : '#ef4444',
        '#e5e7eb'
      ],
      borderWidth: 0,
      cutout: '75%'
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
        enabled: false
      }
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 90) return 'EXCELLENT';
    if (score >= 70) return 'GOOD';
    return 'NEEDS IMPROVEMENT';
  };

  return (
    <div className="h-full p-3 bg-gray-50">
      <h3 className="text-sm font-bold text-center text-gray-800 mb-3">
        데이터 품질 점수
      </h3>
      
      <div className="flex items-center justify-center gap-4">
        {/* 왼쪽: 도넛 차트 */}
        <div className="relative w-32 h-32">
          <Doughnut data={data} options={options} />
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className={`text-lg font-bold ${getScoreColor(score)}`}>
              {score.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-600">
              {getScoreLabel(score)}
            </div>
          </div>
        </div>

        {/* 오른쪽: 통과/실패 통계 */}
        <div className="flex flex-col gap-2">
          <div className="bg-white p-2 rounded-lg shadow text-center">
            <div className="text-lg font-bold text-green-600">{passed}</div>
            <div className="text-xs text-gray-600">통과</div>
          </div>
          <div className="bg-white p-2 rounded-lg shadow text-center">
            <div className="text-lg font-bold text-red-600">{failed}</div>
            <div className="text-xs text-gray-600">실패</div>
          </div>
        </div>
      </div>

      <div className="mt-3 text-center">
        <div className="text-xs text-gray-600">
          총 {total}개 검사 항목
        </div>
      </div>
    </div>
  );
};

export default QualityScoreGauge;
