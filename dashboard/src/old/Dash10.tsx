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

const labels = ['패턴A', '패턴B', '패턴C', '패턴D'];
const data = {
  labels,
  datasets: [
    {
      label: '오류 건수',
      data: [12, 8, 15, 5],
      backgroundColor: 'rgba(255,99,132,0.7)',
    },
  ],
};

const options = {
  responsive: true,
  maintainAspectRatio: false,
  backgroundColor: 'transparent',
  plugins: {
    legend: { display: false },
    title: { display: true, text: '오류 패턴', font: { size: 16 } },
  },
  scales: {
    y: { beginAtZero: true, title: { display: true, text: '오류 건수' } },
    x: { title: { display: true, text: '패턴' } },
  },
};

const Dash10: React.FC = () => (
  <div className="dash dash10" style={{ background: 'transparent', height: '100%', padding: '5px', overflow: 'hidden' }}>
    <Bar data={data} options={options} />
  </div>
);

export default Dash10; 