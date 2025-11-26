import React from 'react';
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

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const labels = ['API_01', 'API_02', 'API_03', 'API_04', 'API_05'];
const data = {
  labels,
  datasets: [
    {
      label: '일일 조회수',
      data: [120, 90, 60, 30, 15],
      backgroundColor: 'rgba(59,125,221,0.7)',
      borderColor: '#3b7ddd',
      borderWidth: 1,
      borderRadius: 6,
    },
    {
      label: '주간 다운로드',
      data: [300, 210, 180, 90, 40],
      backgroundColor: 'rgba(255,179,0,0.7)',
      borderColor: '#ffb300',
      borderWidth: 1,
      borderRadius: 6,
    },
  ],
};

const options = {
  responsive: true,
  maintainAspectRatio: false,
  backgroundColor: 'transparent',
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: '데이터 활용 현황',
      font: { size: 16 },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      title: { display: true, text: '건수' },
    },
    x: {
      title: { display: true, text: 'API명' },
    },
  },
};

const Dash12: React.FC = () => (
  <div className="dash dash12" style={{ background: 'transparent', height: '100%', padding: '5px', overflow: 'hidden' }}>
    <Bar data={data} options={options} />
  </div>
);

export default Dash12; 