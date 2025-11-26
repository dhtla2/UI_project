#!/usr/bin/env python3
"""
API 응답 데이터 변환 서비스

API 응답 데이터를 port_database의 테이블 구조에 맞게 변환합니다.
업데이트된 DB 구조 (25개 테이블)에 맞게 최적화되었습니다.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DataTransformer:
    """API 응답 데이터 변환"""
    
    def __init__(self):
        # 엔드포인트별 테이블명 매핑
        self.endpoint_table_mapping = {
            "tc_work_info": "tc_work_info",
            "qc_work_info": "qc_work_info", 
            "yt_work_info": "yt_work_info",
            "berth_schedule": "berth_schedule",
            "ais_info": "ais_info",
            "cntr_load_unload_info": "cntr_load_unload_info",
            "cntr_report_detail": "cntr_report_detail",
            "vssl_entr_report": "vssl_entr_report",
            "vssl_dprt_report": "vssl_dprt_report",
            "vssl_history": "vssl_history",
            "vssl_pass_report": "vssl_pass_report",
            "vssl_spec_info": "vssl_spec_info",
            "vssl_Tos_VsslNo": "vssl_Tos_VsslNo",
            "vssl_Port_VsslNo": "vssl_Port_VsslNo",
            "cargo_imp_exp_report": "cargo_imp_exp_report",
            "cargo_item_code": "cargo_item_code",
            "dg_imp_report": "dg_imp_report",
            "dg_manifest": "dg_manifest",
            "fac_use_statement": "fac_use_statement",
            "fac_use_stmt_bill": "fac_use_stmt_bill",
            "vssl_sec_isps_info": "vssl_sec_isps_info",
            "vssl_sec_port_info": "vssl_sec_port_info",
            "load_unload_from_to_info": "load_unload_from_to_info",
            "vssl_sanction_info": "vssl_sanction_info",
            "country_code": "country_code",
            "vssl_entr_intn_code": "vssl_entr_intn_code",
            "pa_code": "pa_code",
            "port_code": "port_code"
        }
    
    def transform_data(self, endpoint_name: str, api_response: Any, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        API 응답 데이터를 엔드포인트별로 변환
        
        Args:
            endpoint_name: API 엔드포인트명
            api_response: API 응답 데이터
            base_data: 기본 데이터 (sync_id, timestamp 등)
            
        Returns:
            변환된 데이터 딕셔너리
        """
        try:
            # 엔드포인트별 변환 메서드 호출
            if hasattr(self, f"_transform_{endpoint_name}"):
                transform_method = getattr(self, f"_transform_{endpoint_name}")
                return transform_method(api_response, base_data)
            else:
                # 기본 변환 메서드 사용
                return self._transform_generic(endpoint_name, api_response, base_data)
                
        except Exception as e:
            logger.error(f"❌ 데이터 변환 실패 ({endpoint_name}): {e}")
            # 오류 발생 시 기본 변환으로 폴백
            return self._transform_generic(endpoint_name, api_response, base_data)
    
    def _transform_generic(self, endpoint_name: str, api_response: Any, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """일반적인 API 응답 변환 (API 응답 데이터만 DB에 저장)"""
        try:
            # 디버그 로그 추가
            logger.debug(f"🔍 [{endpoint_name}] API 응답 타입: {type(api_response)}")
            
            # API 응답에서 resultList 추출
            if isinstance(api_response, dict):
                result_list = api_response.get("resultList", [])
                
                # resultList가 딕셔너리인 경우 (Match API 등)
                if isinstance(result_list, dict):
                    logger.info(f"🔍 [{endpoint_name}] resultList가 딕셔너리입니다. 리스트로 변환합니다.")
                    data_list = [result_list]  # 딕셔너리를 리스트로 감싸기
                # resultList가 리스트인 경우 (일반 API)
                elif isinstance(result_list, list):
                    data_list = result_list
                    logger.debug(f"🔍 [{endpoint_name}] resultList 크기: {len(data_list)}")
                # resultList가 없거나 빈 경우
                else:
                    logger.debug(f"🔍 [{endpoint_name}] resultList가 비어있음, 전체 응답 사용")
                    data_list = [api_response]  # 전체 응답을 사용
            else:
                logger.debug(f"🔍 [{endpoint_name}] dict가 아님, 전체 응답 사용")
                data_list = [api_response]
            
            # 빈 데이터 처리
            if not data_list:
                logger.warning(f"⚠️ [{endpoint_name}] 데이터 리스트가 완전히 비어있음")
                return {
                    "table_name": self.endpoint_table_mapping.get(endpoint_name, "unknown_table"),
                    "data": [],
                    "count": 0
                }
            
            transformed_data = []
            
            for idx, item in enumerate(data_list):
                if isinstance(item, dict):
                    # 불필요한 필드 제거 (regNo, raw_data 등)
                    cleaned_item = {}
                    for key, value in item.items():
                        # API 요청 파라미터나 메타데이터 필드 제외
                        if key not in ["regNo", "raw_data", "resultCd", "resultMsg", "resultCount"]:
                            cleaned_item[key] = value
                    
                    # 디버그: cleaned_item이 비어있는지 확인
                    if not cleaned_item:
                        logger.warning(f"⚠️ [{endpoint_name}] 데이터 아이템 #{idx}이(가) 정리 후 비어있음. 원본 키: {list(item.keys())}")
                    
                    # API 응답 데이터만 저장 (비어있지 않은 경우만)
                    if cleaned_item:
                        transformed_data.append(cleaned_item)
            
            table_name = self.endpoint_table_mapping.get(endpoint_name, "unknown_table")
            
            # 디버깅을 위한 로그 추가
            if transformed_data:
                sample_keys = list(transformed_data[0].keys())
                logger.info(f"🔍 {endpoint_name} 변환 완료: {table_name} 테이블, {len(transformed_data)}개 레코드")
                logger.info(f"📋 샘플 컬럼: {sample_keys[:10]}{'...' if len(sample_keys) > 10 else ''}")
            
            return {
                "table_name": table_name,
                "data": transformed_data,
                "count": len(transformed_data)
            }
            
        except Exception as e:
            logger.error(f"❌ 기본 변환 실패 ({endpoint_name}): {e}")
            return {
                "table_name": self.endpoint_table_mapping.get(endpoint_name, "unknown_table"),
                "data": [],
                "count": 0
            }
    
    def _transform_tc_work_info(self, api_response: Any, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """TC 작업정보 변환"""
        try:
            if isinstance(api_response, dict):
                data_list = api_response.get("resultList", [])
                if not data_list:
                    data_list = [api_response]
            else:
                data_list = [api_response]
            
            if not data_list:
                return {
                    "table_name": "tc_work_info",
                    "data": [],
                    "count": 0
                }
            
            transformed_data = []
            
            for item in data_list:
                if isinstance(item, dict):
                    # 불필요한 필드 제거 (regNo, raw_data 등)
                    cleaned_item = {}
                    for key, value in item.items():
                        # API 요청 파라미터나 메타데이터 필드 제외
                        if key not in ["regNo", "raw_data", "resultCd", "resultMsg", "resultCount"]:
                            cleaned_item[key] = value
                    
                    # API 응답 데이터만 저장 (sync_id, sync_timestamp 제거)
                    transformed_data.append(cleaned_item)
            
            return {
                "table_name": "tc_work_info",
                "data": transformed_data,
                "count": len(transformed_data)
            }
            
        except Exception as e:
            logger.error(f"❌ TC 작업정보 변환 실패: {e}")
            return self._transform_generic("tc_work_info", api_response, base_data)
    
    def _transform_qc_work_info(self, api_response: Any, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """QC 작업정보 변환"""
        try:
            if isinstance(api_response, dict):
                data_list = api_response.get("resultList", [])
                if not data_list:
                    data_list = [api_response]
            else:
                data_list = [api_response]
            
            if not data_list:
                return {
                    "table_name": "qc_work_info",
                    "data": [],
                    "count": 0
                }
            
            transformed_data = []
            
            for item in data_list:
                if isinstance(item, dict):
                    # 불필요한 필드 제거 (regNo, raw_data 등)
                    cleaned_item = {}
                    for key, value in item.items():
                        # API 요청 파라미터나 메타데이터 필드 제외
                        if key not in ["regNo", "raw_data", "resultCd", "resultMsg", "resultCount"]:
                            cleaned_item[key] = value
                    
                    # API 응답 데이터만 저장 (sync_id, sync_timestamp 제거)
                    transformed_data.append(cleaned_item)
            
            return {
                "table_name": "qc_work_info",
                "data": transformed_data,
                "count": len(transformed_data)
            }
            
        except Exception as e:
            logger.error(f"❌ QC 작업정보 변환 실패: {e}")
            return self._transform_generic("qc_work_info", api_response, base_data)
    
    def _transform_yt_work_info(self, api_response: Any, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """YT 작업정보 변환"""
        try:
            if isinstance(api_response, dict):
                data_list = api_response.get("resultList", [])
                if not data_list:
                    data_list = [api_response]
            else:
                data_list = [api_response]
            
            if not data_list:
                return {
                    "table_name": "yt_work_info",
                    "data": [],
                    "count": 0
                }
            
            transformed_data = []
            
            for item in data_list:
                if isinstance(item, dict):
                    # 불필요한 필드 제거 (regNo, raw_data 등)
                    cleaned_item = {}
                    for key, value in item.items():
                        # API 요청 파라미터나 메타데이터 필드 제외
                        if key not in ["regNo", "raw_data", "resultCd", "resultMsg", "resultCount"]:
                            cleaned_item[key] = value
                    
                    # API 응답 데이터만 저장 (sync_id, sync_timestamp 제거)
                    transformed_data.append(cleaned_item)
            
            return {
                "table_name": "yt_work_info",
                "data": transformed_data,
                "count": len(transformed_data)
            }
            
        except Exception as e:
            logger.error(f"❌ YT 작업정보 변환 실패: {e}")
            return self._transform_generic("yt_work_info", api_response, base_data)
    
    def _transform_ais_info(self, api_response: Any, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """AIS 정보 변환"""
        try:
            if isinstance(api_response, dict):
                data_list = api_response.get("resultList", [])
                if not data_list:
                    data_list = [api_response]
            else:
                data_list = [api_response]
            
            if not data_list:
                return {
                    "table_name": "ais_info",
                    "data": [],
                    "count": 0
                }
            
            transformed_data = []
            
            for item in data_list:
                if isinstance(item, dict):
                    # 불필요한 필드 제거 (regNo, raw_data 등)
                    cleaned_item = {}
                    for key, value in item.items():
                        # API 요청 파라미터나 메타데이터 필드 제외
                        if key not in ["regNo", "raw_data", "resultCd", "resultMsg", "resultCount"]:
                            cleaned_item[key] = value
                    
                    # API 응답 데이터만 저장 (sync_id, sync_timestamp 제거)
                    transformed_data.append(cleaned_item)
            
            return {
                "table_name": "ais_info",
                "data": transformed_data,
                "count": len(transformed_data)
            }
            
        except Exception as e:
            logger.error(f"❌ AIS 정보 변환 실패: {e}")
            return self._transform_generic("ais_info", api_response, base_data)
    
    def _transform_vssl_spec_info(self, api_response: Any, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """선박 제원 정보 변환 (필드명 매핑 포함)"""
        try:
            if isinstance(api_response, dict):
                data_list = api_response.get("resultList", [])
                if not data_list:
                    data_list = [api_response]
            else:
                data_list = [api_response]
            
            if not data_list:
                return {
                    "table_name": "vssl_spec_info",
                    "data": [],
                    "count": 0
                }
            
            # API 필드명 → DB 컬럼명 매핑
            field_mapping = {
                # API에서 풀네임을 사용하지만 DB는 축약형 사용
                "deadWeight": "deadWgt",      # 재화중량톤수 (API: deadWeight → DB: deadWgt)
                "vsslWidth": "vsslWdth",      # 선박 폭 (API: vsslWidth → DB: vsslWdth)
                "vsslDepth": "vsslDpth",      # 선박 깊이 (API: vsslDepth → DB: vsslDpth)
                # 아래 필드들은 API와 DB가 동일
                # grsTn, netTn, vsslLen, vsslAllLen, vsslDefBrd 등은 그대로 사용
            }
            
            transformed_data = []
            
            for item in data_list:
                if isinstance(item, dict):
                    # 불필요한 필드 제거 및 필드명 매핑
                    cleaned_item = {}
                    for key, value in item.items():
                        # API 요청 파라미터나 메타데이터 필드 제외
                        if key not in ["regNo", "raw_data", "resultCd", "resultMsg", "resultCount"]:
                            # 필드명 매핑 적용
                            mapped_key = field_mapping.get(key, key)
                            cleaned_item[mapped_key] = value
                    
                    transformed_data.append(cleaned_item)
            
            logger.info(f"🔄 vssl_spec_info 필드 매핑 완료: {len(transformed_data)}개 레코드")
            
            return {
                "table_name": "vssl_spec_info",
                "data": transformed_data,
                "count": len(transformed_data)
            }
            
        except Exception as e:
            logger.error(f"❌ 선박 제원 정보 변환 실패: {e}")
            return self._transform_generic("vssl_spec_info", api_response, base_data)

# 싱글톤 인스턴스
data_transformer = DataTransformer()
