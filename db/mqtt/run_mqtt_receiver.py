#!/usr/bin/env python3
"""
MQTT 수신 서비스 실행 스크립트

이 스크립트는 MQTT 검사 결과 수신 서비스를 실행하고 관리합니다.
서비스는 백그라운드에서 실행되며, 시그널을 통해 안전하게 종료할 수 있습니다.

주요 기능:
- MQTT 수신 서비스 시작/중지
- 로깅 설정 및 관리
- 시그널 핸들링 (SIGINT, SIGTERM)
- 서비스 상태 모니터링

실행 방법:
    python run_mqtt_receiver.py

종료 방법:
    Ctrl+C 또는 kill 명령어
"""

import sys
import os
import logging
import signal
import time

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mqtt.mqtt_receiver import MQTTInspectionReceiver
from mqtt.mqtt_config import get_logging_config, get_broker_config, get_tls_config

class MQTTReceiverService:
    """
    MQTT 수신 서비스 관리 클래스
    
    이 클래스는 MQTT 수신 서비스의 생명주기를 관리하고,
    설정 로딩, 로깅 설정, 시그널 처리를 담당합니다.
    
    Attributes:
        receiver (MQTTInspectionReceiver): MQTT 수신 서비스 인스턴스
        running (bool): 서비스 실행 상태
        broker_config (Dict): 브로커 설정
        logging_config (Dict): 로깅 설정
        logger (logging.Logger): 로깅 인스턴스
    """
    
    def __init__(self):
        """
        MQTT 수신 서비스 관리자 초기화
        
        설정을 로드하고 로깅을 설정하며, 시그널 핸들러를 등록합니다.
        """
        # 서비스 인스턴스 및 상태
        self.receiver = None
        self.running = False
        
        # 설정 파일에서 설정 로드
        self.broker_config = get_broker_config()    # 브로커 설정
        self.logging_config = get_logging_config()  # 로깅 설정
        self.tls_config = get_tls_config()  # TLS 설정 가져오기
        
        # 로깅 시스템 설정
        self._setup_logging()
        
        # 시그널 핸들러 등록 (안전한 종료를 위해)
        signal.signal(signal.SIGINT, self._signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, self._signal_handler)  # kill 명령어
    
    def _setup_logging(self):
        """로깅 설정"""
        log_level = getattr(logging, self.logging_config['level'])
        
        # 기본 로깅 설정
        logging.basicConfig(
            level=log_level,
            format=self.logging_config['format'],
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('mqtt_receiver.log') if self.logging_config['file'] else logging.NullHandler()
            ]
        )
        
        self.logger = logging.getLogger("mqtt_service")
        self.logger.info("MQTT 수신 서비스 로깅이 설정되었습니다.")
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        self.logger.info(f"시그널 {signum} 수신, 서비스를 종료합니다...")
        self.stop()
    
    def start(self):
        """MQTT 수신 서비스 시작"""
        try:
            self.logger.info("MQTT 수신 서비스를 시작합니다...")
            
            # MQTT 수신 서비스 생성
            self.receiver = MQTTInspectionReceiver(
                broker_host=self.broker_config['host'],
                broker_port=self.broker_config['port'],
                tls_config=self.tls_config  # TLS 설정을 인자로 전달
            )
            
            # 서비스 시작
            self.receiver.start()
            self.running = True
            
            self.logger.info("MQTT 수신 서비스가 성공적으로 시작되었습니다.")
            self.logger.info(f"브로커: {self.broker_config['host']}:{self.broker_config['port']}")
            
            # 서비스 유지
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("키보드 인터럽트로 서비스를 종료합니다...")
        except Exception as e:
            self.logger.error(f"서비스 시작 중 오류 발생: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """MQTT 수신 서비스 중지"""
        if self.running:
            self.logger.info("MQTT 수신 서비스를 중지합니다...")
            self.running = False
            
            if self.receiver:
                self.receiver.stop()
            
            self.logger.info("MQTT 수신 서비스가 중지되었습니다.")

def main():
    """메인 함수"""
    print("🚀 MQTT 검사 결과 수신 서비스")
    print("=" * 50)
    
    # 서비스 생성 및 시작
    service = MQTTReceiverService()
    service.start()

if __name__ == "__main__":
    main() 