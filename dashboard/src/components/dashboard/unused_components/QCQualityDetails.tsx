import React from 'react';

interface QCQualityDetailsProps {
  qualityDetails?: any;
}

const QCQualityDetails: React.FC<QCQualityDetailsProps> = ({ qualityDetails }) => {
  return (
    <div className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">QC 품질 상세</h3>
      
      {/* 품질 트렌드 차트 영역 */}
      <div className="mb-6">
        <div className="h-32 bg-gray-50 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <div className="text-gray-500 text-sm">품질 트렌드 차트</div>
            <div className="text-xs text-gray-400 mt-1">Chart.js로 구현 예정</div>
          </div>
        </div>
      </div>

      {/* 품질 지표들 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div>
            <div className="text-sm font-medium text-gray-900">검사 완료율</div>
            <div className="text-xs text-gray-500">마지막 7일간</div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-green-600">94.2%</div>
            <div className="text-xs text-green-500">+2.1%</div>
          </div>
        </div>

        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div>
            <div className="text-sm font-medium text-gray-900">오류 발생률</div>
            <div className="text-xs text-gray-500">마지막 7일간</div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-red-600">5.8%</div>
            <div className="text-xs text-red-500">-1.2%</div>
          </div>
        </div>

        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div>
            <div className="text-sm font-medium text-gray-900">평균 처리 시간</div>
            <div className="text-xs text-gray-500">마지막 7일간</div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-blue-600">2.3분</div>
            <div className="text-xs text-blue-500">-0.5분</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QCQualityDetails;
