import React from 'react';

interface QCInspectionHistoryData {
  inspectionId: string;
  inspectionDatetime: string;
  totalChecks: number;
  passCount: number;
  failCount: number;
  passRate: number;
  completenessRate?: number;
  validityRate?: number;
}

interface QCInspectionHistoryProps {
  history: QCInspectionHistoryData[];
}

const QCInspectionHistory: React.FC<QCInspectionHistoryProps> = ({ history }) => {
  return (
    <div className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">QC 검사 히스토리</h3>
      
      {/* 요약 카드들 */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-blue-50 p-3 rounded-lg text-center">
          <div className="text-xs text-blue-600 font-medium">총 검사</div>
          <div className="text-lg font-bold text-blue-900">
            {history.reduce((sum, item) => sum + item.totalChecks, 0)}
          </div>
        </div>
        <div className="bg-green-50 p-3 rounded-lg text-center">
          <div className="text-xs text-green-600 font-medium">통과</div>
          <div className="text-lg font-bold text-green-900">
            {history.reduce((sum, item) => sum + item.passCount, 0)}
          </div>
        </div>
        <div className="bg-red-50 p-3 rounded-lg text-center">
          <div className="text-xs text-red-600 font-medium">실패</div>
          <div className="text-lg font-bold text-red-900">
            {history.reduce((sum, item) => sum + item.failCount, 0)}
          </div>
        </div>
      </div>

      {/* 히스토리 테이블 */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                검사 ID
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                검사 시간
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                통과율
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                상태
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {history.map((item, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                  {item.inspectionId}
                </td>
                <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                  {item.inspectionDatetime}
                </td>
                <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                  <div className="flex items-center">
                    <div className="w-12 bg-gray-200 rounded-full h-1 mr-2">
                      <div 
                        className={`h-1 rounded-full ${
                          item.passRate >= 90 ? 'bg-green-500' : 
                          item.passRate >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${item.passRate}%` }}
                      ></div>
                    </div>
                    <span className="text-xs font-medium">{item.passRate.toFixed(1)}%</span>
                  </div>
                </td>
                <td className="px-3 py-2 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    item.passRate >= 90 ? 'bg-green-100 text-green-800' : 
                    item.passRate >= 70 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {item.passRate >= 90 ? '우수' : item.passRate >= 70 ? '양호' : '주의'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {history.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <div className="text-sm">검사 히스토리가 없습니다.</div>
        </div>
      )}
    </div>
  );
};

export default QCInspectionHistory;
