#!/usr/bin/env python3
"""
MQTT를 통한 검사 결과 전송 클라이언트

이 모듈은 데이터 품질 검사 결과를 MQTT 프로토콜을 통해
원격 서버로 전송하는 클라이언트를 제공합니다.

주요 기능:
- MQTT 브로커 연결 및 메시지 전송
- 검사 결과, 상태, API 정보 전송
- 응답 메시지 수신 및 처리
- 연결 상태 관리 및 오류 처리

토픽 구조:
- data_quality/inspection_results: 검사 결과 전송
- data_quality/inspection_status: 검사 상태 전송
- data_quality/api_call_info: API 호출 정보 전송
- data_quality/api_response_data: API 응답 데이터 전송
- data_quality/response/{inspection_id}: 응답 수신

사용 예시:
    client = MQTTTransmissionClient(broker_host="localhost", broker_port=1883)
    client.connect()
    client.send_inspection_results(inspection_info, results, summary)
    client.disconnect()
"""

import paho.mqtt.client as mqtt
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time
import os

try:
    # 동적 import (상대경로 실행 고려)
    from .mqtt_config import get_mqtt_config
except Exception:
    from mqtt_config import get_mqtt_config

class MQTTTransmissionClient:
    """
    MQTT를 통한 검사 결과 전송 클라이언트
    
    이 클래스는 데이터 품질 검사 결과를 MQTT 브로커로 전송하고,
    서버로부터의 응답을 수신하는 역할을 담당합니다.
    
    Attributes:
        broker_host (str): MQTT 브로커 호스트 주소
        broker_port (int): MQTT 브로커 포트 번호
        client (mqtt.Client): MQTT 클라이언트 인스턴스
        pending_responses (Dict): 대기 중인 응답 메시지
        logger (logging.Logger): 로깅 인스턴스
        connected (bool): 브로커 연결 상태
    """
    
    def __init__(self, broker_host="localhost", broker_port=8883, client_id=None):
        """
        MQTT 전송 클라이언트 초기화
        
        Args:
            broker_host (str): MQTT 브로커 호스트 주소 (기본값: localhost)
            broker_port (int): MQTT 브로커 포트 번호 (기본값: 1883)
            client_id (str, optional): 클라이언트 ID (기본값: 자동 생성)
        """
        # 브로커 연결 정보
        self.broker_host = broker_host
        self.broker_port = broker_port
        
        # 클라이언트 ID 설정 (없으면 자동 생성)
        if client_id is None:
            client_id = f"inspection_client_{int(time.time())}"
        
        # MQTT 클라이언트 설정
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self.on_connect      # 연결 콜백
        self.client.on_message = self.on_message      # 메시지 수신 콜백
        self.client.on_disconnect = self.on_disconnect # 연결 해제 콜백
        
        # 응답 대기 딕셔너리 (inspection_id -> 응답 데이터)
        self.pending_responses = {}
        
        # 로깅 설정
        self.logger = logging.getLogger("mqtt_transmission")
        self.logger.setLevel(logging.INFO)
        
        # 연결 상태 플래그
        self.connected = False
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT 연결 콜백"""
        if rc == 0:
            self.connected = True
            self.logger.info("MQTT 브로커에 연결되었습니다.")
            
            # 응답 토픽 구독
            self.client.subscribe("data_quality/response/#", 1)
            self.logger.info("응답 토픽 구독: data_quality/response/#")
        else:
            self.logger.error(f"MQTT 연결 실패: {rc}")
    
    def on_message(self, client, userdata, msg):
        """MQTT 메시지 수신 콜백 (응답 처리)"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            
            # 응답 토픽에서 inspection_id 추출
            if topic.startswith("data_quality/response/"):
                inspection_id = topic.split("/")[-1]
                
                if inspection_id in self.pending_responses:
                    # 대기 중인 응답 처리
                    self.pending_responses[inspection_id] = data
                    self.logger.info(f"응답 수신: {inspection_id} - {data.get('status')}")
                else:
                    self.logger.warning(f"예상하지 않은 응답: {inspection_id}")
                    
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류: {e}")
        except Exception as e:
            self.logger.error(f"메시지 처리 오류: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT 연결 해제 콜백"""
        self.connected = False
        self.logger.warning("MQTT 브로커와 연결이 해제되었습니다.")
    
    def connect(self):
        """MQTT 브로커 연결"""
        try:
            # TLS 설정 적용
            cfg = get_mqtt_config()
            tls_cfg = cfg.get('tls', {})
            if tls_cfg.get('enable', False):
                cafile = tls_cfg.get('cafile')
                if cafile and os.path.exists(cafile):
                    self.client.tls_set(ca_certs=cafile)
                else:
                    # CA 파일 경로가 없더라도 테스트를 위해 insecure 허용 가능
                    self.client.tls_set()  # 기본 시스템 CA 사용 시도
                if tls_cfg.get('insecure', False):
                    self.client.tls_insecure_set(True)

            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # 연결 대기
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            if not self.connected:
                raise Exception("MQTT 브로커 연결 시간 초과")
                
        except Exception as e:
            self.logger.error(f"MQTT 연결 실패: {e}")
            raise
    
    def disconnect(self):
        """MQTT 브로커 연결 해제"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.logger.info("MQTT 브로커 연결이 해제되었습니다.")
        except Exception as e:
            self.logger.error(f"MQTT 연결 해제 실패: {e}")
    
    def send_inspection_results(self, 
                              inspection_info: Dict[str, Any],
                              inspection_results: List[Dict[str, Any]],
                              inspection_summary: Dict[str, Any],
                              api_call_info: Optional[Dict[str, Any]] = None,
                              api_response_data: Optional[Dict[str, Any]] = None,
                              timeout: int = 30) -> Dict[str, Any]:
        """
        검사 결과를 MQTT로 전송
        """
        try:
            inspection_id = inspection_info.get('inspection_id')
            
            # 전송 데이터 구성
            transmission_data = {
                "inspection_id": inspection_id,
                "inspection_info": inspection_info,
                "inspection_results": inspection_results,
                "inspection_summary": inspection_summary,
                "api_call_info": api_call_info,
                "api_response_data": api_response_data,
                "timestamp": datetime.now().isoformat()
            }
            
            # 응답 대기 설정
            self.pending_responses[inspection_id] = None
            
            # 메시지 전송
            topic = "data_quality/inspection_results"
            payload = json.dumps(transmission_data, ensure_ascii=False, default=str)
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise Exception(f"메시지 전송 실패: {result.rc}")
            
            self.logger.info(f"검사 결과 전송 완료: {inspection_id}")
            
            # 응답 대기
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.pending_responses[inspection_id] is not None:
                    response = self.pending_responses[inspection_id]
                    del self.pending_responses[inspection_id]
                    return response
                time.sleep(0.1)
            
            # 타임아웃
            del self.pending_responses[inspection_id]
            raise Exception(f"응답 대기 시간 초과: {timeout}초")
            
        except Exception as e:
            self.logger.error(f"검사 결과 전송 실패: {e}")
            raise
    
    def send_inspection_status(self, inspection_id: str, status: str) -> bool:
        """
        검사 상태 전송
        """
        try:
            data = {
                "inspection_id": inspection_id,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
            
            topic = "data_quality/inspection_status"
            payload = json.dumps(data, ensure_ascii=False)
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"검사 상태 전송 완료: {inspection_id} -> {status}")
                return True
            else:
                self.logger.error(f"검사 상태 전송 실패: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"검사 상태 전송 실패: {e}")
            return False
    
    def send_api_call_info(self, api_call_info: Dict[str, Any]) -> bool:
        """
        API 호출 정보 전송
        """
        try:
            topic = "data_quality/api_call_info"
            payload = json.dumps(api_call_info, ensure_ascii=False, default=str)
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"API 호출 정보 전송 완료: {api_call_info.get('inspection_id')}")
                return True
            else:
                self.logger.error(f"API 호출 정보 전송 실패: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"API 호출 정보 전송 실패: {e}")
            return False
    
    def send_api_response_data(self, api_response_data: Dict[str, Any]) -> bool:
        """
        API 응답 데이터 전송
        """
        try:
            topic = "data_quality/api_response_data"
            payload = json.dumps(api_response_data, ensure_ascii=False, default=str)
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"API 응답 데이터 전송 완료: {api_response_data.get('inspection_id')}")
                return True
            else:
                self.logger.error(f"API 응답 데이터 전송 실패: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"API 응답 데이터 전송 실패: {e}")
            return False 