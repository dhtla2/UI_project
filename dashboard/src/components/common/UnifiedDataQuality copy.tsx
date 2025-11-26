import React, { useState, useEffect } from 'react';
import { 
  AISQualitySummary, 
  TOSQualitySummaryData, 
  TCQualitySummaryData, 
  QCQualitySummaryData,
  fetchAISQualitySummary,
  fetchTOSQualitySummary,
  fetchTCQualitySummary,
  fetchQCQualitySummary
} from '../../services/apiService';

// 통합된 품질 데이터 타입
type QualitySummaryData = AISQualitySummary | TOSQualitySummaryData | TCQualitySummaryData | QCQualitySummaryData | any;

interface UnifiedDataQualityProps {
  pageType: 'AIS' | 'TOS' | 'TC' | 'QC';
  data?: QualitySummaryData | null;
  onDataLoad?: (data: QualitySummaryData) => void;
}

const UnifiedDataQuality: React.FC<UnifiedDataQualityProps> = ({ 
  pageType, 
  data,
  onDataLoad 
}) => {
  const [qualityData, setQualityData] = useState<QualitySummaryData | null>(data || null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 툴팁 상태 관리
  const [showTooltips, setShowTooltips] = useState<Record<string, boolean>>({
    totalInspections: false,
    passRate: false,
    totalChecks: false,
    lastInspection: false,
    completeness: false,
    validity: false
  });

  // 각 항목별 설명 정의
  const tooltipDescriptions: Record<string, string> = {
    totalInspections: `데이터 품질 검사를 위해 설정된 전체 검사 항목의 개수입니다.
    
    주요 검사 포함 항목:
    • 완전성 검사: 필수 데이터 누락 확인
    • 유효성 검사: 데이터 형식 및 범위 검증`,
    
    passRate: `전체 검사 항목 중 품질 기준을 통과한 항목의 비율입니다.
    
    품질 평가 기준:
    • 90% 이상: 우수한 데이터 품질
    • 70-89%: 보통 수준의 데이터 품질
    • 70% 미만: 개선이 필요한 데이터 품질`,
    
    totalChecks: `품질 검사를 수행한 전체 데이터 레코드의 개수입니다.
    
    검사 대상 포함 항목:
    • 완전성 검사 대상 레코드 수
    • 유효성 검사 대상 레코드 수
    • 실제 처리된 데이터 건수`,
    
    lastInspection: `가장 최근에 데이터 품질 검사를 실행한 날짜와 시간입니다.
    
    검사 주기 정보:
    • 정기 검사: 일일/주간 단위로 실행
    • 실시간 모니터링: 데이터 입력 시점 검사
    • 최신성 확인: 데이터 품질의 현재 상태 파악`,

  // 패널별 상세 설명 추가 (checkItems 내용 이전)
    completeness: `완전성 검사는 데이터에 빈칸이나 누락된 정보가 있는지 확인하는 검사입니다.

    주요 검사 항목:
    • 데이터 업무 요건에 맞게 항상 채워져 있는지 진단
    • 공간객체가 초과하는 객체들이 존재하는지 진단`,

    validity: `유효성 검사는 데이터가 정해진 유효 범위 내에 존재하는지 진단하는 검사입니다.

    주요 검사 항목:
    • 값이 특정 리스트 내에 존재하여야 하거나, 정해진 유효 범위 내에 존재하는지 진단
    • 데이터 값이 해당 도메인의 형식(Pattern)을 준수하는지 진단
    • 공간정보의 공간적 위치(격자, 좌표계) 범위가 일치하는지 진단`
  };
  
  // 페이지별 API 함수 매핑
  const getFetchFunction = (pageType: string) => {
    switch (pageType) {
      case 'AIS': return fetchAISQualitySummary;
      case 'TOS': return fetchTOSQualitySummary;
      case 'TC': return fetchTCQualitySummary;
      case 'QC': return fetchQCQualitySummary;
      default: return fetchAISQualitySummary;
    }
  };

  // 페이지별 제목 매핑
  const getPageTitle = (pageType: string) => {
    switch (pageType) {
      case 'AIS': return 'AIS 데이터 품질 요약';
      case 'TOS': return 'TOS 데이터 품질 요약';
      case 'TC': return 'TC 데이터 품질 요약';
      case 'QC': return 'QC 데이터 품질 요약';
      default: return '데이터 품질 요약';
    }
  };

  // 페이지별 검사 패널 구성
  const getInspectionPanels = (pageType: string) => {
    const basePanels = [
    {
      type: 'completeness',
      title: '완전성 검사',
      color: 'bg-blue-500',
      borderColor: 'border-blue-200',
      bgColor: 'bg-blue-50',
      data: qualityData?.completeness,
      description: '데이터에 <빈칸>이 있는지 검사'
    },
    {
      type: 'validity',
      title: '유효성 검사',
      color: 'bg-green-500',
      borderColor: 'border-green-200',
      bgColor: 'bg-green-50',
      data: qualityData?.validity,
      description: '정해진 유효 범위 내에 존재하는지 진단'
    }
  ];
    // // TC 페이지는 사용성 검사도 포함
    // if (pageType === 'TC') {
    //   basePanels.push({
    //     type: 'usage',
    //     title: '사용성 검사',
    //     color: 'bg-purple-500',
    //     data: (qualityData as TCQualitySummaryData)?.usage
    //   });
    // }

    return basePanels;
  };

  // 품질 데이터 로드
  useEffect(() => {
    const loadQualityData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        if (!data) {
          const fetchFunction = getFetchFunction(pageType);
          const result = await fetchFunction();
          setQualityData(result);
          onDataLoad?.(result);
        } else {
          setQualityData(data);
          onDataLoad?.(data);
        }
      } catch (err) {
        console.error(`${pageType} 품질 데이터 로드 실패:`, err);
        setError('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };
    
    loadQualityData();
  }, [pageType, data, onDataLoad]);

  if (loading) return <div className="flex items-center justify-center h-full">로딩 중...</div>;
  if (error) return <div className="text-red-500 text-center">오류: {error}</div>;

  const inspectionPanels = getInspectionPanels(pageType);
  const gridCols = inspectionPanels.length === 3 ? 'grid-cols-3' : 'grid-cols-2';

  return (
    <div className="h-full p-2 bg-gray-50">
      {/* 1단계: 전체적인 품질 개요 */}
      <div className="mb-3">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
          {getPageTitle(pageType)}
        </h2>
        
        {/* 상단 통계 카드들 */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          {/* 총 검사 항목 */}
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-blue-600">
              {qualityData?.total_inspections || 0}
            </div>
            <div className="text-sm text-gray-600 flex items-center justify-center gap-1">
              총 검사 항목
              <div className="relative">
                <button
                  className="w-3 h-3 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
                  onMouseEnter={() => setShowTooltips(prev => ({...prev, totalInspections: true}))}
                  onMouseLeave={() => setShowTooltips(prev => ({...prev, totalInspections: false}))}
                  onClick={() => setShowTooltips(prev => ({...prev, totalInspections: !prev.totalInspections}))}
                >
                  ?
                </button>
                
                {showTooltips.totalInspections && (
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 mb-2 w-72 bg-white text-gray-800 text-sm rounded-lg p-4 shadow-xl border border-gray-200 z-50">
                    <div className="text-center">
                      <div className="font-semibold mb-2 text-base text-gray-900">총 검사 항목</div>
                      <div className="text-gray-700 leading-relaxed text-sm whitespace-pre-line text-left">
                        {tooltipDescriptions.totalInspections}
                      </div>
                    </div>
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-white"></div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 통과율 */}
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-green-600">
              {qualityData?.pass_rate?.toFixed(1) || 0}%
            </div>
            <div className="text-sm text-gray-600 flex items-center justify-center gap-1">
              통과율
              <div className="relative">
                <button
                  className="w-3 h-3 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
                  onMouseEnter={() => setShowTooltips(prev => ({...prev, passRate: true}))}
                  onMouseLeave={() => setShowTooltips(prev => ({...prev, passRate: false}))}
                  onClick={() => setShowTooltips(prev => ({...prev, passRate: !prev.passRate}))}
                >
                  ?
                </button>
                
                {showTooltips.passRate && (
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 mb-2 w-72 bg-white text-gray-800 text-sm rounded-lg p-4 shadow-xl border border-gray-200 z-10">
                    <div className="text-center">
                      <div className="font-semibold mb-2 text-base text-gray-900">통과율</div>
                      <div className="text-gray-700 leading-relaxed text-sm whitespace-pre-line text-left">
                        {tooltipDescriptions.passRate}
                      </div>
                    </div>
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-white"></div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 검사 대상 */}
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-purple-600">
              {qualityData?.total_checks || 0}
            </div>
            <div className="text-sm text-gray-600 flex items-center justify-center gap-1">
              검사 대상
              <div className="relative">
                <button
                  className="w-3 h-3 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
                  onMouseEnter={() => setShowTooltips(prev => ({...prev, totalChecks: true}))}
                  onMouseLeave={() => setShowTooltips(prev => ({...prev, totalChecks: false}))}
                  onClick={() => setShowTooltips(prev => ({...prev, totalChecks: !prev.totalChecks}))}
                >
                  ?
                </button>
                
                {showTooltips.totalChecks && (
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 mb-2 w-72 bg-white text-gray-800 text-sm rounded-lg p-4 shadow-xl border border-gray-200 z-10">
                    <div className="text-center">
                      <div className="font-semibold mb-2 text-base text-gray-900">검사 대상</div>
                      <div className="text-gray-700 leading-relaxed text-sm whitespace-pre-line text-left">
                        {tooltipDescriptions.totalChecks}
                      </div>
                    </div>
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-white"></div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 마지막 검사 */}
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-orange-600">
              {qualityData?.last_inspection_date || 'N/A'}
            </div>
            <div className="text-sm text-gray-600 flex items-center justify-center gap-1">
              마지막 검사
              <div className="relative">
                <button
                  className="w-3 h-3 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
                  onMouseEnter={() => setShowTooltips(prev => ({...prev, lastInspection: true}))}
                  onMouseLeave={() => setShowTooltips(prev => ({...prev, lastInspection: false}))}
                  onClick={() => setShowTooltips(prev => ({...prev, lastInspection: !prev.lastInspection}))}
                >
                  ?
                </button>
                
                {showTooltips.lastInspection && (
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 mb-2 w-72 bg-white text-gray-800 text-sm rounded-lg p-4 shadow-xl border border-gray-200 z-10">
                    <div className="text-center">
                      <div className="font-semibold mb-2 text-base text-gray-900">마지막 검사</div>
                      <div className="text-gray-700 leading-relaxed text-sm whitespace-pre-line text-left">
                        {tooltipDescriptions.lastInspection}
                      </div>
                    </div>
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-white"></div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 검사 패널들 */}
        <div className={`grid ${gridCols} gap-6 mb-6`}>
        {inspectionPanels.map((panel, index) => (
            <div key={panel.type} className={`bg-white p-6 rounded-lg shadow-lg border-2 ${panel.borderColor}`}>
                
            {/* 패널 헤더 */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className={`w-3 h-3 ${panel.color} p-2 rounded-full mr-3`}></div>
                <h3 className="text-lg font-semibold text-gray-800">
                  {panel.title}
                </h3>
              </div>

              {/* 물음표 아이콘 */}
              <div className="relative">
                <button
                  className="w-4 h-4 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
                  onMouseEnter={() => setShowTooltips(prev => ({...prev, [panel.type]: true}))}
                  onMouseLeave={() => setShowTooltips(prev => ({...prev, [panel.type]: false}))}
                  onClick={() => setShowTooltips(prev => ({...prev, [panel.type]: !prev[panel.type]}))}
                >
                  ?
                </button>
                
                {/* 툴팁 */}
                {showTooltips[panel.type] && (
                  <div className="absolute top-full right-0 transform mb-2 w-80 bg-white text-gray-800 text-sm rounded-lg p-4 shadow-xl border border-gray-200 z-[10000]">
                    <div className="text-left">
                      <div className="font-semibold mb-2 text-base text-gray-900">{panel.title} 상세 설명</div>
                      <div className="text-gray-700 leading-relaxed whitespace-pre-line text-left">
                        {tooltipDescriptions[panel.type]}
                      </div>
                    </div>
                    {/* 화살표 */}
                    <div className="absolute bottom-full right-4 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-white"></div>
                  </div>
                )}
              </div>
            </div>
            
            {/* 메인 설명 */}
            <div className={`${panel.bgColor} p-2 rounded-lg`}>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-800 mb-3">
                  {panel.description}
                </div>
              </div>
            </div>
          </div>
        ))}
        </div>
      </div>
    </div>
  );
};

export default UnifiedDataQuality;
