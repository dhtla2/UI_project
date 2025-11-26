import React, { useState, useEffect } from 'react';
import aisApi from '../../services/aisApi';

const Dash03: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const statistics = await aisApi.getStatistics();
        setStats(statistics);
      } catch (err) {
        setError('통계 데이터를 불러오는데 실패했습니다.');
        console.error('Dash03 통계 로딩 오류:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="dash dash03" style={{ background: 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div>통계 데이터를 불러오는 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dash dash03" style={{ background: 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'red' }}>
        <div>{error}</div>
      </div>
    );
  }

  return (
    <div className="dash dash03" style={{ background: 'transparent', padding: '0px' }}>
      <h3 style={{ marginBottom: '0px', textAlign: 'center', fontSize: '16px' }}>데이터 현황</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
        <div style={{ textAlign: 'center', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h4 style={{ margin: '0 0 5px 0', color: '#3b7ddd', fontSize: '14px' }}>총 선박 수</h4>
          <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#3b7ddd' }}>
            {stats?.totalShips || 0}
          </div>
        </div>
        
        <div style={{ textAlign: 'center', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h4 style={{ margin: '0 0 5px 0', color: '#ffb300', fontSize: '14px' }}>선박 타입 수</h4>
          <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#ffb300' }}>
            {stats?.shipTypes?.length || 0}
          </div>
        </div>
        
        {/* <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#28a745' }}>국적 수</h4>
          <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#28a745' }}>
            {stats?.flags?.length || 0}
          </div>
        </div>
        
        <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#dc3545' }}>항해 상태 수</h4>
          <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#dc3545' }}>
            {stats?.navigationStatus?.length || 0}
          </div>
        </div> */}
      </div>
    </div>
  );
};

export default Dash03; 