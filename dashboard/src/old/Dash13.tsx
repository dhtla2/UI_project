import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js';
import { Pie } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, Title);

const data = {
  labels: ['AIS', 'TOS', '기타'],
  datasets: [
    {
      label: '조회 비율',
      data: [60, 30, 10],
      backgroundColor: [
        '#3b7ddd',
        '#ffb300',
        '#4bc0c0',
      ],
      borderColor: [
        '#3b7ddd',
        '#ffb300',
        '#4bc0c0',
      ],
      borderWidth: 1,
    },
  ],
};

const options = {
  responsive: true,
  maintainAspectRatio: false,
  backgroundColor: 'transparent',
  plugins: {
    legend: {
      position: 'bottom' as const,
    },
    title: {
      display: true,
      text: '사용자 활동 요약',
      font: { size: 16 },
    },
    tooltip: {
      callbacks: {
        label: function(context: any) {
          const label = context.label || '';
          const value = context.parsed;
          const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
          const percentage = ((value / total) * 100).toFixed(1);
          return `${label}: ${value}회 (${percentage}%)`;
        }
      }
    }
  },
};

const Dash13: React.FC = () => (
  <div className="dash dash13" style={{ background: 'transparent', height: '100%', padding: '5px', overflow: 'hidden' }}>
    <Pie data={data} options={options} />
  </div>
);

export default Dash13; 