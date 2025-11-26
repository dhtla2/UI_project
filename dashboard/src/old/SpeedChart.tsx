import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import aisApi from '../../services/aisApi';
import { AISInfo } from '../../types/ais';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface SpeedChartProps {
  title?: string;
}

const SpeedChart: React.FC<SpeedChartProps> = ({ title = '선박 속도 분포' }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const aisData = await aisApi.getAllAISData(1000); // 최근 1000개 데이터
        
        // 속도 구간별로 데이터 그룹화
        const speedRanges = {
          '0-5': 0,
          '5-10': 0,
          '10-15': 0,
          '15-20': 0,
          '20-25': 0,
          '25+': 0
        };

        aisData.forEach((ship: AISInfo) => {
          if (ship.sog !== undefined && ship.sog !== null) {
      const speed = ship.sog;
            if (speed >= 0 && speed < 5) speedRanges['0-5']++;
            else if (speed >= 5 && speed < 10) speedRanges['5-10']++;
            else if (speed >= 10 && speed < 15) speedRanges['10-15']++;
            else if (speed >= 15 && speed < 20) speedRanges['15-20']++;
            else if (speed >= 20 && speed < 25) speedRanges['20-25']++;
            else if (speed >= 25) speedRanges['25+']++;
          }
  });

  const chartData = {
          labels: ['0-5 knots', '5-10 knots', '10-15 knots', '15-20 knots', '20-25 knots', '25+ knots'],
    datasets: [
      {
        label: '선박 수',
              data: Object.values(speedRanges),
              backgroundColor: 'rgba(54, 162, 235, 0.5)',
              borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

        setData(chartData);
      } catch (err) {
        setError('데이터를 불러오는데 실패했습니다.');
        console.error('SpeedChart 데이터 로딩 오류:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 16,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: '선박 수',
        },
      },
      x: {
        title: {
          display: true,
          text: '속도 구간',
        },
      },
    },
  };

  if (loading) {
    return (
      <div style={{ width: '100%', height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div>데이터를 불러오는 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ width: '100%', height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'red' }}>
        <div>{error}</div>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <Bar data={data} options={options} />
    </div>
  );
};

export default SpeedChart; 