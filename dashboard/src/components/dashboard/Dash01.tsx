import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

// Chart.js 등록
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

interface TimeBasedStatistics {
  page_visits: Array<[string, number]>;
  api_calls: Array<[string, number]>;
}

interface VisitorTrends {
  recent_7day_avg: number;
  previous_7day_avg: number;
  trend_percentage: number;
  peak_hour_start: number;
  peak_hour_end: number;
  peak_hour_display: string;
}



// 공통 버튼 스타일 정의 - 작은 크기, 더 강력한 스타일
const buttonBaseStyle: React.CSSProperties = {
  padding: '2px 6px',
  border: '1px solid #ccc',
  borderRadius: '3px',
  backgroundColor: 'white',
  color: '#333',
  cursor: 'pointer',
  fontSize: '10px',
  transition: 'all 0.2s ease',
  marginLeft: '2px',
  position: 'relative',
  zIndex: 1001,
  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
};

// 활성화된 버튼에 적용할 스타일
const activeButtonSyle: React.CSSProperties = {
  ...buttonBaseStyle,
  background: '#007bff',
  color: 'white',
  border: '1px solid #007bff',
  fontWeight: 'bold',
  boxShadow: '0 2px 4px rgba(0,123,255,0.3)'
};

const Dash01: React.FC = () => {
  const [timeStats, setTimeStats] = useState<TimeBasedStatistics | null>(null);
  const [visitorTrends, setVisitorTrends] = useState<VisitorTrends | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timePeriod, setTimePeriod] = useState<'daily' | 'weekly' | 'monthly' | 'custom'>('daily');

  // 사용자 정의 날짜 범위 상태 추가
  const [customDateRange, setCustomDateRange] = useState({
    startDate: '',
    endDate: ''
  });
  const [showDatePicker, setShowDatePicker] = useState(false);

  // 안전한 데이터 검증 함수


  const validateTimeStats = (data: any): TimeBasedStatistics | null => {
    if (!data || typeof data !== 'object') return null;
    
    // API 응답 구조: { success: true, data: [{ period: "daily", data: [...] }] }
    const responseData = data.data && data.data[0] && data.data[0].data;
    
    if (!Array.isArray(responseData)) {
      return {
        page_visits: [],
        api_calls: []
      };
    }
    
    // data 배열을 page_visits와 api_calls 형태로 변환
    const page_visits: Array<[string, number]> = responseData.map((item: any) => [item.period, item.page_visits || 0]);
    const api_calls: Array<[string, number]> = responseData.map((item: any) => [item.period, item.api_calls || 0]);
    
    return {
      page_visits,
      api_calls
    };
  };

  useEffect(() => {
    fetchTimeBasedStatistics();
    fetchVisitorTrends();
  }, [timePeriod]);

  const fetchTimeBasedStatistics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let apiUrl = `/ui/statistics/time-based?period=${timePeriod}`;

      // 사용자 정의 날짜 범위인 경우
      if (timePeriod === 'custom' && customDateRange.startDate && customDateRange.endDate) {
        apiUrl += `&start_date=${customDateRange.startDate}&end_date=${customDateRange.endDate}`;
      }
      
      // 방문 로그는 백엔드 미들웨어에서 자동으로 처리됨
      
      const response = await fetch(apiUrl);
      if (!response.ok) throw new Error('데이터를 가져오는데 실패했습니다.');
      const data = await response.json();
      const validatedData = validateTimeStats(data);
      setTimeStats(validatedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
      setTimeStats(null);
    } finally {
      setLoading(false);
    }
  };

  // 날짜 범위 적용 함수
  const applyCustomDateRange = () => {
    if (customDateRange.startDate && customDateRange.endDate) {
      setTimePeriod('custom');
      setShowDatePicker(false);
      fetchTimeBasedStatistics();
    } else {
      alert('시작 날짜와 종료 날짜를 모두 선택해주세요.');
    }
  };

  // 오늘 날짜 기본값 설정
  const getTodayString = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const getWeekAgoString = () => {
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return weekAgo.toISOString().split('T')[0];
  };

  const fetchVisitorTrends = async () => {
    try {
      const response = await fetch('/ui/statistics/visitor-trends');
      if (!response.ok) throw new Error('방문자 트렌드 데이터를 가져오는데 실패했습니다.');
      const data = await response.json();
      setVisitorTrends(data);
    } catch (err) {
      console.error('방문자 트렌드 데이터 로드 실패:', err);
      setVisitorTrends(null);
    }
  };

  // 로딩, 에러, 데이터 없음 UI
  if (loading) return <div>로딩 중...</div>;
  if (error) return <div>오류: {error}</div>;

  return (
    <div style={{ 
      background: 'transparent', 
      padding: '8px',
      height: '100%',
      position: 'relative',
      overflow: 'visible'
    }}>
      <h2 style={{ 
        marginBottom: '10px',
        color: '#333', 
        textAlign: 'center', 
        fontSize: '18px',
        marginTop: '0',
        paddingTop: '0'
      }}>
        사용자 활동 추이
      </h2>
      
      {/* 기간 선택 버튼들 - 오른쪽 위에 작게 배치 */}
      <div style={{ 
        position: 'absolute',
        top: '8px',
        right: '8px',
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        gap: '2px'
      }}>
        <button
          onClick={() => setTimePeriod('daily')}
          style={timePeriod === 'daily' ? activeButtonSyle : buttonBaseStyle}
        >
          일간
        </button>
        <button
          onClick={() => setTimePeriod('weekly')}
          style={timePeriod === 'weekly' ? activeButtonSyle : buttonBaseStyle}
        >
          주간
        </button>
        <button
          onClick={() => setTimePeriod('monthly')}
          style={timePeriod === 'monthly' ? activeButtonSyle : buttonBaseStyle}
        >
          월간
        </button>

        <button
          onClick={() => setShowDatePicker(!showDatePicker)}
          style={timePeriod === 'custom' ? activeButtonSyle : buttonBaseStyle}
        >
          사용자 정의
        </button>
      </div>

      {/* 사용자 정의 날짜 선택기 */}
      {showDatePicker && (
        <div style={{
          position: 'absolute',
          top: '40px',
          right: '8px',
          background: 'white',
          border: '1px solid #ccc',
          borderRadius: '8px',
          padding: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          zIndex: 10000,
          minWidth: '280px'
        }}>
          <div style={{ marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>
            날짜 범위 선택
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div>
              <label style={{ fontSize: '12px', color: '#666', display: 'block', marginBottom: '4px' }}>
                시작 날짜:
              </label>
              <input
                type="date"
                value={customDateRange.startDate || getWeekAgoString()}
                onChange={(e) => setCustomDateRange(prev => ({ ...prev, startDate: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '4px 8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '12px'
                }}
              />
            </div>
            
            <div>
              <label style={{ fontSize: '12px', color: '#666', display: 'block', marginBottom: '4px' }}>
                종료 날짜:
              </label>
              <input
                type="date"
                value={customDateRange.endDate || getTodayString()}
                onChange={(e) => setCustomDateRange(prev => ({ ...prev, endDate: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '4px 8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '12px'
                }}
              />
            </div>
            
            <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
              <button
                onClick={applyCustomDateRange}
                style={{
                  ...buttonBaseStyle,
                  background: '#28a745',
                  color: 'white',
                  border: '1px solid #28a745',
                  flex: 1
                }}
              >
                적용
              </button>
              <button
                onClick={() => setShowDatePicker(false)}
                style={{
                  ...buttonBaseStyle,
                  background: '#6c757d',
                  color: 'white',
                  border: '1px solid #6c757d',
                  flex: 1
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 시간별 통계 차트 */}
      {timeStats ? (
        <div style={{ 
          height: '300px',  // 고정 높이로 설정
          width: '100%',
          marginTop: '5px'
        }}>
          <Line 
            data={{
              labels: timeStats.page_visits.map(item => {
                const label = item[0];
                if (timePeriod === 'daily') {
                  // 일간: 날짜만 표시 (YYYY-MM-DD)
                  return label;
                } else if (timePeriod === 'weekly') {
                  // 주간: 년월주차 표시 (2025년 1월 1주차)
                  return label;
                } else if (timePeriod === 'monthly') {
                  // 월간: 년월 표시 (2025년 1월)
                  return label;
                }
                return label;
              }), 
              datasets: [
                { 
                  label: '페이지 방문', 
                  data: timeStats.page_visits.map(item => item[1]), 
                  borderColor: 'rgba(54, 162, 235, 1)', 
                  borderWidth: 2, 
                  fill: false 
                },
                { 
                  label: 'API 호출', 
                  data: timeStats.api_calls.map(item => item[1]), 
                  borderColor: 'rgba(255, 99, 132, 1)', 
                  borderWidth: 2, 
                  fill: false 
                }
              ]
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: { legend: { display: false } },
              scales: {
                y: { 
                  beginAtZero: true,
                  grid: { color: 'rgba(0,0,0,0.1)' }
                },
                x: { 
                  ticks: { 
                    maxRotation: timePeriod === 'daily' ? 0 : 45, 
                    minRotation: timePeriod === 'daily' ? 0 : 45,
                    maxTicksLimit: 15,  // 모든 기간에 대해 동일한 최대 틱 수
                    font: {
                      size: timePeriod === 'daily' ? 10 : 9
                    }
                  },
                  grid: { color: 'rgba(0,0,0,0.1)' }
                }
              }
            }}
          />
        </div>
      ) : (
        <div>시간별 통계 데이터가 없습니다.</div>
      )}
      
      {/* 최근 활동 트렌드 및 활동 패턴 분석 */}
      {timeStats && visitorTrends && (
        <div style={{ 
          height: 'calc(50% - 25px)', 
          width: '100%',
          marginTop: '10px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          {/* 최근 활동 트렌드 */}
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid #e9ecef'
          }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#495057', marginBottom: '4px' }}>
              📈 최근 활동 트렌드
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontSize: '11px', color: '#6c757d' }}>
                최근 7일 평균
              </div>
              <div style={{ 
                fontSize: '11px', 
                color: visitorTrends.trend_percentage >= 0 ? '#28a745' : '#dc3545', 
                fontWeight: 'bold' 
              }}>
                {visitorTrends.trend_percentage >= 0 ? '+' : ''}{visitorTrends.trend_percentage}% {visitorTrends.trend_percentage >= 0 ? '↗️' : '↘️'}
              </div>
            </div>
            <div style={{ fontSize: '10px', color: '#6c757d', marginTop: '2px' }}>
              이전 7일 대비 {visitorTrends.trend_percentage >= 0 ? '증가' : '감소'}
            </div>
          </div>
          
          {/* 활동 패턴 분석 */}
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid #e9ecef'
          }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#495057', marginBottom: '4px' }}>
              🕐 활동 패턴 분석
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontSize: '11px', color: '#6c757d' }}>
                가장 활발한 시간
              </div>
              <div style={{ fontSize: '11px', color: '#007bff', fontWeight: 'bold' }}>
                {visitorTrends.peak_hour_display}
              </div>
            </div>
            <div style={{ fontSize: '10px', color: '#6c757d', marginTop: '2px' }}>
              {visitorTrends.peak_hour_start < 12 ? '오전' : visitorTrends.peak_hour_start < 18 ? '오후' : '저녁'} 시간대가 가장 활발
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dash01;