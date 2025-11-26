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
// import InspectionResultsSection from './common/InspectionResultsSection';
import MostAccessedAPIs from './dashboard/MostAccessedAPIs';
import BestQualityAPIs from './dashboard/BestQualityAPIs';
import WorstQualityAPIs from './dashboard/WorstQualityAPIs';
import { fetchAPIQualityData, APIQualityData, fetchAISInspectionHistory, AISInspectionHistoryData, fetchAISSummary, fetchAISQualityStatus, fetchLatestInspectionResults, LatestInspectionResults } from '../services/apiService';
import portImage from '../images/port.jpg';
import '../styles/DashboardLayout.css';

// AIS 개별 차트 컴포넌트들 (현재 사용하지 않음)
// const AISSummary = () => <AISVisualization />;
// const ShipTypeChart = () => <AISVisualization viewMode="shipType" />;
// const NationalityChart = () => <AISVisualization viewMode="nationality" />;
// const SpeedChart = () => <AISVisualization viewMode="speed" />;

interface AISPageProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  onPageChange: (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck') => void;
}

const AISPage: React.FC<AISPageProps> = ({ currentPage, onPageChange }) => {
  // 상태 관리
  const [apiQualityData, setApiQualityData] = useState<APIQualityData[]>([]);
  const [inspectionHistory, setInspectionHistory] = useState<AISInspectionHistoryData[]>([]);
  // AIS 데이터 상태 추가
  const [aisData, setAisData] = useState<any>(null);
  const [historyData, setHistoryData] = useState<any>(null);
  const [aisQualityStatus, setAisQualityStatus] = useState<any>(null);
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
      const historyData = await fetchAISInspectionHistory(period, startDate, endDate);
      setInspectionHistory(historyData);
    } catch (err) {
      console.error('검사 히스토리 로드 실패:', err);
      setInspectionHistory([]);
    }
  };

  // 기간 변경 핸들러
  const handleInspectionPeriodChange = (period: 'daily' | 'weekly' | 'monthly' | 'custom', startDate?: string, endDate?: string) => {
    loadInspectionHistory(period, startDate, endDate);
  };

  // API 품질 데이터 및 검사 히스토리 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // 필드 분석 데이터는 이제 CommonFieldAnalysisSection에서 관리됨
        
        // AIS 데이터, API 품질 데이터, 검사 히스토리, 최신 검사 결과를 병렬로 로드
        console.log('🚀 Starting parallel API calls...');
        const results = await Promise.allSettled([
          fetchAISSummary().then(result => {
            console.log('✅ AIS Summary loaded:', result);
            return result;
          }),
          fetchAPIQualityData().then(result => {
            console.log('✅ API Quality loaded:', result?.length, 'items');
            return result;
          }),
          fetchAISInspectionHistory('daily').then(result => {
            console.log('✅ Inspection History loaded:', result?.length, 'items');
            return result;
          }),
          fetchLatestInspectionResults('AIS').then(result => {
            console.log('✅ Latest Results loaded:', result);
            return result;
          })
        ]);
        
        // 각 결과를 안전하게 처리
        const aisDataResult = results[0].status === 'fulfilled' ? results[0].value : null;
        const apiData = results[1].status === 'fulfilled' ? results[1].value : [];
        const historyData = results[2].status === 'fulfilled' ? results[2].value : [];
        const latestResults = results[3].status === 'fulfilled' ? results[3].value : null;
        
        console.log('📊 Final data:', { aisDataResult, apiData: apiData?.length, historyData: historyData?.length, latestResults });
        
        setAisData(aisDataResult);
        setApiQualityData(apiData);
        setInspectionHistory(historyData);
        setLatestInspectionResults(latestResults);
        
        // AIS 품질 상태 데이터도 별도로 로드
        try {
          const qualityStatus = await fetchAISQualityStatus();
          setAisQualityStatus(qualityStatus);
        } catch (err) {
          console.warn('AIS 품질 상태 데이터 로드 실패:', err);
          // 품질 상태 데이터가 없어도 계속 진행
        }
      } catch (err) {
        console.error('데이터 로드 실패:', err);
        setError('데이터를 불러오는데 실패했습니다.');
        // 에러 발생 시 빈 배열로 설정
        setAisData(null);
        setApiQualityData([]);
        setInspectionHistory([]);
        setAisQualityStatus(null);
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
              aisData={null}
            />


            {/* 검사 결과 섹션 - 완전성과 유효성 검사 결과
            <InspectionResultsSection 
              currentPage={currentPage}
              data={latestInspectionResults ? {
                completeness: {
                  ...latestInspectionResults.completeness,
                  last_updated: latestInspectionResults.completeness.last_updated || undefined,
                  failed_items: [],
                  fieldAnalysisData: [] // CommonFieldAnalysisSection에서 관리됨
                },
                validity: {
                  ...latestInspectionResults.validity,
                  last_updated: latestInspectionResults.validity.last_updated || undefined,
                  failed_items: [],
                  fieldAnalysisData: [] // CommonFieldAnalysisSection에서 관리됨
                }
              } : {
                completeness: {
                  pass_rate: 0,
                  total_checks: 0,
                  pass_count: 0,
                  fail_count: 0,
                  fields_checked: 0,
                  last_updated: undefined,
                  failed_items: [],
                  fieldAnalysisData: []
                },
                validity: {
                  pass_rate: 0,
                  total_checks: 0,
                  pass_count: 0,
                  fail_count: 0,
                  fields_checked: 0,
                  last_updated: undefined,
                  failed_items: [],
                  fieldAnalysisData: []
                }
              }}
              loading={loading}
              error={error}
            /> */}

            {/* 공통 중간 섹션 - 검사 히스토리와 사용자 활동 추이 */}
            <CommonMiddleSection 
              currentPage={currentPage}
              inspectionHistory={inspectionHistory}
              loading={loading}
              error={error}
              onInspectionPeriodChange={handleInspectionPeriodChange}
            />

            {/* 데이터 품질 지표들 */}
            {/* <div className="px-6 mb-6">
              <div className="flex justify-start gap-4 w-4/5">
                <div className="dashboard-card h-80 w-1/3">
                  <QualityScoreGauge />
                </div>
                <div className="dashboard-card h-80 w-1/3">
                  <GridDistributionChart />
                </div>
                <div className="dashboard-card h-80 w-1/3">
                  <CheckTypeResults />
                </div>
              </div>
            </div> */}

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

export default AISPage;
