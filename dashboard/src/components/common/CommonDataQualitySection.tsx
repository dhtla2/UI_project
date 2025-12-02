import React from 'react';
import UnifiedDataQuality from './UnifiedDataQuality';
import MostAccessedAPIs from '../dashboard/MostAccessedAPIs';
import BestQualityAPIs from '../dashboard/BestQualityAPIs';
import WorstQualityAPIs from '../dashboard/WorstQualityAPIs';
import { APIQualityData } from '../../services/apiService';

// 각 페이지별 데이터 타입들
interface AISData {
  // AIS 관련 데이터 타입들 - any로 처리
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

interface CommonDataQualitySectionProps {
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

const CommonDataQualitySection: React.FC<CommonDataQualitySectionProps> = ({
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
  const renderDataQuality = () => {
    switch (currentPage) {
      case 'AIS':
        return <UnifiedDataQuality pageType="AIS" data={aisData as any} />;
      case 'TOS':
        return <UnifiedDataQuality pageType="TOS" data={tosData?.tosQualitySummary} />;
      case 'TC':
        return <UnifiedDataQuality pageType="TC" data={tcData?.tcQualitySummary} />;
      case 'QC':
        return <UnifiedDataQuality pageType="QC" data={qcData?.qcQualitySummary} />;
      case 'YT':
        return <UnifiedDataQuality pageType="YT" data={ytData?.ytQualitySummary} />;
      case 'PortMisVsslNo':
        return <UnifiedDataQuality pageType="PortMisVsslNo" data={matchData?.matchQualitySummary} />;
      case 'TosVsslNo':
        return <UnifiedDataQuality pageType="TosVsslNo" data={matchData?.matchQualitySummary} />;
      case 'VsslSpecInfo':
        return <UnifiedDataQuality pageType="VsslSpecInfo" data={vsslSpecData?.vsslSpecSummary} />;
      default:
        return null;
    }
  };


  // 모든 페이지에 동일한 레이아웃 적용 (품질 대시보드 1/2, API 위젯들 1/6씩)
  return (
    <div className="px-6 mb-6">
      <div className="flex gap-4 w-full">
        <div className="dashboard-card h-80 w-1/2">
          {renderDataQuality()}
        </div>
        <div className="dashboard-card h-80 w-1/6">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500">로딩 중...</div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-red-500 text-sm">{error}</div>
            </div>
          ) : (
            <MostAccessedAPIs data={apiQualityData} />
          )}
        </div>
        <div className="dashboard-card h-80 w-1/6">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500">로딩 중...</div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-red-500 text-sm">{error}</div>
            </div>
          ) : (
            <BestQualityAPIs data={apiQualityData} />
          )}
        </div>
        <div className="dashboard-card h-80 w-1/6">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500">로딩 중...</div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-red-500 text-sm">{error}</div>
            </div>
          ) : (
            <WorstQualityAPIs data={apiQualityData} />
          )}
        </div>
      </div>
    </div>
  );
};

export default CommonDataQualitySection;
