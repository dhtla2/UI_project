import React, { useState, useEffect } from 'react';
import FieldAnalysisTable from '../dashboard/FieldAnalysisTable';
import { 
  fetchAISFieldAnalysis, 
  fetchTOSFieldAnalysis, 
  fetchTCFieldAnalysis, 
  fetchQCFieldAnalysis,
  fetchYTFieldAnalysis,
  fetchPortVsslFieldAnalysis,
  fetchTosVsslFieldAnalysis,
  fetchVsslSpecFieldAnalysis,
  FieldAnalysisData as APIFieldAnalysisData,
  TOSFieldAnalysisData
} from '../../services/apiService';

// 각 페이지별 필드 분석 데이터 타입
interface FieldAnalysisData {
  field: string;
  group: string;
  status: 'PASS' | 'FAIL';
  total: number;
  check: number;
  etc: number;
  message: string;
  checkType: string;
}

interface CommonFieldAnalysisSectionProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  loading: boolean;
  error: string | null;
}

const CommonFieldAnalysisSection: React.FC<CommonFieldAnalysisSectionProps> = ({
  currentPage,
  loading,
  error
}) => {
  const [fieldAnalysisData, setFieldAnalysisData] = useState<FieldAnalysisData[]>([]);
  const [dataLoading, setDataLoading] = useState(false);
  const [dataError, setDataError] = useState<string | null>(null);

  // API 데이터를 테이블 형식으로 변환
  const convertAPIDataToTableData = (apiData: APIFieldAnalysisData): FieldAnalysisData[] => {
    const tableData: FieldAnalysisData[] = [];
    
    apiData.field_statistics.forEach((stat: any) => {
      const status: 'PASS' | 'FAIL' = stat.fail_count > 0 ? 'FAIL' : 'PASS';
      
      // 원본 메시지가 있으면 우선 사용, 없으면 생성
      let message = '';
      const affectedRows = stat.affected_rows || 0;
      
      if (stat.original_message) {
        // DB에 저장된 원본 메시지 사용
        message = stat.original_message;
      } else if (stat.check_type === 'completeness') {
        // 완전성 검사: [필드명] 항목에 전체 [total]개 중 [affected_rows]개의 빈값이 확인 되었습니다
        message = `[${stat.field_name}] 항목에 전체 [${stat.total_checks}]개 중 [${affectedRows}]개의 빈값이 확인 되었습니다`;
      } else if (stat.check_type === 'validity') {
        // 유효성 검사: [검사명] 항목에 전체 [total]개 중 [total - affected_rows]개의 유효값이 확인 되었습니다
        const validCount = stat.total_checks - affectedRows;
        message = `[${stat.field_name}] 항목에 전체 [${stat.total_checks}]개 중 [${validCount}]개의 유효값이 확인 되었습니다`;
      } else {
        // 기타 검사
        message = `[${stat.field_name}] ${stat.check_type} 검사: 전체 ${stat.total_checks}개 중 ${stat.pass_count}개 통과`;
      }
      
      // total_checks는 실제 데이터 행 수 (예: 898)
      // affectedRows는 오류/빈값이 있는 행 수
      // 정상 개수 = 전체 - 오류
      const normalCount = stat.total_checks - affectedRows;
      
      tableData.push({
        field: stat.field_name,
        group: stat.check_type,
        status: status,
        total: stat.total_checks,  // 실제 데이터 행 수 (898)
        check: affectedRows,  // 오류/빈값 개수
        etc: normalCount >= 0 ? normalCount : 0,  // 정상 개수 (음수 방지)
        message: message,
        checkType: stat.check_type
      });
    });
    
    return tableData;
  };

  // API에서 데이터 로드
  useEffect(() => {
    const loadFieldAnalysisData = async () => {
      if (currentPage === 'QualityCheck') {
        // QualityCheck 페이지는 데이터가 없으므로 빈 배열
        setFieldAnalysisData([]);
        return;
      }

      setDataLoading(true);
      setDataError(null);
      
      try {
        // TOS는 기존 API 사용 (이미 테이블 형식으로 반환됨)
        if (currentPage === 'TOS') {
          const tosData = await fetchTOSFieldAnalysis();
          setFieldAnalysisData(tosData);
          setDataLoading(false);
          return;
        }
        
        // 나머지 페이지들은 새 API 사용
        let apiData: APIFieldAnalysisData;
        
        switch (currentPage) {
          case 'AIS':
            apiData = await fetchAISFieldAnalysis();
            break;
          case 'TC':
            apiData = await fetchTCFieldAnalysis();
            break;
          case 'QC':
            apiData = await fetchQCFieldAnalysis();
            break;
          case 'YT':
            apiData = await fetchYTFieldAnalysis();
            break;
          case 'PortMisVsslNo':
            apiData = await fetchPortVsslFieldAnalysis();
            break;
          case 'TosVsslNo':
            apiData = await fetchTosVsslFieldAnalysis();
            break;
          case 'VsslSpecInfo':
            apiData = await fetchVsslSpecFieldAnalysis();
            break;
          default:
            return;
        }
        
        const convertedData = convertAPIDataToTableData(apiData);
        setFieldAnalysisData(convertedData);
      } catch (err) {
        console.error('필드 분석 데이터 로드 실패:', err);
        setDataError('필드 분석 데이터를 불러오는데 실패했습니다.');
        // 에러 시 빈 배열로 설정
        setFieldAnalysisData([]);
      } finally {
        setDataLoading(false);
      }
    };
    
    loadFieldAnalysisData();
  }, [currentPage]);


  return (
    <div className="px-6 mb-6">
      <div className="dashboard-card h-112 w-5/6">
        <FieldAnalysisTable 
          results={fieldAnalysisData}
        />
      </div>
    </div>
  );
};

export default CommonFieldAnalysisSection;
