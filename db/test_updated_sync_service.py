#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
업데이트된 DB 구조에 맞는 동기화 서비스 테스트 스크립트
"""

import sys
import os
import logging
from datetime import datetime

# sync_service 패키지 import
sys.path.append(os.path.join(os.path.dirname(__file__), 'sync_service'))

from sync_service import db_sync_manager, endpoint_mapper

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'test_sync_service_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
        ]
    )

def test_db_connection():
    """DB 연결 테스트"""
    print("🔌 DB 연결 테스트 중...")
    
    try:
        db_manager = db_sync_manager.DBSyncManager()
        if db_manager.connect():
            print("✅ DB 연결 성공")
            
            # 테이블 존재 여부 확인
            print("\n📋 테이블 존재 여부 확인:")
            for table in db_manager.all_tables:
                exists = db_manager.check_table_exists(table)
                status = "✅" if exists else "❌"
                print(f"  {status} {table}")
            
            db_manager.disconnect()
            return True
        else:
            print("❌ DB 연결 실패")
            return False
    except Exception as e:
        print(f"❌ DB 연결 테스트 중 오류: {e}")
        return False

def test_table_structures():
    """테이블 구조 테스트"""
    print("\n🏗️ 테이블 구조 테스트 중...")
    
    try:
        db_manager = db_sync_manager.DBSyncManager()
        if not db_manager.connect():
            print("❌ DB 연결 실패")
            return False
        
        print("\n📊 테이블별 컬럼 정보:")
        for table in db_manager.all_tables:
            if db_manager.check_table_exists(table):
                table_info = db_manager.get_table_info(table)
                if table_info:
                    print(f"\n📋 {table} ({table_info['column_count']}개 컬럼):")
                    for col in table_info['columns'][:5]:  # 처음 5개만 표시
                        print(f"    - {col['field']}: {col['type']}")
                    if table_info['column_count'] > 5:
                        print(f"    ... 외 {table_info['column_count'] - 5}개 컬럼")
                else:
                    print(f"❌ {table}: 테이블 정보 조회 실패")
            else:
                print(f"❌ {table}: 테이블이 존재하지 않음")
        
        db_manager.disconnect()
        return True
    except Exception as e:
        print(f"❌ 테이블 구조 테스트 중 오류: {e}")
        return False

def test_endpoint_mapping():
    """엔드포인트 매핑 테스트"""
    print("\n🎯 엔드포인트 매핑 테스트 중...")
    
    try:
        mapper = endpoint_mapper.EndpointMapper()
        endpoints = mapper.get_all_endpoints()
        
        print(f"📊 총 엔드포인트: {len(endpoints)}개")
        
        print("\n📋 엔드포인트별 매핑 정보:")
        for endpoint_name in endpoints:
            endpoint_info = mapper.get_endpoint_info(endpoint_name)
            if endpoint_info:
                print(f"\n🎯 {endpoint_name}:")
                print(f"    📊 테이블: {endpoint_info['table_name']}")
                print(f"    📂 카테고리: {endpoint_info['category']}")
                print(f"    ⭐ 우선순위: {endpoint_info['priority']}")
                print(f"    ⏰ 동기화 간격: {endpoint_info['sync_interval']}초")
                print(f"    🔗 API 경로: {endpoint_info.get('api_path', 'N/A')}")
                print(f"    📝 설명: {endpoint_info['description']}")
        
        return True
    except Exception as e:
        print(f"❌ 엔드포인트 매핑 테스트 중 오류: {e}")
        return False

def test_sample_data_insertion():
    """샘플 데이터 삽입 테스트"""
    print("\n📝 샘플 데이터 삽입 테스트 중...")
    
    try:
        db_manager = db_sync_manager.DBSyncManager()
        if not db_manager.connect():
            print("❌ DB 연결 실패")
            return False
        
        # TC 작업정보 샘플 데이터
        tc_sample_data = [
            {
                "tmnlId": "BPTS",
                "shpCd": "TEST",
                "callYr": "2025",
                "serNo": "001",
                "tcNo": "TEST001",
                "cntrNo": "TEST1234567",
                "tmnlNm": "테스트터미널",
                "shpNm": "테스트선박",
                "wkId": "양하",
                "jobNo": "JOB001",
                "szTp": "2200",
                "ytNo": "YT001",
                "rtNo": "RT001",
                "block": "A1",
                "bay": "1",
                "roww": "1",
                "ordTime": "20250101000000",
                "wkTime": "20250101000000",
                "jobState": "완료",
                "evntTime": "20250101000000"
            }
        ]
        
        # 테스트 데이터 삽입
        success = db_manager.insert_data("tc_work_info", tc_sample_data)
        if success:
            print("✅ TC 작업정보 샘플 데이터 삽입 성공")
            
            # 삽입된 데이터 확인
            count = db_manager.get_table_count("tc_work_info")
            print(f"📊 tc_work_info 테이블 레코드 수: {count}건")
        else:
            print("❌ TC 작업정보 샘플 데이터 삽입 실패")
        
        # 테스트 데이터 정리
        db_manager.execute_query("DELETE FROM tc_work_info WHERE shpCd = 'TEST'")
        print("🧹 테스트 데이터 정리 완료")
        
        db_manager.disconnect()
        return success
    except Exception as e:
        print(f"❌ 샘플 데이터 삽입 테스트 중 오류: {e}")
        return False

def test_sync_status():
    """동기화 상태 조회 테스트"""
    print("\n📊 동기화 상태 조회 테스트 중...")
    
    try:
        db_manager = db_sync_manager.DBSyncManager()
        if not db_manager.connect():
            print("❌ DB 연결 실패")
            return False
        
        # 동기화 상태 조회
        sync_status = db_manager.get_sync_status("test_sync_001")
        
        print(f"📊 동기화 상태:")
        print(f"    🆔 동기화 ID: {sync_status.get('sync_id', 'N/A')}")
        print(f"    📋 총 테이블: {sync_status.get('total_tables', 0)}개")
        print(f"    ✅ 동기화된 테이블: {sync_status.get('synced_tables', 0)}개")
        print(f"    📝 총 레코드: {sync_status.get('total_records', 0):,}건")
        
        print(f"\n📋 테이블별 상세 정보:")
        for table_name, table_info in sync_status.get('table_details', {}).items():
            status_emoji = "✅" if table_info.get('exists', False) else "❌"
            record_count = table_info.get('record_count', 0)
            print(f"    {status_emoji} {table_name}: {record_count:,}건")
        
        db_manager.disconnect()
        return True
    except Exception as e:
        print(f"❌ 동기화 상태 조회 테스트 중 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 업데이트된 DB 구조 동기화 서비스 테스트")
    print("=" * 60)
    
    setup_logging()
    
    test_results = []
    
    # 1. DB 연결 테스트
    test_results.append(("DB 연결", test_db_connection()))
    
    # 2. 테이블 구조 테스트
    test_results.append(("테이블 구조", test_table_structures()))
    
    # 3. 엔드포인트 매핑 테스트
    test_results.append(("엔드포인트 매핑", test_endpoint_mapping()))
    
    # 4. 샘플 데이터 삽입 테스트
    test_results.append(("샘플 데이터 삽입", test_sample_data_insertion()))
    
    # 5. 동기화 상태 조회 테스트
    test_results.append(("동기화 상태 조회", test_sync_status()))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    success_count = 0
    for test_name, result in test_results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n🎯 전체 테스트 결과: {success_count}/{len(test_results)} 성공")
    
    if success_count == len(test_results):
        print("🎉 모든 테스트가 성공했습니다!")
        print("💡 이제 run_sync_service.py를 사용하여 실제 동기화를 실행할 수 있습니다.")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 로그를 확인하세요.")
    
    return success_count == len(test_results)

if __name__ == "__main__":
    main()
