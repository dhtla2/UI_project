import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const labels = ['유형1', '유형2', '유형3', '유형4'];
const data = {
  labels,
  datasets: [
    {
      label: '건수',
      data: [40, 55, 30, 20],
      backgroundColor: 'rgba(59,125,221,0.7)',
    },
  ],
};

const options = {
  responsive: true,
  maintainAspectRatio: false,
  backgroundColor: 'transparent',
  plugins: {
    legend: { display: false },
    title: { display: true, text: '통계 분석', font: { size: 16 } },
  },
  scales: {
    y: { beginAtZero: true, title: { display: true, text: '건수' } },
    x: { title: { display: true, text: '유형' } },
  },
};

const Dash09: React.FC = () => (
  <div className="dash dash09" style={{ background: 'transparent', height: '100%', padding: '5px', overflow: 'hidden' }}>
    <Bar data={data} options={options} />
  </div>
);

export default Dash09; 