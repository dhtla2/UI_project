import React, { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { mqttDataService } from '../../services/mqttDataService';

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface QualityMetrics {
  period_days: number;
  total_inspections: number;
  avg_pass_rate: number;
  avg_quality_score: number;
  avg_processing_time_ms: number;
  high_quality_count: number;
  low_quality_count: number;
}

interface DataSourceStats {
  data_source: string;
  inspection_count: number;
  avg_pass_rate: number;
  avg_quality_score: number;
  avg_data_rows: number;
  total_data_rows: number;
}

interface PerformanceTrends {
  date: string;
  inspection_count: number;
  avg_processing_time_ms: number;
  avg_pass_rate: number;
}

const MqttDataQuality: React.FC = () => {
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetrics | null>(null);
  const [dataSourceStats, setDataSourceStats] = useState<DataSourceStats[]>([]);
  const [performanceTrends, setPerformanceTrends] = useState<PerformanceTrends[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timePeriod, setTimePeriod] = useState<7 | 14 | 30>(7);

  useEffect(() => {
    fetchData();
  }, [timePeriod]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [metrics, stats, trends] = await Promise.all([
        mqttDataService.getQualityMetricsSummary(timePeriod),
        mqttDataService.getDataSourceStats(timePeriod),
        mqttDataService.getPerformanceTrends(timePeriod)
      ]);

      // 데이터 검증 및 안전한 설정
      setQualityMetrics(metrics);
      setDataSourceStats(Array.isArray(stats) ? stats : []);
      setPerformanceTrends(Array.isArray(trends) ? trends : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : '데이터를 가져오는데 실패했습니다.');
      // 에러 시 빈 배열로 설정
      setDataSourceStats([]);
      setPerformanceTrends([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="flex items-center justify-center h-full">로딩 중...</div>;
  if (error) return <div className="text-red-500 text-center">오류: {error}</div>;
  if (!qualityMetrics) return <div className="text-center">데이터가 없습니다.</div>;

  // 품질 점수 도넛 차트 데이터
  const qualityScoreData = {
    labels: ['고품질 (90%+)', '보통 (70-89%)', '저품질 (<70%)'],
    datasets: [{
      data: [
        qualityMetrics.high_quality_count,
        qualityMetrics.total_inspections - qualityMetrics.high_quality_count - qualityMetrics.low_quality_count,
        qualityMetrics.low_quality_count
      ],
      backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
      borderWidth: 0
    }]
  };

  // 데이터 소스별 통계 바 차트 데이터
  const dataSourceChartData = {
    labels: Array.isArray(dataSourceStats) ? dataSourceStats.map(stat => stat.data_source) : [],
    datasets: [{
      label: '검사 횟수',
      data: Array.isArray(dataSourceStats) ? dataSourceStats.map(stat => stat.inspection_count) : [],
      backgroundColor: 'rgba(59, 130, 246, 0.8)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 1
    }]
  };

  // 성능 트렌드 라인 차트 데이터
  const performanceChartData = {
    labels: Array.isArray(performanceTrends) ? performanceTrends.map(trend => trend.date) : [],
    datasets: [{
      label: '평균 처리 시간 (ms)',
      data: Array.isArray(performanceTrends) ? performanceTrends.map(trend => trend.avg_processing_time_ms) : [],
      borderColor: 'rgba(147, 51, 234, 1)',
      backgroundColor: 'rgba(147, 51, 234, 0.1)',
      borderWidth: 2,
      fill: true
    }]
  };

  return (
    <div className="dash mqtt-data-quality" style={{ 
      background: 'transparent', 
      padding: '15px',
      height: '100%',
      position: 'relative'
    }}>
      <h2 style={{ marginBottom: '15px', color: '#333', textAlign: 'center', fontSize: '18px' }}>
        MQTT 데이터 품질 현황
      </h2>

      {/* 기간 선택 버튼 */}
      <div style={{ 
        position: 'absolute',
        top: '5px',
        right: '5px',
        zIndex: 10,
        display: 'flex',
        gap: '5px'
      }}>
        {[7, 14, 30].map(days => (
          <button
            key={days}
            onClick={() => setTimePeriod(days as 7 | 14 | 30)}
            style={{
              padding: '4px 8px',
              border: `1px solid ${timePeriod === days ? '#007bff' : '#ccc'}`,
              borderRadius: '4px',
              backgroundColor: timePeriod === days ? '#007bff' : 'white',
              color: timePeriod === days ? 'white' : '#333',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            {days}일
          </button>
        ))}
      </div>

      {/* 주요 지표 카드들 */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-white rounded-lg p-3 shadow-sm">
          <div className="text-sm text-gray-600">총 검사 수</div>
          <div className="text-2xl font-bold text-blue-600">{qualityMetrics.total_inspections}</div>
        </div>
        <div className="bg-white rounded-lg p-3 shadow-sm">
          <div className="text-sm text-gray-600">평균 통과율</div>
          <div className="text-2xl font-bold text-green-600">{qualityMetrics.avg_pass_rate}%</div>
        </div>
        <div className="bg-white rounded-lg p-3 shadow-sm">
          <div className="text-sm text-gray-600">평균 품질점수</div>
          <div className="text-2xl font-bold text-purple-600">{qualityMetrics.avg_quality_score}</div>
        </div>
        <div className="bg-white rounded-lg p-3 shadow-sm">
          <div className="text-sm text-gray-600">평균 처리시간</div>
          <div className="text-2xl font-bold text-orange-600">{qualityMetrics.avg_processing_time_ms}ms</div>
        </div>
      </div>

      {/* 차트 그리드 */}
      <div className="grid grid-cols-2 gap-4" style={{ height: 'calc(100% - 120px)' }}>
        {/* 품질 점수 분포 도넛 차트 */}
        <div className="bg-white rounded-lg p-3 shadow-sm">
          <h3 className="text-sm font-semibold mb-2 text-center">품질 점수 분포</h3>
          <div style={{ height: '150px' }}>
            <Doughnut 
              data={qualityScoreData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
              }}
            />
          </div>
        </div>

        {/* 데이터 소스별 통계 바 차트 */}
        <div className="bg-white rounded-lg p-3 shadow-sm">
          <h3 className="text-sm font-semibold mb-2 text-center">데이터 소스별 검사 횟수</h3>
          <div style={{ height: '150px' }}>
            <Bar 
              data={dataSourceChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  y: { beginAtZero: true },
                  x: { ticks: { maxRotation: 45 } }
                }
              }}
            />
          </div>
        </div>

        {/* 성능 트렌드 라인 차트 */}
        <div className="col-span-2 bg-white rounded-lg p-3 shadow-sm">
          <h3 className="text-sm font-semibold mb-2 text-center">성능 트렌드 (처리 시간)</h3>
          <div style={{ height: '120px' }}>
            {Array.isArray(performanceTrends) && performanceTrends.length > 0 ? (
              <Line 
                data={performanceChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: {
                    y: { beginAtZero: true },
                    x: { ticks: { maxRotation: 0 } }
                  }
                }}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500 text-sm">
                성능 트렌드 데이터가 없습니다
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MqttDataQuality;
