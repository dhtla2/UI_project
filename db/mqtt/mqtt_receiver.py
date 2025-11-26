#!/usr/bin/env python3
"""
MQTT 브로커를 통한 검사 결과 수신 서비스

이 모듈은 MQTT 브로커로부터 데이터 품질 검사 결과를 수신하여
데이터베이스에 저장하는 서비스를 제공합니다.

주요 기능:
- MQTT 브로커 연결 및 토픽 구독
- 검사 결과, 상태, API 정보 수신 및 처리
- 데이터베이스에 검사 결과 저장
- 응답 메시지 발행

토픽 구조:
- data_quality/inspection_results: 검사 결과 수신
- data_quality/inspection_status: 검사 상태 업데이트
- data_quality/api_call_info: API 호출 정보
- data_quality/api_response_data: API 응답 데이터
- data_quality/response/{inspection_id}: 응답 발행

사용 예시:
    receiver = MQTTInspectionReceiver(broker_host="localhost", broker_port=1883)
    receiver.start()
"""

import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
from typing import Dict, Any
import sys
import os

try:
    from .mqtt_config import get_broker_config, get_tls_config
except Exception:
    from mqtt_config import get_broker_config, get_tls_config

# 상위 디렉토리의 서비스 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_inspection_service import DataInspectionService
from api_data_service import APIDataService

class MQTTInspectionReceiver:
    """
    MQTT를 통한 검사 결과 수신 서비스
    
    이 클래스는 MQTT 브로커로부터 데이터 품질 검사 결과를 수신하고,
    해당 결과를 데이터베이스에 저장하는 역할을 담당합니다.
    
    Attributes:
        broker_host (str): MQTT 브로커 호스트 주소
        broker_port (int): MQTT 브로커 포트 번호
        client (mqtt.Client): MQTT 클라이언트 인스턴스
        inspection_service (DataInspectionService): 검사 결과 저장 서비스
        api_service (APIDataService): API 데이터 저장 서비스
        logger (logging.Logger): 로깅 인스턴스
        connected (bool): 브로커 연결 상태
    """
    
    def __init__(self, broker_host: str, broker_port: int, tls_config: Dict[str, Any]):
        """
        MQTT 수신 서비스 초기화
        
        Args:
            broker_host (str): MQTT 브로커 호스트 주소 (기본값: localhost)
            broker_port (int): MQTT 브로커 포트 번호 (기본값: 1883)
        """
        # 브로커 연결 정보
        self.broker_host = broker_host
        self.broker_port = broker_port
        
        # MQTT 클라이언트 설정
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect      # 연결 콜백
        self.client.on_message = self.on_message      # 메시지 수신 콜백
        self.client.on_disconnect = self.on_disconnect # 연결 해제 콜백
        
        tls_config = get_tls_config() # config 파일에서 TLS 설정 가져오기
        if tls_config and tls_config.get('enable', False):
            logging.info("적용될 TLS 설정: %s", tls_config) # 설정 내용 로깅
            self.client.tls_set(ca_certs=tls_config.get('cafile'))
            if tls_config.get('insecure', False):
                logging.warning("insecure 모드가 활성화되었습니다. 서버 인증서 검증을 비활성화합니다.")
                self.client.tls_insecure_set(True)

        # 데이터베이스 서비스 인스턴스 생성
        self.inspection_service = DataInspectionService()  # 검사 결과 저장 서비스
        self.api_service = APIDataService()               # API 데이터 저장 서비스
        
        # 로깅 설정
        self.logger = logging.getLogger("mqtt_receiver")
        self.logger.setLevel(logging.INFO)
        
        # 연결 상태 플래그
        self.connected = False
    
    def on_connect(self, client, userdata, flags, rc):
        """
        MQTT 브로커 연결 콜백 함수
        
        브로커에 성공적으로 연결되면 필요한 토픽들을 구독합니다.
        
        Args:
            client (mqtt.Client): MQTT 클라이언트 인스턴스
            userdata: 사용자 정의 데이터 (사용하지 않음)
            flags: 연결 플래그 (사용하지 않음)
            rc (int): 연결 결과 코드 (0: 성공, 그 외: 실패)
        """
        if rc == 0:
            # 연결 성공
            self.connected = True
            self.logger.info("MQTT 브로커에 연결되었습니다.")
            
            # 구독할 토픽 목록 정의 (토픽명, QoS 레벨)
            topics = [
                ("data_quality/inspection_results", 1),      # 검사 결과 수신 토픽
                ("data_quality/inspection_status", 1),       # 검사 상태 업데이트 토픽
                ("data_quality/api_call_info", 1),          # API 호출 정보 토픽
                ("data_quality/api_response_data", 1),      # API 응답 데이터 토픽
                ("data_quality/delay_metrics", 1)           # 지연시간 메트릭 토픽
            ]
            
            # 각 토픽 구독
            for topic, qos in topics:
                client.subscribe(topic, qos)
                self.logger.info(f"토픽 구독: {topic} (QoS: {qos})")
        else:
            # 연결 실패
            self.logger.error(f"MQTT 연결 실패: {rc}")
    
    def on_message(self, client, userdata, msg):
        """
        MQTT 메시지 수신 콜백 함수
        
        수신된 메시지를 토픽에 따라 적절한 처리 함수로 라우팅합니다.
        
        Args:
            client (mqtt.Client): MQTT 클라이언트 인스턴스
            userdata: 사용자 정의 데이터 (사용하지 않음)
            msg (mqtt.MQTTMessage): 수신된 메시지 객체
        """
        try:
            # 메시지 정보 추출
            topic = msg.topic
            payload = msg.payload.decode('utf-8')  # 바이트를 문자열로 디코딩
            data = json.loads(payload)             # JSON 문자열을 딕셔너리로 파싱
            
            self.logger.info(f"메시지 수신: {topic}")
            
            # 토픽별 처리 함수 호출
            if topic == "data_quality/inspection_results":
                self.process_inspection_results(data)      # 검사 결과 처리
            elif topic == "data_quality/inspection_status":
                self.process_inspection_status(data)       # 검사 상태 처리
            elif topic == "data_quality/api_call_info":
                self.process_api_call_info(data)          # API 호출 정보 처리
            elif topic == "data_quality/api_response_data":
                self.process_api_response_data(data)      # API 응답 데이터 처리
            elif topic == "data_quality/delay_metrics":
                self.process_delay_metrics(data)          # 지연시간 메트릭 처리
            else:
                self.logger.warning(f"알 수 없는 토픽: {topic}")
                
        except json.JSONDecodeError as e:
            # JSON 파싱 오류 처리
            self.logger.error(f"JSON 파싱 오류: {e}")
        except Exception as e:
            # 기타 예외 처리
            self.logger.error(f"메시지 처리 오류: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """
        MQTT 브로커 연결 해제 콜백 함수
        
        브로커와의 연결이 해제될 때 호출됩니다.
        
        Args:
            client (mqtt.Client): MQTT 클라이언트 인스턴스
            userdata: 사용자 정의 데이터 (사용하지 않음)
            rc (int): 연결 해제 결과 코드
        """
        self.connected = False
        self.logger.warning("MQTT 브로커와 연결이 해제되었습니다.")
    
    def process_inspection_results(self, data: Dict[str, Any]):
        """
        검사 결과 데이터 처리 함수
        
        수신된 검사 결과를 데이터베이스에 저장하고 성공/실패 응답을 발행합니다.
        
        Args:
            data (Dict[str, Any]): 검사 결과 데이터
                - inspection_id: 검사 ID
                - inspection_info: 검사 기본 정보
                - inspection_results: 개별 검사 결과 목록
                - inspection_summary: 검사 요약 정보
        """
        try:
            # 검사 ID 추출
            inspection_id = data.get('inspection_id')
            
            # 1. 검사 기본 정보 저장
            if 'inspection_info' in data:
                self.inspection_service.save_inspection_info(data['inspection_info'])
                self.logger.info(f"검사 정보 저장 완료: {inspection_id}")
            
            # 2. 개별 검사 결과 저장 (각 결과를 개별적으로 저장)
            if 'inspection_results' in data:
                for result in data['inspection_results']:
                    self.inspection_service.save_inspection_results(inspection_id, [result])
                self.logger.info(f"검사 결과 저장 완료: {inspection_id}")
            
            # 3. 검사 요약 정보 저장
            if 'inspection_summary' in data:
                self.inspection_service.save_inspection_summary(inspection_id, data['inspection_summary'])
                self.logger.info(f"검사 요약 저장 완료: {inspection_id}")
            
            # 4. 성공 응답 메시지 발행
            response = {
                "status": "success",
                "inspection_id": inspection_id,
                "timestamp": datetime.now().isoformat(),
                "message": "검사 결과가 성공적으로 저장되었습니다."
            }
            
            # 응답 토픽으로 성공 메시지 발행
            self.client.publish(
                f"data_quality/response/{inspection_id}",
                json.dumps(response, ensure_ascii=False),
                qos=1
            )
            
        except Exception as e:
            # 오류 발생 시 로그 기록
            self.logger.error(f"검사 결과 처리 실패: {e}")
            
            # 5. 오류 응답 메시지 발행
            error_response = {
                "status": "error",
                "inspection_id": data.get('inspection_id'),
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            
            # 응답 토픽으로 오류 메시지 발행
            self.client.publish(
                f"data_quality/response/{data.get('inspection_id')}",
                json.dumps(error_response, ensure_ascii=False),
                qos=1
            )
    
    def process_inspection_status(self, data: Dict[str, Any]):
        """
        검사 상태 업데이트 처리 함수
        
        검사 진행 상태 변경을 데이터베이스에 반영합니다.
        
        Args:
            data (Dict[str, Any]): 검사 상태 데이터
                - inspection_id: 검사 ID
                - status: 새로운 상태 (예: 'running', 'completed', 'failed')
        """
        try:
            # 검사 ID와 상태 추출
            inspection_id = data.get('inspection_id')
            status = data.get('status')
            
            # 데이터베이스에 상태 업데이트
            self.inspection_service.update_inspection_status(inspection_id, status)
            self.logger.info(f"검사 상태 업데이트 완료: {inspection_id} -> {status}")
            
        except Exception as e:
            self.logger.error(f"검사 상태 처리 실패: {e}")
    
    def process_api_call_info(self, data: Dict[str, Any]):
        """
        API 호출 정보 처리 함수
        
        API 호출 관련 정보를 데이터베이스에 저장합니다.
        
        Args:
            data (Dict[str, Any]): API 호출 정보
                - inspection_id: 검사 ID
                - api_endpoint: API 엔드포인트
                - request_method: HTTP 메서드
                - call_timestamp: 호출 시간
                - response_status: 응답 상태
                - response_time_ms: 응답 시간
        """
        try:
            # API 호출 정보를 데이터베이스에 저장
            self.api_service.save_api_call_info(data)
            self.logger.info(f"API 호출 정보 저장 완료: {data.get('inspection_id')}")
            
        except Exception as e:
            self.logger.error(f"API 호출 정보 처리 실패: {e}")
    
    def process_api_response_data(self, data: Dict[str, Any]):
        """
        API 응답 데이터 처리 함수
        
        API 응답 데이터를 데이터베이스에 저장합니다.
        
        Args:
            data (Dict[str, Any]): API 응답 데이터
                - inspection_id: 검사 ID
                - data_source: 데이터 소스
                - data_type: 데이터 타입
                - request_params: API 호출 파라미터
                - processed_data_count: 처리된 데이터 건수
                - data_columns: 데이터 컬럼 목록
                - data_sample: 데이터 샘플 (처음 3행)
        """
        try:
            # 1) 필수 키 점검
            required_keys = ['inspection_id', 'data_source', 'data_type', 'request_params']
            missing = [k for k in required_keys if k not in data]
            if missing:
                raise KeyError(f"필수 키 누락: {missing}")

            inspection_id = data['inspection_id']
            data_source = data['data_source']
            data_type = data['data_type']
            request_params = data.get('request_params', {})
            processed_data_count = data.get('processed_data_count', 0)
            data_columns = data.get('data_columns', [])
            data_sample = data.get('data_sample', [])

            # 2) DB 저장 페이로드 구성 (raw_response_data 제거)
            payload = {
                'inspection_id': inspection_id,
                'data_source': data_source,
                'data_type': data_type,
                'request_params': request_params,  # API 호출 파라미터 저장
                'processed_data_count': processed_data_count,
                'data_columns': data_columns,
                'data_sample': data_sample,  # 데이터 샘플 저장
                'data_file_name': None,  # CSV 파일은 수신기에서 생성하지 않음
                'data_file_size_bytes': 0,
                'data_checksum': None,
            }

            # 3) DB 저장
            success = self.api_service.save_response_data(payload)
            if success:
                self.logger.info(f"API 응답 데이터 저장 완료: {inspection_id}")
            else:
                self.logger.warning(f"API 응답 데이터 저장 실패: {inspection_id}")
            
        except Exception as e:
            self.logger.error(f"API 응답 데이터 처리 실패: {e}")
    
    def process_delay_metrics(self, data: Dict[str, Any]):
        """
        지연시간 메트릭 데이터 처리 함수
        
        수신된 지연시간 메트릭을 로깅하고 성능 분석에 활용합니다.
        
        Args:
            data (Dict[str, Any]): 지연시간 메트릭 데이터
                - inspection_id: 검사 ID
                - data_source: 데이터 소스
                - api_endpoint: API 엔드포인트
                - http_request_time_ms: HTTP 요청 시간
                - data_processing_time_ms: 데이터 처리 시간
                - quality_check_time_ms: 품질검사 시간
                - mqtt_transmission_time_ms: MQTT 전송 시간
                - total_end_to_end_time_ms: 전체 엔드투엔드 시간
        """
        try:
            inspection_id = data.get('inspection_id', 'unknown')
            data_source = data.get('data_source', 'unknown')
            api_endpoint = data.get('api_endpoint', 'unknown')
            
            # 지연시간 메트릭 로깅
            self.logger.info(f"📊 지연시간 메트릭 수신: {inspection_id}")
            self.logger.info(f"   📍 데이터 소스: {data_source}")
            self.logger.info(f"   🔗 API 엔드포인트: {api_endpoint}")
            self.logger.info(f"   🌐 HTTP 요청: {data.get('http_request_time_ms', 0):.2f}ms")
            self.logger.info(f"   ⚙️  데이터 처리: {data.get('data_processing_time_ms', 0):.2f}ms")
            self.logger.info(f"   🔍 품질검사: {data.get('quality_check_time_ms', 0):.2f}ms")
            self.logger.info(f"   📡 MQTT 전송: {data.get('mqtt_transmission_time_ms', 0):.2f}ms")
            self.logger.info(f"   ⏱️  전체 시간: {data.get('total_end_to_end_time_ms', 0):.2f}ms")
            self.logger.info(f"   📊 데이터 크기: {data.get('data_rows', 0)}행 × {data.get('data_columns', 0)}열")
            
            # 성능 분석 (임계값 기반)
            total_time = data.get('total_end_to_end_time_ms', 0)
            if total_time > 5000:  # 5초 이상
                self.logger.warning(f"⚠️  성능 경고: {inspection_id} - 전체 처리 시간 {total_time:.2f}ms (5초 초과)")
            elif total_time > 10000:  # 10초 이상
                self.logger.error(f"🚨 성능 오류: {inspection_id} - 전체 처리 시간 {total_time:.2f}ms (10초 초과)")
            
        except Exception as e:
            self.logger.error(f"지연시간 메트릭 처리 실패: {e}")
    
    def start(self):
        """
        MQTT 브로커 연결 및 서비스 시작
        
        MQTT 브로커에 연결하고 메시지 수신 루프를 시작합니다.
        """
        # try:
        #     # TLS 설정 적용
        #     cfg = get_mqtt_config()
        #     tls_cfg = cfg.get('tls', {})
        #     if tls_cfg.get('enable', False):
        #         cafile = tls_cfg.get('cafile')
        #         if cafile and os.path.exists(cafile):
        #             self.client.tls_set(ca_certs=cafile)
        #         else:
        #             self.client.tls_set()  # 시스템 CA 사용 시도
        #         if tls_cfg.get('insecure', False):
        #             self.client.tls_insecure_set(True)

        #     # MQTT 브로커에 연결 (keepalive: 60초)
        #     self.client.connect(self.broker_host, self.broker_port, 60)
            
        #     # 메시지 수신 루프 시작 (비동기)
        #     self.client.loop_start()
            
        #     self.logger.info("MQTT 검사 결과 수신 서비스가 시작되었습니다.")
            
        # except Exception as e:
        #     self.logger.error(f"MQTT 서비스 시작 실패: {e}")
        try:
            # TLS 설정 로직을 __init__으로 옮겼으므로 여기서는 삭제합니다.

            # MQTT 브로커에 연결 (keepalive: 60초)
            self.client.connect(self.broker_host, self.broker_port, 60)
            
            # 메시지 수신 루프 시작 (비동기)
            self.client.loop_start()
            
            self.logger.info("MQTT 검사 결과 수신 서비스가 시작되었습니다.")
            
        except Exception as e:
            self.logger.error(f"MQTT 서비스 시작 실패: {e}")
            raise # 오류를 다시 발생시켜 상위 서비스에서 처리하도록 함

    
    def stop(self):
        """
        MQTT 서비스 중지
        
        메시지 수신 루프를 중지하고 브로커 연결을 해제합니다.
        """
        try:
            # 메시지 수신 루프 중지
            self.client.loop_stop()
            
            # 브로커 연결 해제
            self.client.disconnect()
            
            self.logger.info("MQTT 검사 결과 수신 서비스가 중지되었습니다.")
            
        except Exception as e:
            self.logger.error(f"MQTT 서비스 중지 실패: {e}")

# =============================================================================
# 메인 실행 부분
# =============================================================================

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # MQTT 수신 서비스 인스턴스 생성
    receiver = MQTTInspectionReceiver()
    
    try:
        # 서비스 시작
        receiver.start()
        
        # 서비스 유지 (무한 루프)
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Ctrl+C로 서비스 종료
        print("\n서비스를 종료합니다...")
        receiver.stop() 