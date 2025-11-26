import axios from 'axios';

// MQTT 데이터 서비스
export class MqttDataService {
  private baseUrl = ''; // 상대 경로 사용

  // 최근 검사 결과 조회
  async getRecentInspections(limit: number = 10) {
    try {
      const response = await axios.get(`${this.baseUrl}/api/dashboard/recent-inspections?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('최근 검사 결과 조회 실패:', error);
      return [];
    }
  }

  // 품질 메트릭 요약 조회
  async getQualityMetricsSummary(days: number = 7) {
    try {
      const response = await axios.get(`${this.baseUrl}/api/dashboard/quality-metrics?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('품질 메트릭 요약 조회 실패:', error);
      return {};
    }
  }

  // 데이터 소스별 통계 조회
  async getDataSourceStats(days: number = 7) {
    try {
      const response = await axios.get(`${this.baseUrl}/api/dashboard/data-source-stats?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('데이터 소스별 통계 조회 실패:', error);
      return [];
    }
  }

  // 성능 트렌드 조회
  async getPerformanceTrends(days: number = 7) {
    try {
      const response = await axios.get(`${this.baseUrl}/api/dashboard/performance-trends?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('성능 트렌드 조회 실패:', error);
      return [];
    }
  }

  // 지연시간 메트릭 요약 조회
  async getDelayMetricsSummary(days: number = 7) {
    try {
      const response = await axios.get(`${this.baseUrl}/api/dashboard/delay-metrics?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('지연시간 메트릭 요약 조회 실패:', error);
      return {};
    }
  }

  // 오류 요약 조회
  async getErrorSummary(days: number = 7) {
    try {
      const response = await axios.get(`${this.baseUrl}/api/dashboard/error-summary?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('오류 요약 조회 실패:', error);
      return [];
    }
  }

  // 특정 검사 상세 정보 조회
  async getInspectionDetails(inspectionId: string) {
    try {
      const response = await axios.get(`${this.baseUrl}/api/dashboard/inspection-details/${inspectionId}`);
      return response.data;
    } catch (error) {
      console.error('검사 상세 정보 조회 실패:', error);
      return {};
    }
  }

  // 실시간 데이터 스트림 (WebSocket 대신 폴링)
  startRealtimeUpdates(callback: (data: any) => void, interval: number = 5000) {
    const intervalId = setInterval(async () => {
      try {
        const recentData = await this.getRecentInspections(5);
        callback(recentData);
      } catch (error) {
        console.error('실시간 업데이트 실패:', error);
      }
    }, interval);

    return () => clearInterval(intervalId);
  }
}

// 싱글톤 인스턴스
export const mqttDataService = new MqttDataService();
