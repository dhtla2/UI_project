import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { 
  AISQualitySummary, 
  TOSQualitySummaryData, 
  TCQualitySummaryData, 
  QCQualitySummaryData,
  VsslSpecSummaryData,
  FieldAnalysisData,
  fetchAISQualitySummary,
  fetchTOSQualitySummary,
  fetchTCQualitySummary,
  fetchQCQualitySummary,
  fetchPortVsslSummary,
  fetchTosVsslSummary,
  fetchVsslSpecSummary,
  fetchAISFieldAnalysis,
  fetchTOSFieldAnalysis,
  fetchTCFieldAnalysis,
  fetchQCFieldAnalysis,
  fetchPortVsslFieldAnalysis,
  fetchTosVsslFieldAnalysis,
  fetchVsslSpecFieldAnalysis
} from '../../services/apiService';

// 통합된 품질 데이터 타입
type QualitySummaryData = AISQualitySummary | TOSQualitySummaryData | TCQualitySummaryData | QCQualitySummaryData | any;

interface UnifiedDataQualityProps {
  pageType: 'AIS' | 'TOS' | 'TC' | 'QC' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo';
  data?: QualitySummaryData | null;
  onDataLoad?: (data: QualitySummaryData) => void;
}

// 툴팁 위치 타입 정의
interface TooltipPosition {
  top: number;
  left: number;
}

const UnifiedDataQuality: React.FC<UnifiedDataQualityProps> = ({ 
  pageType, 
  data,
  onDataLoad 
}) => {
  const [qualityData, setQualityData] = useState<QualitySummaryData | null>(data || null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // 필드 분석 데이터 및 메시지 순환 state
  const [fieldAnalysisData, setFieldAnalysisData] = useState<any>(null);
  const [completenessMessages, setCompletenessMessages] = useState<string[]>([]);
  const [validityMessages, setValidityMessages] = useState<string[]>([]);
  const [currentCompletenessIndex, setCurrentCompletenessIndex] = useState(0);
  const [currentValidityIndex, setCurrentValidityIndex] = useState(0);

  // 툴팁 상태 관리
  const [showTooltips, setShowTooltips] = useState<Record<string, boolean>>({
    totalInspections: false,
    passRate: false,
    totalChecks: false,
    lastInspection: false,
    completeness: false,
    validity: false
  });

  // 툴팁 위치 상태
  const [tooltipPositions, setTooltipPositions] = useState<Record<string, TooltipPosition>>({});
  
  // 버튼 ref들을 저장할 객체
  const buttonRefs = useRef<Record<string, HTMLButtonElement | null>>({});

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

    // 패널별 상세 설명 추가
    completeness: `📊 데이터 활용도 확보
필수 필드에 값이 존재하는지 확인합니다

✓ 검사 내용:
  • NULL 및 빈값 탐지
  • 필수 필드 누락 확인
  • 데이터 입력 완료도 평가

• 결과 영향:
  → 분석 가능한 데이터 비율 확인
  → 데이터 수집 프로세스 품질 평가
  → 의사결정에 필요한 데이터 준비 상태 진단`,

    validity: `✅ 데이터 신뢰성 보장
데이터가 올바른 형식과 범위를 가지는지 검증합니다

✓ 검사 내용:
  • 날짜/시간 형식 검증
  • 코드 유효성 확인
  • 숫자 범위 및 논리적 타당성

• 결과 영향:
  → 시스템 연동 오류 방지
  → 데이터 신뢰도 확보
  → 비정상 데이터로 인한 분석 왜곡 방지`
  };

  // 툴팁 위치 계산 함수
  const calculateTooltipPosition = (buttonElement: HTMLButtonElement): TooltipPosition => {
    const rect = buttonElement.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    
    return {
      top: rect.bottom + scrollTop + 10, // 버튼 아래쪽에 10px 간격
      left: rect.left + scrollLeft - 150  // 툴팁 너비의 절반 정도 왼쪽으로 조정
    };
  };

  // 툴팁 표시 함수
  const showTooltip = (key: string) => {
    const buttonElement = buttonRefs.current[key];
    if (buttonElement) {
      const position = calculateTooltipPosition(buttonElement);
      setTooltipPositions(prev => ({ ...prev, [key]: position }));
    }
    setShowTooltips(prev => ({ ...prev, [key]: true }));
  };

  // 툴팁 숨기기 함수
  const hideTooltip = (key: string) => {
    setShowTooltips(prev => ({ ...prev, [key]: false }));
  };

  // 툴팁 토글 함수
  const toggleTooltip = (key: string) => {
    if (showTooltips[key]) {
      hideTooltip(key);
    } else {
      showTooltip(key);
    }
  };
  
  // 페이지별 API 함수 매핑
  const getFetchFunction = (pageType: string) => {
    switch (pageType) {
      case 'AIS': return fetchAISQualitySummary;
      case 'TOS': return fetchTOSQualitySummary;
      case 'TC': return fetchTCQualitySummary;
      case 'QC': return fetchQCQualitySummary;
      case 'PortMisVsslNo': return fetchPortVsslSummary;
      case 'TosVsslNo': return fetchTosVsslSummary;
      case 'VsslSpecInfo': return fetchVsslSpecSummary;
      default: return fetchAISQualitySummary;
    }
  };

  // 페이지별 필드 분석 API 함수 매핑
  const getFieldAnalysisFetchFunction = (pageType: string) => {
    switch (pageType) {
      case 'AIS': return fetchAISFieldAnalysis;
      case 'TOS': return fetchTOSFieldAnalysis;
      case 'TC': return fetchTCFieldAnalysis;
      case 'QC': return fetchQCFieldAnalysis;
      case 'PortMisVsslNo': return fetchPortVsslFieldAnalysis;
      case 'TosVsslNo': return fetchTosVsslFieldAnalysis;
      case 'VsslSpecInfo': return fetchVsslSpecFieldAnalysis;
      default: return fetchAISFieldAnalysis;
    }
  };

  // 페이지별 제목 매핑
  const getPageTitle = (pageType: string) => {
    switch (pageType) {
      case 'AIS': return 'AIS 데이터 품질 요약';
      case 'TOS': return 'TOS 데이터 품질 요약';
      case 'TC': return 'TC 데이터 품질 요약';
      case 'QC': return 'QC 데이터 품질 요약';
      case 'PortMisVsslNo': return 'PMIS→TOS 데이터 품질 요약';
      case 'TosVsslNo': return 'TOS→PMIS 데이터 품질 요약';
      case 'VsslSpecInfo': return '선박제원 데이터 품질 요약';
      default: return '데이터 품질 요약';
    }
  };

  // 페이지별 검사 패널 구성
  const getInspectionPanels = (pageType: string) => {
    // 완전성 검사 메시지 동적 생성
    const getCompletenessDescription = () => {
      if (completenessMessages.length === 0) {
        return '✅ 특이 사항 없음';
      } else {
        return completenessMessages[currentCompletenessIndex];
      }
    };

    // 유효성 검사 메시지 동적 생성
    const getValidityDescription = () => {
      if (validityMessages.length === 0) {
        return '✅ 특이 사항 없음';
      } else {
        return validityMessages[currentValidityIndex];
      }
    };

    const basePanels = [
      {
        type: 'completeness',
        title: '완전성 검사',
        subtitle: '데이터 활용도 확보를 위해 필드에 값이 존재하는지 확인합니다.',
        color: 'bg-blue-500',
        borderColor: 'border-blue-200',
        bgColor: 'bg-blue-50',
        data: qualityData?.completeness,
        description: getCompletenessDescription()
      },
      {
        type: 'validity',
        title: '유효성 검사',
        subtitle: '데이터 신뢰성 보장을 위해 형식 및 범위 적합성을 검증합니다.',
        color: 'bg-green-500',
        borderColor: 'border-green-200',
        bgColor: 'bg-green-50',
        data: qualityData?.validity,
        description: getValidityDescription()
      }
    ];

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

  // 필드 분석 데이터 로드 및 완전성/유효성 실패 메시지 필터링
  useEffect(() => {
    const loadFieldAnalysis = async () => {
      try {
        const fetchFunction = getFieldAnalysisFetchFunction(pageType);
        const result: any = await fetchFunction();
        setFieldAnalysisData(result);
        
        let failedCompletenessMessages: string[] = [];
        let failedValidityMessages: string[] = [];
        
        // TOS 페이지는 다른 데이터 구조 사용
        if (pageType === 'TOS' && Array.isArray(result)) {
          // TOS는 배열 형태로 반환됨
          failedCompletenessMessages = result
            .filter((item: any) => item.group === 'completeness' && item.status === 'FAIL')
            .map((item: any) => `${item.field}: ${item.message || '누락됨'}`)
            .filter((msg: string) => msg && msg.trim() !== '');
          
          failedValidityMessages = result
            .filter((item: any) => item.group === 'validity' && item.status === 'FAIL')
            .map((item: any) => `${item.field}: ${item.message || '유효하지 않음'}`)
            .filter((msg: string) => msg && msg.trim() !== '');
        } else if (result && result.field_statistics) {
          // 다른 페이지들은 field_statistics 사용
          failedCompletenessMessages = result.field_statistics
            .filter((stat: any) => stat.check_type === 'completeness' && stat.fail_count > 0)
            .map((stat: any) => {
              // original_message가 있으면 사용, 없으면 field_name과 affected_rows로 생성
              if (stat.original_message && stat.original_message.trim() !== '') {
                return stat.original_message;
              } else {
                return `${stat.field_name}: ${stat.affected_rows}개 레코드에서 누락됨`;
              }
            })
            .filter((msg: string) => msg && msg.trim() !== ''); // 빈 메시지 제거
          
          failedValidityMessages = result.field_statistics
            .filter((stat: any) => stat.check_type === 'validity' && stat.fail_count > 0)
            .map((stat: any) => {
              // original_message가 있으면 사용, 없으면 field_name과 affected_rows로 생성
              if (stat.original_message && stat.original_message.trim() !== '') {
                return stat.original_message;
              } else {
                return `${stat.field_name}: ${stat.affected_rows}개 레코드에서 유효하지 않음`;
              }
            })
            .filter((msg: string) => msg && msg.trim() !== ''); // 빈 메시지 제거
        }
        
        setCompletenessMessages(failedCompletenessMessages);
        setValidityMessages(failedValidityMessages);
        setCurrentCompletenessIndex(0); // 인덱스 초기화
        setCurrentValidityIndex(0); // 인덱스 초기화
      } catch (err) {
        console.error(`${pageType} 필드 분석 데이터 로드 실패:`, err);
        setCompletenessMessages([]);
        setValidityMessages([]);
      }
    };
    
    loadFieldAnalysis();
  }, [pageType]);

  // 완전성 메시지 순환 타이머
  useEffect(() => {
    if (completenessMessages.length <= 1) {
      return; // 메시지가 1개 이하면 순환할 필요 없음
    }

    const timer = setInterval(() => {
      setCurrentCompletenessIndex((prevIndex) => 
        (prevIndex + 1) % completenessMessages.length
      );
    }, 3000); // 3초마다 메시지 변경

    return () => clearInterval(timer);
  }, [completenessMessages]);

  // 유효성 메시지 순환 타이머
  useEffect(() => {
    if (validityMessages.length <= 1) {
      return; // 메시지가 1개 이하면 순환할 필요 없음
    }

    const timer = setInterval(() => {
      setCurrentValidityIndex((prevIndex) => 
        (prevIndex + 1) % validityMessages.length
      );
    }, 3000); // 3초마다 메시지 변경

    return () => clearInterval(timer);
  }, [validityMessages]);

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
          <div className="bg-white p-3 rounded-lg shadow text-center">
            <div className="text-xl font-bold text-blue-600">
              {qualityData?.total_inspections || 0}
            </div>
            <div className="text-sm text-gray-600 flex items-center justify-center gap-1">
              총 검사 항목
              <div className="relative">
                <button
                  ref={el => { buttonRefs.current.totalInspections = el; }}
                  className="w-3 h-3 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
                  onMouseEnter={() => showTooltip('totalInspections')}
                  onMouseLeave={() => hideTooltip('totalInspections')}
                  onClick={() => toggleTooltip('totalInspections')}
                >
                  ?
                </button>
              </div>
            </div>
          </div>

          {/* 통과율 */}
          <div className="bg-white p-3 rounded-lg shadow text-center">
            <div className="text-xl font-bold text-green-600">
              {qualityData?.pass_rate?.toFixed(1) || 0}%
            </div>
            <div className="text-sm text-gray-600 flex items-center justify-center gap-1">
              통과율
              <div className="relative">
                <button
                  ref={el => { buttonRefs.current.passRate = el; }}
                  className="w-3 h-3 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
                  onMouseEnter={() => showTooltip('passRate')}
                  onMouseLeave={() => hideTooltip('passRate')}
                  onClick={() => toggleTooltip('passRate')}
                >
                  ?
                </button>
              </div>
            </div>
          </div>

          {/* 검사 대상 */}
          <div className="bg-white p-3 rounded-lg shadow text-center">
            <div className="text-xl font-bold text-purple-600">
              {qualityData?.total_checks || 0}
            </div>
            <div className="text-sm text-gray-600 flex items-center justify-center gap-1">
              검사 대상
              <div className="relative">
                <button
                  ref={el => { buttonRefs.current.totalChecks = el; }}
                  className="w-3 h-3 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
                  onMouseEnter={() => showTooltip('totalChecks')}
                  onMouseLeave={() => hideTooltip('totalChecks')}
                  onClick={() => toggleTooltip('totalChecks')}
                >
                  ?
                </button>
              </div>
            </div>
          </div>

          {/* 마지막 검사 */}
          <div className="bg-white p-3 rounded-lg shadow text-center">
            <div className="text-xl font-bold text-orange-600">
              {qualityData?.last_inspection_date || 'N/A'}
            </div>
            <div className="text-sm text-gray-600 flex items-center justify-center gap-1">
              마지막 검사
              <div className="relative">
                <button
                  ref={el => { buttonRefs.current.lastInspection = el; }}
                  className="w-3 h-3 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
                  onMouseEnter={() => showTooltip('lastInspection')}
                  onMouseLeave={() => hideTooltip('lastInspection')}
                  onClick={() => toggleTooltip('lastInspection')}
                >
                  ?
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 검사 패널들 */}
        <div className={`grid ${gridCols} gap-6 mb-6`}>
        {inspectionPanels.map((panel, index) => (
            <div key={panel.type} className={`bg-white p-4 rounded-lg shadow-lg border-2 ${panel.borderColor}`}>
                
            {/* 패널 헤더 */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center flex-1">
                <div className={`w-3 h-3 ${panel.color} p-2 rounded-full mr-3 flex-shrink-0`}></div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-gray-800 text-left">
                    {panel.title} : <span className="text-xs font-normal text-gray-600">{(panel as any).subtitle}</span>
                  </h3>
                </div>
              </div>

              {/* 물음표 아이콘 */}
              <div className="relative ml-2 flex-shrink-0">
                <button
                  ref={el => { buttonRefs.current[panel.type] = el; }}
                  className="w-4 h-4 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
                  onMouseEnter={() => showTooltip(panel.type)}
                  onMouseLeave={() => hideTooltip(panel.type)}
                  onClick={() => toggleTooltip(panel.type)}
                >
                  ?
                </button>
              </div>
            </div>
            
            {/* 메인 설명 */}
            <div className={`${panel.bgColor} p-3 rounded-lg overflow-hidden`}>
              <div className="text-left px-6">
                <div 
                  key={panel.type === 'completeness' ? currentCompletenessIndex : currentValidityIndex}
                  className="text-sm font-medium text-gray-800 animate-fadeSlideIn"
                  style={{
                    animation: 'fadeSlideIn 0.5s ease-in-out'
                  }}
                >
                  {panel.description}
                </div>
              </div>
            </div>
          </div>
        ))}
        </div>
      </div>

      {/* Portal을 사용한 툴팁들 */}
      {Object.entries(showTooltips).map(([key, isVisible]) => 
        isVisible && tooltipPositions[key] && createPortal(
          <div 
            className="fixed w-80 bg-white text-gray-800 text-sm rounded-lg p-4 shadow-xl border border-gray-200 z-[10000]"
            style={{
              top: `${tooltipPositions[key].top}px`,
              left: `${tooltipPositions[key].left}px`
            }}
          >
            <div className="text-left">
              <div className="font-semibold mb-2 text-base text-gray-900">
                {key === 'totalInspections' && '총 검사 항목'}
                {key === 'passRate' && '통과율'}
                {key === 'totalChecks' && '검사 대상'}
                {key === 'lastInspection' && '마지막 검사'}
                {key === 'completeness' && '완전성 검사 상세 설명'}
                {key === 'validity' && '유효성 검사 상세 설명'}
              </div>
              <div className="text-gray-700 leading-relaxed whitespace-pre-line text-left">
                {tooltipDescriptions[key]}
              </div>
            </div>
            {/* 화살표 */}
            <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-white"></div>
          </div>,
          document.body
        )
      )}
    </div>
  );
};

export default UnifiedDataQuality;