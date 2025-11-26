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

const labels = ['항목A', '항목B', '항목C', '항목D'];
const data = {
  labels,
  datasets: [
    {
      label: '검사 통과',
      data: [80, 70, 90, 60],
      backgroundColor: 'rgba(59,125,221,0.7)',
    },
    {
      label: '검사 실패',
      data: [5, 10, 3, 15],
      backgroundColor: 'rgba(255,99,132,0.7)',
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
      labels: { 
        font: { size: 10 },
        padding: 8
      } 
    },
    title: { 
      display: true, 
      text: '데이터 검사 결과', 
      font: { size: 12 } 
    },
  },
  scales: {
    y: { 
      beginAtZero: true, 
      title: { display: true, text: '건수', font: { size: 10 } },
      ticks: { font: { size: 9 } }
    },
    x: { 
      title: { display: true, text: '검사 항목', font: { size: 10 } },
      ticks: { font: { size: 9 } }
    },
  },
};

const Dash08: React.FC = () => (
  <div className="dash dash08" style={{ 
    background: 'transparent', 
    height: '100%', 
    padding: '5px', 
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column'
  }}>
    <div style={{ flex: 1, minHeight: 0 }}>
    <Bar data={data} options={options} />
    </div>
  </div>
);

export default Dash08; 