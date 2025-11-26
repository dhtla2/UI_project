import React from 'react';
import WorstQualityAPIs from '../dashboard/WorstQualityAPIs';
import KeyAlerts from '../dashboard/KeyAlerts';
import { APIQualityData } from '../../services/apiService';

interface CommonSideSectionProps {
  loading: boolean;
  error: string | null;
  apiQualityData: APIQualityData[];
}

const CommonSideSection: React.FC<CommonSideSectionProps> = ({
  loading,
  error,
  apiQualityData
}) => {
  return (
    <div className="flex flex-col gap-4 w-1/4">
      <div className="dashboard-card h-80 w-full">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-500">로딩 중...</div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-red-500 text-sm">{error}</div>
          </div>
        ) : (
          <WorstQualityAPIs data={apiQualityData} />
        )}
      </div>
      <div className="dashboard-card h-80 w-full">
        <KeyAlerts />
      </div>
    </div>
  );
};

export default CommonSideSection;
