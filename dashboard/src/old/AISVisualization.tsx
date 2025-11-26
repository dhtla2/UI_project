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
  ArcElement,
  BarElement,
  Filler
} from 'chart.js';
import { Line, Bar, Doughnut, Pie } from 'react-chartjs-2';

// Chart.js 컴포넌트 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  Filler
);

interface AISSummary {
  total_ships: number;
  unique_ship_types: number;
  unique_flags: number;
  avg_speed: number;
  max_speed: number;
  ship_type_distribution: Array<{ type: string; count: number }>;
  flag_distribution: Array<{ flag: string; count: number }>;
  speed_distribution: Array<{ range: string; count: number }>;
}

interface AISVisualizationProps {
  viewMode?: 'summary' | 'shipType' | 'nationality' | 'speed';
}

const AISVisualization: React.FC<AISVisualizationProps> = ({ viewMode = 'summary' }) => {
  const [aisSummary, setAisSummary] = useState<AISSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAISSummary();
  }, []);

  const fetchAISSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/dashboard/ais-summary');
      if (!response.ok) throw new Error('AIS 데이터를 가져오는데 실패했습니다.');
      const data = await response.json();
      setAisSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
      setAisSummary(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="flex items-center justify-center h-full">로딩 중...</div>;
  if (error) return <div className="text-red-500 text-center">오류: {error}</div>;
  if (!aisSummary) return <div className="text-center">데이터가 없습니다.</div>;

  // 차트 데이터 준비
  const shipTypeData = Array.isArray(aisSummary.ship_type_distribution) ? aisSummary.ship_type_distribution : [];
  const flagData = Array.isArray(aisSummary.flag_distribution) ? aisSummary.flag_distribution : [];
  const speedData = Array.isArray(aisSummary.speed_distribution) ? aisSummary.speed_distribution : [];

  // 선박 타입 차트 데이터
  const shipTypeChartData = {
    labels: shipTypeData.map(item => item.type || 'Unknown'),
    datasets: [{
      data: shipTypeData.map(item => item.count || 0),
      backgroundColor: [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
      ],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  };

  // 국적별 차트 데이터
  const flagChartData = {
    labels: flagData.map(item => item.flag || 'Unknown'),
    datasets: [{
      label: '선박 수',
      data: flagData.map(item => item.count || 0),
      backgroundColor: 'rgba(54, 162, 235, 0.8)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1
    }]
  };

  // 속도 분포 차트 데이터
  const speedChartData = {
    labels: speedData.map(item => item.range || 'Unknown'),
    datasets: [{
      label: '선박 수',
      data: speedData.map(item => item.count || 0),
      backgroundColor: 'rgba(255, 99, 132, 0.8)',
      borderColor: 'rgba(255, 99, 132, 1)',
      borderWidth: 1
    }]
  };

  const renderDetailedView = () => {
    switch (viewMode) {
      case 'shipType':
        return (
          <div className="h-full flex flex-col">
            <h3 className="text-lg font-bold text-center mb-2">선박 타입 분포</h3>
            <div className="flex-1 flex items-center justify-center p-4">
              {shipTypeData.length > 0 ? (
                <div className="w-4/5 h-4/5 relative">
                  <Doughnut
                    data={shipTypeChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          display: true,
                          position: 'top',
                          align: 'start',
                          labels: {
                            boxWidth: 12,
                            padding: 8,
                            font: {
                              size: 10
                            }
                          }
                        }
                      }
                    }}
                  />
                </div>
              ) : (
                <div className="text-center text-gray-500">데이터가 없습니다</div>
              )}
            </div>
          </div>
        );
      
      case 'nationality':
        return (
          <div className="h-full flex flex-col">
            <h3 className="text-lg font-bold text-center mb-2">국적별 분포</h3>
            <div className="flex-1 flex items-center justify-center p-4">
              {flagData.length > 0 ? (
                <div className="w-4/5 h-4/5 relative">
                  <Pie
                    data={flagChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          display: true,
                          position: 'top',
                          align: 'start',
                          labels: {
                            boxWidth: 12,
                            padding: 8,
                            font: {
                              size: 10
                            }
                          }
                        }
                      }
                    }}
                  />
                </div>
              ) : (
                <div className="text-center text-gray-500">데이터가 없습니다</div>
              )}
            </div>
          </div>
        );
      
      case 'speed':
        return (
          <div className="h-full flex flex-col">
            <h3 className="text-lg font-bold text-center mb-2">속도 통계</h3>
            <div className="flex-1 flex items-center justify-center p-4">
              {speedData.length > 0 ? (
                <div className="w-4/5 h-4/5 relative">
                  <Bar
                    data={speedChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          display: true,
                          position: 'top',
                          align: 'start',
                          labels: {
                            boxWidth: 12,
                            padding: 8,
                            font: {
                              size: 10
                            }
                          }
                        }
                      },
                      scales: {
                        x: {
                          ticks: {
                            callback: function(value: any, index: number) {
                              // 막대 사이사이에 숫자 표시 (0, 2, 4, 6...)
                              return speedData[index]?.range || '';
                            }
                          }
                        },
                        y: {
                          beginAtZero: true
                        }
                      }
                    }}
                  />
                </div>
              ) : (
                <div className="text-center text-gray-500">데이터가 없습니다</div>
              )}
            </div>
          </div>
        );
      
      default: // summary
        return (
          <div className="space-y-4">
            {/* 상세 통계 카드 - 이름을 위로, 숫자를 아래로 배치 */}
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div className="text-sm text-gray-600 mb-2">총 선박 수</div>
                <div className="text-xl font-bold text-blue-600">{aisSummary.total_ships}</div>
              </div>
              <div className="text-center p-3 bg-red-50 rounded-lg border border-red-200">
                <div className="text-sm text-gray-600 mb-2">선박 타입</div>
                <div className="text-xl font-bold text-red-600">{aisSummary.unique_ship_types}</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="text-sm text-gray-600 mb-2">국적</div>
                <div className="text-xl font-bold text-yellow-600">{aisSummary.unique_flags}</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="text-sm text-gray-600 mb-2">평균 속도 (노트)</div>
                <div className="text-xl font-bold text-green-600">{aisSummary.avg_speed}</div>
                <div className="text-xs text-gray-500">
                  최저: {Math.min(...speedData.map(item => parseFloat(item.range.split('-')[0]) || 0))} | 
                  최고: {aisSummary.max_speed}
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="h-full relative">
      {/* summary 모드일 때만 AIS 데이터 제목 표시 */}
      {viewMode === 'summary' && (
        <div className="mb-4">
          <h2 className="text-lg font-bold text-gray-800 text-center">AIS 데이터</h2>
        </div>
      )}

      {/* 상세 뷰 렌더링 */}
      {renderDetailedView()}
    </div>
  );
};

export default AISVisualization;
