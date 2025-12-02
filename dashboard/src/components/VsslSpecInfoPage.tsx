import React, { useState, useEffect } from 'react';
import Sidebar from './layout/Sidebar';
import TopTabs from './layout/TopTabs';
import CommonTopSection from './common/CommonTopSection';
import CommonSideSection from './common/CommonSideSection';
import CommonMiddleSection from './common/CommonMiddleSection';
import CommonFieldAnalysisSection from './common/CommonFieldAnalysisSection';
import InspectionHistory from './dashboard/InspectionHistory';
import DataQualityStatus from './dashboard/RealTimeMonitoring';
import Dash01 from './dashboard/Dash01';
import MostAccessedAPIs from './dashboard/MostAccessedAPIs';
import BestQualityAPIs from './dashboard/BestQualityAPIs';
import WorstQualityAPIs from './dashboard/WorstQualityAPIs';
import { 
  fetchAPIQualityData, 
  APIQualityData, 
  fetchVsslSpecInspectionHistory, 
  VsslSpecInspectionHistoryData, 
  fetchVsslSpecSummary, 
  VsslSpecSummaryData,
  fetchVsslSpecQualityStatus, 
  fetchLatestInspectionResults, 
  LatestInspectionResults 
} from '../services/apiService';
import portImage from '../images/port.jpg';
import '../styles/DashboardLayout.css';

interface VsslSpecInfoPageProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  onPageChange: (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck') => void;
}

const VsslSpecInfoPage: React.FC<VsslSpecInfoPageProps> = ({ currentPage, onPageChange }) => {
  // 상태 관리
  const [apiQualityData, setApiQualityData] = useState<APIQualityData[]>([]);
  const [inspectionHistory, setInspectionHistory] = useState<VsslSpecInspectionHistoryData[]>([]);
  // VsslSpecInfo 데이터 상태 추가
  const [vsslSpecData, setVsslSpecData] = useState<any>(null);
  const [vsslSpecQualityStatus, setVsslSpecQualityStatus] = useState<any>(null);
  // 최신 검사 결과 상태 추가
  const [latestInspectionResults, setLatestInspectionResults] = useState<LatestInspectionResults | null>(null);
  // fieldAnalysisData는 이제 CommonFieldAnalysisSection에서 관리됨
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // CSS 변수로 배경 이미지 설정
  useEffect(() => {
    document.documentElement.style.setProperty('--port-bg-image', `url(${portImage})`);
  }, []);

  // 검사 히스토리 로드 함수 (기간별)
  const loadInspectionHistory = async (period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily', startDate?: string, endDate?: string) => {
    try {
      const historyData = await fetchVsslSpecInspectionHistory(period, startDate, endDate);
      setInspectionHistory(historyData);
    } catch (err) {
      console.error('검사 히스토리 로드 실패:', err);
      setInspectionHistory([]);
    }
  };

  // 검사 기간 변경 핸들러
  const handleInspectionPeriodChange = (period: 'daily' | 'weekly' | 'monthly' | 'custom', startDate?: string, endDate?: string) => {
    loadInspectionHistory(period, startDate, endDate);
  };

  // API 품질 데이터 및 검사 히스토리 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // VsslSpecInfo 데이터, API 품질 데이터, 검사 히스토리, 최신 검사 결과를 병렬로 로드
        const results = await Promise.allSettled([
          fetchVsslSpecSummary(),
          fetchAPIQualityData(),
          fetchVsslSpecInspectionHistory('daily'),
          fetchLatestInspectionResults('VsslSpecInfo')
        ]);
        
        // 각 결과를 안전하게 처리
        const vsslSpecDataResult = results[0].status === 'fulfilled' ? results[0].value : null;
        const apiData = results[1].status === 'fulfilled' ? results[1].value : [];
        const historyData = results[2].status === 'fulfilled' ? results[2].value : [];
        const latestResults = results[3].status === 'fulfilled' ? results[3].value : null;
        
        setVsslSpecData(vsslSpecDataResult);
        setApiQualityData(apiData);
        setInspectionHistory(historyData);
        setLatestInspectionResults(latestResults);
        
        // VsslSpecInfo 품질 상태 데이터도 별도로 로드
        try {
          const qualityStatus = await fetchVsslSpecQualityStatus();
          setVsslSpecQualityStatus(qualityStatus);
        } catch (err) {
          console.warn('VsslSpecInfo 품질 상태 데이터 로드 실패:', err);
          // 품질 상태 데이터가 없어도 계속 진행
        }
      } catch (err) {
        console.error('데이터 로드 실패:', err);
        setError('데이터를 불러오는데 실패했습니다.');
        // 에러 발생 시 빈 배열로 설정
        setVsslSpecData(null);
        setApiQualityData([]);
        setInspectionHistory([]);
        setVsslSpecQualityStatus(null);
        setLatestInspectionResults(null);
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
            <TopTabs 
              currentPage={currentPage}
              onPageChange={onPageChange}
            />
          </div>
            
            
            {/* 공통 상단 섹션 - 데이터 품질 대시보드 + API 품질 카드들 */}
            <CommonTopSection 
              currentPage={currentPage}
              loading={loading}
              error={error}
              apiQualityData={apiQualityData}
              vsslSpecData={{ vsslSpecSummary: vsslSpecData }}
            />

            {/* 공통 중간 섹션 - 검사 히스토리와 사용자 활동 추이 */}
            <CommonMiddleSection 
              currentPage={currentPage}
              inspectionHistory={inspectionHistory}
              loading={loading}
              error={error}
              onInspectionPeriodChange={handleInspectionPeriodChange}
            />

            {/* 필드별 상세 분석 테이블 - 공통 컴포넌트 */}
            <CommonFieldAnalysisSection 
              currentPage={currentPage}
              loading={loading}
              error={error}
            />
            
        </div>
        </div>
      </div>
    </div>
  );
};

export default VsslSpecInfoPage;