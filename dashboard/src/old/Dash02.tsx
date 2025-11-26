import React from 'react';
import ShipTypeChart from '../charts/ShipTypeChart';

const Dash02: React.FC = () => (
  <div className="dash dash02" style={{ background: 'transparent' }}>
    <ShipTypeChart title="선박 타입별 분포" />
  </div>
);

export default Dash02; 