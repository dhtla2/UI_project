import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { fetchAISChartsData, AISChartsData } from '../../services/apiService';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface CheckTypeResult {
  type: string;
  total: number;
  passed: number;
  failed: number;
  rate: number;
}

const CheckTypeResults: React.FC = () => {
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

  const results: CheckTypeResult[] = aisChartsData?.check_type_results.map(item => ({
    type: item.type,
    total: item.total_checks,
    passed: item.pass_count,
    failed: item.total_checks - item.pass_count,
    rate: item.pass_rate
  })) || [];
  const data = {
    labels: results.map(r => r.type),
    datasets: [
      {
        label: '통과율 (%)',
        data: results.map(r => r.rate),
        backgroundColor: results.map(r => 
          r.rate >= 90 ? '#22c55e' : 
          r.rate >= 70 ? '#f59e0b' : '#ef4444'
        ),
        borderColor: results.map(r => 
          r.rate >= 90 ? '#16a34a' : 
          r.rate >= 70 ? '#d97706' : '#dc2626'
        ),
        borderWidth: 2
      }
    ]
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
          afterLabel: function(context: any) {
            const index = context.dataIndex;
            const result = results[index];
            return [
              `총 검사: ${result.total}개`,
              `통과: ${result.passed}개`,
              `실패: ${result.failed}개`
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

  return (
    <div className="h-full p-3 bg-gray-50">
      <h3 className="text-sm font-bold text-center text-gray-800 mb-3">
        검사 유형별 통과율
      </h3>
      
      <div className="flex items-center justify-center gap-4">
        {/* 왼쪽: 바 차트 */}
        <div className="w-36 h-36">
          <Bar data={data} options={options} />
        </div>

        {/* 오른쪽: 상세 정보 */}
        <div className="flex flex-col gap-2">
          {results.map((result, index) => (
            <div key={index} className="bg-white p-2 rounded-lg shadow">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-semibold text-gray-800">{result.type}</span>
                <span className={`text-sm font-bold ${
                  result.rate >= 90 ? 'text-green-600' : 
                  result.rate >= 70 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {result.rate.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between text-xs text-gray-600">
                <span>통과: {result.passed}개</span>
                <span>실패: {result.failed}개</span>
                <span>총계: {result.total}개</span>
              </div>
              <div className="mt-1 w-full bg-gray-200 rounded-full h-1.5">
                <div 
                  className={`h-1.5 rounded-full ${
                    result.rate >= 90 ? 'bg-green-500' : 
                    result.rate >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${result.rate}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CheckTypeResults;
