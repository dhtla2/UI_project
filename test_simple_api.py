#!/usr/bin/env python3
"""
간단한 API 테스트 스크립트
엔드포인트가 제대로 등록되었는지 확인합니다.
"""

import requests
import json

def test_simple_api():
    """간단한 API 테스트"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 간단한 API 테스트 시작...\n")
    
    # 1. 루트 엔드포인트 테스트
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ 루트 엔드포인트: {response.status_code}")
        print(f"   응답: {response.json()}")
    except Exception as e:
        print(f"❌ 루트 엔드포인트 실패: {e}")
        return
    
    print("\n" + "="*50 + "\n")
    
    # 2. 시간별 통계 엔드포인트 테스트
    try:
        print("시간별 통계 엔드포인트 테스트 중...")
        response = requests.get(f"{base_url}/ui/statistics/time-based?period=daily&days=30")
        print(f"✅ 시간별 통계 엔드포인트: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   오류 응답: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드 서버에 연결할 수 없습니다.")
        print("   백엔드 서버가 실행 중인지 확인해주세요.")
        print("   실행 명령: cd backend && python main.py")
    except Exception as e:
        print(f"❌ 시간별 통계 엔드포인트 실패: {e}")
    
    print("\n" + "="*50)
    print("🎯 테스트 완료!")

if __name__ == "__main__":
    test_simple_api() 