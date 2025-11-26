// 품질 검사 API 서비스

const API_BASE_URL = '';

export interface QualityCheckRequest {
  data_type: string;
  api_params: Record<string, any>;
  quality_meta: Record<string, any>;
}

export interface QualityCheckResult {
  success: boolean;
  message: string;
  inspection_id?: string;
  results?: {
    overall_rate: number;
    total_checks: number;
    total_passed: number;
    breakdown: Record<string, {
      status: 'PASS' | 'FAIL';
      pass_rate: number;
      total_checks: number;
      failed_checks: number;
    }>;
  };
  timestamp: string;
}

export interface QualityCheckHistory {
  id: string;
  data_type: string;
  status: string;
  created_at: string;
  results?: Record<string, any>;
}

// 품질 검사 실행
export const runQualityCheck = async (request: QualityCheckRequest): Promise<QualityCheckResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/quality-check/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data: QualityCheckResult = await response.json();
    return data;
  } catch (error) {
    console.error('Error running quality check:', error);
    throw error;
  }
};

// 품질 검사 히스토리 조회
export const getQualityCheckHistory = async (): Promise<QualityCheckHistory[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/quality-check/history`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data: QualityCheckHistory[] = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching quality check history:', error);
    throw error;
  }
};

// 특정 검사 결과 상세 조회
export const getQualityCheckDetail = async (inspectionId: string): Promise<QualityCheckResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/quality-check/detail/${inspectionId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data: QualityCheckResult = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching quality check detail:', error);
    throw error;
  }
};

// 데이터 타입별 통계 조회
export const getQualityCheckStats = async (): Promise<{
  total_inspections: number;
  data_type_stats: Array<{
    data_type: string;
    total_inspections: number;
    avg_pass_rate: number;
    avg_quality_score: number;
    last_inspection: string;
  }>;
  recent_inspections: QualityCheckHistory[];
}> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/quality-check/stats`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching quality check stats:', error);
    throw error;
  }
};
