import React, { useState, useEffect } from 'react';
import { TOSQualitySummaryData, fetchTOSQualitySummary } from '../../services/apiService';

interface TOSDataQualityProps {
  data?: TOSQualitySummaryData | null;
}

const TOSDataQuality: React.FC<TOSDataQualityProps> = ({ data }) => {
  const [tosQualityData, setTosQualityData] = useState<TOSQualitySummaryData | null>(data || null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // TOS 품질 데이터 로드
  useEffect(() => {
    const loadTOSQualityData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchTOSQualitySummary();
        setTosQualityData(data);
      } catch (err) {
        console.error('TOS 품질 데이터 로드 실패:', err);
        setError('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };
    
    if (!data) {
      loadTOSQualityData();
    } else {
      setLoading(false);
    }
  }, [data]);

  if (loading) return <div className="flex items-center justify-center h-full">로딩 중...</div>;
  if (error) return <div className="text-red-500 text-center">오류: {error}</div>;

  return (
    <div className="h-full p-2 bg-gray-50">
      {/* 1단계: 전체적인 품질 개요 */}
      <div className="mb-3">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
          TOS 데이터 품질 요약
        </h2>
        
        {/* 상단 통계 카드들 */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-blue-600">
              {tosQualityData?.total_inspections || 0}
            </div>
            <div className="text-sm text-gray-600">총 검사 항목</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-green-600">
              {tosQualityData?.pass_rate.toFixed(1) || 0}%
            </div>
            <div className="text-sm text-gray-600">통과율</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-purple-600">
              {tosQualityData?.total_checks || 0}
            </div>
            <div className="text-sm text-gray-600">검사 대상</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl font-bold text-orange-600">
              {tosQualityData?.last_inspection_date || 'N/A'}
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
                <div className="font-semibold text-gray-700">{tosQualityData?.completeness.fields_checked || 0}</div>
                <div className="text-gray-500">총 항목</div>
              </div>
              <div className="text-center bg-green-50 p-2 rounded">
                <div className="font-semibold text-green-700">
                  {tosQualityData?.completeness.pass_count || 0}
                </div>
                <div className="text-green-600">통과</div>
              </div>
              <div className="text-center bg-red-50 p-2 rounded">
                <div className="font-semibold text-red-700">
                  {tosQualityData?.completeness.fail_count || 0}
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
                <div className="font-semibold text-gray-700">{tosQualityData?.validity.fields_checked || 0}</div>
                <div className="text-gray-500">총 항목</div>
              </div>
              <div className="text-center bg-green-50 p-2 rounded">
                <div className="font-semibold text-green-700">
                  {tosQualityData?.validity.pass_count || 0}
                </div>
                <div className="text-green-600">통과</div>
              </div>
              <div className="text-center bg-red-50 p-2 rounded">
                <div className="font-semibold text-red-700">
                  {tosQualityData?.validity.fail_count || 0}
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

export default TOSDataQuality;
