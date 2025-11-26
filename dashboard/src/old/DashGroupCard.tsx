import React from 'react';
import Dash34Row from './Dash34Row';
import Dash03 from './Dash03';
import Dash05 from './Dash05';
import Dash06 from './Dash06';
import './DashGroupCard.css';

const DashGroupCard: React.FC = () => (
  <div className="dash-group-card">
    <div className="dash-group-grid">
      <div className="dash34-row-cell"><Dash34Row /></div>
      <div className="dash03-large"><Dash03 /></div>
      <div className="dash05"><Dash05 /></div>
      <div className="dash06"><Dash06 /></div>
    </div>
  </div>
);

export default DashGroupCard; 