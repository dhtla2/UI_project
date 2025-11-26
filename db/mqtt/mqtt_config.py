#!/usr/bin/env python3
"""
MQTT 설정 관리 모듈

이 모듈은 MQTT 브로커, 클라이언트, 토픽, 로깅, 성능 관련 설정을 
중앙에서 관리합니다. 환경 변수를 통해 설정을 동적으로 변경할 수 있습니다.

환경 변수 설정 예시:
    export MQTT_BROKER_HOST=192.168.1.100
    export MQTT_BROKER_PORT=1883
    export MQTT_LOG_LEVEL=DEBUG
    export MQTT_RESPONSE_TIMEOUT=60
"""

import os
from typing import Dict, Any

# =============================================================================
# MQTT 브로커 설정
# =============================================================================
MQTT_BROKER_CONFIG = {
    'host': os.getenv('MQTT_BROKER_HOST', 'localhost'),      # 브로커 호스트 주소
    'port': int(os.getenv('MQTT_BROKER_PORT', 8883)),        # 브로커 포트 번호
    'username': os.getenv('MQTT_BROKER_USERNAME', None),     # 인증 사용자명 (선택사항)
    'password': os.getenv('MQTT_BROKER_PASSWORD', None),     # 인증 비밀번호 (선택사항)
    'keepalive': int(os.getenv('MQTT_BROKER_KEEPALIVE', 60)), # 연결 유지 시간(초)
    'qos': int(os.getenv('MQTT_BROKER_QOS', 1))             # 메시지 품질 수준 (0, 1, 2)
}

# =============================================================================
# MQTT TLS 설정 (8883 사용 시 권장)
# =============================================================================
MQTT_TLS_CONFIG = {
    'enable': os.getenv('MQTT_TLS_ENABLE', 'true').lower() == 'true',                 # TLS 활성화 여부
    'cafile': os.getenv('MQTT_TLS_CAFILE', '/etc/mosquitto/certs_new/ca.crt'),     # CA 인증서 경로
    'insecure': os.getenv('MQTT_TLS_INSECURE', 'false').lower() == 'true'              # 자가서명/이름불일치 허용(테스트용)
}

# =============================================================================
# MQTT 토픽 설정
# =============================================================================
MQTT_TOPICS = {
    'inspection_results': 'data_quality/inspection_results',    # 검사 결과 전송 토픽
    'inspection_status': 'data_quality/inspection_status',      # 검사 상태 업데이트 토픽
    'api_call_info': 'data_quality/api_call_info',             # API 호출 정보 토픽
    'api_response_data': 'data_quality/api_response_data',     # API 응답 데이터 토픽
    'delay_metrics': 'data_quality/delay_metrics',              # 지연시간 메트릭 전송 토픽
    'response': 'data_quality/response'                        # 응답 수신 토픽 (와일드카드: #)
}

# =============================================================================
# MQTT 클라이언트 설정
# =============================================================================
MQTT_CLIENT_CONFIG = {
    'client_id_prefix': 'inspection_client',     # 클라이언트 ID 접두사
    'clean_session': True,                       # 세션 정리 여부
    'auto_reconnect': True,                      # 자동 재연결 여부
    'max_inflight_messages': 20,                 # 동시 처리 가능한 메시지 수
    'message_retry_set': 1                       # 메시지 재시도 설정
}

# =============================================================================
# MQTT 로깅 설정
# =============================================================================
MQTT_LOGGING_CONFIG = {
    'level': os.getenv('MQTT_LOG_LEVEL', 'INFO'),                    # 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s', # 로그 포맷
    'file': os.getenv('MQTT_LOG_FILE', None)                         # 로그 파일 경로 (선택사항)
}

# =============================================================================
# MQTT 성능 설정
# =============================================================================
MQTT_PERFORMANCE_CONFIG = {
    'connection_timeout': int(os.getenv('MQTT_CONNECTION_TIMEOUT', 10)), # 연결 타임아웃(초)
    'response_timeout': int(os.getenv('MQTT_RESPONSE_TIMEOUT', 30)),     # 응답 대기 타임아웃(초)
    'retry_attempts': int(os.getenv('MQTT_RETRY_ATTEMPTS', 3)),         # 재시도 횟수
    'retry_delay': float(os.getenv('MQTT_RETRY_DELAY', 1.0))           # 재시도 간격(초)
}

# =============================================================================
# 설정 반환 함수들
# =============================================================================

def get_mqtt_config() -> Dict[str, Any]:
    """
    MQTT 전체 설정을 반환합니다.
    
    Returns:
        Dict[str, Any]: 브로커, 토픽, 클라이언트, 로깅, 성능 설정을 포함한 전체 설정
    """
    return {
        'broker': MQTT_BROKER_CONFIG,      # 브로커 설정
        'topics': MQTT_TOPICS,             # 토픽 설정
        'client': MQTT_CLIENT_CONFIG,      # 클라이언트 설정
        'logging': MQTT_LOGGING_CONFIG,    # 로깅 설정
        'performance': MQTT_PERFORMANCE_CONFIG,  # 성능 설정
        'tls': MQTT_TLS_CONFIG             # TLS 설정
    }

def get_broker_config() -> Dict[str, Any]:
    """
    MQTT 브로커 설정을 반환합니다.
    
    Returns:
        Dict[str, Any]: 브로커 호스트, 포트, 인증 정보 등
    """
    return MQTT_BROKER_CONFIG

def get_topics_config() -> Dict[str, str]:
    """
    MQTT 토픽 설정을 반환합니다.
    
    Returns:
        Dict[str, str]: 토픽 이름과 경로 매핑
    """
    return MQTT_TOPICS

def get_client_config() -> Dict[str, Any]:
    """
    MQTT 클라이언트 설정을 반환합니다.
    
    Returns:
        Dict[str, Any]: 클라이언트 ID, 세션, 재연결 등 설정
    """
    return MQTT_CLIENT_CONFIG

def get_logging_config() -> Dict[str, Any]:
    """
    MQTT 로깅 설정을 반환합니다.
    
    Returns:
        Dict[str, Any]: 로그 레벨, 포맷, 파일 경로 등
    """
    return MQTT_LOGGING_CONFIG

def get_performance_config() -> Dict[str, Any]:
    """
    MQTT 성능 설정을 반환합니다.
    
    Returns:
        Dict[str, Any]: 타임아웃, 재시도 등 성능 관련 설정
    """
    return MQTT_PERFORMANCE_CONFIG 

def get_tls_config() -> Dict[str, Any]:
    """
    MQTT TLS 설정을 반환합니다.
    
    Returns:
        Dict[str, Any]: TLS 활성화, CA 파일, insecure 옵션
    """
    return MQTT_TLS_CONFIG