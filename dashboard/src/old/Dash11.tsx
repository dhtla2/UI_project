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

const labels = ['분석A', '분석B', '분석C', '분석D'];
const data = {
  labels,
  datasets: [
    {
      label: '오류 비율(%)',
      data: [10, 7, 12, 5],
      backgroundColor: 'rgba(255,179,0,0.7)',
    },
  ],
};

const options = {
  responsive: true,
  maintainAspectRatio: false,
  backgroundColor: 'transparent',
  plugins: {
    legend: { display: false },
    title: { display: true, text: '오류 패턴 분석', font: { size: 16 } },
  },
  scales: {
    y: { beginAtZero: true, title: { display: true, text: '오류 비율(%)' } },
    x: { title: { display: true, text: '분석 항목' } },
  },
};

const Dash11: React.FC = () => (
  <div className="dash dash11" style={{ background: 'transparent', height: '100%', padding: '5px', overflow: 'hidden' }}>
    <Bar data={data} options={options} />
  </div>
);

export default Dash11; 