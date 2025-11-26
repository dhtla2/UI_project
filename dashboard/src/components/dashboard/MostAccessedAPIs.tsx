import React from 'react';

interface APIData {
  api_type: string;
  total_inspections: number;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
}

interface MostAccessedAPIsProps {
  data: APIData[];
}

const MostAccessedAPIs: React.FC<MostAccessedAPIsProps> = ({ data }) => {
  console.log('MostAccessedAPIs received data:', data);
  console.log('Data type:', typeof data);
  console.log('Is array:', Array.isArray(data));
  console.log('Data length:', data?.length);
  console.log('Data content:', JSON.stringify(data, null, 2));
  
  // data가 배열이 아니거나 비어있는 경우 처리
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 h-full">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-2">🔥</span>
          <h3 className="text-lg font-semibold text-gray-800">가장 많이 검사된 데이터</h3>
        </div>
        <div className="flex items-center justify-center h-32">
          <div className="text-gray-500 text-sm">데이터가 없습니다</div>
        </div>
      </div>
    );
  }

  // 가장 많이 검사된 데이터 TOP 3 (total_inspections 기준)
  const mostAccessed = data
    .sort((a, b) => b.total_inspections - a.total_inspections)
    .slice(0, 3);

  return (
    <div className="bg-white rounded-lg shadow-md p-4 h-full">
      <div className="flex items-center mb-4">
        <span className="text-2xl mr-2">🔥</span>
        <h3 className="text-lg font-semibold text-gray-800">가장 많이 검사된 데이터</h3>
      </div>
      <div className="space-y-3">
        {mostAccessed.map((item, index) => (
          <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
            <div className="flex items-center">
              <span className="text-sm font-bold text-blue-600 mr-2">#{index + 1}</span>
              <span className="text-sm font-medium text-gray-700 truncate">
                {item.api_type.replace(/_/g, ' ')}
              </span>
            </div>
            <span className="text-sm font-bold text-blue-600">
              {item.total_inspections}건
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MostAccessedAPIs;
