import React, { useState, useEffect } from 'react';
import Sidebar from './layout/Sidebar';
import TopTabs from './layout/TopTabs';
import AISDataQuality from './dashboard/AISDataQuality';
import AISQualityDetails from './dashboard/AISQualityDetails';
import CommonTopSection from './common/CommonTopSection';
import CommonSideSection from './common/CommonSideSection';
import CommonMiddleSection from './common/CommonMiddleSection';
import FieldAnalysisTable from './dashboard/FieldAnalysisTable';
import InspectionHistory from './dashboard/InspectionHistory';
import DataQualityStatus from './dashboard/RealTimeMonitoring';
import Dash01 from './dashboard/Dash01';
import { fetchAPIQualityData, APIQualityData, fetchAISInspectionHistory, AISInspectionHistoryData } from '../services/apiService';
import portImage from '../images/port.jpg';
import '../styles/DashboardLayout.css';

// AIS 개별 차트 컴포넌트들 (현재 사용하지 않음)
// const AISSummary = () => <AISVisualization />;
// const ShipTypeChart = () => <AISVisualization viewMode="shipType" />;
// const NationalityChart = () => <AISVisualization viewMode="nationality" />;
// const SpeedChart = () => <AISVisualization viewMode="speed" />;

interface AISPageProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'QualityCheck';
  onPageChange: (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'QualityCheck') => void;
}

const AISPage: React.FC<AISPageProps> = ({ currentPage, onPageChange }) => {
  // 상태 관리
  const [apiQualityData, setApiQualityData] = useState<APIQualityData[]>([]);
  const [inspectionHistory, setInspectionHistory] = useState<AISInspectionHistoryData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // CSS 변수로 배경 이미지 설정
  useEffect(() => {
    document.documentElement.style.setProperty('--port-bg-image', `url(${portImage})`);
  }, []);

  // API 품질 데이터 및 검사 히스토리 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // API 품질 데이터와 검사 히스토리를 병렬로 로드
        const [apiData, historyData] = await Promise.all([
          fetchAPIQualityData(),
          fetchAISInspectionHistory()
        ]);
        
        setApiQualityData(apiData);
        setInspectionHistory(historyData);
      } catch (err) {
        console.error('데이터 로드 실패:', err);
        setError('데이터를 불러오는데 실패했습니다.');
        // 에러 발생 시 빈 배열로 설정
        setApiQualityData([]);
        setInspectionHistory([]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return (
    <div className="dashboard-layout">
      <Sidebar currentPage={currentPage} onPageChange={onPageChange} />
      <div className="dashboard-main-area">
        <div className="flex gap-8">
        <div className="dashboard-main-content">
          <div className="dashboard-top-tabs">
            <TopTabs currentPage={currentPage} onPageChange={onPageChange} />
          </div>
            
            {/* 공통 상단 섹션 - 사용자 활동 추이 + API 품질 카드 2개 */}
            <CommonTopSection 
              currentPage={currentPage}
              loading={loading}
              error={error}
              apiQualityData={apiQualityData}
            />


            {/* 공통 중간 섹션 - 검사 히스토리와 사용자 활동 추이 */}
            <CommonMiddleSection 
              currentPage={currentPage}
              inspectionHistory={inspectionHistory}
              loading={loading}
              error={error}
            />

            {/* 필드별 상세 분석 테이블 */}
            <div className="px-6 mb-6">
              <div className="dashboard-card h-112 w-4/5">
                <FieldAnalysisTable 
                  results={[
                    // 완전성 검사 결과들
                    { field: 'mmsiNo', group: '선박 식별', status: 'PASS', total: 898, check: 0, etc: 898, message: '[mmsiNo] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', checkType: 'completeness' },
                    { field: 'imoNo', group: '선박 식별', status: 'PASS', total: 898, check: 0, etc: 898, message: '[imoNo] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', checkType: 'completeness' },
                    { field: 'lon', group: '위치 정보', status: 'PASS', total: 898, check: 0, etc: 898, message: '[lon] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', checkType: 'completeness' },
                    { field: 'lat', group: '위치 정보', status: 'PASS', total: 898, check: 0, etc: 898, message: '[lat] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', checkType: 'completeness' },
                    // 유효성 검사 결과들
                    { field: 'lon', group: '위치 정보', status: 'PASS', total: 898, check: 898, etc: 0, message: '[lon] 항목에 전체 [898]개 중 [898]개의 범위값이 확인 되었습니다', checkType: 'validity' },
                    { field: 'lat', group: '위치 정보', status: 'PASS', total: 898, check: 898, etc: 0, message: '[lat] 항목에 전체 [898]개 중 [898]개의 범위값이 확인 되었습니다', checkType: 'validity' },
                    { field: 'lon,lat', group: '위치 정보', status: 'FAIL', total: 898, check: 543, etc: 355, message: '[유효성-그리드] ([\'lon\', \'lat\']) 항목에 전체 (898)개 중 육지 (543)개, 바다 (355)개 확인 되었습니다', checkType: 'validity' }
                  ]}
                />
              </div>
            </div>
            
        </div>
        </div>
      </div>
    </div>
  );
};

export default AISPage;
