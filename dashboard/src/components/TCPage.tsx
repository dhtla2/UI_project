import React, { useState, useEffect } from 'react';
import Sidebar from './layout/Sidebar';
import TopTabs from './layout/TopTabs';
// import TCQualityDetails from './dashboard/TCQualityDetails';
import CommonTopSection from './common/CommonTopSection';
import CommonMiddleSection from './common/CommonMiddleSection';
import CommonSideSection from './common/CommonSideSection';
import CommonFieldAnalysisSection from './common/CommonFieldAnalysisSection';
import TCInspectionHistory from './dashboard/TCInspectionHistory';
import TCFieldAnalysisTable from './dashboard/TCFieldAnalysisTable';
// import InspectionResultsSection from './common/InspectionResultsSection';
import MostAccessedAPIs from './dashboard/MostAccessedAPIs';
import BestQualityAPIs from './dashboard/BestQualityAPIs';
import WorstQualityAPIs from './dashboard/WorstQualityAPIs';
import { fetchAPIQualityData, APIQualityData, fetchTCQualityStatus, TCQualityStatusData, fetchTCQualitySummary, TCQualitySummaryData, fetchLatestInspectionResults, LatestInspectionResults, fetchTCInspectionHistory, TCInspectionHistoryData } from '../services/apiService';
import '../styles/DashboardLayout.css';

interface TCData {
  totalWork: number;
  totalTerminals: number;
  totalShips: number;
  totalContainers: number;
  workDays: number;
  recentWork: number;
  activeTerminals: number;
  activeShips: number;
  workTypes: Array<{ workType: string; count: number }>;
  terminals: Array<{ terminalId: string; terminalName: string; count: number }>;
  lastInspectionDate?: string;
}

interface TCHistoryData {
  date: string;
  totalWork: number;
  terminals: number;
  ships: number;
  containers: number;
}

interface TCDataQualityStatusData {
  workEfficiency: { status: string; rate: number; lastCheck: string };
  terminalUtilization: { status: string; rate: number; lastCheck: string };
  overall: { status: string; score: number; lastUpdate: string };
  alerts: Array<{ type: string; message: string; timestamp: string }>;
}

interface TCFieldAnalysisData {
  field: string;
  totalChecks: number;
  passCount: number;
  failCount: number;
  passRate: number;
  commonIssues: string[];
}

interface TCPageProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  onPageChange: (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck') => void;
}

const TCPage: React.FC<TCPageProps> = ({ currentPage, onPageChange }) => {
  // 상태 관리
  const [apiQualityData, setApiQualityData] = useState<APIQualityData[]>([]);
  const [tcData, setTcData] = useState<TCData>({
    totalWork: 0,
    totalTerminals: 0,
    totalShips: 0,
    totalContainers: 0,
    workDays: 0,
    recentWork: 0,
    activeTerminals: 0,
    activeShips: 0,
    workTypes: [],
    terminals: []
  });
  const [historyData, setHistoryData] = useState<TCHistoryData[]>([]);
  const [fieldAnalysisData, setFieldAnalysisData] = useState<TCFieldAnalysisData[]>([]);
  const [inspectionHistory, setInspectionHistory] = useState<TCInspectionHistoryData[]>([]);
  const [tcQualityStatus, setTcQualityStatus] = useState<TCQualityStatusData | null>(null);
  const [tcQualitySummary, setTcQualitySummary] = useState<TCQualitySummaryData | null>(null);
  const [latestInspectionResults, setLatestInspectionResults] = useState<LatestInspectionResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 검사 히스토리 로드 함수 (기간별)
  const loadInspectionHistory = async (period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily', startDate?: string, endDate?: string) => {
    try {
      const historyData = await fetchTCInspectionHistory(period, startDate, endDate);
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

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // TC 데이터와 공통 API 데이터를 병렬로 로드 (Promise.allSettled 사용)
        const results = await Promise.allSettled([
          fetch('/api/dashboard/tc-summary'),
          fetch('/api/dashboard/tc-work-history'),
          fetchTCQualityStatus(),
          fetchTCQualitySummary(),
          fetchAPIQualityData(),
          fetchLatestInspectionResults('TC'),
          fetchTCInspectionHistory('daily')
        ]);

        // 성공한 API 결과들만 처리
        const [tcSummaryResult, tcHistoryResult, tcQualityResult, tcQualitySummaryResult, commonApiResult, latestResults, inspectionHistoryResult] = results;

        // TC 요약 데이터 처리
        if (tcSummaryResult.status === 'fulfilled' && tcSummaryResult.value.ok) {
          const tcSummaryData = await tcSummaryResult.value.json();
          setTcData(tcSummaryData);
        } else {
          console.warn('TC 요약 데이터 로드 실패:', tcSummaryResult);
        }

        // TC 히스토리 데이터 처리
        if (tcHistoryResult.status === 'fulfilled' && tcHistoryResult.value.ok) {
          const tcHistoryData = await tcHistoryResult.value.json();
          setHistoryData(tcHistoryData);
        } else {
          console.warn('TC 히스토리 데이터 로드 실패:', tcHistoryResult);
        }

        // TC 품질 상태 데이터 처리
        if (tcQualityResult.status === 'fulfilled') {
          setTcQualityStatus(tcQualityResult.value);
        } else {
          console.warn('TC 품질 상태 데이터 로드 실패:', tcQualityResult.reason);
          setTcQualityStatus(null);
        }

        // TC 품질 요약 데이터 처리
        if (tcQualitySummaryResult.status === 'fulfilled') {
          setTcQualitySummary(tcQualitySummaryResult.value);
        } else {
          console.warn('TC 품질 요약 데이터 로드 실패:', tcQualitySummaryResult.reason);
          setTcQualitySummary(null);
        }

        // 공통 API 데이터 처리
        if (commonApiResult.status === 'fulfilled') {
          setApiQualityData(commonApiResult.value);
        } else {
          console.warn('공통 API 데이터 로드 실패:', commonApiResult.reason);
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

        // setDataQualityStatus({
        //   workEfficiency: { status: 'PASS', rate: 85.2, lastCheck: '2024-09-08 10:30' },
        //   terminalUtilization: { status: 'PASS', rate: 78.5, lastCheck: '2024-09-08 10:30' },
        //   overall: { status: 'PASS', score: 81.8, lastUpdate: '2024-09-08 10:30' },
        //   alerts: []
        // });

      } catch (err) {
        console.error('TC 데이터 로드 실패:', err);
        setError('데이터를 불러오는데 실패했습니다.');
        // 에러 발생 시 빈 배열로 설정
        setApiQualityData([]);
        setTcData({
          totalWork: 0,
          totalTerminals: 0,
          totalShips: 0,
          totalContainers: 0,
          workDays: 0,
          recentWork: 0,
          activeTerminals: 0,
          activeShips: 0,
          workTypes: [],
          terminals: []
        });
        setHistoryData([]);
        setFieldAnalysisData([]);
        // setDataQualityStatus(null);
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
              tcData={{
                tcData,
                historyData,
                tcQualityStatus,
                tcQualitySummary
              }}
            />


            {/* 검사 결과 섹션 - 완전성, 유효성, 사용성 검사 결과
            <InspectionResultsSection 
              currentPage={currentPage}
              data={latestInspectionResults ? {
                completeness: {
                  ...latestInspectionResults.completeness,
                  last_updated: latestInspectionResults.completeness.last_updated || undefined
                },
                validity: {
                  ...latestInspectionResults.validity,
                  last_updated: latestInspectionResults.validity.last_updated || undefined
                },
                ...(latestInspectionResults.usage && { 
                  usage: {
                    ...latestInspectionResults.usage,
                    last_updated: latestInspectionResults.usage.last_updated || undefined
                  }
                })
              } : {}}
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

            {/* TC 필드별 상세 분석 테이블 - 공통 컴포넌트 */}
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

export default TCPage;