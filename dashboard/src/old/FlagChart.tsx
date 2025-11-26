import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js';
import { Pie } from 'react-chartjs-2';
import { FlagStats } from '../../types/ais';
import aisApi from '../../services/aisApi';

ChartJS.register(ArcElement, Tooltip, Legend, Title);

interface FlagChartProps {
  title?: string;
}

const FlagChart: React.FC<FlagChartProps> = ({ title = '국적별 선박 분포' }) => {
  const [data, setData] = useState<FlagStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const statistics = await aisApi.getStatistics();
        setData(statistics.flags);
      } catch (err) {
        setError('데이터를 불러오는데 실패했습니다.');
        console.error('FlagChart 데이터 로딩 오류:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const chartData = {
    labels: data.map(item => item.flag || 'Unknown'),
    datasets: [
      {
        label: '선박 수',
        data: data.map(item => item.count),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40',
          '#FF6384',
          '#C9CBCF',
          '#4BC0C0',
          '#FF6384',
        ],
        borderColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40',
          '#FF6384',
          '#C9CBCF',
          '#4BC0C0',
          '#FF6384',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 16,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value}척 (${percentage}%)`;
          }
        }
      }
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
      <Pie data={chartData} options={options} />
    </div>
  );
};

export default FlagChart; 