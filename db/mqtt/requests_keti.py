#!/usr/bin/env python3
"""
requests_keti: requests 대체 래퍼

- 목적: 기존 노트북/스크립트에서 `import requests`를 `import requests_keti as requests` 형태로
        바꿔치기하여 공통 헤더(예: API 키), 기본 타임아웃, 재시도, 로깅 등을 일관 적용.

- 사용 예:
    import requests_keti as requests
    resp = requests.get(url, params=..., headers={...})

- 동작:
  - config.py의 API_CONFIG 값을 읽어 기본 base header/timeout을 적용
  - 호출 시 전달한 headers/timeout이 있으면 우선 적용
  - 간단한 재시도(backoff) 내장
"""

from __future__ import annotations

import requests
from requests import Response
from typing import Any, Dict, Optional
import time
import logging
import json as _json
from urllib.parse import urlparse
from datetime import datetime as _dt
import uuid as _uuid

import pandas as _pd

try:
    # notebook이나 외부에서 실행 시 상대/절대 모두 대응
    from .config import API_CONFIG, API_METADATA, API_PARAMS
except Exception:
    from config import API_CONFIG, API_METADATA, API_PARAMS

# 동기 전송을 위해 직접 MQTT 클라이언트 사용
try:
    from .db.mqtt.mqtt_sender import MQTTTransmissionClient
    from .db.mqtt.mqtt_config import get_mqtt_config as _get_mqtt_cfg
except Exception:
    try:
        from db.mqtt.mqtt_sender import MQTTTransmissionClient
        from db.mqtt.mqtt_config import get_mqtt_config as _get_mqtt_cfg
    except Exception:
        MQTTTransmissionClient = None  # type: ignore
        _get_mqtt_cfg = lambda: {}

try:
    # 품질검사 매니저
    from .inspectors.data_quality_check import Manager
except Exception:
    from inspectors.data_quality_check import Manager

_HAS_EXTERNAL_UTILS = True
try:
    # CSV 저장 유틸 재사용 (없을 수 있음)
    from .test_api_with_mqtt import save_df_to_csv_with_info
except Exception:
    try:
        from test_api_with_mqtt import save_df_to_csv_with_info
    except Exception:
        _HAS_EXTERNAL_UTILS = False

import os as _os
import hashlib as _hashlib

if not _HAS_EXTERNAL_UTILS:
    # 내장 대체 구현
    def _calculate_file_checksum(filepath: str) -> str:
        try:
            md5 = _hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception:
            return ""

    def save_df_to_csv_with_info(df: _pd.DataFrame, inspection_id: str, data_source: str, data_type: str) -> dict:
        try:
            data_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'data')
            _os.makedirs(data_dir, exist_ok=True)
            ts = _dt.now().strftime("%Y%m%d_%H%M%S")
            short_id = _uuid.uuid4().hex[:8]
            filename = f"{data_source.lower()}_{ts}_{short_id}_{data_source}_{data_type}_{ts}.csv"
            filepath = _os.path.join(data_dir, filename)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            file_size = _os.path.getsize(filepath)
            checksum = _calculate_file_checksum(filepath)
            return {
                'data_file_name': filename,
                'data_file_path': filepath,
                'data_file_size_bytes': file_size,
                'data_checksum': checksum,
                'processed_data_count': int(len(df)),
                'data_columns': list(map(str, df.columns.tolist()))
            }
        except Exception:
            return {}

    def create_dynamic_meta(data_source: str, df: _pd.DataFrame) -> dict:
        cols = set(df.columns.tolist())

        def _int_minmax(series_name: str, default_min: int, default_max: int):
            if series_name not in cols:
                return default_min, default_max
            try:
                series = _pd.to_numeric(df[series_name].dropna().astype(str).str.lstrip('0').replace('', '0'))
                if series.empty:
                    return default_min, default_max
                return int(series.min()), int(series.max())
            except Exception:
                return default_min, default_max

        def _str_minmax(series_name: str, default_min: str, default_max: str):
            if series_name not in cols:
                return default_min, default_max
            try:
                series = df[series_name].dropna().astype(str)
                if series.empty:
                    return default_min, default_max
                return series.min(), series.max()
            except Exception:
                return default_min, default_max

        ser_min, ser_max = _int_minmax('serNo', 0, 999)
        yr_min, yr_max = _int_minmax('callYr', 2000, 2100)
        wk_min, wk_max = _str_minmax('wkTime', '20000101000000', '21001231235959')
        has_ord = 'ordTime' in cols and df['ordTime'].notna().any()
        if has_ord:
            ord_min, ord_max = _str_minmax('ordTime', wk_min, wk_max)

        def _usage(candidates):
            return [c for c in candidates if c in cols]

        meta = { 'DV': {}, 'DC': {}, 'DU': {} }

        meta['DV']['RANGE'] = {
            'serNo': { 'rtype': 'I', 'ctype': 'I', 'val1': ser_min, 'val2': ser_max },
            'callYr': { 'rtype': 'I', 'ctype': 'I', 'val1': yr_min, 'val2': yr_max },
        }

        date_dict = { 'wkTime': { 'val1': wk_min, 'val2': wk_max } }
        if has_ord:
            date_dict['ordTime'] = { 'val1': ord_min, 'val2': ord_max }
        meta['DV']['DATE'] = { 'D': date_dict }

        if data_source == 'TC':
            meta['DC']['DUPLICATE'] = { 'U': {**({'cntrNo': ['cntrNo']} if 'cntrNo' in cols else {}), **({'tcNo': ['tcNo']} if 'tcNo' in cols else {})} }
            meta['DU']['USAGE'] = { 'columns': _usage(['cntrNo','tmnlId','wkTime','tcNo']) }
        elif data_source == 'QC':
            meta['DC']['DUPLICATE'] = { 'U': {**({'cntrNo': ['cntrNo']} if 'cntrNo' in cols else {}), **({'qcNo': ['qcNo']} if 'qcNo' in cols else {})} }
            meta['DU']['USAGE'] = { 'columns': _usage(['cntrNo','tmnlId','wkTime','qcNo']) }
        elif data_source == 'YT':
            meta['DC']['DUPLICATE'] = { 'U': {**({'cntrNo': ['cntrNo']} if 'cntrNo' in cols else {}), **({'ytNo': ['ytNo']} if 'ytNo' in cols else {})} }
            meta['DU']['USAGE'] = { 'columns': _usage(['cntrNo','tmnlId','wkTime','ytNo']) }
        else:
            meta['DU']['USAGE'] = { 'columns': _usage(list(cols)) }

        return meta


_logger = logging.getLogger("requests_keti")
if not _logger.handlers:
    _logger.addHandler(logging.NullHandler())
_logger.setLevel(logging.WARNING)


def _merge_headers(user_headers: Optional[Dict[str, str]]) -> Dict[str, str]:
    base_headers = {
        "x-ncp-apigw-api-key": API_CONFIG.get("api_key", ""),
        "accept": "*/*",
    }
    if user_headers:
        base_headers.update(user_headers)
    return base_headers


def _with_retries(func, *args, **kwargs) -> Response:
    max_retries = API_CONFIG.get("max_retries", 3)
    delay = 0.5
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt >= max_retries:
                _logger.error(f"requests_keti: 실패(최대 재시도 초과): {e}")
                raise
            _logger.warning(f"requests_keti: 오류 발생, 재시도 {attempt}/{max_retries}: {e}")
            time.sleep(delay)
            delay = min(5.0, delay * 2)


def get(url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None, **kwargs) -> Response:
    """HTTP GET + 품질검사 + MQTT 전송 후 Response 반환"""
    return _keti(url, method="GET", params=params, headers=headers, timeout=timeout, **kwargs)


def post(url: str, data: Any = None, json: Any = None, headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None, **kwargs) -> Response:
    """HTTP POST + 품질검사 + MQTT 전송 후 Response 반환"""
    return _keti(url, method="POST", data=data, json=json, headers=headers, timeout=timeout, **kwargs)


def put(url: str, data: Any = None, json: Any = None, headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None, **kwargs) -> Response:
    merged_headers = _merge_headers(headers)
    effective_timeout = timeout if timeout is not None else API_CONFIG.get("timeout", 30)
    return _with_retries(requests.put, url, data=data, json=json, headers=merged_headers, timeout=effective_timeout, **kwargs)


def delete(url: str, headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None, **kwargs) -> Response:
    merged_headers = _merge_headers(headers)
    effective_timeout = timeout if timeout is not None else API_CONFIG.get("timeout", 30)
    return _with_retries(requests.delete, url, headers=merged_headers, timeout=effective_timeout, **kwargs)


def _infer_source_and_table(path: str) -> (str, str):
    upper = (path or "").upper()
    
    # 작업정보 API들
    if "TCWORKINFO" in upper or "/TC" in upper:
        return "TC", "tc_work_info"
    if "QCWORKINFO" in upper or "/QC" in upper:
        return "QC", "qc_work_info"
    if "YTWORKINFO" in upper or "/YT" in upper:
        return "YT", "yt_work_info"
    
    # 선석계획
    if "BERTHSCHEDULE" in upper:
        return "BERTH", "berth_schedule"
    
    # AIS 정보
    if "AISINFO" in upper:
        return "AIS", "ais_info"
    
    # 컨테이너 양적하정보
    if "CNTRLOADUNLOAD" in upper:
        return "CNTR", "cntr_load_unload_info"
    
    # 컨테이너 신고상세정보
    if "CNTRREPORTDETAIL" in upper:
        return "CNTR_DETAIL", "cntr_report_detail"
    
    # 선박 입항신고정보
    if "VSSLENTRREPORT" in upper:
        return "VSSL_ENTR", "vssl_entr_report"
    
    # 선박 출항신고정보
    if "VSSLEDPRTREPORT" in upper:
        return "VSSL_DPRT", "vssl_dprt_report"
    
    # 선박 이력정보
    if "VSSLHISTORY" in upper or "VTCHISTORY" in upper:
        return "VSSL_HIST", "vssl_history"
    
    # 선박 외항통과신고정보
    if "VSSLPASSREPORT" in upper:
        return "VSSL_PASS", "vssl_pass_report"
    
    # 화물반출입신고정보
    if "CARGOIMPEXP" in upper:
        return "CARGO", "cargo_imp_exp_report"
    
    # 화물품목코드
    if "CARGOITEMCODE" in upper:
        return "CARGO_CODE", "cargo_item_code"
    
    # 위험물반입신고서
    if "DGIMP" in upper:
        return "DG_IMP", "dg_imp_report"
    
    # 위험물 적하알림표
    if "DGMANIFEST" in upper:
        return "DG_MANIFEST", "dg_manifest"
    
    # 항만시설사용 신청/결과정보
    if "FACUSESTATEMENT" in upper:
        return "FAC_USE", "fac_use_statement"
    
    # 항만시설사용신고정보-화물료
    if "FACUSESTMTBILL" in upper:
        return "FAC_BILL", "fac_use_stmt_bill"
    
    # 선박보안인증서 통보
    if "VSSLSECISPS" in upper:
        return "VSSL_SEC_ISPS", "vssl_sec_isps_info"
    
    # 선박보안인증서 통보 경유지 정보
    if "VSSLSECPORT" in upper:
        return "VSSL_SEC_PORT", "vssl_sec_port_info"
    
    # 제재대상선박 정보
    if "VSSLSANCTION" in upper:
        return "VSSL_SANCTION", "vssl_sanction_info"
    
    # 국가코드
    if "COUNTRYCODE" in upper:
        return "COUNTRY", "country_code"
    
    # 선박 입항신고 국제통신 코드
    if "VSSLENTRINTN" in upper:
        return "VSSL_ENTR_INTN", "vssl_entr_intn_code"
    
    # PA 코드
    if "PACODE" in upper:
        return "PA", "pa_code"
    
    # 항만코드
    if "PORTCODE" in upper:
        return "PORT", "port_code"
    
    # 선박양적하 시작종료정보
    if "LOADUNLOADFROMTO" in upper:
        return "LOAD_UNLOAD", "load_unload_from_to_info"
    
    # 기본값 (알 수 없는 API)
    return "UNKNOWN", "unknown_table"

def _get_default_params_from_endpoint(path: str) -> dict:
    """
    API 엔드포인트에 따라 기본 파라미터를 반환합니다.
    
    Args:
        path: API 경로
    
    Returns:
        dict: 기본 파라미터
    """
    try:
        # 1. API_PARAMS.endpoint_defaults에서 정확한 엔드포인트 키 찾기
        endpoint_key = None
        
        # 경로에서 엔드포인트 키 추출
        path_lower = path.lower()
        if "tcworkinfo" in path_lower:
            endpoint_key = "tc_work_info"
        elif "qcworkinfo" in path_lower:
            endpoint_key = "qc_work_info"
        elif "ytworkinfo" in path_lower:
            endpoint_key = "yt_work_info"
        elif "berthschedule" in path_lower:
            endpoint_key = "berth_schedule"
        elif "aisinfo" in path_lower:
            endpoint_key = "ais_info"
        elif "cntrloadunload" in path_lower:
            endpoint_key = "cntr_load_unload_info"
        elif "cntrreportdetail" in path_lower:
            endpoint_key = "cntr_report_detail"
        elif "vsslentrreport" in path_lower:
            endpoint_key = "vssl_entr_report"
        elif "vssldprtreport" in path_lower:
            endpoint_key = "vssl_dprt_report"
        elif "vsslhistory" in path_lower or "vtchistory" in path_lower:
            endpoint_key = "vssl_history"
        elif "vsslpassreport" in path_lower:
            endpoint_key = "vssl_pass_report"
        elif "cargoimpexp" in path_lower:
            endpoint_key = "cargo_imp_exp_report"
        elif "cargoitemcode" in path_lower:
            endpoint_key = "cargo_item_code"
        elif "dgimp" in path_lower:
            endpoint_key = "dg_imp_report"
        elif "dgmanifest" in path_lower:
            endpoint_key = "dg_manifest"
        elif "facusestatement" in path_lower:
            endpoint_key = "fac_use_statement"
        elif "facusestmtbill" in path_lower:
            endpoint_key = "fac_use_stmt_bill"
        elif "vsslsecisps" in path_lower:
            endpoint_key = "vssl_sec_isps_info"
        elif "vsslsecport" in path_lower:
            endpoint_key = "vssl_sec_port_info"
        elif "vsslsanction" in path_lower:
            endpoint_key = "vssl_sanction_info"
        elif "countrycode" in path_lower:
            endpoint_key = "country_code"
        elif "vsslentrintn" in path_lower:
            endpoint_key = "vssl_entr_intn_code"
        elif "pacode" in path_lower:
            endpoint_key = "pa_code"
        elif "portcode" in path_lower:
            endpoint_key = "port_code"
        elif "loadunloadfromto" in path_lower:
            endpoint_key = "load_unload_from_to_info"
        
        # 2. API_PARAMS.endpoint_defaults에서 기본 파라미터 가져오기
        if endpoint_key and endpoint_key in API_PARAMS.get("endpoint_defaults", {}):
            default_params = API_PARAMS["endpoint_defaults"][endpoint_key].copy()
            _logger.debug(f"기본 파라미터 로드: {endpoint_key}")
            return default_params
        
        # 3. 기본 파라미터가 없는 경우 빈 딕셔너리 반환
        _logger.warning(f"기본 파라미터에서 {endpoint_key}를 찾을 수 없음")
        return {}
        
    except Exception as e:
        _logger.error(f"기본 파라미터 로드 실패: {e}")
        return {}

def _get_metadata_from_endpoint(path: str, data_source: str, df: _pd.DataFrame) -> dict:
    """
    API 엔드포인트에 따라 적절한 메타데이터를 반환합니다.
    
    Args:
        path: API 경로
        data_source: 데이터 소스 (TC, QC, YT 등)
        df: 데이터프레임
    
    Returns:
        dict: 메타데이터
    """
    try:
        # 1. API_METADATA에서 정확한 엔드포인트 키 찾기
        endpoint_key = None
        
        # 경로에서 엔드포인트 키 추출
        path_lower = path.lower()
        if "tcworkinfo" in path_lower:
            endpoint_key = "tc_work_info"
        elif "qcworkinfo" in path_lower:
            endpoint_key = "qc_work_info"
        elif "ytworkinfo" in path_lower:
            endpoint_key = "yt_work_info"
        elif "berthschedule" in path_lower:
            endpoint_key = "berth_schedule"
        elif "aisinfo" in path_lower:
            endpoint_key = "ais_info"
        elif "cntrloadunload" in path_lower:
            endpoint_key = "cntr_load_unload_info"
        elif "cntrreportdetail" in path_lower:
            endpoint_key = "cntr_report_detail"
        elif "vsslentrreport" in path_lower:
            endpoint_key = "vssl_entr_report"
        elif "vssldprtreport" in path_lower:
            endpoint_key = "vssl_dprt_report"
        elif "vsslhistory" in path_lower or "vtchistory" in path_lower:
            endpoint_key = "vssl_history"
        elif "vsslpassreport" in path_lower:
            endpoint_key = "vssl_pass_report"
        elif "cargoimpexp" in path_lower:
            endpoint_key = "cargo_imp_exp_report"
        elif "cargoitemcode" in path_lower:
            endpoint_key = "cargo_item_code"
        elif "dgimp" in path_lower:
            endpoint_key = "dg_imp_report"
        elif "dgmanifest" in path_lower:
            endpoint_key = "dg_manifest"
        elif "facusestatement" in path_lower:
            endpoint_key = "fac_use_statement"
        elif "facusestmtbill" in path_lower:
            endpoint_key = "fac_use_stmt_bill"
        elif "vsslsecisps" in path_lower:
            endpoint_key = "vssl_sec_isps_info"
        elif "vsslsecport" in path_lower:
            endpoint_key = "vssl_sec_port_info"
        elif "vsslsanction" in path_lower:
            endpoint_key = "vssl_sanction_info"
        elif "countrycode" in path_lower:
            endpoint_key = "country_code"
        elif "vsslentrintn" in path_lower:
            endpoint_key = "vssl_entr_intn_code"
        elif "pacode" in path_lower:
            endpoint_key = "pa_code"
        elif "portcode" in path_lower:
            endpoint_key = "port_code"
        elif "loadunloadfromto" in path_lower:
            endpoint_key = "load_unload_from_to_info"
        
        # 2. API_METADATA에서 메타데이터 가져오기
        if endpoint_key and endpoint_key in API_METADATA:
            meta = API_METADATA[endpoint_key].copy()
            _logger.debug(f"API_METADATA에서 메타데이터 로드: {endpoint_key}")
            return meta
        
        # 3. 기본 메타데이터 (API_METADATA에 없는 경우)
        _logger.warning(f"API_METADATA에서 {endpoint_key}를 찾을 수 없음. 기본 메타데이터 사용")
        return _create_fallback_metadata(data_source, df)
        
    except Exception as e:
        _logger.error(f"메타데이터 로드 실패: {e}")
        return _create_fallback_metadata(data_source, df)

def _create_fallback_metadata(data_source: str, df: _pd.DataFrame) -> dict:
    """
    기본 메타데이터를 생성합니다 (API_METADATA에 없는 경우).
    
    Args:
        data_source: 데이터 소스
        df: 데이터프레임
    
    Returns:
        dict: 기본 메타데이터
    """
    cols = set(df.columns.tolist())
    
    def _int_minmax(series_name: str, default_min: int, default_max: int):
        if series_name not in cols:
            return default_min, default_max
        try:
            series = _pd.to_numeric(df[series_name].dropna().astype(str).str.lstrip('0').replace('', '0'))
            if series.empty:
                return default_min, default_max
            return int(series.min()), int(series.max())
        except Exception:
            return default_min, default_max
    
    def _str_minmax(series_name: str, default_min: str, default_max: str):
        if series_name not in cols:
            return default_min, default_max
        try:
            series = df[series_name].dropna().astype(str)
            if series.empty:
                return default_min, default_max
            return series.min(), series.max()
        except Exception:
            return default_min, default_max
    
    # 기본 범위 설정
    ser_min, ser_max = _int_minmax('serNo', 0, 999)
    yr_min, yr_max = _int_minmax('callYr', 2000, 2100)
    wk_min, wk_max = _str_minmax('wkTime', '20000101000000', '21001231235959')
    
    has_ord = 'ordTime' in cols and df['ordTime'].notna().any()
    if has_ord:
        ord_min, ord_max = _str_minmax('ordTime', wk_min, wk_max)
    
    def _usage(candidates):
        return [c for c in candidates if c in cols]
    
    meta = {'DV': {}, 'DC': {}, 'DU': {}}
    
    # 기본 범위 검사
    meta['DV']['RANGE'] = {
        'serNo': {'rtype': 'I', 'ctype': 'I', 'val1': ser_min, 'val2': ser_max},
        'callYr': {'rtype': 'I', 'ctype': 'I', 'val1': yr_min, 'val2': yr_max},
    }
    
    # 날짜 검사
    date_dict = {'wkTime': {'val1': wk_min, 'val2': wk_max}}
    if has_ord:
        date_dict['ordTime'] = {'val1': ord_min, 'val2': ord_max}
    meta['DV']['DATE'] = {'S': date_dict}
    
    # 중복 검사 - 실제 존재하는 컬럼만 사용 (안전한 기본값)
    duplicate_cols = {}
    
    # TC 작업정보 API의 실제 컬럼들 (안전하게 체크)
    tc_safe_cols = ['tmnlId', 'shpCd', 'callYr', 'serNo', 'tcNo', 'cntrNo', 'wkTime', 'ordTime']
    for col in tc_safe_cols:
        if col in cols:
            duplicate_cols[col] = [col]
    
    # 중복 검사가 가능한 컬럼이 있을 때만 추가
    if duplicate_cols:
        meta['DC']['DUPLICATE'] = {'U': duplicate_cols}
    
    # USAGE - 실제 존재하는 컬럼만 사용 (더 안전한 접근)
    safe_columns = []
    for col in ['tmnlId', 'shpCd', 'callYr', 'serNo', 'wkTime']:
        if col in cols:
            safe_columns.append(col)
    
    # 안전한 컬럼이 없으면 기본값 사용
    if not safe_columns:
        safe_columns = list(cols)[:5]  # 처음 5개 컬럼 사용
    
    meta['DU']['USAGE'] = {
        'columns': safe_columns
    }
    
    return meta


def _sanitize_metadata(meta: dict, available_columns: list) -> dict:
    """
    메타데이터에서 존재하지 않는 컬럼 참조를 제거합니다.
    
    Args:
        meta: 원본 메타데이터
        available_columns: 실제 존재하는 컬럼 목록
    
    Returns:
        dict: 정리된 메타데이터
    """
    if not meta or not isinstance(meta, dict):
        return meta
    
    available_cols_set = set(available_columns)
    sanitized_meta = meta.copy()
    
    # DUPLICATE 섹션 정리
    if 'DC' in sanitized_meta and 'DUPLICATE' in sanitized_meta['DC']:
        duplicate_section = sanitized_meta['DC']['DUPLICATE']
        if 'U' in duplicate_section:
            # 존재하지 않는 컬럼 제거
            safe_duplicates = {}
            for col, col_list in duplicate_section['U'].items():
                if col in available_cols_set:
                    safe_duplicates[col] = col_list
            
            if safe_duplicates:
                sanitized_meta['DC']['DUPLICATE']['U'] = safe_duplicates
            else:
                # 안전한 컬럼이 없으면 DUPLICATE 섹션 제거
                del sanitized_meta['DC']['DUPLICATE']
    
    # USAGE 섹션 정리
    if 'DU' in sanitized_meta and 'USAGE' in sanitized_meta['DU']:
        if 'columns' in sanitized_meta['DU']['USAGE']:
            # 존재하는 컬럼만 유지
            safe_columns = [col for col in sanitized_meta['DU']['USAGE']['columns'] 
                          if col in available_cols_set]
            
            if safe_columns:
                sanitized_meta['DU']['USAGE']['columns'] = safe_columns
            else:
                # 안전한 컬럼이 없으면 처음 3개 컬럼 사용
                sanitized_meta['DU']['USAGE']['columns'] = available_columns[:3]
    
    return sanitized_meta


def _keti(url: str,
          method: str = "GET",
          params: Optional[Dict[str, Any]] = None,
          data: Any = None,
          json: Any = None,
          headers: Optional[Dict[str, str]] = None,
          timeout: Optional[int] = None,
          ) -> Response:
    """
    KETI 통합 호출: HTTP 요청 → 응답 파싱 → 품질검사 → MQTT 백그라운드 전송 → Response 반환

    - 기존 `requests.get/post` 사용 패턴을 유지하면서 후속 품질검사/전송을 자동 처리
    - 사용 예: resp = requests_keti._keti(url, method="GET", params=..., headers=...)
    """
    start_time = _dt.now()
    overall_start_time = time.time()  # 전체 시작 시간
    
    parsed = urlparse(url)
    path = parsed.path or url

    merged_headers = _merge_headers(headers)
    effective_timeout = timeout if timeout is not None else API_CONFIG.get("timeout", 30)

    # 1) 기본 파라미터와 사용자 파라미터 병합
    default_params = _get_default_params_from_endpoint(path)
    merged_params = default_params.copy()
    
    # 사용자가 전달한 파라미터가 있으면 기본값을 덮어씀
    if params:
        merged_params.update(params)
    if json:
        merged_params.update(json)
    if data:
        merged_params.update(data)
    
    _logger.debug(f"병합된 파라미터: {merged_params}")
    
    # 2) HTTP 호출
    if method.upper() == "POST":
        response = _with_retries(requests.post, url, data=merged_params, headers=merged_headers, timeout=effective_timeout)
    else:
        response = _with_retries(requests.get, url, params=merged_params, headers=merged_headers, timeout=effective_timeout)

    end_time = _dt.now()

    # 2) 응답 파싱 시도 (JSON이 아니면 조용히 종료)
    try:
        response_payload = response.json()
    except Exception:
        return response

    # 3) DF 변환 (여러 응답 스키마 대응)
    if isinstance(response_payload, list):
        df = _pd.DataFrame(response_payload)
        response_status = 'success'
    elif isinstance(response_payload, dict):
        # 스키마 1: { status: 'success', data: [...] }
        if response_payload.get('status') == 'success' and 'data' in response_payload:
            df = _pd.DataFrame(response_payload['data'])
            response_status = response_payload.get('status', 'success')
        # 스키마 2: { resultCd, resultMsg, resultCount, resultList: [...] }
        elif 'resultList' in response_payload:
            data_list = response_payload.get('resultList') or []
            # resultList가 dict인 경우 리스트로 감싸기
            if isinstance(data_list, dict):
                data_list = [data_list]
            df = _pd.DataFrame(data_list)
            rc = str(response_payload.get('resultCd', '')).upper()
            response_status = 'success' if rc in {'0', 'SUCCESS', 'S000', ''} else rc
        else:
            # 예상 스키마가 아니면 전송 생략하고 Response만 반환
            return response
    else:
        return response
    
    # 데이터프레임 안전성 검사 및 로깅
    if df.empty:
        _logger.warning(f"빈 데이터프레임 생성됨: {path}")
        return response
    
    _logger.debug(f"데이터프레임 생성 완료: {path}, 컬럼: {list(df.columns)}, 행수: {len(df)}")
    
    # 컬럼이 비어있는 경우 안전하게 처리
    if len(df.columns) == 0:
        _logger.warning(f"컬럼이 없는 데이터프레임: {path}")
        return response

    # 4) 메타 구축 및 품질검사
    data_source, table_name = _infer_source_and_table(path)
    inspection_id = f"{data_source.lower()}_inspection_{int(time.time())}_{_uuid.uuid4().hex[:6]}"

    api_call_info: Dict[str, Any] = {
        'inspection_id': inspection_id,
        'api_endpoint': path.lstrip('/'),
        'request_method': method.upper(),
        'request_headers': merged_headers,
        'request_params': _json.dumps(json if json is not None else data if data is not None else params, ensure_ascii=False, default=str) if any([json, data, params]) else None,
        'call_timestamp': start_time.isoformat(),
        'response_status': response_status,
        'response_time_ms': (end_time - start_time).total_seconds() * 1000,
        'error_message': None
    }

    # API 호출 파라미터와 데이터 메타 정보만 저장 (raw_response_data 제거)
    inferred_type = 'work_info' if 'WORKINFO' in (path or '').upper() else 'unknown'
    
    api_response_data: Dict[str, Any] = {
        'inspection_id': inspection_id,
        'data_source': data_source,
        'data_type': inferred_type,
        'request_params': merged_params,  # 병합된 파라미터 저장
        'processed_data_count': int(len(df)),
        'data_columns': list(map(str, df.columns.tolist())),
        'data_sample': df.head(3).to_dict('records') if len(df) > 0 else []  # 처음 3행 샘플만 저장
    }

    quality_check_start_time = time.time()  # 품질검사 시작 시간
    
    quality_manager = Manager()
    
    # API_METADATA에서 해당 엔드포인트의 메타데이터 가져오기
    meta = _get_metadata_from_endpoint(path, data_source, df)
    
    # 메타데이터 안전성 검사
    if not meta or not isinstance(meta, dict):
        _logger.warning(f"유효하지 않은 메타데이터: {path}, 메타데이터: {meta}")
        # 기본 메타데이터 생성
        meta = _create_fallback_metadata(data_source, df)
    
    # 메타데이터에서 존재하지 않는 컬럼 참조 제거
    meta = _sanitize_metadata(meta, df.columns.tolist())
    
    _logger.debug(f"최종 메타데이터: {path}, 메타데이터: {meta}")
    
    inspection_output = quality_manager.comprehensive_check(df, meta)
    
    quality_check_end_time = time.time()  # 품질검사 완료 시간
    quality_check_duration = (quality_check_end_time - quality_check_start_time) * 1000  # 밀리초

    # 결과 정규화
    def _as_int(value: Any) -> int:
        try:
            if hasattr(value, 'iloc'):
                # pandas Series 등 단일 원소 처리
                return int(value.iloc[0])
            return int(value)
        except Exception:
            try:
                return int(str(value))
            except Exception:
                return 0

    normalized_results = []
    for check_type, items in inspection_output.inspection_result.results.items():
        for result in items:
            try:
                if isinstance(result, dict):
                    parsed_item = result
                elif hasattr(result, '__dict__'):
                    parsed_item = result.__dict__
                elif isinstance(result, str):
                    try:
                        parsed_item = _json.loads(result)
                    except Exception:
                        parsed_item = {'message': result, 'type': 'string_result'}
                else:
                    parsed_item = {'raw_result': str(result), 'type': str(type(result))}

                total = _as_int(parsed_item.get('total', 0))
                check_cnt = _as_int(parsed_item.get('check', 0))
                message_text = parsed_item.get('message', '')

                # 영향 행수 및 상태
                if '빈값' in message_text:
                    affected_rows = check_cnt
                    status = 'PASS' if check_cnt == 0 else 'FAIL'
                else:
                    affected_rows = max(total - check_cnt, 0)
                    status = 'PASS' if affected_rows == 0 else 'FAIL'

                normalized_results.append({
                    'check_type': check_type,
                    'check_name': f"{check_type}",
                    'message': message_text,
                    'status': status,
                    'severity': parsed_item.get('severity', 'MEDIUM'),
                    'affected_rows': affected_rows,
                    'affected_columns': [],
                    'details': parsed_item,
                })
            except Exception as _:
                normalized_results.append({
                    'check_type': check_type,
                    'check_name': 'parse_error',
                    'message': 'parse_error',
                    'status': 'ERROR',
                    'severity': 'HIGH',
                    'affected_rows': 0,
                    'affected_columns': [],
                    'details': {'raw_result': str(result)},
                })

    # 요약/검사정보
    summary = inspection_output.inspection_result.summary
    summary_data: Dict[str, Any] = {
        'inspection_id': inspection_id,
        'total_checks': len(normalized_results),
        'passed_checks': sum(1 for r in normalized_results if r['status'] == 'PASS'),
        'failed_checks': sum(1 for r in normalized_results if r['status'] == 'FAIL'),
        'warning_checks': 0,
        'error_checks': 0,
        'pass_rate': (sum(1 for r in normalized_results if r['status'] == 'PASS') / len(normalized_results)) * 100 if normalized_results else 0,
        'data_quality_score': 100.0 - (sum(1 for r in normalized_results if r['status'] == 'FAIL') / len(normalized_results)) * 100 if normalized_results else 100.0,
        'summary_json': _json.dumps(summary, ensure_ascii=False, default=str),
        'recommendations': f'{data_source} 작업 정보 품질 검사 완료'
    }

    inspection_info: Dict[str, Any] = {
        'inspection_id': inspection_id,
        'table_name': table_name,
        'data_source': data_source,
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'inspection_type': 'comprehensive',
        'inspection_status': 'completed',
        'start_time': start_time,
        'end_time': end_time,
        'processing_time_ms': (end_time - start_time).total_seconds() * 1000,
        'created_by': 'requests_keti'
    }

    # 로컬 CSV 저장은 수행하지 않음(수신기에서 저장)

    # 동기 MQTT 전송 (연결 → 메타 전송 → 결과 전송(응답 대기) → 해제)
    mqtt_start_time = time.time()  # MQTT 전송 시작 시간
    
    try:
        if MQTTTransmissionClient is None:
            raise RuntimeError("MQTT client unavailable")
        client = MQTTTransmissionClient()
        client.connect()
        try:
            # FK 오류 방지: 검사본(inspection_info 포함) 먼저 → 메타 2종 전송
            perf = _get_mqtt_cfg().get('performance', {})
            timeout_sec = int(perf.get('response_timeout', 30))
            client.send_all_in_order(
                inspection_info=inspection_info,
                inspection_results=normalized_results,
                inspection_summary=summary_data,
                api_call_info=api_call_info,
                api_response_data=api_response_data,
                await_response=True,
                timeout=timeout_sec,
            )
            _logger.debug(f"requests_keti: MQTT sent ok (inspection_id={inspection_id}, rows={len(df)})")
            
            # MQTT 전송 완료 시간 및 지연시간 메트릭 생성
            mqtt_end_time = time.time()
            mqtt_duration = (mqtt_end_time - mqtt_start_time) * 1000  # 밀리초
            
            # 전체 엔드투엔드 시간 계산
            overall_end_time = time.time()
            total_duration = (overall_end_time - overall_start_time) * 1000  # 밀리초
            
            # 지연시간 메트릭 구성
            delay_metrics = {
                'inspection_id': inspection_id,
                'data_source': data_source,
                'api_endpoint': path.lstrip('/'),
                'http_request_time_ms': api_call_info.get('response_time_ms', 0),
                'data_processing_time_ms': inspection_info.get('processing_time_ms', 0),
                'quality_check_time_ms': quality_check_duration,
                'mqtt_transmission_time_ms': mqtt_duration,
                'total_end_to_end_time_ms': total_duration,
                'timestamp': _dt.now().isoformat(),
                'data_rows': len(df),
                'data_columns': len(df.columns)
            }
            
            # 지연시간 메트릭 전송
            try:
                client.send_delay_metrics(delay_metrics)
                _logger.debug(f"지연시간 메트릭 전송 완료: {inspection_id}")
            except Exception as e:
                _logger.warning(f"지연시간 메트릭 전송 실패: {e}")
                
        finally:
            client.disconnect()
    except Exception as e:
        _logger.error(f"requests_keti: MQTT send failed: {e}")

    # 최종적으로 원본 Response 반환
    return response


