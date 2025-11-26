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

const labels = ['컬럼A', '컬럼B', '컬럼C', '컬럼D', '컬럼E', '컬럼F'];
const data = {
  labels,
  datasets: [
    {
      label: '에러레이트(%)',
      data: [2.1, 1.5, 3.2, 0.8, 2.7, 1.1],
      backgroundColor: 'rgba(59,125,221,0.7)',
      borderColor: '#3b7ddd',
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
      display: false,
    },
    title: {
      display: true,
      text: '컬럼별 에러레이트 추이',
      font: { size: 14 },
    },
    tooltip: {
      callbacks: {
        label: function(context: any) {
          return `${context.parsed.y}%`;
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: { display: true, text: '에러레이트(%)', font: { size: 12 } },
      max: 5,
      ticks: { font: { size: 10 } }
    },
    x: {
      title: { display: true, text: '컬럼명', font: { size: 12 } },
      ticks: { font: { size: 10 } }
    },
  },
};

const Dash07: React.FC = () => (
  <div className="dash dash07" style={{ background: 'transparent', height: '100%', padding: '5px', overflow: 'hidden' }}>
    <Bar data={data} options={options} />
  </div>
);

export default Dash07; 