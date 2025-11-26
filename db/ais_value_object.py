from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import pymysql
import pandas as pd
import math
from typing import Dict
from ais_service import AISInfo

@dataclass
class AISProcessedInfo(AISInfo):
    """
    AISInfo를 상속받아 가공된 데이터를 추가로 저장하는 클래스
    """
    # 가공된 위치 정보
    location_zone: Optional[str] = None  # 위치 구역 (예: 부산항, 인천항 등)
    is_in_port: bool = False  # 항구 내부 여부
    distance_from_port: Optional[float] = None  # 항구로부터의 거리 (해리)
    
    # 가공된 항해 정보
    speed_category: Optional[str] = None  # 속도 구분 (정박, 저속, 고속 등)
    course_direction: Optional[str] = None  # 진행 방향 (N, S, E, W, NE, NW, SE, SW)
    is_moving: bool = False  # 이동 중인지 여부
    
    # 가공된 선박 정보
    ship_size_category: Optional[str] = None  # 선박 크기 구분 (소형, 중형, 대형)
    cargo_type_category: Optional[str] = None  # 화물 타입 구분
    
    # 시간 관련 가공 정보
    time_category: Optional[str] = None  # 시간대 구분 (새벽, 오전, 오후, 저녁, 밤)
    is_recent_data: bool = False  # 최근 데이터 여부 (24시간 이내)
    
    # 위험도 관련 가공 정보
    risk_level: Optional[str] = None  # 위험도 레벨 (낮음, 보통, 높음)
    collision_risk: Optional[float] = None  # 충돌 위험도 (0-1)
    
    def __post_init__(self):
        """부모 클래스 초기화 후 가공 데이터 계산"""
        super().__post_init__()
        self._calculate_processed_data()
    
    def _calculate_processed_data(self):
        """가공된 데이터 계산"""
        self._calculate_location_data()
        self._calculate_navigation_data()
        self._calculate_ship_data()
        self._calculate_time_data()
        self._calculate_risk_data()
    
    def _calculate_location_data(self):
        """위치 관련 가공 데이터 계산"""
        if self.lon and self.lat:
            # 부산항 근처 여부 확인 (예시)
            busan_port_lon, busan_port_lat = 129.0, 35.1
            distance = self._calculate_distance(self.lon, self.lat, busan_port_lon, busan_port_lat)
            
            if distance < 10:  # 10해리 이내
                self.location_zone = "부산항"
                self.is_in_port = True
            elif distance < 50:  # 50해리 이내
                self.location_zone = "부산항 근해"
                self.is_in_port = False
            else:
                self.location_zone = "원양"
                self.is_in_port = False
            
            self.distance_from_port = distance
    
    def _calculate_navigation_data(self):
        """항해 관련 가공 데이터 계산"""
        # 속도 구분
        if self.sog is None or self.sog == 0:
            self.speed_category = "정박"
            self.is_moving = False
        elif self.sog < 5:
            self.speed_category = "저속"
            self.is_moving = True
        elif self.sog < 15:
            self.speed_category = "중속"
            self.is_moving = True
        else:
            self.speed_category = "고속"
            self.is_moving = True
        
        # 진행 방향 계산
        if self.cog is not None:
            self.course_direction = self._get_direction_from_course(self.cog)
    
    def _calculate_ship_data(self):
        """선박 관련 가공 데이터 계산"""
        # 선박 크기 구분
        if self.vssl_len:
            if self.vssl_len < 100:
                self.ship_size_category = "소형"
            elif self.vssl_len < 200:
                self.ship_size_category = "중형"
            else:
                self.ship_size_category = "대형"
        
        # 화물 타입 구분
        if self.vssl_tp:
            if "CARGO" in self.vssl_tp.upper():
                self.cargo_type_category = "화물선"
            elif "TANKER" in self.vssl_tp.upper():
                self.cargo_type_category = "탱커선"
            elif "CONTAINER" in self.vssl_tp.upper():
                self.cargo_type_category = "컨테이너선"
            else:
                self.cargo_type_category = "기타"
    
    def _calculate_time_data(self):
        """시간 관련 가공 데이터 계산"""
        if self.dt_pos_utc:
            try:
                # 시간대 구분 (UTC 기준)
                hour = int(self.dt_pos_utc[8:10])
                if 5 <= hour < 12:
                    self.time_category = "오전"
                elif 12 <= hour < 17:
                    self.time_category = "오후"
                elif 17 <= hour < 21:
                    self.time_category = "저녁"
                else:
                    self.time_category = "밤"
                
                # 최근 데이터 여부 (24시간 이내)
                # 실제로는 datetime 비교가 필요하지만 여기서는 간단히 처리
                self.is_recent_data = True  # 실제로는 시간 비교 로직 필요
                
            except (ValueError, IndexError):
                pass
    
    def _calculate_risk_data(self):
        """위험도 관련 가공 데이터 계산"""
        risk_score = 0
        
        # 속도가 높을수록 위험도 증가
        if self.sog and self.sog > 15:
            risk_score += 2
        elif self.sog and self.sog > 10:
            risk_score += 1
        
        # 항구 내부에서 고속 이동 시 위험도 증가
        if self.is_in_port and self.sog and self.sog > 10:
            risk_score += 3
        
        # 정박 상태가 아닐 때 위험도 증가
        if self.vssl_navi != "MOORED":
            risk_score += 1
        
        # 위험도 레벨 결정
        if risk_score >= 4:
            self.risk_level = "높음"
            self.collision_risk = 0.8
        elif risk_score >= 2:
            self.risk_level = "보통"
            self.collision_risk = 0.5
        else:
            self.risk_level = "낮음"
            self.collision_risk = 0.2
    
    def _calculate_distance(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """두 지점 간의 거리 계산 (해리 단위)"""
        # Haversine 공식 사용
        R = 3440.065  # 지구 반지름 (해리)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _get_direction_from_course(self, course: float) -> str:
        """코스를 방향으로 변환"""
        if 337.5 <= course or course < 22.5:
            return "N"
        elif 22.5 <= course < 67.5:
            return "NE"
        elif 67.5 <= course < 112.5:
            return "E"
        elif 112.5 <= course < 157.5:
            return "SE"
        elif 157.5 <= course < 202.5:
            return "S"
        elif 202.5 <= course < 247.5:
            return "SW"
        elif 247.5 <= course < 292.5:
            return "W"
        else:
            return "NW"
    
    def get_processed_info(self) -> Dict:
        """가공된 정보를 딕셔너리로 반환"""
        return {
            'location_zone': self.location_zone,
            'is_in_port': self.is_in_port,
            'distance_from_port': self.distance_from_port,
            'speed_category': self.speed_category,
            'course_direction': self.course_direction,
            'is_moving': self.is_moving,
            'ship_size_category': self.ship_size_category,
            'cargo_type_category': self.cargo_type_category,
            'time_category': self.time_category,
            'is_recent_data': self.is_recent_data,
            'risk_level': self.risk_level,
            'collision_risk': self.collision_risk
        }