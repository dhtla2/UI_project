import React from 'react';
import Dash01 from '../dashboard/Dash01';
import Dash02 from '../dashboard/Dash02';
import Dash03 from '../dashboard/Dash03';
import Dash04 from '../dashboard/Dash04';
import Dash05 from '../dashboard/Dash05';
import Dash06 from '../dashboard/Dash06';
import Dash07 from '../dashboard/Dash07';
import './MainContent.css';

const MainContent: React.FC = () => {
  return (
    <main className="main-content">
      <div className="main-top-row">
        <div className="dash01-02-card">
          <Dash01 />
          <Dash02 />
        </div>
        <div className="dash03-06-group">
          <div className="dash34-row">
            <Dash03 />
            <Dash04 />
          </div>
          <div className="dash56-row">
            <Dash05 />
            <Dash06 />
          </div>
        </div>
      </div>
      <div className="main-row">
        <Dash07 />
      </div>
    </main>
  );
};

export default MainContent; 