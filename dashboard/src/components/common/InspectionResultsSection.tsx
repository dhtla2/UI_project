import React, { useState, useEffect } from 'react';
import { fetchFailedItems, FailedItemData } from '../../services/apiService';

// 각 페이지별 검사 타입 설정
const INSPECTION_CONFIG = {
  'AIS': ['completeness', 'validity'],
  'TOS': ['completeness', 'validity'], 
  'TC': ['completeness', 'validity', 'usage'],
  'QC': ['completeness', 'validity'],
  'YT': ['completeness', 'validity'],
  'PortMisVsslNo': ['completeness', 'validity'],
  'TosVsslNo': ['completeness', 'validity'],
  'VsslSpecInfo': ['completeness', 'validity'],
  'QualityCheck': ['completeness', 'validity'] // QualityCheck 페이지는 기본적으로 완전성과 유효성만
} as const;

// 검사 타입별 한글 이름
const INSPECTION_NAMES = {
  'completeness': '완전성 검사',
  'validity': '유효성 검사',
  'consistency': '일관성 검사',
  'usage': '사용성 검사'
} as const;

// 검사 타입별 아이콘과 색상
const INSPECTION_STYLES = {
  'completeness': {
    icon: '📊',
    color: 'blue',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-600',
    borderColor: 'border-blue-200'
  },
  'validity': {
    icon: '✅',
    color: 'green',
    bgColor: 'bg-green-50',
    textColor: 'text-green-600',
    borderColor: 'border-green-200'
  },
  'consistency': {
    icon: '🔄',
    color: 'purple',
    bgColor: 'bg-purple-50',
    textColor: 'text-purple-600',
    borderColor: 'border-purple-200'
  },
  'usage': {
    icon: '📈',
    color: 'orange',
    bgColor: 'bg-orange-50',
    textColor: 'text-orange-600',
    borderColor: 'border-orange-200'
  }
} as const;

interface InspectionData {
  pass_rate: number;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  fields_checked?: number;
  last_updated?: string;
  failed_items?: Array<{
    field: string;
    reason: string;
    message: string;
  }>;
  fieldAnalysisData?: Array<{
    field: string;
    group: string;
    status: string;
    total: number;
    check: number;
    etc: number;
    message: string;
    checkType: string;
  }>;
}

interface InspectionResultsSectionProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  data: Record<string, InspectionData>;
  loading?: boolean;
  error?: string | null;
}

const InspectionCard: React.FC<{
  type: keyof typeof INSPECTION_NAMES;
  data: InspectionData;
  currentPage: string;
}> = ({ type, data, currentPage }) => {
  const style = INSPECTION_STYLES[type];
  const name = INSPECTION_NAMES[type];
  
  // 각 검사 타입별 간결한 설명 (기본 표시)
  const shortDescriptions = {
    'completeness': '📊 데이터 활용도 확보를 위해 필드에 값이 존재하는지 확인합니다.',
    'validity': '✅ 데이터 신뢰성 보장을 위해 형식 및 범위 적합성을 검증합니다.',
    'consistency': '🔄 데이터 일관성 유지를 위해 논리적 연관성을 확인합니다.',
    'usage': '📈 실무 활용성 평가를 위해 업무 적용 가능성을 진단합니다.'
  };
  
  // 각 검사 타입별 상세 설명 (툴팁용)
  const detailedDescriptions = {
    'completeness': {
      title: '완전성 검사란?',
      summary: '필수 필드에 값이 존재하는지 확인합니다',
      checkItems: [
        'NULL 및 빈값 탐지',
        '필수 필드 누락 확인',
        '데이터 입력 완료도 평가'
      ],
      impact: [
        '분석 가능한 데이터 비율 확인',
        '데이터 수집 프로세스 품질 평가',
        '의사결정에 필요한 데이터 준비 상태 진단'
      ],
      currentStatus: data.fields_checked ? `현재 ${data.fields_checked}개 필드 검사 완료` : ''
    },
    'validity': {
      title: '유효성 검사란?',
      summary: '데이터가 올바른 형식과 범위를 가지는지 검증합니다',
      checkItems: [
        '날짜/시간 형식 검증',
        '코드 유효성 확인',
        '숫자 범위 및 논리적 타당성'
      ],
      impact: [
        '시스템 연동 오류 방지',
        '데이터 신뢰도 확보',
        '비정상 데이터로 인한 분석 왜곡 방지'
      ],
      currentStatus: data.pass_rate >= 90 ? '데이터 품질 우수' : data.pass_rate >= 70 ? '일부 개선 필요' : '즉시 조치 필요'
    },
    'consistency': {
      title: '일관성 검사란?',
      summary: '관련 데이터 간의 논리적 일치성을 확인합니다',
      checkItems: [
        '연관 필드 간 일치성',
        '시간 순서 논리 검증',
        '참조 무결성 확인'
      ],
      impact: [
        '데이터 모순 탐지',
        '업무 로직 정합성 확보',
        '교차 검증을 통한 오류 방지'
      ],
      currentStatus: `${data.total_checks}개 검사 항목 평가`
    },
    'usage': {
      title: '사용성 검사란?',
      summary: '실제 업무에서 활용 가능한 데이터인지 평가합니다',
      checkItems: [
        '업무 규칙 준수 확인',
        '실무 적용 가능성 검증',
        '데이터 품질 종합 평가'
      ],
      impact: [
        '실제 업무 활용도 향상',
        '데이터 기반 의사결정 지원',
        '시스템 운영 효율성 제고'
      ],
      currentStatus: `활용도 ${data.pass_rate.toFixed(1)}%`
    }
  };
  
  const [showTooltip, setShowTooltip] = useState(false);
  const [displayItems, setDisplayItems] = useState<Array<{
    field: string;
    reason: string;
    message: string;
    status: 'success' | 'fail';
  }>>([]);
  const [loading, setLoading] = useState(false);

  // DB에서 실패한 항목 데이터 가져오기
  useEffect(() => {
    const fetchItems = async () => {
      setLoading(true);
      try {
        const response = await fetchFailedItems(currentPage);
        
        // 검사 타입에 맞는 항목들 필터링
        const checkTypeMapping = {
          'completeness': 'completeness',
          'validity': 'validity', 
          'consistency': 'consistency',
          'usage': 'usage'
        };
        
        const targetCheckType = checkTypeMapping[type];
        if (!targetCheckType) return;
        
        // 성공률이 100%가 아니면 무조건 실패한 항목 표시, 100%이면 성공한 항목 표시
        const failedItems = response.failed_items.filter(item => 
          item.field.toLowerCase().includes(targetCheckType) || 
          item.message.toLowerCase().includes(targetCheckType)
        );
        
        const successItems = response.success_items.filter(item => 
          item.field.toLowerCase().includes(targetCheckType) || 
          item.message.toLowerCase().includes(targetCheckType)
        );
        
        // 성공률이 100%가 아니면 실패한 항목 우선 표시
        if (data.pass_rate < 100 && failedItems.length > 0) {
          // 실패한 항목이 있으면 실패한 항목 표시 (최대 1개)
          setDisplayItems(failedItems.slice(0, 1).map(item => ({
            field: item.field,
            reason: item.reason,
            message: item.message,
            status: 'fail' as const
          })));
        } else if (data.pass_rate === 100 && successItems.length > 0) {
          // 성공률이 100%이고 성공한 항목이 있으면 성공한 항목 표시 (최대 1개)
          setDisplayItems(successItems.slice(0, 1).map(item => ({
            field: item.field,
            reason: item.reason,
            message: item.message,
            status: 'success' as const
          })));
        } else if (successItems.length > 0) {
          // 실패한 항목이 없으면 성공한 항목 표시 (최대 1개)
          setDisplayItems(successItems.slice(0, 1).map(item => ({
            field: item.field,
            reason: item.reason,
            message: item.message,
            status: 'success' as const
          })));
        } else {
          // 데이터가 없으면 빈 배열
          setDisplayItems([]);
        }
      } catch (error) {
        console.error('실패한 항목 데이터 조회 실패:', error);
        setDisplayItems([]);
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, [type, currentPage]);

  return (
    <div className={`bg-white p-6 rounded-lg shadow border-2 ${style.borderColor} h-full relative`}>
      {/* 헤더 */}
      <div className="flex items-center mb-4">
        <span className="text-2xl mr-3">{style.icon}</span>
        <h3 className={`text-lg font-semibold ${style.textColor}`}>
          {name}
        </h3>
        {/* 물음표 아이콘 */}
        <div className="relative ml-2">
          <button
            className="w-3 h-3 bg-gradient-to-br from-yellow-200 to-yellow-300 hover:from-yellow-300 hover:to-yellow-400 rounded-full flex items-center justify-center text-[10px] text-yellow-700 font-bold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            onClick={() => setShowTooltip(!showTooltip)}
          >
            ?
          </button>
          
          {/* 상세 툴팁 */}
          {showTooltip && (
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-96 bg-white text-gray-800 text-sm rounded-lg p-5 shadow-xl border-2 border-gray-200 z-10">
              <div className="space-y-3">
                {/* 제목 */}
                <div className="text-center border-b border-gray-200 pb-2">
                  <div className="font-bold text-base text-gray-900">{detailedDescriptions[type].title}</div>
                  <div className="text-xs text-gray-600 mt-1">{detailedDescriptions[type].summary}</div>
                </div>
                
                {/* 현재 상태 */}
                {detailedDescriptions[type].currentStatus && (
                  <div className={`text-center py-2 px-3 rounded ${
                    data.pass_rate >= 90 ? 'bg-green-50 text-green-700' : 
                    data.pass_rate >= 70 ? 'bg-yellow-50 text-yellow-700' : 
                    'bg-red-50 text-red-700'
                  }`}>
                    <div className="text-xs font-medium">
                      {detailedDescriptions[type].currentStatus}
                    </div>
                    <div className="text-xs mt-1">
                      통과: {data.pass_count}개 | 실패: {data.fail_count}개
                    </div>
                  </div>
                )}
                
                {/* 검사 내용 */}
                <div>
                  <div className="text-xs font-semibold text-gray-700 mb-1">검사 내용:</div>
                  <ul className="text-xs text-gray-600 space-y-1">
                    {detailedDescriptions[type].checkItems.map((item, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-blue-500 mr-1">✓</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                {/* 결과 영향 */}
                <div>
                  <div className="text-xs font-semibold text-gray-700 mb-1">결과 영향:</div>
                  <ul className="text-xs text-gray-600 space-y-1">
                    {detailedDescriptions[type].impact.map((item, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-green-500 mr-1">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              {/* 화살표 */}
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-white"></div>
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-gray-200" style={{marginTop: '-2px'}}></div>
            </div>
          )}
        </div>
      </div>
      
      {/* 통과율 (큰 글씨) */}
      <div className="text-center mb-6">
        <div className={`text-2xl font-bold mb-2 ${
          data.pass_rate >= 90 
            ? 'text-green-600' 
            : data.pass_rate >= 70 
            ? 'text-yellow-600' 
            : 'text-red-600'
        }`}>
          {data.pass_rate.toFixed(1)}%
        </div>
        <div className="text-sm text-gray-500 mb-4">
          {data.pass_count}/{data.total_checks} 통과
        </div>
        
        {/* 진행률 바 */}
        <div className="w-full bg-gray-400 rounded-full h-3 mb-2 relative overflow-hidden border border-gray-300">
          {/* 진행률 바 */}
          <div 
            className={`h-3 rounded-full transition-all duration-500 relative z-10 ${
              data.pass_rate >= 90 
                ? 'bg-gradient-to-r from-green-400 to-green-500' 
                : data.pass_rate >= 70 
                ? 'bg-gradient-to-r from-yellow-400 to-yellow-500' 
                : 'bg-gradient-to-r from-red-400 to-red-500'
            }`}
            style={{ width: `${Math.min(data.pass_rate, 100)}%` }}
          ></div>
        </div>
        
        {/* 진행률 바 아래 상태 표시 */}
        <div className="text-xs text-gray-500">
          {data.pass_rate >= 90 
            ? '🟢 우수' 
            : data.pass_rate >= 70 
            ? '🟡 보통' 
            : '🔴 개선 필요'
          }
        </div>
      </div>
      
      {/* 간결한 설명 */}
      <div className="mb-4 text-center px-6">
        <div className="text-sm font-medium text-gray-800">
          {shortDescriptions[type]}
        </div>
      </div>
      
      {/* 상세 정보 */}
      <div className={`${style.bgColor} p-4 rounded-lg`}>
        <div className="space-y-3 text-sm">
          {/* 검사된 필드 정보 */}
          <div className="text-center">
            <div className="text-gray-600 mb-3">검사된 필드: {data.fields_checked || data.total_checks}개</div>
            
            {/* 통과/실패 개수와 비율 */}
            <div className="flex justify-center items-center gap-4 text-xs">
              <div className="flex items-center gap-1">
                <span className="text-green-600">✅</span>
                <span className="font-medium text-green-600">{data.pass_count}개 통과</span>
                <span className="text-gray-500">({((data.pass_count / data.total_checks) * 100).toFixed(1)}%)</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-red-600">❌</span>
                <span className="font-medium text-red-600">{data.fail_count}개 실패</span>
                <span className="text-gray-500">({((data.fail_count / data.total_checks) * 100).toFixed(1)}%)</span>
              </div>
            </div>
          </div>
          
          {data.last_updated && (
            <div className="text-xs text-gray-500 mt-3 pt-2 border-t border-gray-200 text-center">
              업데이트: {new Date(data.last_updated).toLocaleString('ko-KR')}
            </div>
          )}
        </div>
      </div>
      
      {/* 항목 상세 정보 (최대 1개) */}
      <div className="mt-4 space-y-2">
        <div className="text-sm font-medium text-gray-700 mb-2">
          {loading ? '로딩 중...' : 
           displayItems.some(item => item.status === 'fail') ? '실패한 항목 예시' : 
           displayItems.length > 0 ? '성공한 항목 예시' : '항목 정보 없음'}
        </div>
        <div className="space-y-2 max-h-32 overflow-y-auto">
          {loading ? (
            <div className="text-xs p-2 rounded border bg-gray-50 border-gray-200 text-center text-gray-500">
              데이터를 불러오는 중...
            </div>
          ) : displayItems.length > 0 ? (
            displayItems.map((item, index) => (
              <div key={index} className={`text-xs p-2 rounded border ${
                item.status === 'fail' 
                  ? 'bg-red-50 border-red-200' 
                  : 'bg-green-50 border-green-200'
              }`}>
                <div className="flex items-start gap-2">
                  <div className="flex-1 min-w-0">
                    <div className={`font-medium mb-1 ${
                      item.status === 'fail' ? 'text-red-700' : 'text-green-700'
                    }`}>
                      {item.field}
                    </div>
                    <div className="text-gray-600 text-xs mb-1">
                      {item.reason}
                    </div>
                    <div className="text-gray-500 text-xs">
                      {item.message}
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-xs p-2 rounded border bg-gray-50 border-gray-200 text-center text-gray-500">
              표시할 항목이 없습니다
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const InspectionResultsSection: React.FC<InspectionResultsSectionProps> = ({
  currentPage,
  data,
  loading = false,
  error = null
}) => {
  const inspectionTypes = INSPECTION_CONFIG[currentPage];
  
  // 카드 너비 계산
  const getCardWidth = () => {
    const length = inspectionTypes.length;
    if (length === 2) return 'w-1/2';
    if (length === 3) return 'w-1/3';
    if (length === 4) return 'w-1/4';
    return 'w-1/2'; // 기본값
  };

  if (loading) {
    return (
      <div className="px-6 mb-6">
        <div className="flex gap-4 w-5/6">
          {inspectionTypes.map((type, index) => (
            <div key={type} className={`dashboard-card h-[32rem] ${getCardWidth()}`}>
              <div className="flex items-center justify-center h-full">
                <div className="text-gray-500">로딩 중...</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-6 mb-6">
        <div className="flex gap-4 w-5/6">
          {inspectionTypes.map((type, index) => (
            <div key={type} className={`dashboard-card h-[32rem] ${getCardWidth()}`}>
              <div className="flex items-center justify-center h-full">
                <div className="text-red-500 text-sm">{error}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="px-6 mb-6">
      <div className="flex gap-4 w-5/6">
        {inspectionTypes.map((type) => (
          <div key={type} className={`dashboard-card h-[32rem] ${getCardWidth()}`}>
            <InspectionCard 
              type={type} 
              data={data[type] || { 
                pass_rate: 0, 
                total_checks: 0, 
                pass_count: 0, 
                fail_count: 0 
              }}
              currentPage={currentPage}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default InspectionResultsSection;
