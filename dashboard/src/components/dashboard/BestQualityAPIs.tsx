import React from 'react';

interface APIData {
  api_type: string;
  total_inspections: number;
  total_checks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
}

interface BestQualityAPIsProps {
  data: APIData[];
}

const BestQualityAPIs: React.FC<BestQualityAPIsProps> = ({ data }) => {
  console.log('BestQualityAPIs received data:', data);
  
  // data가 배열이 아니거나 비어있는 경우 처리
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 h-full">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-2">✅</span>
          <h3 className="text-lg font-semibold text-gray-800">가장 통과률이 높은 데이터</h3>
        </div>
        <div className="flex items-center justify-center h-32">
          <div className="text-gray-500 text-sm">데이터가 없습니다</div>
        </div>
      </div>
    );
  }

  // 가장 통과률이 높은 데이터 TOP 3
  const bestQuality = data
    .sort((a, b) => b.pass_rate - a.pass_rate)
    .slice(0, 3);

  return (
    <div className="bg-white rounded-lg shadow-md p-4 h-full">
      <div className="flex items-center mb-4">
        <span className="text-2xl mr-2">✅</span>
        <h3 className="text-lg font-semibold text-gray-800">가장 통과률이 높은 데이터</h3>
      </div>
      <div className="space-y-3">
        {bestQuality.map((item, index) => (
          <div key={index} className="flex justify-between items-center p-2 bg-green-50 rounded">
            <div className="flex items-center">
              <span className="text-sm font-bold text-green-600 mr-2">#{index + 1}</span>
              <span className="text-sm font-medium text-gray-700 truncate">
                {item.api_type.replace(/_/g, ' ')}
              </span>
            </div>
            <span className="text-sm font-bold text-green-600">
              {item.pass_rate}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BestQualityAPIs;
