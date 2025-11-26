import React, { useState } from 'react';

interface FieldResult {
  field: string;
  group: string;
  status: 'PASS' | 'FAIL';
  total: number;
  check: number;
  etc: number;
  message: string;
  checkType: string;
}

interface FieldAnalysisTableProps {
  results: FieldResult[];
}

const FieldAnalysisTable: React.FC<FieldAnalysisTableProps> = ({ results }) => {
  const [filter, setFilter] = useState<'all' | 'completeness' | 'validity'>('all');
  const [sortBy, setSortBy] = useState<'field' | 'group' | 'status'>('field');

  const filteredResults = results.filter(result => 
    filter === 'all' || result.checkType === filter
  );

  const sortedResults = [...filteredResults].sort((a, b) => {
    switch (sortBy) {
      case 'field':
        return a.field.localeCompare(b.field);
      case 'group':
        return a.group.localeCompare(b.group);
      case 'status':
        return a.status.localeCompare(b.status);
      default:
        return 0;
    }
  });

  const getStatusBadge = (status: string) => {
    if (status === 'PASS') {
      return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">양호</span>;
    }
    return <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">주의</span>;
  };

  const getCheckTypeBadge = (checkType: string) => {
    if (checkType === 'completeness') {
      return <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">완전성</span>;
    }
    return <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs">유효성</span>;
  };

  return (
    <div className="h-full p-4 bg-gray-50">
      <h3 className="text-lg font-bold text-center text-gray-800 mb-4">
        필드별 상세 분석
      </h3>
      
      {/* 필터 및 정렬 컨트롤 */}
      <div className="mb-4 flex gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">검사 유형</label>
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value as any)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
          >
            <option value="all">전체</option>
            <option value="completeness">완전성</option>
            <option value="validity">유효성</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">정렬 기준</label>
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
          >
            <option value="field">필드명</option>
            <option value="group">그룹</option>
            <option value="status">상태</option>
          </select>
        </div>
      </div>

      {/* 테이블 */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full table-fixed divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="w-[15%] px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  필드명
                </th>
                <th className="w-[12%] px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  그룹
                </th>
                <th className="w-[10%] px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  검사 유형
                </th>
                <th className="w-[8%] px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  상태
                </th>
                <th className="w-[15%] px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  검사 결과
                </th>
                <th className="w-[40%] px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  메시지
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedResults.map((result, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="w-[15%] px-4 py-3 text-sm font-medium text-gray-900 text-center">
                    {result.field}
                  </td>
                  <td className="w-[12%] px-4 py-3 text-sm text-gray-500 text-center">
                    {result.group}
                  </td>
                  <td className="w-[10%] px-4 py-3 text-center">
                    {getCheckTypeBadge(result.checkType)}
                  </td>
                  <td className="w-[8%] px-4 py-3 text-center">
                    {getStatusBadge(result.status)}
                  </td>
                  <td className="w-[15%] px-4 py-3 text-sm text-gray-500 text-center">
                    <div className="text-xs">
                      <div>총계: {result.total}</div>
                      <div>정상: {result.etc}</div>
                      <div>오류: {result.check}</div>
                    </div>
                  </td>
                  <td className="w-[40%] px-4 py-3 text-sm text-gray-500 text-left">
                    <div className="line-clamp-2">
                      {result.message || (
                        result.check > 0 
                          ? `${result.field}: ${result.check.toLocaleString()}개 레코드에서 문제 발생 (전체 ${result.total.toLocaleString()}개 중)`
                          : '✅ 정상'
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FieldAnalysisTable;
