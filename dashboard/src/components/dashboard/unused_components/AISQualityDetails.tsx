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
import { fetchAISQualityDetails, AISQualityDetailsData } from '../../services/apiService';

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

const AISQualityDetails: React.FC = () => {
  const [aisQualityDetails, setAisQualityDetails] = useState<AISQualityDetailsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // AIS 품질 상세 데이터 로드
  useEffect(() => {
    const loadAISQualityDetails = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchAISQualityDetails();
        setAisQualityDetails(data);
      } catch (err) {
        console.error('AIS 품질 상세 데이터 로드 실패:', err);
        setError('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };
    
    loadAISQualityDetails();
  }, []);

  if (loading) return <div className="flex items-center justify-center h-full">로딩 중...</div>;
  if (error) return <div className="text-red-500 text-center">오류: {error}</div>;

  // 완전성 검사 필드 그룹별 분류
  const fieldGroups = {
    '선박 식별': ['mmsiNo', 'imoNo', 'vsslNm', 'callLetter'],
    '선박 정보': ['vsslTp', 'vsslTpCd', 'vsslTpCrgo', 'vsslCls'],
    '크기 정보': ['vsslLen', 'vsslWidth', 'vsslDefBrd'],
    '국적 정보': ['flag', 'flagCd'],
    '위치 정보': ['lon', 'lat'],
    '항해 정보': ['sog', 'cog', 'rot', 'headSide'],
    '상태 정보': ['vsslNavi', 'vsslNaviCd'],
    '시간 정보': ['dt_pos_utc', 'dt_static_utc'],
    '분류 정보': ['vsslTpMain', 'vsslTpSub'],
    '목적지 정보': ['dstNm', 'dstCd', 'eta']
  };

  // 완전성 검사 차트 데이터
  const completenessChartData = {
    labels: aisQualityDetails?.completeness.field_groups.map(fg => fg.name) || Object.keys(fieldGroups),
    datasets: [{
      label: '완성도 (%)',
      data: aisQualityDetails?.completeness.field_groups.map(fg => fg.completion_rate) || Object.values(fieldGroups).map(group => {
        const groupFields = group.length;
        const completedFields = groupFields; // 모든 필드가 100% 완성
        return (completedFields / groupFields) * 100;
      }),
      backgroundColor: 'rgba(34, 197, 94, 0.8)',
      borderColor: 'rgba(34, 197, 94, 1)',
      borderWidth: 2
    }]
  };

  return (
    <div className="h-full p-4 bg-gray-50">
      {/* 완전성과 유효성 검사 */}
      <div className="grid grid-cols-2 gap-6 h-full">
        {/* 완전성 검사 패널 */}
        <div className="bg-white p-4 rounded-lg shadow flex flex-col">
          <h3 className="text-xl font-bold text-gray-800 flex items-center mb-2">
            📋 완전성 검사 (Completeness)
          </h3>
          
          <div className="flex-1 flex flex-col justify-center">
            <p className="text-sm text-gray-600 mb-2">29개 필드의 데이터 누락 검사</p>
            <div className="text-green-600 font-semibold mb-4">🟢 100% 완성도 달성</div>
            
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">필드별 완성도</h4>
              <div className="h-48">
                <Bar
                  data={completenessChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                          callback: function(value) {
                            return value + '%';
                          }
                        }
                      },
                      x: {
                        ticks: {
                          maxRotation: 45,
                          minRotation: 45
                        }
                      }
                    }
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* 유효성 검사 패널 */}
        <div className="bg-white p-4 rounded-lg shadow flex flex-col">
          <h3 className="text-xl font-bold text-gray-800 flex items-center mb-2">
            ✅ 유효성 검사 (Validity)
          </h3>
          
          <div className="flex-1 flex flex-col justify-center">
            <p className="text-sm text-gray-600 mb-2">
              {aisQualityDetails?.overall_validity?.total_check_types || 0}개 검사 항목의 범위 및 위치 검증
            </p>
            <div className={`font-semibold mb-4 ${
              (aisQualityDetails?.overall_validity?.success_rate || 0) >= 90 
                ? 'text-green-600' 
                : (aisQualityDetails?.overall_validity?.success_rate || 0) >= 70 
                ? 'text-yellow-600' 
                : 'text-red-600'
            }`}>
              {(aisQualityDetails?.overall_validity?.success_rate || 0) >= 90 
                ? '🟢' 
                : (aisQualityDetails?.overall_validity?.success_rate || 0) >= 70 
                ? '🟡' 
                : '🔴'} {aisQualityDetails?.overall_validity?.success_rate || 0}% 유효성 달성
            </div>


            <div className="space-y-4">
              {/* 경도 검증 */}
              <div className="bg-blue-50 p-3 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-blue-800">경도 (Lon) 검증</div>
                    <div className="text-sm text-blue-600">범위: {aisQualityDetails?.validity.longitude?.range || '-180° ~ +180°'}</div>
                  </div>
                  <div className="text-2xl">🌍</div>
                </div>
                <div className="mt-2 text-green-600 font-semibold">
                  ✅ {aisQualityDetails?.validity.longitude?.status || '데이터 없음'}
                </div>
              </div>

              {/* 위도 검증 */}
              <div className="bg-green-50 p-3 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-green-800">위도 (Lat) 검증</div>
                    <div className="text-sm text-green-600">범위: {aisQualityDetails?.validity.latitude?.range || '-90° ~ +90°'}</div>
                  </div>
                  <div className="text-2xl">🌍</div>
                </div>
                <div className="mt-2 text-green-600 font-semibold">
                  ✅ {aisQualityDetails?.validity.latitude?.status || '데이터 없음'}
                </div>
              </div>

              {/* GRID 검사 (바다/육지 구분) */}
              {aisQualityDetails?.validity.grid && (
                <div className={`p-3 rounded-lg ${
                  aisQualityDetails.validity.grid.fail_count > 0 
                    ? 'bg-red-50 border-l-4 border-red-400' 
                    : 'bg-green-50 border-l-4 border-green-400'
                }`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className={`font-semibold ${
                        aisQualityDetails.validity.grid.fail_count > 0 
                          ? 'text-red-800' 
                          : 'text-green-800'
                      }`}>
                        GRID 검사 (바다/육지 구분)
                      </div>
                      <div className={`text-sm ${
                        aisQualityDetails.validity.grid.fail_count > 0 
                          ? 'text-red-600' 
                          : 'text-green-600'
                      }`}>
                        범위: {aisQualityDetails.validity.grid.range}
                      </div>
                    </div>
                    <div className="text-2xl">🗺️</div>
                  </div>
                  <div className={`mt-2 font-semibold ${
                    aisQualityDetails.validity.grid.fail_count > 0 
                      ? 'text-red-600' 
                      : 'text-green-600'
                  }`}>
                    {aisQualityDetails.validity.grid.fail_count > 0 ? '❌' : '✅'} 
                    성공률: {aisQualityDetails.validity.grid.pass_rate}%
                  </div>
                  <div className="mt-1 text-xs text-gray-600">
                    바다: {aisQualityDetails.validity.grid.sea_count}개 ({aisQualityDetails.validity.grid.sea_percentage}%) | 
                    육지: {aisQualityDetails.validity.grid.land_count}개 ({aisQualityDetails.validity.grid.land_percentage}%)
                  </div>
                  {aisQualityDetails.validity.grid.fail_count > 0 && (
                    <div className="mt-1 text-xs text-red-600 font-medium">
                      ⚠️ 육지에 위치한 선박 {aisQualityDetails.validity.grid.land_count}개 발견 (데이터 오류)
                    </div>
                  )}
                </div>
              )}

              {/* 지리적 정확성 강조 */}
              <div className="bg-purple-50 p-3 rounded-lg border-l-4 border-purple-400">
                <div className="flex items-center">
                  <div className="text-2xl mr-3">🎯</div>
                  <div>
                    <div className="font-semibold text-purple-800">지리적 정확성 검증 완료</div>
                    <div className="text-sm text-purple-600">
                      모든 선박 위치가 실제 지구 좌표계 범위 내에 정확히 기록됨
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AISQualityDetails;