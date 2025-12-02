import React, { useState, useEffect } from 'react';
import Sidebar from './layout/Sidebar';
import TopTabs from './layout/TopTabs';
import CommonTopSection from './common/CommonTopSection';
import CommonMiddleSection from './common/CommonMiddleSection';
import CommonFieldAnalysisSection from './common/CommonFieldAnalysisSection';
import { fetchAPIQualityData, APIQualityData, fetchYTQualitySummary, YTQualitySummaryData, fetchLatestInspectionResults, LatestInspectionResults, fetchYTInspectionHistory, YTInspectionHistoryData } from '../services/apiService';
import portImage from '../images/port.jpg';
import '../styles/DashboardLayout.css';

interface YTPageProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  onPageChange: (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck') => void;
}

interface YTData {
  totalWork: number;
  totalTerminals: number;
  totalVehicles: number;
  totalContainers: number;
  workDays: number;
  recentWork: number;
  activeTerminals: number;
  activeVehicles: number;
  workTypes: Array<{ workType: string; count: number }>;
  terminals: Array<{ terminalId: string; terminalName: string; count: number }>;
  lastInspectionDate?: string;
}

interface YTHistoryData {
  date: string;
  totalWork: number;
  terminals: number;
  vehicles: number;
  containers: number;
}

interface YTDataQualityStatusData {
  workEfficiency: { status: string; rate: number; lastCheck: string };
  terminalUtilization: { status: string; rate: number; lastCheck: string };
  overall: { status: string; score: number; lastUpdate: string };
  alerts: Array<{ type: string; message: string; timestamp: string }>;
}

interface YTFieldAnalysisData {
  field: string;
  totalChecks: number;
  passCount: number;
  failCount: number;
  passRate: number;
  commonIssues: string[];
}

const YTPage: React.FC<YTPageProps> = ({ currentPage, onPageChange }) => {
  // 상태 관리
  const [apiQualityData, setApiQualityData] = useState<APIQualityData[]>([]);
  const [ytData, setYtData] = useState<YTData>({
    totalWork: 0,
    totalTerminals: 0,
    totalVehicles: 0,
    totalContainers: 0,
    workDays: 0,
    recentWork: 0,
    activeTerminals: 0,
    activeVehicles: 0,
    workTypes: [],
    terminals: []
  });
  const [historyData, setHistoryData] = useState<YTHistoryData[]>([]);
  const [fieldAnalysisData, setFieldAnalysisData] = useState<YTFieldAnalysisData[]>([]);
  const [inspectionHistory, setInspectionHistory] = useState<YTInspectionHistoryData[]>([]);
  const [ytQualitySummary, setYtQualitySummary] = useState<YTQualitySummaryData | null>(null);
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
      const historyData = await fetchYTInspectionHistory(period, startDate, endDate);
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
        
        // YT 품질 데이터와 검사 히스토리를 병렬로 로드 (Promise.allSettled 사용)
        const results = await Promise.allSettled([
          fetch('/api/dashboard/yt-summary'),
          fetch('/api/dashboard/yt-work-history'),
          fetchYTQualitySummary(),
          fetchAPIQualityData(),
          fetchLatestInspectionResults('YT'),
          fetchYTInspectionHistory('daily')
        ]);

        // 성공한 API 결과들만 처리
        const [ytSummaryResult, ytHistoryResult, ytQualitySummaryResult, commonApiResult, latestResults, inspectionHistoryResult] = results;

        // YT 요약 데이터 처리
        if (ytSummaryResult.status === 'fulfilled' && ytSummaryResult.value.ok) {
          const ytSummaryData = await ytSummaryResult.value.json();
          setYtData(ytSummaryData);
        } else {
          console.warn('YT 요약 데이터 로드 실패:', ytSummaryResult);
        }

        // YT 히스토리 데이터 처리
        if (ytHistoryResult.status === 'fulfilled' && ytHistoryResult.value.ok) {
          const ytHistoryData = await ytHistoryResult.value.json();
          setHistoryData(ytHistoryData);
        } else {
          console.warn('YT 히스토리 데이터 로드 실패:', ytHistoryResult);
          setHistoryData([]);
        }

        // YT 품질 요약 데이터 처리
        if (ytQualitySummaryResult.status === 'fulfilled') {
          setYtQualitySummary(ytQualitySummaryResult.value);
        } else {
          console.warn('YT 품질 요약 데이터 로드 실패:', ytQualitySummaryResult.reason);
          setYtQualitySummary(null);
        }

        // 공통 API 품질 데이터 처리
        if (commonApiResult.status === 'fulfilled') {
          setApiQualityData(commonApiResult.value);
        } else {
          console.warn('공통 API 품질 데이터 로드 실패:', commonApiResult.reason);
          setApiQualityData([]);
        }

        // 최신 검사 결과 처리
        if (latestResults.status === 'fulfilled') {
          setLatestInspectionResults(latestResults.value);
        } else {
          console.warn('최신 검사 결과 로드 실패:', latestResults.reason);
          setLatestInspectionResults(null);
        }

        // 검사 히스토리 처리
        if (inspectionHistoryResult.status === 'fulfilled') {
          setInspectionHistory(inspectionHistoryResult.value);
        } else {
          console.warn('검사 히스토리 로드 실패:', inspectionHistoryResult.reason);
          setInspectionHistory([]);
        }

        // 필드 분석 데이터는 CommonFieldAnalysisSection에서 별도로 로드됨
        setFieldAnalysisData([]);

      } catch (error) {
        console.error('데이터 로드 중 오류 발생:', error);
        setError(error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.');
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
            
            {/* 공통 상단 섹션 - 사용자 활동 추이 + API 품질 카드 2개 */}
            <CommonTopSection 
              currentPage={currentPage}
              loading={loading}
              error={error}
              apiQualityData={apiQualityData}
              ytData={{
                ytData,
                historyData,
                ytQualitySummary
              }}
            />

          {/* 공통 중간 섹션 - 검사 히스토리와 사용자 활동 추이 */}
          <CommonMiddleSection 
            currentPage={currentPage}
            inspectionHistory={inspectionHistory}
            loading={loading}
            error={error}
            onInspectionPeriodChange={handleInspectionPeriodChange}
          />

          {/* YT 필드 분석 테이블 - 공통 컴포넌트 */}
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

export default YTPage;

