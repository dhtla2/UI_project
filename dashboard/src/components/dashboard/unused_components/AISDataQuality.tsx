import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  Filler
} from 'chart.js';
import { Line, Bar, Doughnut, Pie } from 'react-chartjs-2';
import { fetchAISQualitySummary, AISQualitySummary } from '../../services/apiService';

// Chart.js 컴포넌트 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  Filler
);

interface DataQualityResult {
  inspection_id: string;
  check_type: string;
  check_name: string;
  status: string;
  severity: string;
  affected_rows: number;
  message: string;
  details: string;
  created_at: string;
}

interface AISDataQualityProps {
  inspectionId?: string;
  data?: any; // 외부에서 전달받은 데이터
}

const AISDataQuality: React.FC<AISDataQualityProps> = ({ 
  inspectionId = 'ais_info_inspection_1756440755_8ae3fb',
  data
}) => {
  const [qualityResults, setQualityResults] = useState<DataQualityResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [aisQualityData, setAisQualityData] = useState<AISQualitySummary | null>(null);

  // AIS 품질 데이터 로드
  useEffect(() => {
    const loadAISQualityData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchAISQualitySummary();
        setAisQualityData(data);
      } catch (err) {
        console.error('AIS 품질 데이터 로드 실패:', err);
        setError('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };
    
    loadAISQualityData();
  }, []);

  // 고정된 AIS 검사 결과 데이터 (실제로는 API에서 가져올 예정)
  const mockData: DataQualityResult[] = [
    // 완전성 검사 결과 (29개)
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[mmsiNo] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[imoNo] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslNm] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[callLetter] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslTp] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslTpCd] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslTpCrgo] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslCls] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslLen] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslWidth] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[flag] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[flagCd] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslDefBrd] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[lon] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[lat] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[sog] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[cog] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[rot] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[headSide] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslNavi] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslNaviCd] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[source] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[dt_pos_utc] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[dt_static_utc] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslTpMain] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[vsslTpSub] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[dstNm] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[dstCd] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'completeness', check_name: 'completeness', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[eta] 항목에 전체 [898]개 중 [0]개의 빈값이 확인 되었습니다', details: '{"total": 898, "check": "0", "etc": "898"}', created_at: '2025-08-26 10:15:56' },
    
    // 유효성 검사 결과 (2개)
    { inspection_id: inspectionId, check_type: 'validity', check_name: 'validity', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[lon] 항목에 전체 [898]개 중 [898]개의 범위값이 확인 되었습니다', details: '{"total": 898, "check": 898, "etc": 0}', created_at: '2025-08-26 10:15:56' },
    { inspection_id: inspectionId, check_type: 'validity', check_name: 'validity', status: 'PASS', severity: 'MEDIUM', affected_rows: 0, message: '[lat] 항목에 전체 [898]개 중 [898]개의 범위값이 확인 되었습니다', details: '{"total": 898, "check": 898, "etc": 0}', created_at: '2025-08-26 10:15:56' }
  ];

  useEffect(() => {
    // 실제로는 API에서 데이터를 가져올 예정
    setQualityResults(mockData);
    setLoading(false);
  }, [inspectionId]);

  if (loading) return <div className="flex items-center justify-center h-full">로딩 중...</div>;
  if (error) return <div className="text-red-500 text-center">오류: {error}</div>;

  // 통계 계산
  const totalChecks = qualityResults.length;
  const passedChecks = qualityResults.filter(r => r.status === 'PASS').length;
  const passRate = (passedChecks / totalChecks) * 100;
  
  const completenessChecks = qualityResults.filter(r => r.check_type === 'completeness');
  const validityChecks = qualityResults.filter(r => r.check_type === 'validity');

  // 완전성 검사 필드 그룹별 분류
  const fieldGroups = {
    '선박 식별': ['mmsiNo', 'imoNo', 'vsslNm', 'callLetter'],
    '선박 정보': ['vsslTp', 'vsslTpCd', 'vsslTpCrgo', 'vsslCls'],
    '크기 정보': ['vsslLen', 'vsslWidth', 'vsslDefBrd'],
    '국적 정보': ['flag', 'flagCd'],
    '위치 정보': ['lon', 'lat'],
    '항해 정보': ['sog', 'cog', 'rot', 'headSide'],
    '상태 정보': ['vsslNavi', 'vsslNaviCd'],
    '시간 정보': ['dt_pos_utc', 'dt_static_utc'],
    '분류 정보': ['vsslTpMain', 'vsslTpSub'],
    '목적지 정보': ['dstNm', 'dstCd', 'eta']
  };

  // 완전성 검사 차트 데이터
  const completenessChartData = {
    labels: Object.keys(fieldGroups),
    datasets: [{
      label: '완성도 (%)',
      data: Object.values(fieldGroups).map(group => {
        const groupFields = group.length;
        const completedFields = groupFields; // 모든 필드가 100% 완성
        return (completedFields / groupFields) * 100;
      }),
      backgroundColor: 'rgba(34, 197, 94, 0.8)',
      borderColor: 'rgba(34, 197, 94, 1)',
      borderWidth: 2
    }]
  };

  return (
    <div className="h-full p-2 bg-gray-50">
      {/* 1단계: 전체적인 품질 개요 */}
      <div className="mb-3">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
          AIS 데이터 품질 요약
        </h2>
        
        {/* 상단 통계 카드들 */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-blue-600">
              {aisQualityData?.total_inspections || 0}
            </div>
            <div className="text-sm text-gray-600">총 검사 항목</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-green-600">
              {aisQualityData?.pass_rate.toFixed(1) || 0}%
            </div>
            <div className="text-sm text-gray-600">통과율</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-purple-600">
              {aisQualityData?.total_checks || 0}
            </div>
            <div className="text-sm text-gray-600">검사 대상</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-orange-600">
              {aisQualityData?.last_inspection_date || 'N/A'}
            </div>
            <div className="text-sm text-gray-600">마지막 검사</div>
          </div>
        </div>

        {/* 완전성 검사와 유효성 검사 패널 - 통과율과 세부 통계 */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* 완전성 검사 패널 */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
              <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
              완전성 검사 (Completeness)
            </h3>
            
            {/* 아이콘 제거로 공간 최소화 */}
            <div className="mb-3">
              {/* 아이콘과 숫자 제거로 깔끔한 디자인 */}
            </div>

            {/* 세부 통계 - 컴팩트하게 */}
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="text-center bg-gray-50 p-2 rounded">
                <div className="font-semibold text-gray-700">{completenessChecks.length}</div>
                <div className="text-gray-500">총 항목</div>
              </div>
              <div className="text-center bg-green-50 p-2 rounded">
                <div className="font-semibold text-green-700">
                  {completenessChecks.filter(c => c.status === 'PASS').length}
                </div>
                <div className="text-green-600">통과</div>
              </div>
              <div className="text-center bg-red-50 p-2 rounded">
                <div className="font-semibold text-red-700">
                  {completenessChecks.filter(c => c.status === 'FAIL').length}
                </div>
                <div className="text-red-600">실패</div>
              </div>
            </div>
          </div>

          {/* 유효성 검사 패널 */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              유효성 검사 (Validity)
            </h3>
            
            {/* 아이콘 제거로 공간 최소화 */}
            <div className="mb-3">
              {/* 아이콘과 숫자 제거로 깔끔한 디자인 */}
            </div>

            {/* 세부 통계 - 컴팩트하게 */}
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="text-center bg-gray-50 p-2 rounded">
                <div className="font-semibold text-gray-700">{validityChecks.length}</div>
                <div className="text-gray-500">총 항목</div>
              </div>
              <div className="text-center bg-green-50 p-2 rounded">
                <div className="font-semibold text-green-700">
                  {validityChecks.filter(c => c.status === 'PASS').length}
                </div>
                <div className="text-green-600">통과</div>
              </div>
              <div className="text-center bg-red-50 p-2 rounded">
                <div className="font-semibold text-red-700">
                  {validityChecks.filter(c => c.status === 'FAIL').length}
                </div>
                <div className="text-red-600">실패</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default AISDataQuality;
