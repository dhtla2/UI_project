import axios from 'axios';
import { AISInfo } from '../types/ais';

const API_BASE_URL = ''; // 상대 경로 사용

export class AISApiService {
  private static instance: AISApiService;
  private baseURL: string;

  private constructor() {
    this.baseURL = API_BASE_URL;
  }

  public static getInstance(): AISApiService {
    if (!AISApiService.instance) {
      AISApiService.instance = new AISApiService();
    }
    return AISApiService.instance;
  }

  // 모든 AIS 데이터 가져오기
  async getAllAISData(limit?: number): Promise<AISInfo[]> {
    try {
      const response = await axios.get(`${this.baseURL}/ais/all`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('AIS 데이터 가져오기 실패:', error);
      return [];
    }
  }

  // MMSI로 선박 검색
  async getShipsByMMSI(mmsi: string): Promise<AISInfo[]> {
    try {
      const response = await axios.get(`${this.baseURL}/ais/mmsi/${mmsi}`);
      return response.data;
    } catch (error) {
      console.error('MMSI 검색 실패:', error);
      return [];
    }
  }

  // 선박명으로 검색
  async getShipsByName(name: string): Promise<AISInfo[]> {
    try {
      const response = await axios.get(`${this.baseURL}/ais/name/${name}`);
      return response.data;
    } catch (error) {
      console.error('선박명 검색 실패:', error);
      return [];
    }
  }

  // 국적별 선박 검색
  async getShipsByFlag(flag: string): Promise<AISInfo[]> {
    try {
      const response = await axios.get(`${this.baseURL}/ais/flag/${flag}`);
      return response.data;
    } catch (error) {
      console.error('국적별 검색 실패:', error);
      return [];
    }
  }

  // 선박 타입별 필터링
  async getShipsByType(shipType: string): Promise<AISInfo[]> {
    try {
      const response = await axios.get(`${this.baseURL}/ais/type/${shipType}`);
      return response.data;
    } catch (error) {
      console.error('선박 타입별 검색 실패:', error);
      return [];
    }
  }

  // 통계 데이터 가져오기
  async getStatistics(): Promise<{
    totalShips: number;
    shipTypes: { shipType: string; count: number }[];
    flags: { flag: string; count: number }[];
    navigationStatus: { status: string; count: number }[];
  }> {
    try {
      const response = await axios.get(`${this.baseURL}/ais/statistics`);
      return response.data;
    } catch (error) {
      console.error('통계 데이터 가져오기 실패:', error);
      return {
        totalShips: 0,
        shipTypes: [],
        flags: [],
        navigationStatus: []
      };
    }
  }

  // 최신 데이터 가져오기
  async getLatestData(): Promise<AISInfo[]> {
    try {
      const response = await axios.get(`${this.baseURL}/ais/latest`);
      return response.data;
    } catch (error) {
      console.error('최신 데이터 가져오기 실패:', error);
      return [];
    }
  }
}

export default AISApiService.getInstance(); 