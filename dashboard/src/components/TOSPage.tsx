import React, { useState, useEffect } from 'react';
import Sidebar from './layout/Sidebar';
import TopTabs from './layout/TopTabs';
import CommonTopSection from './common/CommonTopSection';
import CommonSideSection from './common/CommonSideSection';
import CommonMiddleSection from './common/CommonMiddleSection';
import CommonFieldAnalysisSection from './common/CommonFieldAnalysisSection';
import DataQualityStatus from './dashboard/RealTimeMonitoring';
import InspectionHistory from './dashboard/InspectionHistory';
import FieldAnalysisTable from './dashboard/FieldAnalysisTable';
// import InspectionResultsSection from './common/InspectionResultsSection';
import { fetchTOSQualitySummary, fetchTOSFieldAnalysis, TOSFieldAnalysisData, fetchTOSInspectionHistory, TOSInspectionHistoryData, TOSQualitySummaryData, fetchAPIQualityData, fetchLatestInspectionResults, LatestInspectionResults } from '../services/apiService';
import portImage from '../images/port.jpg';
import '../styles/DashboardLayout.css';

interface TOSPageProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  onPageChange: (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck') => void;
}

const TOSPage: React.FC<TOSPageProps> = ({ currentPage, onPageChange }) => {
  // 상태 관리
  const [tosQualitySummary, setTosQualitySummary] = useState<TOSQualitySummaryData | null>(null);
  const [inspectionHistory, setInspectionHistory] = useState<TOSInspectionHistoryData[]>([]);
  const [fieldAnalysisData, setFieldAnalysisData] = useState<TOSFieldAnalysisData[]>([]);
  const [apiQualityData, setApiQualityData] = useState<any[]>([]);
  // 최신 검사 결과 상태 추가
  const [latestInspectionResults, setLatestInspectionResults] = useState<LatestInspectionResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // CSS 변수로 배경 이미지 설정
  useEffect(() => {
    document.documentElement.style.setProperty('--port-bg-image', `url(${portImage})`);
  }, []);

  // 검사 히스토리 로드 함수 (기간별)
  const loadInspectionHistory = async (period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily', startDate?: string, endDate?: string) => {
    try {
      const historyData = await fetchTOSInspectionHistory(period, startDate, endDate);
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
        
        // TOS 품질 데이터와 검사 히스토리를 병렬로 로드 (Promise.allSettled 사용)
        const results = await Promise.allSettled([
          fetchTOSQualitySummary(),
          fetchTOSFieldAnalysis(),
          fetchTOSInspectionHistory('daily'), // 기본값으로 일간 데이터 로드
          // fetchTOSDataQualityStatus(),
          fetchAPIQualityData(),
          fetchLatestInspectionResults('TOS')
        ]);
        
        // 성공한 API 결과들만 처리
        const [tosSummaryResult, tosFieldResult, tosHistoryResult, apiQualityResult, latestResults] = results;
        
        
        // TOS 품질 요약 데이터 처리
        if (tosSummaryResult.status === 'fulfilled') {
          setTosQualitySummary(tosSummaryResult.value);
        } else {
          console.warn('TOS 품질 요약 데이터 로드 실패:', tosSummaryResult.reason);
          setTosQualitySummary(null);
        }
        
        
        // TOS 검사 히스토리 처리
        if (tosHistoryResult.status === 'fulfilled') {
          setInspectionHistory(tosHistoryResult.value);
        } else {
          console.warn('TOS 검사 히스토리 로드 실패:', tosHistoryResult.reason);
          setInspectionHistory([]);
        }
        
        // TOS 필드 분석 데이터 처리
        if (tosFieldResult.status === 'fulfilled') {
          setFieldAnalysisData(tosFieldResult.value);
        } else {
          console.warn('TOS 필드 분석 데이터 로드 실패:', tosFieldResult.reason);
          setFieldAnalysisData([]);
        }
        
        // TOS 데이터 품질 상태 처리
        // if (tosStatusResult.status === 'fulfilled') {
        //   setDataQualityStatus(tosStatusResult.value);
        // } else {
        //   console.warn('TOS 데이터 품질 상태 로드 실패:', tosStatusResult.reason);
        //   setDataQualityStatus(null);
        // }
        
        // API 품질 데이터 처리
        if (apiQualityResult.status === 'fulfilled') {
          console.log('TOS 페이지 - API 품질 데이터 로드 성공:', apiQualityResult.value);
          setApiQualityData(apiQualityResult.value);
        } else {
          console.warn('TOS 페이지 - API 품질 데이터 로드 실패:', apiQualityResult.reason);
          setApiQualityData([]);
        }
        
        // 최신 검사 결과 처리
        if (latestResults.status === 'fulfilled') {
          setLatestInspectionResults(latestResults.value);
        } else {
          console.warn('최신 검사 결과 로드 실패:', latestResults.reason);
          setLatestInspectionResults(null);
        }
      } catch (err) {
        console.error('예상치 못한 데이터 로드 실패:', err);
        setError('데이터를 불러오는데 실패했습니다.');
        // 에러 발생 시 빈 배열로 설정
        setTosQualitySummary(null);
        setInspectionHistory([]);
        setFieldAnalysisData([]);
        // setDataQualityStatus(null);
        setApiQualityData([]);
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
              tosData={{
                tosQualitySummary
              }}
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

            {/* TOS 필드별 상세 분석 테이블 - 공통 컴포넌트 */}
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

export default TOSPage;
