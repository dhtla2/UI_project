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
import { fetchAPIQualityData, APIQualityData, fetchTCQualityStatus, TCQualityStatusData, fetchTCQualitySummary, TCQualitySummaryData, fetchLatestInspectionResults, LatestInspectionResults } from '../services/apiService';
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

interface TCInspectionHistoryData {
  inspectionId: string;
  inspectionDatetime: string;
  totalChecks: number;
  passCount: number;
  failCount: number;
  passRate: number;
  completenessRate?: number;
  validityRate?: number;
}

interface TCPageProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'QualityCheck';
  onPageChange: (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'QualityCheck') => void;
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
          fetchLatestInspectionResults('TC')
        ]);

        // 성공한 API 결과들만 처리
        const [tcSummaryResult, tcHistoryResult, tcQualityResult, tcQualitySummaryResult, commonApiResult, latestResults] = results;

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

        // 모의 데이터 설정 (실제 API가 구현되면 교체)
        setFieldAnalysisData([
          {
            field: '작업 ID',
            totalChecks: 150,
            passCount: 145,
            failCount: 5,
            passRate: 96.7,
            commonIssues: ['누락된 ID', '잘못된 형식']
          },
          {
            field: '터미널 ID',
            totalChecks: 150,
            passCount: 150,
            failCount: 0,
            passRate: 100.0,
            commonIssues: []
          },
          {
            field: '선박 코드',
            totalChecks: 150,
            passCount: 142,
            failCount: 8,
            passRate: 94.7,
            commonIssues: ['잘못된 선박 코드', '누락된 정보']
          }
        ]);

        // setDataQualityStatus({
        //   workEfficiency: { status: 'PASS', rate: 85.2, lastCheck: '2024-09-08 10:30' },
        //   terminalUtilization: { status: 'PASS', rate: 78.5, lastCheck: '2024-09-08 10:30' },
        //   overall: { status: 'PASS', score: 81.8, lastUpdate: '2024-09-08 10:30' },
        //   alerts: []
        // });

        setInspectionHistory([
          {
            inspectionId: 'tc_work_20240903_001',
            inspectionDatetime: '2025-09-03 10:11',
            totalChecks: 30,
            passCount: 25,
            failCount: 5,
            passRate: 83.3,
            completenessRate: 82.8,
            validityRate: 100.0
          },
          {
            inspectionId: 'tc_work_20240903_002',
            inspectionDatetime: '2025-09-03 13:19',
            totalChecks: 30,
            passCount: 25,
            failCount: 5,
            passRate: 83.3,
            completenessRate: 82.8,
            validityRate: 100.0
          },
          {
            inspectionId: 'tc_work_20240903_003',
            inspectionDatetime: '2025-09-03 13:50',
            totalChecks: 30,
            passCount: 25,
            failCount: 5,
            passRate: 83.3,
            completenessRate: 82.8,
            validityRate: 100.0
          }
        ]);

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
              inspectionHistory={inspectionHistory.map(record => ({
                date: record.inspectionDatetime.split(' ')[0], // 날짜 부분만 추출
                score: record.passRate,
                totalChecks: record.totalChecks,
                passedChecks: record.passCount,
                failedChecks: record.failCount,
                completenessRate: record.completenessRate || 0,
                validityRate: record.validityRate || 0
              }))}
              loading={loading}
              error={error}
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