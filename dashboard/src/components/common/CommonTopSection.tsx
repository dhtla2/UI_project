import React from 'react';
import CommonDataQualitySection from './CommonDataQualitySection';
import { APIQualityData } from '../../services/apiService';

// 각 페이지별 데이터 타입들
interface AISData {
  overall: {
    total: number;
    pass: number;
    fail: number;
    pass_rate: number;
  };
  completeness: {
    total: number;
    pass: number;
    fail: number;
    pass_rate: number;
  };
  validity: {
    total: number;
    pass: number;
    fail: number;
    pass_rate: number;
  };
}

interface TOSData {
  tosQualitySummary: any;
  tosQualityDetails?: any;
}

interface TCData {
  tcData: any;
  historyData: any;
  tcQualityStatus: any;
  tcQualitySummary?: any;
}

interface QCData {
  qcData: any;
  historyData: any;
  qcQualityStatus: any;
  qcQualitySummary?: any;
}

interface MatchData {
  matchQualitySummary: any;
}

interface VsslSpecData {
  vsslSpecSummary: any;
}

interface CommonTopSectionProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  loading: boolean;
  error: string | null;
  apiQualityData: APIQualityData[];
  
  // 페이지별 데이터
  aisData?: any;
  tosData?: TOSData;
  tcData?: TCData;
  qcData?: QCData;
  ytData?: any;
  matchData?: MatchData;
  vsslSpecData?: VsslSpecData;
}

const CommonTopSection: React.FC<CommonTopSectionProps> = ({
  currentPage,
  loading,
  error,
  apiQualityData,
  aisData,
  tosData,
  tcData,
  qcData,
  ytData,
  matchData,
  vsslSpecData
}) => {
  // QualityCheck 페이지는 데이터 품질 대시보드를 표시하지 않음
  if (currentPage === 'QualityCheck') {
    return null;
  }

  return (
    <CommonDataQualitySection
      currentPage={currentPage as 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck'}
      loading={loading}
      error={error}
      apiQualityData={apiQualityData}
      aisData={aisData}
      tosData={tosData}
      tcData={tcData}
      qcData={qcData}
      ytData={ytData}
      matchData={matchData}
      vsslSpecData={vsslSpecData}
    />
  );
};

export default CommonTopSection;
