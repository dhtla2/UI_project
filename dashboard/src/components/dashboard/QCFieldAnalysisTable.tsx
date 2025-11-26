import React from 'react';

interface QCFieldAnalysisData {
  field: string;
  totalChecks: number;
  passCount: number;
  failCount: number;
  passRate: number;
  commonIssues: string[];
}

interface QCFieldAnalysisTableProps {
  data: QCFieldAnalysisData[];
}

const QCFieldAnalysisTable: React.FC<QCFieldAnalysisTableProps> = ({ data }) => {
  return (
    <div className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">QC 필드 분석</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                필드명
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                총 검사
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                통과
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                실패
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                통과율
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                주요 이슈
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((item, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {item.field}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {item.totalChecks}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className="text-green-600 font-medium">{item.passCount}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className="text-red-600 font-medium">{item.failCount}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${item.passRate}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{item.passRate.toFixed(1)}%</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500 text-left">
                  {item.commonIssues.length > 0 ? (
                    <div className="space-y-1">
                      {item.commonIssues.map((issue, issueIndex) => (
                        <span 
                          key={issueIndex}
                          className="inline-block bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full mr-1"
                        >
                          {issue}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-green-600">없음</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default QCFieldAnalysisTable;
