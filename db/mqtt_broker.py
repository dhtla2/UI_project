#!/usr/bin/env python3
"""
MQTT 브로커를 통한 검사 결과 수신 서비스
"""

import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
from typing import Dict, Any

from data_inspection_service import DataInspectionService
from api_data_service import APIDataService

class MQTTInspectionReceiver:
    """MQTT를 통한 검사 결과 수신 서비스"""
    
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        
        # MQTT 클라이언트 설정
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # 서비스 인스턴스
        self.inspection_service = DataInspectionService()
        self.api_service = APIDataService()
        
        # 로깅 설정
        self.logger = logging.getLogger("mqtt_receiver")
        self.logger.setLevel(logging.INFO)
        
        # 연결 상태
        self.connected = False
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT 연결 콜백"""
        if rc == 0:
            self.connected = True
            self.logger.info("MQTT 브로커에 연결되었습니다.")
            
            # 토픽 구독
            topics = [
                ("data_quality/inspection_results", 1),      # 검사 결과
                ("data_quality/inspection_status", 1),       # 검사 상태
                ("data_quality/api_call_info", 1),          # API 호출 정보
                ("data_quality/api_response_data", 1)       # API 응답 데이터
            ]
            
            for topic, qos in topics:
                client.subscribe(topic, qos)
                self.logger.info(f"토픽 구독: {topic} (QoS: {qos})")
        else:
            self.logger.error(f"MQTT 연결 실패: {rc}")
    
    def on_message(self, client, userdata, msg):
        """MQTT 메시지 수신 콜백"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            
            self.logger.info(f"메시지 수신: {topic}")
            
            # 토픽별 처리
            if topic == "data_quality/inspection_results":
                self.process_inspection_results(data)
            elif topic == "data_quality/inspection_status":
                self.process_inspection_status(data)
            elif topic == "data_quality/api_call_info":
                self.process_api_call_info(data)
            elif topic == "data_quality/api_response_data":
                self.process_api_response_data(data)
            else:
                self.logger.warning(f"알 수 없는 토픽: {topic}")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류: {e}")
        except Exception as e:
            self.logger.error(f"메시지 처리 오류: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT 연결 해제 콜백"""
        self.connected = False
        self.logger.warning("MQTT 브로커와 연결이 해제되었습니다.")
    
    def process_inspection_results(self, data: Dict[str, Any]):
        """검사 결과 처리"""
        try:
            inspection_id = data.get('inspection_id')
            
            # 1. 검사 정보 저장
            if 'inspection_info' in data:
                self.inspection_service.save_inspection_info(data['inspection_info'])
                self.logger.info(f"검사 정보 저장 완료: {inspection_id}")
            
            # 2. 검사 결과 저장
            if 'inspection_results' in data:
                for result in data['inspection_results']:
                    self.inspection_service.save_inspection_results(inspection_id, [result])
                self.logger.info(f"검사 결과 저장 완료: {inspection_id}")
            
            # 3. 검사 요약 저장
            if 'inspection_summary' in data:
                self.inspection_service.save_inspection_summary(inspection_id, data['inspection_summary'])
                self.logger.info(f"검사 요약 저장 완료: {inspection_id}")
            
            # 4. 성공 응답 발행
            response = {
                "status": "success",
                "inspection_id": inspection_id,
                "timestamp": datetime.now().isoformat(),
                "message": "검사 결과가 성공적으로 저장되었습니다."
            }
            
            self.client.publish(
                f"data_quality/response/{inspection_id}",
                json.dumps(response, ensure_ascii=False),
                qos=1
            )
            
        except Exception as e:
            self.logger.error(f"검사 결과 처리 실패: {e}")
            
            # 오류 응답 발행
            error_response = {
                "status": "error",
                "inspection_id": data.get('inspection_id'),
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            
            self.client.publish(
                f"data_quality/response/{data.get('inspection_id')}",
                json.dumps(error_response, ensure_ascii=False),
                qos=1
            )
    
    def process_inspection_status(self, data: Dict[str, Any]):
        """검사 상태 처리"""
        try:
            inspection_id = data.get('inspection_id')
            status = data.get('status')
            
            self.inspection_service.update_inspection_status(inspection_id, status)
            self.logger.info(f"검사 상태 업데이트 완료: {inspection_id} -> {status}")
            
        except Exception as e:
            self.logger.error(f"검사 상태 처리 실패: {e}")
    
    def process_api_call_info(self, data: Dict[str, Any]):
        """API 호출 정보 처리"""
        try:
            self.api_service.save_api_call_info(data)
            self.logger.info(f"API 호출 정보 저장 완료: {data.get('inspection_id')}")
            
        except Exception as e:
            self.logger.error(f"API 호출 정보 처리 실패: {e}")
    
    def process_api_response_data(self, data: Dict[str, Any]):
        """API 응답 데이터 처리"""
        try:
            self.api_service.save_response_data(data)
            self.logger.info(f"API 응답 데이터 저장 완료: {data.get('inspection_id')}")
            
        except Exception as e:
            self.logger.error(f"API 응답 데이터 처리 실패: {e}")
    
    def start(self):
        """MQTT 브로커 연결 및 서비스 시작"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            self.logger.info("MQTT 검사 결과 수신 서비스가 시작되었습니다.")
            
        except Exception as e:
            self.logger.error(f"MQTT 서비스 시작 실패: {e}")
    
    def stop(self):
        """MQTT 서비스 중지"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.logger.info("MQTT 검사 결과 수신 서비스가 중지되었습니다.")
            
        except Exception as e:
            self.logger.error(f"MQTT 서비스 중지 실패: {e}")

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # MQTT 수신 서비스 시작
    receiver = MQTTInspectionReceiver()
    
    try:
        receiver.start()
        
        # 서비스 유지
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n서비스를 종료합니다...")
        receiver.stop() 