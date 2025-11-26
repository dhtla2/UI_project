import React from 'react';

interface TCFieldAnalysisTableProps {
  results?: Array<{
    field: string;
    totalChecks: number;
    passCount: number;
    failCount: number;
    passRate: number;
    commonIssues: string[];
  }>;
}

const TCFieldAnalysisTable: React.FC<TCFieldAnalysisTableProps> = ({ results }) => {
  const mockResults = results || [
    {
      field: '작업 ID',
      totalChecks: 150,
      passCount: 145,
      failCount: 5,
      passRate: 96.7,
      commonIssues: ['누락된 ID', '잘못된 형식']
    },
    {
      field: '터미널 ID',
      totalChecks: 150,
      passCount: 150,
      failCount: 0,
      passRate: 100.0,
      commonIssues: []
    },
    {
      field: '선박 코드',
      totalChecks: 150,
      passCount: 142,
      failCount: 8,
      passRate: 94.7,
      commonIssues: ['잘못된 선박 코드', '누락된 정보']
    },
    {
      field: '컨테이너 번호',
      totalChecks: 150,
      passCount: 138,
      failCount: 12,
      passRate: 92.0,
      commonIssues: ['잘못된 형식', '중복 번호']
    },
    {
      field: '작업 시간',
      totalChecks: 150,
      passCount: 148,
      failCount: 2,
      passRate: 98.7,
      commonIssues: ['미래 시간']
    },
    {
      field: '작업 유형',
      totalChecks: 150,
      passCount: 150,
      failCount: 0,
      passRate: 100.0,
      commonIssues: []
    }
  ];

  const getStatusColor = (passRate: number) => {
    if (passRate >= 95) return 'text-green-600 bg-green-100';
    if (passRate >= 85) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">TC 필드별 상세 분석</h3>
      
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
                주요 문제점
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {mockResults.map((result, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {result.field}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {result.totalChecks}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                  {result.passCount}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                  {result.failCount}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(result.passRate)}`}>
                    {result.passRate}%
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500 text-left">
                  {result.commonIssues.length > 0 ? (
                    <ul className="list-disc list-inside space-y-1">
                      {result.commonIssues.map((issue, issueIndex) => (
                        <li key={issueIndex} className="text-xs">{issue}</li>
                      ))}
                    </ul>
                  ) : (
                    <span className="text-green-600">문제 없음</span>
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

export default TCFieldAnalysisTable;
