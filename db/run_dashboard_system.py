#!/usr/bin/env python3
"""
Dashboard 시스템 실행 스크립트

MQTT 리시버와 Dashboard API 서버를 동시에 실행합니다.
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def run_command(command, name, cwd=None):
    """명령어를 실행하고 프로세스 정보를 반환합니다."""
    try:
        print(f"🚀 {name} 시작 중...")
        print(f"   명령어: {command}")
        print(f"   작업 디렉토리: {cwd or '현재 디렉토리'}")
        
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ {name} 시작 완료 (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ {name} 시작 실패: {e}")
        return None

def stop_process(process, name):
    """프로세스를 안전하게 종료합니다."""
    if process and process.poll() is None:
        print(f"🛑 {name} 종료 중... (PID: {process.pid})")
        try:
            process.terminate()
            process.wait(timeout=5)
            print(f"✅ {name} 종료 완료")
        except subprocess.TimeoutExpired:
            print(f"⚠️  {name} 강제 종료 중...")
            process.kill()
            process.wait()
            print(f"✅ {name} 강제 종료 완료")
        except Exception as e:
            print(f"❌ {name} 종료 실패: {e}")

def main():
    """메인 실행 함수"""
    print("🎯 Dashboard 시스템 시작")
    print("=" * 50)
    
    # 현재 스크립트 위치
    current_dir = Path(__file__).parent
    print(f"📁 작업 디렉토리: {current_dir}")
    
    # 필요한 Python 패키지 확인
    required_packages = ['flask', 'flask-cors', 'pymysql']
    print("\n📦 필요한 Python 패키지 확인 중...")
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - 설치 필요: pip install {package}")
            return
    
    # 프로세스 목록
    processes = []
    
    try:
        # 1. MQTT 리시버 시작
        mqtt_receiver_cmd = "python run_mqtt_receiver.py"
        mqtt_process = run_command(mqtt_receiver_cmd, "MQTT 리시버", current_dir)
        if mqtt_process:
            processes.append(("MQTT 리시버", mqtt_process))
        
        # 잠시 대기
        time.sleep(3)
        
        # 2. Dashboard API 서버 시작
        dashboard_api_cmd = "python dashboard_api_server.py"
        api_process = run_command(dashboard_api_cmd, "Dashboard API 서버", current_dir)
        if api_process:
            processes.append(("Dashboard API 서버", api_process))
        
        print("\n🎉 모든 서비스가 시작되었습니다!")
        print("=" * 50)
        print("📊 Dashboard: http://localhost:3000")
        print("🔌 MQTT 리시버: localhost:8883")
        print("🌐 API 서버: http://localhost:8000")
        print("📋 API 헬스체크: http://localhost:8000/api/dashboard/health")
        print("\n💡 사용 방법:")
        print("   1. MQTT 리시버가 데이터를 수신합니다")
        print("   2. Dashboard API 서버가 데이터를 제공합니다")
        print("   3. React Dashboard에서 데이터를 시각화합니다")
        print("\n⏹️  종료하려면 Ctrl+C를 누르세요")
        
        # 프로세스 모니터링
        while True:
            time.sleep(1)
            
            # 프로세스 상태 확인
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name}가 예기치 않게 종료되었습니다")
                    return
            
    except KeyboardInterrupt:
        print("\n\n🛑 사용자에 의해 종료 요청됨")
    except Exception as e:
        print(f"\n❌ 예기치 않은 오류: {e}")
    finally:
        print("\n🔄 서비스 종료 중...")
        
        # 모든 프로세스 종료
        for name, process in processes:
            stop_process(process, name)
        
        print("✅ 모든 서비스가 종료되었습니다")

if __name__ == "__main__":
    main()
