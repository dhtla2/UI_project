from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
import math

@dataclass
class AISInfo:
    """
    AIS 정보를 담는 기본 데이터 클래스
    DB에 있는 원본 데이터만 저장
    """
    # 기본 정보
    id: Optional[int] = None
    mmsi_no: Optional[str] = None
    imo_no: Optional[str] = None
    vssl_nm: Optional[str] = None
    call_letter: Optional[str] = None
    
    # 선박 타입 정보
    vssl_tp: Optional[str] = None
    vssl_tp_cd: Optional[str] = None
    vssl_tp_crgo: Optional[str] = None
    vssl_cls: Optional[str] = None
    
    # 선박 크기 정보
    vssl_len: Optional[float] = None
    vssl_width: Optional[float] = None
    
    # 국적 정보
    flag: Optional[str] = None
    flag_cd: Optional[str] = None
    vssl_def_brd: Optional[float] = None
    
    # 위치 정보
    lon: Optional[float] = None
    lat: Optional[float] = None
    
    # 항해 정보
    sog: Optional[float] = None  # Speed Over Ground
    cog: Optional[float] = None  # Course Over Ground
    rot: Optional[float] = None  # Rate of Turn
    head_side: Optional[float] = None  # Heading
    
    # 항해 상태
    vssl_navi: Optional[str] = None
    vssl_navi_cd: Optional[str] = None
    
    # 데이터 소스
    source: Optional[str] = None
    dt_pos_utc: Optional[str] = None
    dt_static_utc: Optional[str] = None
    
    # 선박 타입 상세
    vssl_tp_main: Optional[str] = None
    vssl_tp_sub: Optional[str] = None
    
    # 목적지 정보
    dst_nm: Optional[str] = None
    dst_cd: Optional[str] = None
    eta: Optional[str] = None
    
    # 시스템 정보
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """데이터 검증 및 변환"""
        # 숫자 필드 변환
        numeric_fields = ['vssl_len', 'vssl_width', 'vssl_def_brd', 'lon', 'lat', 'sog', 'cog', 'rot', 'head_side']
        for field in numeric_fields:
            value = getattr(self, field)
            if isinstance(value, str):
                try:
                    setattr(self, field, float(value) if value else None)
                except ValueError:
                    setattr(self, field, None)

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

@dataclass
class AISAnalyticsInfo(AISProcessedInfo):
    """
    AISProcessedInfo를 상속받아 분석 데이터를 추가로 저장하는 클래스
    """
    # 통계 분석 데이터
    average_speed: Optional[float] = None  # 평균 속도
    total_distance: Optional[float] = None  # 총 이동 거리
    port_visit_count: int = 0  # 항구 방문 횟수
    navigation_time: Optional[float] = None  # 항해 시간 (시간)
    
    # 패턴 분석 데이터
    frequent_routes: Optional[List[str]] = None  # 자주 이용하는 항로
    preferred_speed_range: Optional[str] = None  # 선호 속도 범위
    typical_navigation_status: Optional[str] = None  # 일반적인 항해 상태
    
    # 예측 데이터
    predicted_eta: Optional[str] = None  # 예상 도착 시간
    predicted_destination: Optional[str] = None  # 예상 목적지
    route_efficiency: Optional[float] = None  # 항로 효율성 (0-1)

# 사용 예시
if __name__ == "__main__":
    # 기본 AISInfo 객체 생성 (DB 데이터만)
    basic_ais = AISInfo(
        mmsi_no="312773000",
        vssl_nm="HAO XIANG 11",
        vssl_tp="GENERAL_CARGO",
        flag="Belize",
        lon=128.99793333,
        lat=35.08112667,
        sog=0.0,
        cog=173.2,
        vssl_navi="MOORED",
        dt_pos_utc="20221101191752"
    )
    
    print("=== 기본 AISInfo (DB 데이터만) ===")
    print(f"선박명: {basic_ais.vssl_nm}")
    print(f"위치: {basic_ais.lon}, {basic_ais.lat}")
    print(f"속도: {basic_ais.sog}")
    
    # 가공된 AISProcessedInfo 객체 생성
    processed_ais = AISProcessedInfo(
        mmsi_no="312773000",
        vssl_nm="HAO XIANG 11",
        vssl_tp="GENERAL_CARGO",
        flag="Belize",
        lon=128.99793333,
        lat=35.08112667,
        sog=0.0,
        cog=173.2,
        vssl_navi="MOORED",
        dt_pos_utc="20221101191752"
    )
    
    print("\n=== 가공된 AISProcessedInfo ===")
    print(f"선박명: {processed_ais.vssl_nm}")
    print(f"위치 구역: {processed_ais.location_zone}")
    print(f"항구 내부: {processed_ais.is_in_port}")
    print(f"속도 구분: {processed_ais.speed_category}")
    print(f"이동 중: {processed_ais.is_moving}")
    print(f"선박 크기: {processed_ais.ship_size_category}")
    print(f"위험도: {processed_ais.risk_level}")
    print(f"가공된 정보: {processed_ais.get_processed_info()}") 