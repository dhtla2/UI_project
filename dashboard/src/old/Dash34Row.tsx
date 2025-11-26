import React from 'react';
import Dash03 from './Dash03';
import Dash04 from './Dash04';
import './Dash34Row.css';

const Dash34Row: React.FC = () => (
  <div className="dash34-row">
    <div className="dash34-cell"><Dash03 /></div>
    <div className="dash34-cell"><Dash04 /></div>
  </div>
);

export default Dash34Row; 