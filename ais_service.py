import mysql.connector
from typing import List, Optional, Dict, Any
from ais_models import AISInfo, AISProcessedInfo, AISAnalyticsInfo
import pandas as pd
from datetime import datetime, timedelta

class AISRepository:
    """AIS 데이터베이스 접근을 담당하는 클래스"""
    
    def __init__(self, host='localhost', user='root', password='1234', database='ais_database'):
        self.connection_params = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
    
    def get_connection(self):
        """데이터베이스 연결 생성"""
        return mysql.connector.connect(**self.connection_params)
    
    def get_all_ais_data(self) -> List[AISInfo]:
        """모든 AIS 데이터 조회"""
        query = """
        SELECT * FROM ais_data 
        ORDER BY created_at DESC
        """
        
        ais_list = []
        with self.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                
                for row in rows:
                    ais_info = AISInfo(**row)
                    ais_list.append(ais_info)
        
        return ais_list
    
    def get_ais_by_mmsi(self, mmsi_no: str) -> List[AISInfo]:
        """MMSI 번호로 AIS 데이터 조회"""
        query = """
        SELECT * FROM ais_data 
        WHERE mmsi_no = %s 
        ORDER BY dt_pos_utc DESC
        """
        
        ais_list = []
        with self.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, (mmsi_no,))
                rows = cursor.fetchall()
                
                for row in rows:
                    ais_info = AISInfo(**row)
                    ais_list.append(ais_info)
        
        return ais_list
    
    def get_ais_by_location(self, min_lon: float, max_lon: float, min_lat: float, max_lat: float) -> List[AISInfo]:
        """지정된 영역의 AIS 데이터 조회"""
        query = """
        SELECT * FROM ais_data 
        WHERE lon BETWEEN %s AND %s AND lat BETWEEN %s AND %s
        ORDER BY created_at DESC
        """
        
        ais_list = []
        with self.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, (min_lon, max_lon, min_lat, max_lat))
                rows = cursor.fetchall()
                
                for row in rows:
                    ais_info = AISInfo(**row)
                    ais_list.append(ais_info)
        
        return ais_list
    
    def get_ais_by_ship_type(self, ship_type: str) -> List[AISInfo]:
        """선박 타입으로 AIS 데이터 조회"""
        query = """
        SELECT * FROM ais_data 
        WHERE vssl_tp LIKE %s
        ORDER BY created_at DESC
        """
        
        ais_list = []
        with self.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, (f'%{ship_type}%',))
                rows = cursor.fetchall()
                
                for row in rows:
                    ais_info = AISInfo(**row)
                    ais_list.append(ais_info)
        
        return ais_list
    
    def get_recent_ais_data(self, hours: int = 24) -> List[AISInfo]:
        """최근 N시간 내의 AIS 데이터 조회"""
        query = """
        SELECT * FROM ais_data 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY created_at DESC
        """
        
        ais_list = []
        with self.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, (hours,))
                rows = cursor.fetchall()
                
                for row in rows:
                    ais_info = AISInfo(**row)
                    ais_list.append(ais_info)
        
        return ais_list

class AISService:
    """AIS 데이터 비즈니스 로직을 담당하는 클래스"""
    
    def __init__(self, repository: AISRepository):
        self.repository = repository
    
    def get_basic_ais_data(self) -> List[AISInfo]:
        """기본 AIS 데이터 조회 (DB 데이터만)"""
        return self.repository.get_all_ais_data()
    
    def get_processed_ais_data(self) -> List[AISProcessedInfo]:
        """가공된 AIS 데이터 조회"""
        basic_data = self.repository.get_all_ais_data()
        processed_data = []
        
        for ais_info in basic_data:
            # AISInfo를 AISProcessedInfo로 변환
            processed_info = AISProcessedInfo(
                id=ais_info.id,
                mmsi_no=ais_info.mmsi_no,
                imo_no=ais_info.imo_no,
                vssl_nm=ais_info.vssl_nm,
                call_letter=ais_info.call_letter,
                vssl_tp=ais_info.vssl_tp,
                vssl_tp_cd=ais_info.vssl_tp_cd,
                vssl_tp_crgo=ais_info.vssl_tp_crgo,
                vssl_cls=ais_info.vssl_cls,
                vssl_len=ais_info.vssl_len,
                vssl_width=ais_info.vssl_width,
                flag=ais_info.flag,
                flag_cd=ais_info.flag_cd,
                vssl_def_brd=ais_info.vssl_def_brd,
                lon=ais_info.lon,
                lat=ais_info.lat,
                sog=ais_info.sog,
                cog=ais_info.cog,
                rot=ais_info.rot,
                head_side=ais_info.head_side,
                vssl_navi=ais_info.vssl_navi,
                vssl_navi_cd=ais_info.vssl_navi_cd,
                source=ais_info.source,
                dt_pos_utc=ais_info.dt_pos_utc,
                dt_static_utc=ais_info.dt_static_utc,
                vssl_tp_main=ais_info.vssl_tp_main,
                vssl_tp_sub=ais_info.vssl_tp_sub,
                dst_nm=ais_info.dst_nm,
                dst_cd=ais_info.dst_cd,
                eta=ais_info.eta,
                created_at=ais_info.created_at
            )
            processed_data.append(processed_info)
        
        return processed_data
    
    def get_analytics_ais_data(self) -> List[AISAnalyticsInfo]:
        """분석용 AIS 데이터 조회"""
        processed_data = self.get_processed_ais_data()
        analytics_data = []
        
        for processed_info in processed_data:
            # AISProcessedInfo를 AISAnalyticsInfo로 변환
            analytics_info = AISAnalyticsInfo(
                # 기본 정보 복사
                id=processed_info.id,
                mmsi_no=processed_info.mmsi_no,
                imo_no=processed_info.imo_no,
                vssl_nm=processed_info.vssl_nm,
                call_letter=processed_info.call_letter,
                vssl_tp=processed_info.vssl_tp,
                vssl_tp_cd=processed_info.vssl_tp_cd,
                vssl_tp_crgo=processed_info.vssl_tp_crgo,
                vssl_cls=processed_info.vssl_cls,
                vssl_len=processed_info.vssl_len,
                vssl_width=processed_info.vssl_width,
                flag=processed_info.flag,
                flag_cd=processed_info.flag_cd,
                vssl_def_brd=processed_info.vssl_def_brd,
                lon=processed_info.lon,
                lat=processed_info.lat,
                sog=processed_info.sog,
                cog=processed_info.cog,
                rot=processed_info.rot,
                head_side=processed_info.head_side,
                vssl_navi=processed_info.vssl_navi,
                vssl_navi_cd=processed_info.vssl_navi_cd,
                source=processed_info.source,
                dt_pos_utc=processed_info.dt_pos_utc,
                dt_static_utc=processed_info.dt_static_utc,
                vssl_tp_main=processed_info.vssl_tp_main,
                vssl_tp_sub=processed_info.vssl_tp_sub,
                dst_nm=processed_info.dst_nm,
                dst_cd=processed_info.dst_cd,
                eta=processed_info.eta,
                created_at=processed_info.created_at,
                # 가공된 정보 복사
                location_zone=processed_info.location_zone,
                is_in_port=processed_info.is_in_port,
                distance_from_port=processed_info.distance_from_port,
                speed_category=processed_info.speed_category,
                course_direction=processed_info.course_direction,
                is_moving=processed_info.is_moving,
                ship_size_category=processed_info.ship_size_category,
                cargo_type_category=processed_info.cargo_type_category,
                time_category=processed_info.time_category,
                is_recent_data=processed_info.is_recent_data,
                risk_level=processed_info.risk_level,
                collision_risk=processed_info.collision_risk
            )
            
            # 분석 데이터 계산
            self._calculate_analytics_data(analytics_info)
            analytics_data.append(analytics_info)
        
        return analytics_data
    
    def _calculate_analytics_data(self, analytics_info: AISAnalyticsInfo):
        """분석 데이터 계산"""
        # 같은 MMSI의 과거 데이터 조회
        historical_data = self.repository.get_ais_by_mmsi(analytics_info.mmsi_no)
        
        if len(historical_data) > 1:
            # 평균 속도 계산
            speeds = [data.sog for data in historical_data if data.sog is not None and data.sog > 0]
            if speeds:
                analytics_info.average_speed = sum(speeds) / len(speeds)
            
            # 선호 속도 범위 계산
            if analytics_info.average_speed:
                if analytics_info.average_speed < 5:
                    analytics_info.preferred_speed_range = "저속 (0-5노트)"
                elif analytics_info.average_speed < 15:
                    analytics_info.preferred_speed_range = "중속 (5-15노트)"
                else:
                    analytics_info.preferred_speed_range = "고속 (15노트 이상)"
            
            # 일반적인 항해 상태 계산
            navi_statuses = [data.vssl_navi for data in historical_data if data.vssl_navi]
            if navi_statuses:
                from collections import Counter
                most_common_status = Counter(navi_statuses).most_common(1)[0][0]
                analytics_info.typical_navigation_status = most_common_status
    
    def get_ships_by_risk_level(self, risk_level: str) -> List[AISProcessedInfo]:
        """위험도 레벨별 선박 조회"""
        processed_data = self.get_processed_ais_data()
        return [ship for ship in processed_data if ship.risk_level == risk_level]
    
    def get_ships_in_port(self) -> List[AISProcessedInfo]:
        """항구 내부 선박 조회"""
        processed_data = self.get_processed_ais_data()
        return [ship for ship in processed_data if ship.is_in_port]
    
    def get_moving_ships(self) -> List[AISProcessedInfo]:
        """이동 중인 선박 조회"""
        processed_data = self.get_processed_ais_data()
        return [ship for ship in processed_data if ship.is_moving]
    
    def get_ships_by_size(self, size_category: str) -> List[AISProcessedInfo]:
        """선박 크기별 조회"""
        processed_data = self.get_processed_ais_data()
        return [ship for ship in processed_data if ship.ship_size_category == size_category]
    
    def get_ships_by_cargo_type(self, cargo_type: str) -> List[AISProcessedInfo]:
        """화물 타입별 선박 조회"""
        processed_data = self.get_processed_ais_data()
        return [ship for ship in processed_data if ship.cargo_type_category == cargo_type]
    
    def get_statistics(self) -> Dict[str, Any]:
        """전체 통계 정보 조회"""
        processed_data = self.get_processed_ais_data()
        
        if not processed_data:
            return {}
        
        stats = {
            'total_ships': len(processed_data),
            'ships_in_port': len([s for s in processed_data if s.is_in_port]),
            'moving_ships': len([s for s in processed_data if s.is_moving]),
            'high_risk_ships': len([s for s in processed_data if s.risk_level == '높음']),
            'medium_risk_ships': len([s for s in processed_data if s.risk_level == '보통']),
            'low_risk_ships': len([s for s in processed_data if s.risk_level == '낮음']),
            'ship_types': {},
            'cargo_types': {},
            'size_categories': {}
        }
        
        # 선박 타입별 통계
        for ship in processed_data:
            if ship.cargo_type_category:
                stats['cargo_types'][ship.cargo_type_category] = stats['cargo_types'].get(ship.cargo_type_category, 0) + 1
            
            if ship.ship_size_category:
                stats['size_categories'][ship.ship_size_category] = stats['size_categories'].get(ship.ship_size_category, 0) + 1
        
        return stats

# 사용 예시
if __name__ == "__main__":
    # 저장소와 서비스 초기화
    repository = AISRepository()
    service = AISService(repository)
    
    print("=== 기본 AIS 데이터 조회 ===")
    basic_data = service.get_basic_ais_data()
    print(f"총 {len(basic_data)}개의 기본 AIS 데이터")
    
    if basic_data:
        print(f"첫 번째 데이터: {basic_data[0].vssl_nm}")
    
    print("\n=== 가공된 AIS 데이터 조회 ===")
    processed_data = service.get_processed_ais_data()
    print(f"총 {len(processed_data)}개의 가공된 AIS 데이터")
    
    if processed_data:
        first_ship = processed_data[0]
        print(f"선박명: {first_ship.vssl_nm}")
        print(f"위치 구역: {first_ship.location_zone}")
        print(f"속도 구분: {first_ship.speed_category}")
        print(f"위험도: {first_ship.risk_level}")
    
    print("\n=== 통계 정보 ===")
    stats = service.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== 항구 내부 선박 ===")
    port_ships = service.get_ships_in_port()
    print(f"항구 내부 선박 수: {len(port_ships)}")
    
    print("\n=== 이동 중인 선박 ===")
    moving_ships = service.get_moving_ships()
    print(f"이동 중인 선박 수: {len(moving_ships)}")
    
    print("\n=== 위험도별 선박 ===")
    high_risk_ships = service.get_ships_by_risk_level('높음')
    print(f"높은 위험도 선박 수: {len(high_risk_ships)}") 