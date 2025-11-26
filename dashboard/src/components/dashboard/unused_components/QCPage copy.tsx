import React, { useState, useEffect } from 'react';
import Sidebar from './layout/Sidebar';
import TopTabs from './layout/TopTabs';
// import QCQualityDetails from './dashboard/QCQualityDetails';
import CommonTopSection from './common/CommonTopSection';
import CommonMiddleSection from './common/CommonMiddleSection';
import CommonSideSection from './common/CommonSideSection';
import CommonFieldAnalysisSection from './common/CommonFieldAnalysisSection';
import QCInspectionHistory from './dashboard/QCInspectionHistory';
import QCFieldAnalysisTable from './dashboard/QCFieldAnalysisTable';
// import InspectionResultsSection from './common/InspectionResultsSection';
import MostAccessedAPIs from './dashboard/MostAccessedAPIs';
import BestQualityAPIs from './dashboard/BestQualityAPIs';
import WorstQualityAPIs from './dashboard/WorstQualityAPIs';
import { fetchAPIQualityData, APIQualityData, fetchQCQualityStatus, QCQualityStatusData, fetchQCQualitySummary, QCQualitySummaryData, fetchLatestInspectionResults, LatestInspectionResults } from '../services/apiService';
import portImage from '../images/port.jpg';
import '../styles/DashboardLayout.css';

interface QCPageProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'QualityCheck';
  onPageChange: (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'QualityCheck') => void;
}

interface QCData {
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

interface QCHistoryData {
  date: string;
  totalWork: number;
  terminals: number;
  ships: number;
  containers: number;
}

interface QCDataQualityStatusData {
  workEfficiency: { status: string; rate: number; lastCheck: string };
  terminalUtilization: { status: string; rate: number; lastCheck: string };
  overall: { status: string; score: number; lastUpdate: string };
  alerts: Array<{ type: string; message: string; timestamp: string }>;
}

interface QCFieldAnalysisData {
  field: string;
  totalChecks: number;
  passCount: number;
  failCount: number;
  passRate: number;
  commonIssues: string[];
}

interface QCInspectionHistoryData {
  inspectionId: string;
  inspectionDatetime: string;
  totalChecks: number;
  passCount: number;
  failCount: number;
  passRate: number;
  completenessRate?: number;
  validityRate?: number;
}

const QCPage: React.FC<QCPageProps> = ({ currentPage, onPageChange }) => {
  // 상태 관리
  const [apiQualityData, setApiQualityData] = useState<APIQualityData[]>([]);
  const [qcData, setQcData] = useState<QCData>({
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
  const [historyData, setHistoryData] = useState<QCHistoryData[]>([]);
  const [fieldAnalysisData, setFieldAnalysisData] = useState<QCFieldAnalysisData[]>([]);
  const [inspectionHistory, setInspectionHistory] = useState<QCInspectionHistoryData[]>([]);
  const [qcQualityStatus, setQcQualityStatus] = useState<QCQualityStatusData | null>(null);
  const [qcQualitySummary, setQcQualitySummary] = useState<QCQualitySummaryData | null>(null);
  const [latestInspectionResults, setLatestInspectionResults] = useState<LatestInspectionResults | null>(null);
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
        
        // QC 품질 데이터와 검사 히스토리를 병렬로 로드 (Promise.allSettled 사용)
        const results = await Promise.allSettled([
          fetch('/api/dashboard/qc-summary'),
          fetch('/api/dashboard/qc-work-history'),
          fetchQCQualityStatus(),
          fetchQCQualitySummary(),
          fetchAPIQualityData(),
          fetchLatestInspectionResults('QC')
        ]);

        // 성공한 API 결과들만 처리
        const [qcSummaryResult, qcHistoryResult, qcQualityResult, qcQualitySummaryResult, commonApiResult, latestResults] = results;

        // QC 요약 데이터 처리
        if (qcSummaryResult.status === 'fulfilled' && qcSummaryResult.value.ok) {
          const qcSummaryData = await qcSummaryResult.value.json();
          setQcData(qcSummaryData);
        } else {
          console.warn('QC 요약 데이터 로드 실패:', qcSummaryResult);
        }

        // QC 히스토리 데이터 처리
        if (qcHistoryResult.status === 'fulfilled' && qcHistoryResult.value.ok) {
          const qcHistoryData = await qcHistoryResult.value.json();
          setHistoryData(qcHistoryData);
        } else {
          console.warn('QC 히스토리 데이터 로드 실패:', qcHistoryResult);
          // Mock 히스토리 데이터 설정
          setHistoryData([]);
        }

        // QC 품질 상태 데이터 처리
        if (qcQualityResult.status === 'fulfilled') {
          setQcQualityStatus(qcQualityResult.value);
        } else {
          console.warn('QC 품질 상태 데이터 로드 실패:', qcQualityResult.reason);
          setQcQualityStatus(null);
        }

        // QC 품질 요약 데이터 처리
        if (qcQualitySummaryResult.status === 'fulfilled') {
          setQcQualitySummary(qcQualitySummaryResult.value);
        } else {
          console.warn('QC 품질 요약 데이터 로드 실패:', qcQualitySummaryResult.reason);
          setQcQualitySummary(null);
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

        // Mock 데이터 설정
        setFieldAnalysisData([
          {
            field: 'serNo',
            totalChecks: 100,
            passCount: 95,
            failCount: 5,
            passRate: 95.0,
            commonIssues: ['범위 초과', '형식 오류']
          },
          {
            field: 'callYr',
            totalChecks: 100,
            passCount: 98,
            failCount: 2,
            passRate: 98.0,
            commonIssues: ['유효하지 않은 연도']
          }
        ]);

        // setDataQualityStatus({
        //   workEfficiency: { status: 'PASS', rate: 85.5, lastCheck: '2025-09-12 10:30:00' },
        //   terminalUtilization: { status: 'PASS', rate: 92.3, lastCheck: '2025-09-12 10:30:00' },
        //   overall: { status: 'PASS', score: 88.9, lastUpdate: '2025-09-12 10:30:00' },
        //   alerts: [
        //     { type: 'warning', message: '작업 효율성이 기준치보다 낮습니다.', timestamp: '2025-09-12 09:15:00' }
        //   ]
        // });

        setInspectionHistory([
          {
            inspectionId: 'qc_inspection_001',
            inspectionDatetime: '2025-09-12 10:00:00',
            totalChecks: 50,
            passCount: 45,
            failCount: 5,
            passRate: 90.0,
            completenessRate: 85.0,
            validityRate: 95.0
          },
          {
            inspectionId: 'qc_inspection_002',
            inspectionDatetime: '2025-09-11 15:30:00',
            totalChecks: 48,
            passCount: 44,
            failCount: 4,
            passRate: 91.7,
            completenessRate: 88.0,
            validityRate: 92.0
          }
        ]);

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
              qcData={{
                qcData,
                historyData,
                qcQualityStatus,
                qcQualitySummary
              }}
            />


          {/* 검사 결과 섹션 - 완전성과 유효성 검사 결과
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
              }
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

          {/* QC 필드 분석 테이블 - 공통 컴포넌트 */}
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

export default QCPage;