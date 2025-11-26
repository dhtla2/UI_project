#!/usr/bin/env python3
"""
MQTT 기능 테스트 스크립트

이 스크립트는 MQTT 시스템의 다양한 기능을 테스트합니다.
연결, 메시지 전송, 검사 결과 전송 등을 단계별로 검증합니다.

테스트 항목:
1. MQTT 브로커 연결 테스트
2. 기본 메시지 전송 테스트
3. 검사 결과 전송 테스트

실행 방법:
    python test_mqtt.py

사전 요구사항:
- MQTT 브로커 (mosquitto) 실행 중
- MQTT 수신 서비스 실행 중 (선택사항)
"""

import sys
import os
import json
import time
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mqtt.mqtt_sender import MQTTTransmissionClient
from mqtt.mqtt_config import get_broker_config, get_topics_config

def test_mqtt_connection():
    """
    MQTT 브로커 연결 테스트
    
    MQTT 브로커에 연결하고 해제하는 기본적인 연결 기능을 테스트합니다.
    
    Returns:
        bool: 연결 테스트 성공 여부
    """
    print("🔗 MQTT 연결 테스트")
    print("=" * 30)
    
    # 브로커 설정 로드
    broker_config = get_broker_config()
    
    try:
        # MQTT 클라이언트 인스턴스 생성
        client = MQTTTransmissionClient(
            broker_host=broker_config['host'],
            broker_port=broker_config['port']
        )
        
        # 브로커에 연결
        client.connect()
        print(f"✅ MQTT 브로커 연결 성공: {broker_config['host']}:{broker_config['port']}")
        
        # 연결 해제
        client.disconnect()
        print("✅ MQTT 브로커 연결 해제 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ MQTT 연결 실패: {e}")
        return False

def test_mqtt_message_sending():
    """
    MQTT 메시지 전송 테스트
    
    기본적인 메시지 전송 기능을 테스트합니다.
    검사 결과 토픽으로 테스트 메시지를 전송합니다.
    
    Returns:
        bool: 메시지 전송 테스트 성공 여부
    """
    print("\n📤 MQTT 메시지 전송 테스트")
    print("=" * 30)
    
    # 설정 로드
    broker_config = get_broker_config()
    topics_config = get_topics_config()
    
    try:
        # MQTT 클라이언트 생성 및 연결
        client = MQTTTransmissionClient(
            broker_host=broker_config['host'],
            broker_port=broker_config['port']
        )
        client.connect()
        
        # 테스트용 메시지 데이터 생성
        test_data = {
            "test_id": f"test_{int(time.time())}",      # 고유 테스트 ID
            "message": "MQTT 테스트 메시지",              # 테스트 메시지
            "timestamp": datetime.now().isoformat(),     # 타임스탬프
            "data": {
                "sample": "test_data",                   # 샘플 데이터
                "number": 123,                          # 숫자 데이터
                "boolean": True                         # 불린 데이터
            }
        }
        
        # 메시지 전송 (검사 결과 토픽 사용)
        topic = topics_config['inspection_results']
        payload = json.dumps(test_data, ensure_ascii=False)
        
        result = client.client.publish(topic, payload, qos=1)
        
        # 전송 결과 확인
        if result.rc == 0:
            print(f"✅ 메시지 전송 성공")
            print(f"  - 토픽: {topic}")
            print(f"  - 데이터: {test_data['test_id']}")
        else:
            print(f"❌ 메시지 전송 실패: {result.rc}")
        
        # 연결 해제
        client.disconnect()
        
        return True
        
    except Exception as e:
        print(f"❌ MQTT 메시지 전송 테스트 실패: {e}")
        return False

def test_mqtt_inspection_results():
    """
    검사 결과 전송 테스트
    
    실제 검사 결과 데이터를 MQTT로 전송하는 기능을 테스트합니다.
    검사 정보, 결과, 요약을 포함한 완전한 검사 데이터를 전송합니다.
    
    Returns:
        bool: 검사 결과 전송 테스트 성공 여부
    """
    print("\n🔍 검사 결과 전송 테스트")
    print("=" * 30)
    
    # 브로커 설정 로드
    broker_config = get_broker_config()
    
    try:
        # MQTT 클라이언트 생성 및 연결
        client = MQTTTransmissionClient(
            broker_host=broker_config['host'],
            broker_port=broker_config['port']
        )
        client.connect()
        
        # 테스트용 검사 기본 정보 생성
        inspection_info = {
            'inspection_id': f"test_inspection_{int(time.time())}",  # 고유 검사 ID
            'table_name': 'test_table',                              # 테이블명
            'data_source': 'TEST',                                   # 데이터 소스
            'total_rows': 100,                                       # 총 행 수
            'total_columns': 5,                                      # 총 열 수
            'inspection_type': 'comprehensive',                      # 검사 유형
            'inspection_status': 'completed',                        # 검사 상태
            'start_time': datetime.now(),                           # 시작 시간
            'end_time': datetime.now(),                             # 종료 시간
            'processing_time_ms': 1500,                             # 처리 시간
            'created_by': 'test_user'                               # 생성자
        }
        
        # 테스트용 검사 결과 데이터 생성
        inspection_results = [
            {
                'inspection_id': inspection_info['inspection_id'],
                'check_type': 'COMPLETENESS',                        # 검사 유형
                'check_name': 'COMPLETENESS',                        # 검사명
                'message': '완전성 검사 완료',                        # 메시지
                'status': 'PASS',                                   # 상태 (PASS/FAIL)
                'severity': 'MEDIUM',                               # 심각도
                'affected_rows': 0,                                 # 영향받은 행 수
                'affected_columns': '["test_column"]',              # 영향받은 열
                'details': '{"total": 100, "check": 0, "etc": 100}' # 상세 정보
            }
        ]
        
        # 테스트용 검사 요약 정보 생성
        inspection_summary = {
            'inspection_id': inspection_info['inspection_id'],
            'total_checks': 1,                                      # 총 검사 수
            'passed_checks': 1,                                     # 통과 검사 수
            'failed_checks': 0,                                     # 실패 검사 수
            'warning_checks': 0,                                    # 경고 검사 수
            'error_checks': 0,                                      # 오류 검사 수
            'pass_rate': 100.0,                                     # 통과율
            'data_quality_score': 100.0,                           # 데이터 품질 점수
            'summary_json': '{"total_checks": 1, "passed": 1}',     # 요약 JSON
            'recommendations': '테스트 검사 완료'                     # 권장사항
        }
        
        # 검사 결과를 MQTT로 전송
        result = client.send_inspection_results(
            inspection_info=inspection_info,      # 검사 기본 정보
            inspection_results=inspection_results, # 검사 결과 목록
            inspection_summary=inspection_summary, # 검사 요약 정보
            timeout=10                            # 응답 대기 시간
        )
        
        print(f"✅ 검사 결과 전송 성공")
        print(f"  - 검사 ID: {inspection_info['inspection_id']}")
        print(f"  - 결과: {result}")
        
        # 연결 해제
        client.disconnect()
        
        return True
        
    except Exception as e:
        print(f"❌ 검사 결과 전송 테스트 실패: {e}")
        return False

def main():
    """
    메인 테스트 함수
    
    MQTT 시스템의 모든 기능을 순차적으로 테스트하고 결과를 요약합니다.
    """
    print("🧪 MQTT 기능 테스트")
    print("=" * 50)
    
    # 1. MQTT 브로커 연결 테스트
    connection_success = test_mqtt_connection()
    
    # 연결 실패 시 조기 종료
    if not connection_success:
        print("\n❌ MQTT 브로커 연결 실패. 브로커가 실행 중인지 확인하세요.")
        print("   sudo systemctl start mosquitto")
        return
    
    # 2. 기본 메시지 전송 테스트
    message_success = test_mqtt_message_sending()
    
    # 3. 검사 결과 전송 테스트 (실제 데이터 구조)
    inspection_success = test_mqtt_inspection_results()
    
    # 테스트 결과 요약 출력
    print("\n📊 테스트 결과 요약")
    print("=" * 30)
    print(f"연결 테스트: {'✅ 성공' if connection_success else '❌ 실패'}")
    print(f"메시지 전송: {'✅ 성공' if message_success else '❌ 실패'}")
    print(f"검사 결과 전송: {'✅ 성공' if inspection_success else '❌ 실패'}")
    
    # 전체 테스트 결과 판정
    if all([connection_success, message_success, inspection_success]):
        print("\n🎉 모든 테스트가 성공했습니다!")
        print("MQTT 시스템이 정상적으로 작동합니다.")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")
        print("실패한 항목을 확인하고 문제를 해결하세요.")

if __name__ == "__main__":
    main() 