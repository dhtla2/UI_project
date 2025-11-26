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
    
    def __init__(self, client_id: Optional[str] = None):
        """
        MQTT 전송 클라이언트 초기화.
        모든 설정은 mqtt_config.py에서 가져옵니다.
        
        Args:
            client_id (str, optional): 클라이언트 ID. 지정하지 않으면 자동 생성됩니다.
        """
        # --- 설정 파일에서 브로커 정보 가져오기 ---
        broker_config = get_mqtt_config().get('broker', {})
        self.broker_host = broker_config.get('host', 'localhost')
        self.broker_port = broker_config.get('port', 1883)
        
        # 클라이언트 ID 설정 (없으면 자동 생성)
        if client_id is None:
            client_id_prefix = get_mqtt_config().get('client', {}).get('client_id_prefix', 'client')
            client_id = f"{client_id_prefix}_{int(time.time())}"
        
        # MQTT 클라이언트 설정
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self.on_connect      # 연결 콜백
        self.client.on_message = self.on_message      # 메시지 수신 콜백
        self.client.on_disconnect = self.on_disconnect # 연결 해제 콜백
        
        # 응답 대기 딕셔너리 (inspection_id -> 응답 데이터)
        self.pending_responses = {}
        
        # 로깅 설정 (기본은 콘솔 미출력)
        log_config = get_mqtt_config().get('logging', {})
        self.logger = logging.getLogger("mqtt_transmission")
        if not self.logger.handlers:
            self.logger.addHandler(logging.NullHandler())
        self.logger.setLevel(log_config.get('level', 'WARNING'))
        
        # 연결 상태 플래그
        self.connected = False
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT 연결 콜백"""
        if rc == 0:
            self.connected = True
            self.logger.debug("MQTT 브로커에 연결되었습니다.")
            
            # 응답 토픽 구독
            self.client.subscribe("data_quality/response/#", 1)
            self.logger.debug("응답 토픽 구독: data_quality/response/#")
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
                    self.logger.debug(f"응답 수신: {inspection_id} - {data.get('status')}")
                else:
                    self.logger.debug(f"예상하지 않은 응답: {inspection_id}")
                    
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류: {e}")
        except Exception as e:
            self.logger.error(f"메시지 처리 오류: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT 연결 해제 콜백"""
        self.connected = False
        self.logger.debug("MQTT 브로커와 연결이 해제되었습니다.")
    
    def connect(self):
        """MQTT 브로커 연결"""
        try:
            # TLS 설정 적용
            cfg = get_mqtt_config()
            tls_cfg = cfg.get('tls', {})
            if tls_cfg.get('enable', False):
                # insecure 모드가 True일 경우, cafile을 무시하고 검증을 비활성화합니다.
                if tls_cfg.get('insecure', True): # 개발 환경에서는 True로 강제하여 테스트할 수 있습니다.
                    self.client.tls_set()  # ca_certs를 지정하지 않습니다.
                    self.client.tls_insecure_set(True) # 인증서 검증을 비활성화합니다.
                    self.logger.warning("insecure TLS 모드로 연결합니다. (인증서 검증 비활성화)")
                else:
                    # insecure 모드가 아닐 때만 cafile을 사용하여 안전하게 연결합니다.
                    cafile = tls_cfg.get('cafile')
                    if cafile and os.path.exists(cafile):
                        self.client.tls_set(ca_certs=cafile)
                    else:
                        # cafile이 없으면 시스템 기본 인증서를 사용 (일반적으로 실패)
                        self.client.tls_set()

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
            self.logger.debug("MQTT 브로커 연결이 해제되었습니다.")
        except Exception as e:
            self.logger.error(f"MQTT 연결 해제 실패: {e}")
    
    def send_inspection_results(self, 
                              inspection_info: Dict[str, Any],
                              inspection_results: List[Dict[str, Any]],
                              inspection_summary: Dict[str, Any],
                              api_call_info: Optional[Dict[str, Any]] = None,
                              api_response_data: Optional[Dict[str, Any]] = None,
                              timeout: int = 30,
                              await_response: bool = True) -> Dict[str, Any]:
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
            
            # 응답 대기 설정 (옵션)
            if await_response:
                self.pending_responses[inspection_id] = None
            
            # 메시지 전송
            topic = "data_quality/inspection_results"
            payload = json.dumps(transmission_data, ensure_ascii=False, default=str)
            # 목적지 프린트
            try:
                cfg = get_mqtt_config()
                tls_cfg = cfg.get('tls', {})
                # print(f"[MQTT SEND] {self.broker_host}:{self.broker_port} topic={topic} tls={tls_cfg.get('enable', False)} insecure={tls_cfg.get('insecure', False)}")
            except Exception:
                # print(f"[MQTT SEND] {self.broker_host}:{self.broker_port} topic={topic}")
                pass
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise Exception(f"메시지 전송 실패: {result.rc}")
            
            self.logger.debug(f"검사 결과 전송 완료: {inspection_id}")
            
            # 응답 대기 (옵션)
            if await_response:
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
            else:
                # 응답 미대기 모드: 즉시 반환
                return {"status": "published", "inspection_id": inspection_id}
            
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
            # 목적지 프린트
            try:
                cfg = get_mqtt_config()
                tls_cfg = cfg.get('tls', {})
                # print(f"[MQTT SEND] {self.broker_host}:{self.broker_port} topic={topic} tls={tls_cfg.get('enable', False)} insecure={tls_cfg.get('insecure', False)}")
            except Exception:
                # print(f"[MQTT SEND] {self.broker_host}:{self.broker_port} topic={topic}")
                pass
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"검사 상태 전송 완료: {inspection_id} -> {status}")
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
            # 필수 키 점검(누락 시 경고만 남기고 전송은 진행)
            required_keys = [
                'inspection_id', 'api_endpoint', 'request_params', 'request_headers',
                'response_status_code', 'response_time_ms', 'data_retrieval_start_time',
                'data_retrieval_end_time', 'data_retrieval_duration_ms',
                'total_records_retrieved', 'data_file_path'
            ]
            missing = [k for k in required_keys if k not in api_call_info]
            if missing:
                self.logger.warning(f"api_call_info 누락 키: {missing}. 수신측 DB 제약(FK/NOT NULL) 위반 가능.")

            topic = "data_quality/api_call_info"
            payload = json.dumps(api_call_info, ensure_ascii=False, default=str)
            # 목적지 프린트
            try:
                cfg = get_mqtt_config()
                tls_cfg = cfg.get('tls', {})
                # print(f"[MQTT SEND] {self.broker_host}:{self.broker_port} topic={topic} tls={tls_cfg.get('enable', False)} insecure={tls_cfg.get('insecure', False)}")
            except Exception:
                # print(f"[MQTT SEND] {self.broker_host}:{self.broker_port} topic={topic}")
                pass
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"API 호출 정보 전송 완료: {api_call_info.get('inspection_id')}")
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
            # 필수 키 점검(누락 시 경고만 남기고 전송은 진행)
            required_keys = [
                'inspection_id', 'data_source', 'data_type', 'raw_response_data',
                'processed_data_count', 'data_columns', 'data_file_name',
                'data_file_size_bytes', 'data_checksum'
            ]
            missing = [k for k in required_keys if k not in api_response_data]
            if missing:
                self.logger.warning(f"api_response_data 누락 키: {missing}. 수신측 DB 제약 위반 가능.")

            topic = "data_quality/api_response_data"
            payload = json.dumps(api_response_data, ensure_ascii=False, default=str)
            # 목적지 프린트
            try:
                cfg = get_mqtt_config()
                tls_cfg = cfg.get('tls', {})
                # print(f"[MQTT SEND] {self.broker_host}:{self.broker_port} topic={topic} tls={tls_cfg.get('enable', False)} insecure={tls_cfg.get('insecure', False)}")
            except Exception:
                # print(f"[MQTT SEND] {self.broker_host}:{self.broker_port} topic={topic}")
                pass
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"API 응답 데이터 전송 완료: {api_response_data.get('inspection_id')}")
                return True
            else:
                self.logger.error(f"API 응답 데이터 전송 실패: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"API 응답 데이터 전송 실패: {e}")
            return False 

    def send_all_in_order(
        self,
        inspection_info: Dict[str, Any],
        inspection_results: List[Dict[str, Any]],
        inspection_summary: Dict[str, Any],
        api_call_info: Optional[Dict[str, Any]] = None,
        api_response_data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        await_response: bool = True
    ) -> Dict[str, Any]:
        """
        검사본을 먼저 전송한 뒤(inspection_info 포함) 메타(api_call_info, api_response_data)를 전송한다.
        FK 제약으로 인한 저장 순서 문제를 방지하기 위한 헬퍼.
        """
        # 1) 검사 결과 먼저 전송(inspection_info 포함)
        resp = self.send_inspection_results(
            inspection_info=inspection_info,
            inspection_results=inspection_results,
            inspection_summary=inspection_summary,
            api_call_info=None,
            api_response_data=None,
            timeout=timeout,
            await_response=await_response,
        )

        # 2) 메타 전송(실패해도 전체 실패로 간주하지 않음)
        try:
            if api_call_info:
                self.send_api_call_info(api_call_info)
        except Exception as e:
            self.logger.warning(f"api_call_info 전송 경고: {e}")

        try:
            if api_response_data:
                self.send_api_response_data(api_response_data)
        except Exception as e:
            self.logger.warning(f"api_response_data 전송 경고: {e}")

        return resp
    
    def send_delay_metrics(self, delay_metrics: Dict[str, Any]) -> bool:
        """
        지연시간 메트릭을 MQTT로 전송
        """
        try:
            topic = "data_quality/delay_metrics"
            payload = json.dumps(delay_metrics, ensure_ascii=False, default=str)
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"지연시간 메트릭 전송 완료: {delay_metrics.get('inspection_id', 'unknown')}")
                return True
            else:
                self.logger.error(f"지연시간 메트릭 전송 실패: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"지연시간 메트릭 전송 실패: {e}")
            return False