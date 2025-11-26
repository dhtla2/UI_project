from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import pymysql
import pandas as pd
from database_config import MYSQL_CONFIG

@dataclass
class AISInfo:
    """
    AIS 정보를 담는 데이터 클래스
    테이블의 각 컬럼에 대응하는 변수들을 정의
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
    
    def get_location(self) -> tuple:
        """위치 정보 반환 (경도, 위도)"""
        return (self.lon, self.lat)
    
    def get_ship_info(self) -> dict:
        """선박 기본 정보 반환"""
        return {
            'mmsi_no': self.mmsi_no,
            'imo_no': self.imo_no,
            'vssl_nm': self.vssl_nm,
            'call_letter': self.call_letter,
            'vssl_tp': self.vssl_tp,
            'flag': self.flag
        }
    
    def get_navigation_info(self) -> dict:
        """항해 정보 반환"""
        return {
            'sog': self.sog,
            'cog': self.cog,
            'rot': self.rot,
            'head_side': self.head_side,
            'vssl_navi': self.vssl_navi,
            'lon': self.lon,
            'lat': self.lat
        }

class AISService:
    """
    AIS 데이터를 조회하고 AISInfo 클래스에 저장하는 서비스 클래스
    """
    
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        # database_config.py의 설정을 기본값으로 사용
        self.host = host or MYSQL_CONFIG['host']
        self.port = port or MYSQL_CONFIG['port']
        self.user = user or MYSQL_CONFIG['user']
        self.password = password or MYSQL_CONFIG['password']
        self.database = database or MYSQL_CONFIG['database']
        self.connection = None
        self.ais_data: List[AISInfo] = []  # 조회한 데이터를 저장할 리스트
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            print(f"MySQL 데이터베이스 '{self.database}'에 연결되었습니다.")
            return True
        except Exception as e:
            print(f"데이터베이스 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.connection:
            self.connection.close()
            print("데이터베이스 연결이 종료되었습니다.")
    
    def _row_to_ais_info(self, row: tuple) -> AISInfo:
        """데이터베이스 행을 AISInfo 객체로 변환"""
        return AISInfo(
            id=row[0],
            mmsi_no=row[1],
            imo_no=row[2],
            vssl_nm=row[3],
            call_letter=row[4],
            vssl_tp=row[5],
            vssl_tp_cd=row[6],
            vssl_tp_crgo=row[7],
            vssl_cls=row[8],
            vssl_len=row[9],
            vssl_width=row[10],
            flag=row[11],
            flag_cd=row[12],
            vssl_def_brd=row[13],
            lon=row[14],
            lat=row[15],
            sog=row[16],
            cog=row[17],
            rot=row[18],
            head_side=row[19],
            vssl_navi=row[20],
            vssl_navi_cd=row[21],
            source=row[22],
            dt_pos_utc=row[23],
            dt_static_utc=row[24],
            vssl_tp_main=row[25],
            vssl_tp_sub=row[26],
            dst_nm=row[27],
            dst_cd=row[28],
            eta=row[29],
            created_at=row[30]
        )
    
    def load_all_data(self, limit: int = None) -> List[AISInfo]:
        """
        모든 데이터를 조회하여 AISInfo 객체 리스트로 반환
        
        Args:
            limit (int): 조회할 레코드 수 제한
            
        Returns:
            List[AISInfo]: AISInfo 객체 리스트
        """
        query = "SELECT * FROM ais_info"
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # 조회한 데이터를 AISInfo 객체로 변환하여 저장
            self.ais_data = [self._row_to_ais_info(row) for row in rows]
            print(f"총 {len(self.ais_data)}개의 데이터를 AISInfo 객체로 로드했습니다.")
            
            return self.ais_data
            
        except Exception as e:
            print(f"데이터 로드 오류: {e}")
            return []
    
    def load_by_mmsi(self, mmsi_no: str) -> List[AISInfo]:
        """
        특정 MMSI 번호로 데이터를 조회하여 AISInfo 객체 리스트로 반환
        
        Args:
            mmsi_no (str): MMSI 번호
            
        Returns:
            List[AISInfo]: AISInfo 객체 리스트
        """
        query = "SELECT * FROM ais_info WHERE mmsi_no = %s ORDER BY dt_pos_utc DESC"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (mmsi_no,))
            rows = cursor.fetchall()
            
            # 조회한 데이터를 AISInfo 객체로 변환하여 저장
            self.ais_data = [self._row_to_ais_info(row) for row in rows]
            print(f"MMSI {mmsi_no}에 대한 {len(self.ais_data)}개의 데이터를 AISInfo 객체로 로드했습니다.")
            
            return self.ais_data
            
        except Exception as e:
            print(f"데이터 로드 오류: {e}")
            return []
    
    def load_by_ship_name(self, ship_name: str) -> List[AISInfo]:
        """
        선박명으로 데이터를 조회하여 AISInfo 객체 리스트로 반환
        
        Args:
            ship_name (str): 선박명
            
        Returns:
            List[AISInfo]: AISInfo 객체 리스트
        """
        query = "SELECT * FROM ais_info WHERE vssl_nm LIKE %s ORDER BY dt_pos_utc DESC"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (f'%{ship_name}%',))
            rows = cursor.fetchall()
            
            # 조회한 데이터를 AISInfo 객체로 변환하여 저장
            self.ais_data = [self._row_to_ais_info(row) for row in rows]
            print(f"선박명 '{ship_name}'에 대한 {len(self.ais_data)}개의 데이터를 AISInfo 객체로 로드했습니다.")
            
            return self.ais_data
            
        except Exception as e:
            print(f"데이터 로드 오류: {e}")
            return []
    
    def load_by_flag(self, flag: str) -> List[AISInfo]:
        """
        국적으로 데이터를 조회하여 AISInfo 객체 리스트로 반환
        
        Args:
            flag (str): 국적
            
        Returns:
            List[AISInfo]: AISInfo 객체 리스트
        """
        query = "SELECT * FROM ais_info WHERE flag = %s ORDER BY dt_pos_utc DESC"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (flag,))
            rows = cursor.fetchall()
            
            # 조회한 데이터를 AISInfo 객체로 변환하여 저장
            self.ais_data = [self._row_to_ais_info(row) for row in rows]
            print(f"국적 '{flag}'에 대한 {len(self.ais_data)}개의 데이터를 AISInfo 객체로 로드했습니다.")
            
            return self.ais_data
            
        except Exception as e:
            print(f"데이터 로드 오류: {e}")
            return []
    
    def get_loaded_data(self) -> List[AISInfo]:
        """
        현재 로드된 AISInfo 객체 리스트 반환
        
        Returns:
            List[AISInfo]: 현재 로드된 데이터
        """
        return self.ais_data
    
    def get_latest_data(self) -> Optional[AISInfo]:
        """
        로드된 데이터 중 가장 최신 데이터 반환
        
        Returns:
            AISInfo: 가장 최신 데이터
        """
        if self.ais_data:
            return self.ais_data[0]
        return None
    
    def get_ship_locations(self) -> List[tuple]:
        """
        로드된 데이터의 모든 선박 위치 반환
        
        Returns:
            List[tuple]: (경도, 위도) 튜플 리스트
        """
        return [ship.get_location() for ship in self.ais_data if ship.lon and ship.lat]
    
    def get_unique_ships(self) -> List[str]:
        """
        로드된 데이터의 고유한 선박명 리스트 반환
        
        Returns:
            List[str]: 고유한 선박명 리스트
        """
        unique_names = set()
        for ship in self.ais_data:
            if ship.vssl_nm:
                unique_names.add(ship.vssl_nm)
        return list(unique_names)
    
    def filter_by_ship_type(self, ship_type: str) -> List[AISInfo]:
        """
        로드된 데이터에서 특정 선박 타입으로 필터링
        
        Args:
            ship_type (str): 선박 타입
            
        Returns:
            List[AISInfo]: 필터링된 데이터
        """
        return [ship for ship in self.ais_data if ship.vssl_tp == ship_type]
    
    def filter_by_navigation_status(self, status: str) -> List[AISInfo]:
        """
        로드된 데이터에서 특정 항해 상태로 필터링
        
        Args:
            status (str): 항해 상태
            
        Returns:
            List[AISInfo]: 필터링된 데이터
        """
        return [ship for ship in self.ais_data if ship.vssl_navi == status]
    
    def export_to_csv(self, filename: str):
        """
        로드된 데이터를 CSV 파일로 내보내기
        
        Args:
            filename (str): 저장할 파일명
        """
        if not self.ais_data:
            print("내보낼 데이터가 없습니다.")
            return
        
        # AISInfo 객체들을 딕셔너리 리스트로 변환
        data_list = []
        for ship in self.ais_data:
            data_list.append({
                'id': ship.id,
                'mmsi_no': ship.mmsi_no,
                'imo_no': ship.imo_no,
                'vssl_nm': ship.vssl_nm,
                'call_letter': ship.call_letter,
                'vssl_tp': ship.vssl_tp,
                'vssl_tp_cd': ship.vssl_tp_cd,
                'vssl_tp_crgo': ship.vssl_tp_crgo,
                'vssl_cls': ship.vssl_cls,
                'vssl_len': ship.vssl_len,
                'vssl_width': ship.vssl_width,
                'flag': ship.flag,
                'flag_cd': ship.flag_cd,
                'vssl_def_brd': ship.vssl_def_brd,
                'lon': ship.lon,
                'lat': ship.lat,
                'sog': ship.sog,
                'cog': ship.cog,
                'rot': ship.rot,
                'head_side': ship.head_side,
                'vssl_navi': ship.vssl_navi,
                'vssl_navi_cd': ship.vssl_navi_cd,
                'source': ship.source,
                'dt_pos_utc': ship.dt_pos_utc,
                'dt_static_utc': ship.dt_static_utc,
                'vssl_tp_main': ship.vssl_tp_main,
                'vssl_tp_sub': ship.vssl_tp_sub,
                'dst_nm': ship.dst_nm,
                'dst_cd': ship.dst_cd,
                'eta': ship.eta,
                'created_at': ship.created_at
            })
        
        # DataFrame으로 변환하여 CSV 저장
        df = pd.DataFrame(data_list)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"로드된 데이터가 {filename} 파일로 저장되었습니다.")

# 사용 예시
if __name__ == "__main__":
    # AIS 서비스 객체 생성
    ais_service = AISService()
    
    # 데이터베이스 연결
    if ais_service.connect():
        print("\n=== AIS 데이터 조회 및 AISInfo 객체 저장 예시 ===\n")
        
        # 1. 특정 MMSI 번호로 데이터 조회하여 AISInfo 객체에 저장
        print("1. MMSI 312773000으로 데이터 조회:")
        ships = ais_service.load_by_mmsi("312773000")
        
        if ships:
            # 저장된 AISInfo 객체들 사용
            latest_ship = ais_service.get_latest_data()
            print(f"최신 데이터 - 선박명: {latest_ship.vssl_nm}")
            print(f"위치: {latest_ship.get_location()}")
            print(f"선박 정보: {latest_ship.get_ship_info()}")
            print(f"항해 정보: {latest_ship.get_navigation_info()}")
            
            # 고유한 선박명 확인
            unique_ships = ais_service.get_unique_ships()
            print(f"고유한 선박명: {unique_ships}")
            
            # 선박 위치들 확인
            locations = ais_service.get_ship_locations()
            print(f"총 {len(locations)}개의 위치 데이터")
            
            # 특정 선박 타입으로 필터링
            cargo_ships = ais_service.filter_by_ship_type("GENERAL_CARGO")
            print(f"화물선 수: {len(cargo_ships)}")
            
            # 특정 항해 상태로 필터링
            moored_ships = ais_service.filter_by_navigation_status("MOORED")
            print(f"계류 중인 선박 수: {len(moored_ships)}")
            
            # CSV로 내보내기
            ais_service.export_to_csv("loaded_ais_data.csv")
        
        # 2. 선박명으로 데이터 조회
        print("\n2. 선박명 'HAO XIANG'으로 데이터 조회:")
        hao_xiang_data = ais_service.load_by_ship_name("HAO XIANG")
        print(f"조회된 데이터 수: {len(hao_xiang_data)}")
        
        # 3. 국적으로 데이터 조회
        print("\n3. 국적 'Belize'로 데이터 조회:")
        belize_data = ais_service.load_by_flag("Belize")
        print(f"조회된 데이터 수: {len(belize_data)}")
        
        # 연결 해제
        ais_service.disconnect()
    else:
        print("데이터베이스 연결에 실패했습니다.") 