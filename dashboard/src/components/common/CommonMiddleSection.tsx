import React from 'react';
import InspectionHistory from '../dashboard/InspectionHistory';
import Dash01 from '../dashboard/Dash01';

// InspectionHistory 컴포넌트가 기대하는 타입
interface InspectionRecord {
  date: string;
  score: number;
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  completenessRate: number;
  validityRate: number;
}

interface CommonMiddleSectionProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  inspectionHistory: InspectionRecord[];
  loading?: boolean;
  error?: string | null;
  onInspectionPeriodChange?: (period: 'daily' | 'weekly' | 'monthly' | 'custom', startDate?: string, endDate?: string) => void;
}

const CommonMiddleSection: React.FC<CommonMiddleSectionProps> = ({
  currentPage,
  inspectionHistory,
  loading = false,
  error = null,
  onInspectionPeriodChange
}) => {
  return (
    <div className="px-6 mb-6">
      <div className="flex gap-6 mb-6 w-5/6">
        {/* 검사 히스토리 추이 */}
        <div className="dashboard-card h-112 w-1/2">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500">로딩 중...</div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-red-500 text-sm">{error}</div>
            </div>
          ) : (
            <InspectionHistory 
              history={inspectionHistory} 
              currentPage={currentPage}
              onPeriodChange={onInspectionPeriodChange}
            />
          )}
        </div>
        
        {/* 사용자 활동 추이 */}
        <div className="dashboard-card h-112 w-1/2">
          <Dash01 />
        </div>
      </div>
    </div>
  );
};

export default CommonMiddleSection;
