import React from 'react';

interface QCDataQualityStatusProps {
  qualityStatus?: any;
}

const QCDataQualityStatus: React.FC<QCDataQualityStatusProps> = ({ qualityStatus }) => {
  return (
    <div className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">QC 데이터 품질 상태</h3>
      
      {/* 전체 상태 */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">전체 상태</span>
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
            양호
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }}></div>
        </div>
        <div className="text-xs text-gray-500 mt-1">85% - 정상 범위</div>
      </div>

      {/* 세부 상태들 */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">데이터 수집</span>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-green-600 font-medium">정상</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">데이터 검증</span>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <span className="text-sm text-yellow-600 font-medium">주의</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">데이터 저장</span>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-green-600 font-medium">정상</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">데이터 전송</span>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-green-600 font-medium">정상</span>
          </div>
        </div>
      </div>

      {/* 알림 섹션 */}
      <div className="mt-6 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-start space-x-2">
          <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
          <div>
            <div className="text-sm font-medium text-yellow-800">주의사항</div>
            <div className="text-xs text-yellow-700 mt-1">
              데이터 검증 과정에서 일부 오류가 감지되었습니다. 확인이 필요합니다.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QCDataQualityStatus;
