import React from 'react';
import AISVisualization from '../dashboard/AISVisualization';

const RightSidebar: React.FC = () => {
  // AIS 개별 차트 컴포넌트들
  const ShipTypeChart = () => <AISVisualization viewMode="shipType" />;
  const NationalityChart = () => <AISVisualization viewMode="nationality" />;
  const SpeedChart = () => <AISVisualization viewMode="speed" />;

  return (
    <div className="right-sidebar bg-white shadow-lg p-4 w-80 h-full overflow-y-auto mt-8">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-800 text-center">
          AIS 상세 분석
        </h3>
      </div>
      
      {/* 선박 타입 분포 */}
      <div className="mb-6">
        <div className="bg-gray-50 p-3 rounded-xl shadow-sm">
          <h4 className="text-sm font-semibold text-gray-700 mb-2 text-center">
            선박 타입 분포
          </h4>
          <div className="h-72">
            <ShipTypeChart />
          </div>
        </div>
      </div>

      {/* 국적별 분포 */}
      <div className="mb-6">
        <div className="bg-gray-50 p-3 rounded-xl shadow-sm">
          <h4 className="text-sm font-semibold text-gray-700 mb-2 text-center">
            국적별 분포
          </h4>
          <div className="h-72">
            <NationalityChart />
          </div>
        </div>
      </div>

      {/* 속도 통계 */}
      <div className="mb-6">
        <div className="bg-gray-50 p-3 rounded-xl shadow-sm">
          <h4 className="text-sm font-semibold text-gray-700 mb-2 text-center">
            속도 통계
          </h4>
          <div className="h-72">
            <SpeedChart />
          </div>
        </div>
      </div>
    </div>
  );
};

export default RightSidebar;
