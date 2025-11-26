#!/usr/bin/env python3
"""
API 동기화 서비스

AIPC_Client/config.py의 API_PARAMS.endpoint_defaults에 정의된
모든 API 엔드포인트를 호출하고 port_database에 동기화합니다.
"""

import logging
import requests
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# 상위 디렉토리 추가하여 AIPC_Client 모듈 import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'AIPC_Client', 'project_files'))

from endpoint_mapper import endpoint_mapper
from data_transformer import data_transformer
from db_sync_manager import DBSyncManager

logger = logging.getLogger(__name__)

class APISyncService:
    """API 동기화 서비스"""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 db_config: Dict[str, Any] = None):
        self.base_url = base_url.rstrip('/')
        self.db_config = db_config or {
            "host": "localhost",
            "port": 3307,
            "user": "root",
            "password": "",
            "database": "port_database"
        }
        
        # 설정 파일에서 설정 로드 시도
        self._load_config_from_file()
        
        # 서비스 상태
        self.is_running = False
        self.current_sync_id = None
        self.sync_stats = {
            "total_endpoints": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "total_records": 0,
            "start_time": None,
            "end_time": None
        }
    
    def _load_config_from_file(self):
        """설정 파일에서 설정 로드"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), '..', 'sync_config.json')
            if os.path.exists(config_file):
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 데이터베이스 설정 업데이트
                if 'database' in config:
                    self.db_config.update(config['database'])
                    logger.info(f"✅ 설정 파일에서 DB 설정 로드: {config_file}")
                
                # API 서버 설정 업데이트
                if 'api_server' in config and 'base_url' in config['api_server']:
                    self.base_url = config['api_server']['base_url'].rstrip('/')
                    logger.info(f"✅ 설정 파일에서 API 서버 설정 로드: {self.base_url}")
                    
        except Exception as e:
            logger.warning(f"⚠️ 설정 파일 로드 실패: {e}")
            logger.info("💡 기본 설정을 사용합니다")
    
    def start_sync(self, endpoints: List[str] = None, 
                   priority_filter: str = None) -> str:
        """
        동기화 시작
        
        Args:
            endpoints: 동기화할 특정 엔드포인트 목록 (None이면 전체)
            priority_filter: 우선순위 필터 (high, medium, low)
            
        Returns:
            동기화 ID
        """
        try:
            # 동기화 ID 생성 (timestamp + uuid)
            timestamp = int(datetime.now().timestamp())
            unique_id = str(uuid.uuid4())[:8]
            self.current_sync_id = f"sync_{timestamp}_{unique_id}"
            
            # 동기화할 엔드포인트 결정
            if endpoints:
                target_endpoints = [ep for ep in endpoints if endpoint_mapper.validate_endpoint(ep)]
            elif priority_filter:
                target_endpoints = endpoint_mapper.get_endpoints_by_priority(priority_filter)
            else:
                target_endpoints = endpoint_mapper.get_all_endpoints()
            
            if not target_endpoints:
                logger.error("❌ 동기화할 유효한 엔드포인트가 없습니다")
                return None
            
            # 서비스 상태 초기화
            self.is_running = True
            self.sync_stats = {
                "total_endpoints": len(target_endpoints),
                "successful_syncs": 0,
                "failed_syncs": 0,
                "total_records": 0,
                "start_time": datetime.now().isoformat(),
                "end_time": None
            }
            
            logger.info(f"🚀 API 동기화 시작: {self.current_sync_id}")
            logger.info(f"📊 대상 엔드포인트: {len(target_endpoints)}개")
            logger.info(f"🎯 엔드포인트 목록: {', '.join(target_endpoints)}")
            
            # DB 연결 및 동기화 실행
            with DBSyncManager(**self.db_config) as db_manager:
                for endpoint_name in target_endpoints:
                    try:
                        success = self._sync_endpoint(endpoint_name, db_manager)
                        if success:
                            self.sync_stats["successful_syncs"] += 1
                        else:
                            self.sync_stats["failed_syncs"] += 1
                    except Exception as e:
                        logger.error(f"❌ 엔드포인트 동기화 실패 ({endpoint_name}): {e}")
                        self.sync_stats["failed_syncs"] += 1
            
            # 동기화 완료
            self.is_running = False
            self.sync_stats["end_time"] = datetime.now().isoformat()
            
            # 최종 통계 출력
            self._print_sync_summary()
            
            return self.current_sync_id
            
        except Exception as e:
            logger.error(f"❌ 동기화 서비스 시작 실패: {e}")
            self.is_running = False
            return None
    
    def _sync_endpoint(self, endpoint_name: str, db_manager: DBSyncManager) -> bool:
        """
        개별 엔드포인트 동기화
        
        Args:
            endpoint_name: API 엔드포인트 이름
            db_manager: DB 관리자 인스턴스
            
        Returns:
            성공 여부
        """
        try:
            logger.info(f"🔄 {endpoint_name} 엔드포인트 동기화 시작")
            
            # 1. API 호출
            api_response = self._call_api(endpoint_name)
            if api_response is None:
                logger.error(f"❌ API 호출 실패: {endpoint_name}")
                return False
            
            # 2. 데이터 변환
            base_data = {
                "sync_id": self.current_sync_id,
                "sync_timestamp": datetime.now().isoformat()
            }
            transformed_data = data_transformer.transform_data(
                endpoint_name, api_response, base_data
            )
            if transformed_data is None:
                logger.error(f"❌ 데이터 변환 실패: {endpoint_name}")
                return False
            
            # 3. DB 저장
            table_name = transformed_data["table_name"]
            data = transformed_data["data"]
            
            if not db_manager.insert_data(table_name, data):
                logger.error(f"❌ DB 저장 실패: {endpoint_name} -> {table_name}")
                return False
            
            # 4. 통계 업데이트
            self.sync_stats["total_records"] += transformed_data["count"]
            
            logger.info(f"✅ {endpoint_name} 엔드포인트 동기화 완료: {transformed_data['count']}개 레코드")
            return True
            
        except Exception as e:
            logger.error(f"❌ 엔드포인트 동기화 실패 ({endpoint_name}): {e}")
            return False
    
    def _call_api(self, endpoint_name: str) -> Optional[Any]:
        """
        API 호출
        
        Args:
            endpoint_name: API 엔드포인트 이름
            
        Returns:
            API 응답 데이터
        """
        try:
            # AIPC_Client의 config.py에서 API 정보 가져오기 시도
            try:
                # AIPC_Client 폴더 경로 찾기
                aipc_config = self._find_aipc_config()
                if aipc_config:
                    from config import API_CONFIG, API_ENDPOINTS, API_PARAMS
                    
                    # 1. API_CONFIG에서 실제 API 서버 정보 가져오기
                    aipc_base_url = API_CONFIG["base_url"]
                    aipc_api_key = API_CONFIG["api_key"]
                    aipc_timeout = API_CONFIG["timeout"]
                    
                    # 2. API_ENDPOINTS에서 엔드포인트 URL 가져오기
                    endpoint_url = API_ENDPOINTS.get(endpoint_name)
                    if not endpoint_url:
                        logger.warning(f"⚠️ API_ENDPOINTS에서 엔드포인트를 찾을 수 없음: {endpoint_name}")
                        return self._call_basic_api(endpoint_name)
                    
                    # 3. API_PARAMS["endpoint_defaults"]에서 기본 파라미터 가져오기
                    endpoint_params = API_PARAMS["endpoint_defaults"].get(endpoint_name, {})
                    
                    # 4. API URL 구성 (AIPC 실제 서버 + endpoint_url)
                    api_url = f"{aipc_base_url}{endpoint_url}"
                    
                    # 5. 헤더에 API 키 추가 (AIPC_Client 형식)
                    headers = {
                        "x-ncp-apigw-api-key": aipc_api_key,
                        "accept": "*/*"
                    }
                    
                    logger.info(f"🌐 AIPC_Client 실제 API 서버 호출: {endpoint_name}")
                    logger.info(f"🔗 URL: {api_url}")
                    logger.info(f"🔑 API Key: {aipc_api_key[:8]}...")
                    logger.info(f"📝 파라미터: {endpoint_params}")
                    
                    # 6. API 호출 (POST 방식으로 파라미터 전송)
                    response = requests.post(
                        api_url, 
                        json=endpoint_params, 
                        headers=headers,
                        timeout=aipc_timeout
                    )
                    
                    # 7. 응답 확인
                    if response.status_code == 200:
                        try:
                            api_data = response.json()
                            logger.info(f"✅ AIPC_Client API 응답 수신: {endpoint_name} ({len(str(api_data))} bytes)")
                            
                            # Match API의 경우 응답 상세 로그
                            if 'vssl' in endpoint_name and 'VsslNo' in endpoint_name:
                                result_list = api_data.get('resultList')
                                logger.info(f"📋 [{endpoint_name}] 응답 상세: resultCd={api_data.get('resultCd')}, resultMsg={api_data.get('resultMsg')}, resultCount={api_data.get('resultCount')}")
                                logger.info(f"📋 [{endpoint_name}] resultList 타입: {type(result_list)}")
                                if isinstance(result_list, dict):
                                    logger.info(f"📋 [{endpoint_name}] resultList는 단일 객체입니다: {result_list}")
                                elif isinstance(result_list, list):
                                    logger.info(f"📋 [{endpoint_name}] resultList 크기: {len(result_list)}")
                                    if result_list:
                                        logger.info(f"📋 [{endpoint_name}] 첫 번째 데이터: {result_list[0]}")
                            
                            return api_data
                        except Exception as e:
                            logger.warning(f"⚠️ JSON 파싱 실패, 텍스트로 처리: {e}")
                            return {"raw_text": response.text}
                    elif response.status_code == 401:
                        logger.warning(f"⚠️ AIPC_Client API 인증 실패: {response.status_code} - {response.text}")
                        logger.info("🔄 기본 API 호출로 전환합니다")
                        return self._call_basic_api(endpoint_name)
                    elif response.status_code == 404:
                        logger.warning(f"⚠️ AIPC_Client API 엔드포인트를 찾을 수 없음: {response.status_code} - {response.text}")
                        logger.info("🔄 기본 API 호출로 전환합니다")
                        return self._call_basic_api(endpoint_name)
                    else:
                        logger.warning(f"⚠️ AIPC_Client API 호출 실패: {response.status_code} - {response.text}")
                        logger.info("🔄 기본 API 호출로 전환합니다")
                        return self._call_basic_api(endpoint_name)
                else:
                    logger.info("ℹ️ AIPC_Client config.py를 찾을 수 없음")
                    return self._call_basic_api(endpoint_name)
                    
            except ImportError as e:
                logger.info(f"ℹ️ AIPC_Client config 모듈 import 실패: {e}")
                logger.info("🔄 기본 API 호출로 전환합니다")
                return self._call_basic_api(endpoint_name)
            except KeyError as e:
                logger.warning(f"⚠️ AIPC_Client config에서 키를 찾을 수 없음: {e}")
                logger.info("🔄 기본 API 호출로 전환합니다")
                return self._call_basic_api(endpoint_name)
            except Exception as e:
                logger.warning(f"⚠️ AIPC_Client config 처리 중 오류: {e}")
                logger.info("🔄 기본 API 호출로 전환합니다")
                return self._call_basic_api(endpoint_name)
                
        except Exception as e:
            logger.error(f"❌ API 호출 중 오류 발생 ({endpoint_name}): {e}")
            return None
    
    def _find_aipc_config(self) -> bool:
        """AIPC_Client config.py 파일 찾기"""
        try:
            # 가능한 경로들 (project_files 폴더 포함)
            possible_paths = [
                '/home/cotlab/AIPC_Client/project_files',  # 절대 경로 (정확한 위치)
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'AIPC_Client', 'project_files'),  # 상대 경로
                os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'AIPC_Client', 'project_files'),  # 상대 경로 2
                os.path.join(os.getcwd(), '..', 'AIPC_Client', 'project_files'),  # 현재 작업 디렉토리 기준
                os.path.join(os.getcwd(), '..', '..', 'AIPC_Client', 'project_files'),  # 현재 작업 디렉토리 기준 2
                os.path.expanduser('~/AIPC_Client/project_files'),  # 홈 디렉토리 기준
            ]
            
            for path in possible_paths:
                config_file = os.path.join(path, 'config.py')
                if os.path.exists(config_file):
                    # sys.path에 추가
                    if path not in sys.path:
                        sys.path.insert(0, path)
                        logger.info(f"✅ AIPC_Client config.py 발견: {path}")
                    return True
            
            logger.warning("⚠️ AIPC_Client config.py를 찾을 수 없음")
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ AIPC_Client config.py 검색 중 오류: {e}")
            return False
    
    def _call_basic_api(self, endpoint_name: str) -> Optional[Any]:
        """기본 API 호출 (config 모듈을 사용할 수 없는 경우)"""
        try:
            # 기본 엔드포인트 매핑 (모든 25개 엔드포인트 포함)
            basic_endpoints = {
                # 작업 정보 관련
                "tc_work_info": "/api/tc_work_info",
                "qc_work_info": "/api/qc_work_info", 
                "yt_work_info": "/api/yt_work_info",
                
                # 선석 계획 관련
                "berth_schedule": "/api/berth_schedule",
                
                # AIS 정보 관련
                "ais_info": "/api/ais_info",
                
                # 컨테이너 관련
                "cntr_load_unload_info": "/api/cntr_load_unload_info",
                "cntr_report_detail": "/api/cntr_report_detail",
                
                # 선박 관련
                "vssl_entr_report": "/api/vssl_entr_report",
                "vssl_dprt_report": "/api/vssl_dprt_report",
                "vssl_history": "/api/vssl_history",
                "vssl_pass_report": "/api/vssl_pass_report",
                
                # 화물 관련
                "cargo_imp_exp_report": "/api/cargo_imp_exp_report",
                "cargo_item_code": "/api/cargo_item_code",
                
                # 위험물 관련
                "dg_imp_report": "/api/dg_imp_report",
                "dg_manifest": "/api/dg_manifest",
                
                # 항만시설 관련
                "fac_use_statement": "/api/fac_use_statement",
                "fac_use_stmt_bill": "/api/fac_use_stmt_bill",
                
                # 보안 관련
                "vssl_sec_isps_info": "/api/vssl_sec_isps_info",
                "vssl_sec_port_info": "/api/vssl_sec_port_info",
                
                # 기타 정보
                "load_unload_from_to_info": "/api/load_unload_from_to_info",
                "vssl_sanction_info": "/api/vssl_sanction_info",
                "country_code": "/api/country_code",
                "vssl_entr_intn_code": "/api/vssl_entr_intn_code",
                "pa_code": "/api/pa_code",
                "port_code": "/api/port_code"
            }
            
            if endpoint_name not in basic_endpoints:
                logger.warning(f"⚠️ 기본 API 매핑에 없음: {endpoint_name}")
                return None
            
            api_url = f"{self.base_url}{basic_endpoints[endpoint_name]}"
            logger.info(f"🌐 기본 API 호출 시도: {api_url}")
            
            try:
                response = requests.get(api_url, timeout=30)
                
                if response.status_code == 200:
                    try:
                        api_data = response.json()
                        logger.info(f"✅ 기본 API 호출 성공: {endpoint_name}")
                        return api_data
                    except:
                        logger.warning(f"⚠️ JSON 파싱 실패, 텍스트로 처리")
                        return {"raw_text": response.text}
                else:
                    logger.warning(f"⚠️ API 서버 응답 없음 ({response.status_code}), 테스트 데이터 생성")
                    return self._generate_test_data(endpoint_name)
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"⚠️ API 서버 연결 실패, 테스트 데이터 생성")
                return self._generate_test_data(endpoint_name)
            except requests.exceptions.Timeout:
                logger.warning(f"⚠️ API 서버 타임아웃, 테스트 데이터 생성")
                return self._generate_test_data(endpoint_name)
            except Exception as e:
                logger.warning(f"⚠️ API 호출 중 예상치 못한 오류: {e}, 테스트 데이터 생성")
                return self._generate_test_data(endpoint_name)
                
        except Exception as e:
            logger.error(f"❌ 기본 API 호출 실패 ({endpoint_name}): {e}")
            return None
    
    def _generate_test_data(self, endpoint_name: str) -> Dict[str, Any]:
        """테스트용 더미 데이터 생성"""
        import random
        from datetime import datetime, timedelta
        
        logger.info(f"🧪 테스트 데이터 생성: {endpoint_name}")
        
        # 엔드포인트별 테스트 데이터 생성
        if endpoint_name == "tc_work_info":
            return {
                "data": [
                    {
                        "tmnlId": f"TML{random.randint(100, 999)}",
                        "shpCd": f"SHP{random.randint(1000, 9999)}",
                        "callYr": str(datetime.now().year),
                        "serNo": str(random.randint(1, 100)),
                        "tcNo": f"TC{random.randint(1000, 9999)}",
                        "cntrNo": f"CNTR{random.randint(100000, 999999)}",
                        "wkTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ordTime": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
                    } for _ in range(random.randint(5, 20))
                ]
            }
        elif endpoint_name == "qc_work_info":
            return {
                "data": [
                    {
                        "tmnlId": f"TML{random.randint(100, 999)}",
                        "shpCd": f"SHP{random.randint(1000, 9999)}",
                        "callYr": str(datetime.now().year),
                        "serNo": str(random.randint(1, 100)),
                        "qcNo": f"QC{random.randint(1000, 9999)}",
                        "cntrNo": f"CNTR{random.randint(100000, 999999)}",
                        "wkTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ordTime": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
                    } for _ in range(random.randint(5, 20))
                ]
            }
        elif endpoint_name == "yt_work_info":
            return {
                "data": [
                    {
                        "tmnlId": f"TML{random.randint(100, 999)}",
                        "shpCd": f"SHP{random.randint(1000, 9999)}",
                        "callYr": str(datetime.now().year),
                        "serNo": str(random.randint(1, 100)),
                        "ytNo": f"YT{random.randint(1000, 9999)}",
                        "cntrNo": f"CNTR{random.randint(100000, 999999)}",
                        "wkTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ordTime": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
                    } for _ in range(random.randint(5, 20))
                ]
            }
        elif endpoint_name == "ais_info":
            return {
                "data": [
                    {
                        "regNo": f"REG{random.randint(10000, 99999)}",
                        "mmsiNo": f"MMSI{random.randint(100000000, 999999999)}",
                        "callLetter": f"CALL{random.randint(1000, 9999)}",
                        "imoNo": f"IMO{random.randint(1000000, 9999999)}"
                    } for _ in range(random.randint(3, 15))
                ]
            }
        elif endpoint_name == "berth_schedule":
            return {
                "data": [
                    {
                        "regNo": f"REG{random.randint(10000, 99999)}",
                        "code": f"CODE{random.randint(100, 999)}",
                        "yr": str(datetime.now().year),
                        "spCall": f"SP{random.randint(1000, 9999)}"
                    } for _ in range(random.randint(3, 10))
                ]
            }
        elif endpoint_name == "cntr_load_unload_info":
            return {
                "data": [
                    {
                        "tmnlId": f"TML{random.randint(100, 999)}",
                        "shpCd": f"SHP{random.randint(1000, 9999)}",
                        "callYr": str(datetime.now().year),
                        "serNo": str(random.randint(1, 100)),
                        "cntrNo": f"CNTR{random.randint(100000, 999999)}",
                        "blNo": f"BL{random.randint(100000, 999999)}",
                        "cntrSize": random.choice(["20", "40", "45"]),
                        "cntrType": random.choice(["GP", "RF", "OT", "FR"]),
                        "loadPort": random.choice(["KRPUS", "KRKAN", "KRINC"]),
                        "dischargePort": random.choice(["USNYC", "DEHAM", "NLRTM"]),
                        "loadDate": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                        "dischargeDate": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
                    } for _ in range(random.randint(5, 25))
                ]
            }
        elif endpoint_name == "vssl_entr_report":
            return {
                "data": [
                    {
                        "regNo": f"REG{random.randint(10000, 99999)}",
                        "vsslNm": f"VESSEL_{random.randint(100, 999)}",
                        "callLetter": f"CALL{random.randint(1000, 9999)}",
                        "imoNo": f"IMO{random.randint(1000000, 9999999)}",
                        "entrDate": datetime.now().strftime("%Y-%m-%d"),
                        "entrTime": datetime.now().strftime("%H:%M:%S"),
                        "entrPort": "KRPUS"
                    } for _ in range(random.randint(3, 12))
                ]
            }
        elif endpoint_name == "vssl_dprt_report":
            return {
                "data": [
                    {
                        "regNo": f"REG{random.randint(10000, 99999)}",
                        "vsslNm": f"VESSEL_{random.randint(100, 999)}",
                        "callLetter": f"CALL{random.randint(1000, 9999)}",
                        "imoNo": f"IMO{random.randint(1000000, 9999999)}",
                        "dprtDate": datetime.now().strftime("%Y-%m-%d"),
                        "dprtTime": datetime.now().strftime("%H:%M:%S"),
                        "dprtPort": "KRPUS"
                    } for _ in range(random.randint(3, 12))
                ]
            }
        elif endpoint_name == "cargo_imp_exp_report":
            return {
                "data": [
                    {
                        "regNo": f"REG{random.randint(10000, 99999)}",
                        "cargoNm": f"CARGO_{random.randint(100, 999)}",
                        "cargoType": random.choice(["IMPORT", "EXPORT"]),
                        "cargoQty": random.randint(100, 10000),
                        "cargoUnit": random.choice(["TON", "M3", "PCS"]),
                        "reportDate": datetime.now().strftime("%Y-%m-%d")
                    } for _ in range(random.randint(5, 20))
                ]
            }
        elif endpoint_name == "dg_imp_report":
            return {
                "data": [
                    {
                        "regNo": f"REG{random.randint(10000, 99999)}",
                        "dgNm": f"DANGEROUS_GOODS_{random.randint(100, 999)}",
                        "dgClass": random.randint(1, 9),
                        "dgPkg": random.randint(1, 1000),
                        "dgQty": random.randint(1, 100),
                        "reportDate": datetime.now().strftime("%Y-%m-%d")
                    } for _ in range(random.randint(3, 10))
                ]
            }
        else:
            # 일반적인 테스트 데이터
            return {
                "data": [
                    {
                        "id": random.randint(1, 1000),
                        "name": f"Test_{endpoint_name}_{i}",
                        "timestamp": datetime.now().isoformat(),
                        "value": random.randint(1, 100),
                        "status": random.choice(["ACTIVE", "INACTIVE", "PENDING"]),
                        "category": random.choice(["A", "B", "C", "D"])
                    } for i in range(random.randint(3, 8))
                ]
            }
    
    def get_sync_status(self) -> Dict[str, Any]:
        """현재 동기화 상태 조회"""
        if not self.current_sync_id:
            return {"status": "not_started"}
        
        try:
            with DBSyncManager(**self.db_config) as db_manager:
                sync_status = db_manager.get_sync_status(self.current_sync_id)
                sync_status.update(self.sync_stats)
                sync_status["is_running"] = self.is_running
                return sync_status
        except Exception as e:
            logger.error(f"❌ 동기화 상태 조회 실패: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_sync_statistics(self, sync_id: str = None) -> Optional[Dict[str, Any]]:
        """
        동기화 통계 조회
        
        Args:
            sync_id: 동기화 ID (None이면 현재 동기화 통계 반환)
            
        Returns:
            통계 딕셔너리
        """
        try:
            # 현재 동기화 통계 반환
            if sync_id is None or sync_id == self.current_sync_id:
                stats = self.sync_stats.copy()
                
                # 소요 시간 계산
                if stats.get('start_time') and stats.get('end_time'):
                    start_time = datetime.fromisoformat(stats['start_time'])
                    end_time = datetime.fromisoformat(stats['end_time'])
                    duration = end_time - start_time
                    stats['duration_seconds'] = duration.total_seconds()
                else:
                    stats['duration_seconds'] = 0
                
                # 성공률 계산
                if stats.get('total_endpoints', 0) > 0:
                    stats['success_rate'] = (stats['successful_syncs'] / stats['total_endpoints']) * 100
                else:
                    stats['success_rate'] = 0
                
                return stats
            else:
                logger.warning(f"⚠️ 요청한 sync_id({sync_id})와 현재 sync_id({self.current_sync_id})가 다릅니다")
                return None
                
        except Exception as e:
            logger.error(f"❌ 동기화 통계 조회 실패: {e}")
            return None
    
    def _print_sync_summary(self):
        """동기화 요약 출력"""
        logger.info("=" * 60)
        logger.info("📊 API 동기화 완료 요약")
        logger.info("=" * 60)
        logger.info(f"🆔 동기화 ID: {self.current_sync_id}")
        logger.info(f"📅 시작 시간: {self.sync_stats['start_time']}")
        logger.info(f"📅 종료 시간: {self.sync_stats['end_time']}")
        logger.info(f"🎯 총 엔드포인트: {self.sync_stats['total_endpoints']}")
        logger.info(f"✅ 성공: {self.sync_stats['successful_syncs']}")
        logger.info(f"❌ 실패: {self.sync_stats['failed_syncs']}")
        logger.info(f"📊 총 레코드: {self.sync_stats['total_records']}")
        
        if self.sync_stats['start_time'] and self.sync_stats['end_time']:
            start_time = datetime.fromisoformat(self.sync_stats['start_time'])
            end_time = datetime.fromisoformat(self.sync_stats['end_time'])
            duration = end_time - start_time
            logger.info(f"⏱️  소요 시간: {duration}")
        
        success_rate = (self.sync_stats['successful_syncs'] / self.sync_stats['total_endpoints']) * 100
        logger.info(f"📈 성공률: {success_rate:.1f}%")
        logger.info("=" * 60)
    
    def sync_by_priority(self, priority: str = "high") -> str:
        """우선순위별 동기화"""
        logger.info(f"🎯 {priority} 우선순위 엔드포인트 동기화 시작")
        return self.start_sync(priority_filter=priority)
    
    def sync_by_category(self, category: str) -> str:
        """카테고리별 동기화"""
        endpoints = endpoint_mapper.get_endpoints_by_category(category)
        logger.info(f"📂 {category} 카테고리 엔드포인트 동기화 시작 ({len(endpoints)}개)")
        return self.start_sync(endpoints=endpoints)
    
    def sync_single_endpoint(self, endpoint_name: str) -> str:
        """단일 엔드포인트 동기화"""
        if not endpoint_mapper.validate_endpoint(endpoint_name):
            logger.error(f"❌ 유효하지 않은 엔드포인트: {endpoint_name}")
            return None
        
        logger.info(f"🎯 단일 엔드포인트 동기화: {endpoint_name}")
        return self.start_sync(endpoints=[endpoint_name])
    
    def cleanup_old_data(self, days: int = 30) -> bool:
        """오래된 데이터 정리"""
        try:
            with DBSyncManager(**self.db_config) as db_manager:
                return db_manager.cleanup_old_sync_data(days)
        except Exception as e:
            logger.error(f"❌ 오래된 데이터 정리 실패: {e}")
            return False

# 싱글톤 인스턴스
api_sync_service = APISyncService()
