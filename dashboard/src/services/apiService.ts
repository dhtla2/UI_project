// API 서비스 함수들

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

export interface APIQualityData {
  api_type: string;
  total_inspections: number;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
}

export interface AISSummaryData {
  total_ships: number;
  unique_ship_types: number;
  unique_flags: number;
  avg_speed: number;
  max_speed: number;
  ship_type_distribution: Array<{ type: string; count: number }>;
  flag_distribution: Array<{ flag: string; count: number }>;
  speed_distribution: Array<{ range: string; count: number }>;
}

export interface UIStatisticsData {
  total_page_visits: number;
  total_api_calls: number;
  unique_users: number;
  login_status_stats: Array<[string, number]>;
  most_visited_pages: Array<[string, number]>;
  most_called_apis: Array<[string, number]>;
  avg_response_time_ms: number;
}

// API 품질 데이터 조회
export const fetchAPIQualityData = async (): Promise<APIQualityData[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/api-quality`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('API Quality Data Response:', result);
    console.log('API Quality Data Array:', result.data);
    return result.data || [];
  } catch (error) {
    console.error('API 품질 데이터 조회 실패:', error);
    throw error;
  }
};

// AIS 요약 데이터 조회
export const fetchAISSummary = async (): Promise<AISSummaryData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/ais-summary`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data?.[0] || null;
  } catch (error) {
    console.error('AIS 요약 데이터 조회 실패:', error);
    throw error;
  }
};

// UI 통계 데이터 조회
export const fetchUIStatistics = async (): Promise<UIStatisticsData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/ui/statistics`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('UI 통계 데이터 조회 실패:', error);
    throw error;
  }
};

// 시간별 통계 데이터 조회
export const fetchTimeBasedStatistics = async (
  period: 'daily' | 'weekly' | 'monthly' = 'daily',
  days: number = 30
): Promise<{
  page_visits: Array<[string, number]>;
  api_calls: Array<[string, number]>;
  period: string;
  days: number;
  generated_at: string;
}> => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/ui/statistics/time-based?period=${period}&days=${days}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('시간별 통계 데이터 조회 실패:', error);
    throw error;
  }
};

// 헬스 체크
export const healthCheck = async (): Promise<{ status: string; service: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('헬스 체크 실패:', error);
    throw error;
  }
};

// AIS 품질 요약 데이터 타입
export interface AISQualitySummary {
  total_inspections: number;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  last_inspection_date: string | null;
  completeness: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
  validity: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
}

// AIS 품질 상세 데이터 타입
export interface AISQualityDetailsData {
  completeness: {
    field_groups: Array<{
      name: string;
      completion_rate: number;
    }>;
  };
  validity: {
    longitude?: {
      range: string;
      count: number;
      pass_count: number;
      fail_count: number;
      status: string;
    };
    latitude?: {
      range: string;
      count: number;
      pass_count: number;
      fail_count: number;
      status: string;
    };
    grid?: {
      range: string;
      count: number;
      land_count: number;
      sea_count: number;
      land_percentage: number;
      sea_percentage: number;
      pass_count: number;
      fail_count: number;
      pass_rate: number;
      status: string;
    };
  };
  overall_validity?: {
    total_check_types: number;
    successful_check_types: number;
    failed_check_types: number;
    success_rate: number;
    status: string;
  };
}

// AIS 차트 데이터 타입
export interface AISChartsData {
  grid_distribution: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
  check_type_results: Array<{
    type: string;
    total_checks: number;
    pass_count: number;
    pass_rate: number;
  }>;
  quality_score: number;
}

// AIS 품질 요약 데이터 조회
export const fetchAISQualitySummary = async (): Promise<AISQualitySummary> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/ais-quality-summary`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data[0];
  } catch (error) {
    console.error("Error fetching AIS quality summary:", error);
    throw error;
  }
};

// AIS 품질 상세 데이터 조회
export const fetchAISQualityDetails = async (): Promise<AISQualityDetailsData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/ais-quality-details`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: AISQualityDetailsData = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching AIS quality details:", error);
    throw error;
  }
};

// TOS 품질 상세 데이터 타입
export interface TOSQualityDetailsData {
  completeness: {
    field_groups: Array<{
      name: string;
      completion_rate: number;
    }>;
    total_fields: number;
    successful_fields: number;
    failed_fields: number;
    overall_rate: number;
  };
  validity: {
    date_diff?: {
      range: string;
      count: number;
      pass_count: number;
      fail_count: number;
      status: string;
    };
  };
  overall_validity?: {
    total_check_types: number;
    successful_check_types: number;
    failed_check_types: number;
    success_rate: number;
    status: string;
  };
}

// TOS 품질 요약 데이터 타입
export interface TOSQualitySummaryData {
  total_inspections: number;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  last_inspection_date: string | null;
  completeness: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
  validity: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
}

// TC 품질 요약 데이터 인터페이스
export interface TCQualitySummaryData {
  total_inspections: number;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  last_inspection_date: string | null;
  completeness: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
  validity: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
  usage?: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
}

// QC 품질 요약 데이터 인터페이스
export interface QCQualitySummaryData {
  total_inspections: number;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  last_inspection_date: string | null;
  completeness: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
  validity: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
}

export interface YTQualitySummaryData {
  total_inspections: number;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  last_inspection_date: string | null;
  completeness: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
  validity: {
    fields_checked: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
}

// TOS 품질 요약 데이터 조회
export const fetchTOSQualitySummary = async (): Promise<TOSQualitySummaryData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tos-quality-summary`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data[0];
  } catch (error) {
    console.error("Error fetching TOS quality summary:", error);
    throw error;
  }
};

// TC 품질 요약 데이터 조회
export const fetchTCQualitySummary = async (): Promise<TCQualitySummaryData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tc-quality-summary`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data[0];
  } catch (error) {
    console.error("Error fetching TC quality summary:", error);
    throw error;
  }
};

// QC 품질 요약 데이터 조회
export const fetchQCQualitySummary = async (): Promise<QCQualitySummaryData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/qc-quality-summary`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data[0];
  } catch (error) {
    console.error("Error fetching QC quality summary:", error);
    throw error;
  }
};

// YT 품질 요약 데이터 조회
export const fetchYTQualitySummary = async (): Promise<YTQualitySummaryData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/yt-quality-summary`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data[0];
  } catch (error) {
    console.error("Error fetching YT quality summary:", error);
    throw error;
  }
};

// TOS 품질 상세 데이터 조회
export const fetchTOSQualityDetails = async (): Promise<TOSQualityDetailsData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tos-quality-details`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: TOSQualityDetailsData = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching TOS quality details:", error);
    throw error;
  }
};

// TOS 필드별 분석 데이터 타입
export interface TOSFieldAnalysisData {
  field: string;
  group: string;
  status: 'PASS' | 'FAIL';
  total: number;
  check: number;
  etc: number;
  message: string;
  checkType: 'completeness' | 'validity';
}

// TOS 필드별 분석 데이터 조회
export const fetchTOSFieldAnalysis = async (): Promise<TOSFieldAnalysisData[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tos-field-analysis`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    const apiData = result.data?.[0] || { field_statistics: [], severity_distribution: [] };
    
    // 새 API 형식을 기존 형식으로 변환
    const convertedData: TOSFieldAnalysisData[] = [];
    
    apiData.field_statistics.forEach((stat: any) => {
      const status: 'PASS' | 'FAIL' = stat.fail_count > 0 ? 'FAIL' : 'PASS';
      
      // 원본 메시지가 있으면 우선 사용, 없으면 생성
      let message = '';
      const affectedRows = stat.affected_rows || 0;
      
      if (stat.original_message) {
        // DB에 저장된 원본 메시지 사용
        message = stat.original_message;
      } else if (stat.check_type === 'completeness') {
        message = `[${stat.field_name}] 항목에 전체 [${stat.total_checks}]개 중 [${affectedRows}]개의 빈값이 확인 되었습니다`;
      } else if (stat.check_type === 'validity') {
        const validCount = stat.total_checks - affectedRows;
        message = `[${stat.field_name}] 항목에 전체 [${stat.total_checks}]개 중 [${validCount}]개의 유효값이 확인 되었습니다`;
      } else {
        message = `[${stat.field_name}] ${stat.check_type} 검사: 전체 ${stat.total_checks}개 중 ${stat.pass_count}개 통과`;
      }
      
      convertedData.push({
        field: stat.field_name,
        group: stat.check_type || 'general',
        status: status,
        total: stat.total_checks,  // 실제 검사한 레코드 수
        check: affectedRows,  // 오류/빈값 개수
        etc: stat.total_checks - affectedRows,  // 정상 개수
        message: message,
        checkType: (stat.check_type || 'validity') as 'completeness' | 'validity'
      });
    });
    
    return convertedData;
  } catch (error) {
    console.error("Error fetching TOS field analysis:", error);
    throw error;
  }
};

// TOS 검사 히스토리 데이터 타입
export interface TOSInspectionHistoryData {
  date: string;
  score: number;
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  completenessRate: number;
  validityRate: number;
}

// TOS 검사 히스토리 데이터 조회
export const fetchTOSInspectionHistory = async (
  period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily',
  startDate?: string,
  endDate?: string
): Promise<TOSInspectionHistoryData[]> => {
  try {
    let url = `${API_BASE_URL}/api/dashboard/tos-inspection-history?period=${period}`;
    
    if (period === 'custom' && startDate && endDate) {
      url += `&start_date=${startDate}&end_date=${endDate}`;
    }
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: TOSInspectionHistoryData[] = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching TOS inspection history:", error);
    throw error;
  }
};

// TOS 데이터 품질 상태 타입
export interface TOSDataQualityStatusData {
  completeness: {
    status: 'PASS' | 'FAIL' | 'WARNING';
    rate: number;
    lastCheck: string;
  };
  validity: {
    status: 'PASS' | 'FAIL' | 'WARNING';
    rate: number;
    lastCheck: string;
  };
  overall: {
    status: 'PASS' | 'FAIL' | 'WARNING';
    score: number;
    lastUpdate: string;
  };
  alerts: Array<{
    id: string;
    type: 'error' | 'warning' | 'info';
    message: string;
    timestamp: string;
  }>;
}

// TOS 데이터 품질 상태 조회
export const fetchTOSDataQualityStatus = async (): Promise<TOSDataQualityStatusData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tos-data-quality-status`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: TOSDataQualityStatusData = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching TOS data quality status:", error);
    throw error;
  }
};

// AIS 차트 데이터 조회
export const fetchAISChartsData = async (): Promise<AISChartsData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/ais-charts`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: AISChartsData = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching AIS charts data:", error);
    throw error;
  }
};

// AIS 검사 히스토리 데이터 타입
export interface AISInspectionHistoryData {
  date: string;
  score: number;
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  completenessRate: number;
  validityRate: number;
}

// AIS 검사 히스토리 데이터 조회 (기간별 필터링 지원)
export const fetchAISInspectionHistory = async (
  period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily',
  startDate?: string,
  endDate?: string
): Promise<AISInspectionHistoryData[]> => {
  try {
    let url = `${API_BASE_URL}/api/dashboard/ais-inspection-history?period=${period}`;
    
    if (period === 'custom' && startDate && endDate) {
      url += `&start_date=${startDate}&end_date=${endDate}`;
    }
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: AISInspectionHistoryData[] = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching AIS inspection history:", error);
    throw error;
  }
};

// TC 데이터 품질 상태 타입
export interface TCQualityStatusData {
  overall: {
    rate: number;
    total: number;
    pass: number;
    fail: number;
  };
  breakdown: {
    [key: string]: {
      total: number;
      pass: number;
      fail: number;
      rate: number;
    };
  };
  alerts: Array<{
    type: string;
    message: string;
  }>;
}

// TC 데이터 품질 상태 조회
export const fetchTCQualityStatus = async (): Promise<TCQualityStatusData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tc-quality-status`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: TCQualityStatusData = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching TC quality status:", error);
    throw error;
  }
};

// TC 검사 히스토리 데이터 타입
export interface TCInspectionHistoryData {
  date: string;
  score: number;
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  completenessRate: number;
  validityRate: number;
}

// TC 검사 히스토리 데이터 조회 (기간별 필터링 지원)
export const fetchTCInspectionHistory = async (
  period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily',
  startDate?: string,
  endDate?: string
): Promise<TCInspectionHistoryData[]> => {
  try {
    let url = `${API_BASE_URL}/api/dashboard/tc-inspection-history?period=${period}`;
    
    if (period === 'custom' && startDate && endDate) {
      url += `&start_date=${startDate}&end_date=${endDate}`;
    }
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: TCInspectionHistoryData[] = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching TC inspection history:", error);
    throw error;
  }
};

// QC 데이터 품질 상태 타입
export interface QCQualityStatusData {
  overall: {
    rate: number;
    total: number;
    pass: number;
    fail: number;
  };
  breakdown: {
    [key: string]: {
      total: number;
      pass: number;
      fail: number;
      rate: number;
    };
  };
  alerts: Array<{
    type: string;
    message: string;
  }>;
}

// QC 데이터 품질 상태 조회
export const fetchQCQualityStatus = async (): Promise<QCQualityStatusData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/qc-quality-status`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: QCQualityStatusData = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching QC quality status:", error);
    throw error;
  }
};

// QC 검사 히스토리 데이터 타입
export interface QCInspectionHistoryData {
  date: string;
  score: number;
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  completenessRate: number;
  validityRate: number;
}

// QC 검사 히스토리 데이터 조회 (기간별 필터링 지원)
export const fetchQCInspectionHistory = async (
  period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily',
  startDate?: string,
  endDate?: string
): Promise<QCInspectionHistoryData[]> => {
  try {
    let url = `${API_BASE_URL}/api/dashboard/qc-inspection-history?period=${period}`;
    
    if (period === 'custom' && startDate && endDate) {
      url += `&start_date=${startDate}&end_date=${endDate}`;
    }
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: QCInspectionHistoryData[] = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching QC inspection history:", error);
    throw error;
  }
};

// YT 검사 히스토리 데이터 타입
export interface YTInspectionHistoryData {
  date: string;
  score: number;
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  completenessRate: number;
  validityRate: number;
}

// YT 검사 히스토리 데이터 조회 (기간별 필터링 지원)
export const fetchYTInspectionHistory = async (
  period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily',
  startDate?: string,
  endDate?: string
): Promise<YTInspectionHistoryData[]> => {
  try {
    let url = `${API_BASE_URL}/api/dashboard/yt-inspection-history?period=${period}`;
    
    if (period === 'custom' && startDate && endDate) {
      url += `&start_date=${startDate}&end_date=${endDate}`;
    }
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: YTInspectionHistoryData[] = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching YT inspection history:", error);
    throw error;
  }
};

// 데이터 품질 상태 타입
export interface DataQualityStatusData {
  completeness: {
    status: 'PASS' | 'FAIL' | 'WARNING';
    rate: number;
    lastCheck: string;
  };
  validity: {
    status: 'PASS' | 'FAIL' | 'WARNING';
    rate: number;
    lastCheck: string;
  };
  overall: {
    status: 'PASS' | 'FAIL' | 'WARNING';
    score: number;
    lastUpdate: string;
  };
  alerts: Array<{
    id: string;
    type: 'error' | 'warning' | 'info';
    message: string;
    timestamp: string;
  }>;
}

// 데이터 품질 상태 조회
export const fetchDataQualityStatus = async (): Promise<DataQualityStatusData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/data-quality-status`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: DataQualityStatusData = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching data quality status:", error);
    throw error;
  }
};

// 실패한 항목 데이터 조회
export interface FailedItemData {
  field: string;
  reason: string;
  message: string;
  details: string;
  affected_rows: number;
  created_at: string | null;
}

export interface FailedItemsResponse {
  failed_items: FailedItemData[];
  success_items: FailedItemData[];
  page: string;
}

export const fetchFailedItems = async (page: string = 'AIS'): Promise<FailedItemsResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/failed-items?page=${page}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data || [];
  } catch (error) {
    console.error('실패한 항목 데이터 조회 실패:', error);
    throw error;
  }
};

// AIS 데이터 관련 인터페이스 추가
export interface AISSummaryData {
  total_ships: number;
  unique_ship_types: number;
  unique_flags: number;
  avg_speed: number;
  max_speed: number;
  ship_type_distribution: Array<{type: string, count: number}>;
  flag_distribution: Array<{flag: string, count: number}>;
  speed_distribution: Array<{range: string, count: number}>;
}

export interface AISQualityStatusData {
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

// AIS API 함수들 추가

export const fetchAISQualityStatus = async (): Promise<AISQualityStatusData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/ais-quality-status`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data?.[0] || null;
  } catch (error) {
    console.error('AIS 품질 상태 데이터 조회 실패:', error);
    throw error;
  }
};

// 최신 검사 결과 조회
export interface LatestInspectionResults {
  completeness: {
    pass_rate: number;
    total_checks: number;
    pass_count: number;
    fail_count: number;
    fields_checked: number;
    last_updated: string | null;
  };
  validity: {
    pass_rate: number;
    total_checks: number;
    pass_count: number;
    fail_count: number;
    fields_checked: number;
    last_updated: string | null;
  };
  usage?: {
    pass_rate: number;
    total_checks: number;
    pass_count: number;
    fail_count: number;
    fields_checked: number;
    last_updated: string | null;
  };
}

export const fetchLatestInspectionResults = async (page: string = 'AIS'): Promise<LatestInspectionResults> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/latest-inspection-results?page=${page}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('최신 검사 결과 조회 실패:', error);
    throw error;
  }
};

// 필드 분석 데이터 인터페이스
export interface FieldAnalysisData {
  field_statistics: Array<{
    field_name: string;
    check_type: string;
    total_checks: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
    affected_rows: number;  // 오류/빈값의 합계
    original_message?: string;  // 원본 메시지 (선택적)
  }>;
  severity_distribution: Array<{
    severity: string;
    count: number;
    check_type: string;
  }>;
}

// AIS 필드 분석 데이터 조회
export const fetchAISFieldAnalysis = async (): Promise<FieldAnalysisData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/ais-field-analysis`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data?.[0] || { field_statistics: [], severity_distribution: [] };
  } catch (error) {
    console.error('AIS 필드 분석 데이터 조회 실패:', error);
    throw error;
  }
};

// TC 필드 분석 데이터 조회
export const fetchTCFieldAnalysis = async (): Promise<FieldAnalysisData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tc-field-analysis`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data?.[0] || { field_statistics: [], severity_distribution: [] };
  } catch (error) {
    console.error('TC 필드 분석 데이터 조회 실패:', error);
    throw error;
  }
};

// QC 필드 분석 데이터 조회
export const fetchQCFieldAnalysis = async (): Promise<FieldAnalysisData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/qc-field-analysis`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data?.[0] || { field_statistics: [], severity_distribution: [] };
  } catch (error) {
    console.error('QC 필드 분석 데이터 조회 실패:', error);
    throw error;
  }
};

// YT 필드별 분석 데이터 조회
export const fetchYTFieldAnalysis = async (): Promise<FieldAnalysisData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/yt-field-analysis`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data?.[0] || { field_statistics: [], severity_distribution: [] };
  } catch (error) {
    console.error('YT 필드 분석 데이터 조회 실패:', error);
    throw error;
  }
};

// ==================== Match API Functions (PortMisVsslNo & TosVsslNo) ====================

// Match API 요약 데이터 인터페이스
export interface MatchSummaryData {
  total_records: number;
  unique_ports: number;
  unique_terminals: number;
  unique_pmis_vessels: number;
  unique_tos_vessels: number;
  last_updated: string | null;
  quality_info: {
    total_inspections: number;
    total_checks: number;
    pass_rate: number;
    last_inspection_date: string | null;
  };
}

// PortMisVsslNo (PMIS→TOS) 요약 데이터 조회
export const fetchPortVsslSummary = async (): Promise<MatchSummaryData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/port-vssl/summary`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data || null;
  } catch (error) {
    console.error('PortMisVsslNo 요약 데이터 조회 실패:', error);
    throw error;
  }
};

// TosVsslNo (TOS→PMIS) 요약 데이터 조회
export const fetchTosVsslSummary = async (): Promise<MatchSummaryData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tos-vssl/summary`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data || null;
  } catch (error) {
    console.error('TosVsslNo 요약 데이터 조회 실패:', error);
    throw error;
  }
};

// PortMisVsslNo 최신 검사 결과 조회
export const fetchPortVsslLatestResults = async (): Promise<LatestInspectionResults> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/port-vssl/latest-results`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data || { completeness: null, validity: null, consistency: null, usage: null };
  } catch (error) {
    console.error('PortMisVsslNo 최신 검사 결과 조회 실패:', error);
    throw error;
  }
};

// TosVsslNo 최신 검사 결과 조회
export const fetchTosVsslLatestResults = async (): Promise<LatestInspectionResults> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tos-vssl/latest-results`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data || { completeness: null, validity: null, consistency: null, usage: null };
  } catch (error) {
    console.error('TosVsslNo 최신 검사 결과 조회 실패:', error);
    throw error;
  }
};

// PortMisVsslNo 검사 히스토리 조회
export const fetchPortVsslInspectionHistory = async (
  period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily',
  startDate?: string,
  endDate?: string
): Promise<AISInspectionHistoryData[]> => {
  try {
    let url = `${API_BASE_URL}/api/dashboard/port-vssl/inspection-history?period=${period}`;
    if (period === 'custom' && startDate && endDate) {
      url += `&start_date=${startDate}&end_date=${endDate}`;
    }
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data || [];
  } catch (error) {
    console.error('PortMisVsslNo 검사 히스토리 조회 실패:', error);
    throw error;
  }
};

// TosVsslNo 검사 히스토리 조회
export const fetchTosVsslInspectionHistory = async (
  period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily',
  startDate?: string,
  endDate?: string
): Promise<AISInspectionHistoryData[]> => {
  try {
    let url = `${API_BASE_URL}/api/dashboard/tos-vssl/inspection-history?period=${period}`;
    if (period === 'custom' && startDate && endDate) {
      url += `&start_date=${startDate}&end_date=${endDate}`;
    }
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data || [];
  } catch (error) {
    console.error('TosVsslNo 검사 히스토리 조회 실패:', error);
    throw error;
  }
};

// PortMisVsslNo 필드 분석 데이터 조회
export const fetchPortVsslFieldAnalysis = async (): Promise<FieldAnalysisData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/port-vssl/field-analysis`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data?.[0] || { field_statistics: [], severity_distribution: [] };
  } catch (error) {
    console.error('PortMisVsslNo 필드 분석 데이터 조회 실패:', error);
    throw error;
  }
};

// TosVsslNo 필드 분석 데이터 조회
export const fetchTosVsslFieldAnalysis = async (): Promise<FieldAnalysisData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tos-vssl/field-analysis`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data?.[0] || { field_statistics: [], severity_distribution: [] };
  } catch (error) {
    console.error('TosVsslNo 필드 분석 데이터 조회 실패:', error);
    throw error;
  }
};

// PortMisVsslNo 품질 상태 조회
export const fetchPortVsslQualityStatus = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/port-vssl/quality-status`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data || {};
  } catch (error) {
    console.error('PortMisVsslNo 품질 상태 조회 실패:', error);
    throw error;
  }
};

// TosVsslNo 품질 상태 조회
export const fetchTosVsslQualityStatus = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tos-vssl/quality-status`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.data || {};
  } catch (error) {
    console.error('TosVsslNo 품질 상태 조회 실패:', error);
    throw error;
  }
};

// VsslSpecInfo 관련 인터페이스 및 함수들
export interface VsslSpecSummaryData {
  total_inspections: number;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  last_inspection_date: string | null;
  completeness: {
    rate: string;
    total: number;
    passed: string;
  };
  validity: {
    rate: string;
    total: number;
    passed: string;
  };
  usage: any;
}

export interface VsslSpecFieldAnalysisData {
  field_name: string;
  check_type: string;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  affected_rows: number;
  message: string;
}

export interface VsslSpecInspectionHistoryData {
  date: string;
  score: number;
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  completenessRate: number;
  validityRate: number;
}

export interface VsslSpecQualityStatusData {
  status: string;
  message: string;
  last_check: string | null;
  total_checks: number;
  pass_rate: number;
}

// VsslSpecInfo 품질 요약 데이터 조회
export const fetchVsslSpecSummary = async (): Promise<VsslSpecSummaryData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/vssl-spec/summary`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data || {};
  } catch (error) {
    console.error('VsslSpecInfo 품질 요약 조회 실패:', error);
    throw error;
  }
};

// VsslSpecInfo 최신 검사 결과 조회
export const fetchVsslSpecLatestResults = async (): Promise<any[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/vssl-spec/latest-results`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data || [];
  } catch (error) {
    console.error('VsslSpecInfo 최신 검사 결과 조회 실패:', error);
    throw error;
  }
};

// VsslSpecInfo 검사 히스토리 조회
export const fetchVsslSpecInspectionHistory = async (
  period: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily',
  startDate?: string,
  endDate?: string
): Promise<VsslSpecInspectionHistoryData[]> => {
  try {
    const params = new URLSearchParams({ period });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await fetch(`${API_BASE_URL}/api/dashboard/vssl-spec/inspection-history?${params}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data || [];
  } catch (error) {
    console.error('VsslSpecInfo 검사 히스토리 조회 실패:', error);
    throw error;
  }
};

// VsslSpecInfo 필드 분석 조회
export const fetchVsslSpecFieldAnalysis = async (): Promise<FieldAnalysisData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/vssl-spec/field-analysis`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data?.[0] || { field_statistics: [], severity_distribution: [] };
  } catch (error) {
    console.error('VsslSpecInfo 필드 분석 조회 실패:', error);
    throw error;
  }
};

// VsslSpecInfo 품질 상태 조회
export const fetchVsslSpecQualityStatus = async (): Promise<VsslSpecQualityStatusData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/vssl-spec/quality-status`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data || {};
  } catch (error) {
    console.error('VsslSpecInfo 품질 상태 조회 실패:', error);
    throw error;
  }
};
