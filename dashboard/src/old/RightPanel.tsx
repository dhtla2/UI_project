import React from 'react';
import Dash12 from '../dashboard/Dash12';
import Dash13 from '../dashboard/Dash13';
import './RightPanel.css';

const RightPanel: React.FC = () => {
  return (
    <aside className="right-panel">
      <Dash12 />
      <Dash13 />
    </aside>
  );
};

export default RightPanel; 