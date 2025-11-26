import React from 'react';
import Dash08 from '../dashboard/Dash08';
import Dash09 from '../dashboard/Dash09';
import Dash10 from '../dashboard/Dash10';
import Dash11 from '../dashboard/Dash11';
import Dash14 from '../dashboard/Dash14';
import './BottomPanel.css';

const BottomPanel: React.FC = () => {
  return (
    <section className="bottom-panel">
      <div className="bottom-grid">
        <Dash08 />
        <Dash09 />
        <Dash10 />
        <Dash11 />
        <Dash14 />
      </div>
    </section>
  );
};

export default BottomPanel; 