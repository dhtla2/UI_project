#!/usr/bin/env python3
"""
API 동기화 서비스 실행 스크립트

사용법:
    python run_sync_service.py [옵션]

옵션:
    --start-scheduler     스케줄러 시작
    --stop-scheduler      스케줄러 중지
    --manual-sync         수동 동기화 실행
    --sync-type TYPE      동기화 타입 (full, high, medium, low)
    --status              서비스 상태 조회
    --history             동기화 히스토리 조회
    --cleanup DAYS        오래된 데이터 정리 (기본: 30일)
    --endpoint NAME       특정 엔드포인트만 동기화
    --priority PRIORITY   우선순위별 동기화 (high, medium, low)
    --category CATEGORY   카테고리별 동기화
    --help               도움말 표시

예시:
    python run_sync_service.py --start-scheduler
    python run_sync_service.py --manual-sync --sync-type high
    python run_sync_service.py --endpoint tc_work_info
    python run_sync_service.py --priority high
    python run_sync_service.py --category work_info
"""

import sys
import os
import logging
import argparse
from datetime import datetime

# sync_service 패키지 import
sys.path.append(os.path.join(os.path.dirname(__file__), 'sync_service'))

from sync_service import (
    api_sync_service, 
    sync_scheduler, 
    endpoint_mapper
)

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'sync_service_{datetime.now().strftime("%Y%m%d")}.log')
        ]
    )

def print_banner():
    """배너 출력"""
    print("=" * 70)
    print("🚀 API 동기화 서비스 (업데이트된 DB 구조)")
    print("=" * 70)
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 지원 엔드포인트: {len(endpoint_mapper.get_all_endpoints())}개")
    print(f"🗄️  대상 데이터베이스: port_database (Port 3307)")
    print(f"📊 업데이트된 테이블: 25개 (TC/QC/YT 작업정보 포함)")
    print("=" * 70)

def print_endpoint_info():
    """엔드포인트 정보 출력"""
    print("\n📋 지원하는 API 엔드포인트:")
    print("-" * 50)
    
    summary = endpoint_mapper.get_endpoint_summary()
    print(f"총 엔드포인트: {summary['total_endpoints']}개")
    
    print("\n🎯 우선순위별:")
    for priority, count in summary['priorities'].items():
        print(f"  {priority}: {count}개")
    
    print("\n📂 카테고리별:")
    for category, count in summary['categories'].items():
        print(f"  {category}: {count}개")
    
    print("\n⏰ 동기화 간격별:")
    for interval, count in summary['sync_intervals'].items():
        print(f"  {interval}초: {count}개")

def start_scheduler():
    """스케줄러 시작"""
    print("🚀 동기화 스케줄러 시작 중...")
    
    if sync_scheduler.start_scheduler():
        print("✅ 스케줄러가 성공적으로 시작되었습니다")
        print("\n📅 등록된 스케줄:")
        
        status = sync_scheduler.get_schedule_status()
        for schedule_name, schedule_info in status['default_schedules'].items():
            print(f"  • {schedule_name}: {schedule_info['interval']} - {schedule_info['description']}")
        
        print("\n💡 스케줄러를 중지하려면: python run_sync_service.py --stop-scheduler")
    else:
        print("❌ 스케줄러 시작 실패")

def stop_scheduler():
    """스케줄러 중지"""
    print("🛑 동기화 스케줄러 중지 중...")
    
    if sync_scheduler.stop_scheduler():
        print("✅ 스케줄러가 성공적으로 중지되었습니다")
    else:
        print("❌ 스케줄러 중지 실패")

def run_manual_sync(sync_type="full"):
    """수동 동기화 실행"""
    print(f"🖱️ 수동 동기화 실행: {sync_type}")
    
    if sync_type == "full":
        print("🎯 전체 API 엔드포인트 동기화 시작...")
        sync_id = api_sync_service.start_sync()
    elif sync_type in ["high", "medium", "low"]:
        print(f"🎯 {sync_type} 우선순위 API 동기화 시작...")
        sync_id = api_sync_service.sync_by_priority(sync_type)
    else:
        print(f"❌ 지원하지 않는 동기화 타입: {sync_type}")
        return
    
    if sync_id:
        print(f"✅ 동기화 완료: {sync_id}")
        
        # 동기화 상태 조회
        status = api_sync_service.get_sync_status()
        print(f"\n📊 동기화 결과:")
        print(f"  • 총 엔드포인트: {status.get('total_endpoints', 0)}개")
        print(f"  • 성공: {status.get('successful_syncs', 0)}개")
        print(f"  • 실패: {status.get('failed_syncs', 0)}개")
        print(f"  • 총 레코드: {status.get('total_records', 0)}개")
    else:
        print("❌ 동기화 실패")

def sync_single_endpoint(endpoint_name):
    """단일 엔드포인트 동기화"""
    if not endpoint_mapper.validate_endpoint(endpoint_name):
        print(f"❌ 유효하지 않은 엔드포인트: {endpoint_name}")
        print(f"💡 지원하는 엔드포인트: {', '.join(endpoint_mapper.get_all_endpoints())}")
        return
    
    print(f"🎯 단일 엔드포인트 동기화: {endpoint_name}")
    
    endpoint_info = endpoint_mapper.get_endpoint_info(endpoint_name)
    print(f"📋 엔드포인트 정보:")
    print(f"  • 테이블: {endpoint_info['table_name']}")
    print(f"  • 카테고리: {endpoint_info['category']}")
    print(f"  • 우선순위: {endpoint_info['priority']}")
    print(f"  • 동기화 간격: {endpoint_info['sync_interval']}초")
    print(f"  • 설명: {endpoint_info['description']}")
    
    sync_id = api_sync_service.sync_single_endpoint(endpoint_name)
    
    if sync_id:
        print(f"✅ 동기화 완료: {sync_id}")
    else:
        print("❌ 동기화 실패")

def sync_by_priority(priority):
    """우선순위별 동기화"""
    if priority not in ["high", "medium", "low"]:
        print(f"❌ 유효하지 않은 우선순위: {priority}")
        return
    
    endpoints = endpoint_mapper.get_endpoints_by_priority(priority)
    print(f"🎯 {priority} 우선순위 API 동기화 시작 ({len(endpoints)}개)")
    print(f"📋 대상 엔드포인트: {', '.join(endpoints)}")
    
    sync_id = api_sync_service.sync_by_priority(priority)
    
    if sync_id:
        print(f"✅ 동기화 완료: {sync_id}")
    else:
        print("❌ 동기화 실패")

def sync_by_category(category):
    """카테고리별 동기화"""
    endpoints = endpoint_mapper.get_endpoints_by_category(category)
    
    if not endpoints:
        print(f"❌ 해당 카테고리를 찾을 수 없음: {category}")
        print(f"💡 지원하는 카테고리: {', '.join(set([info['category'] for info in endpoint_mapper.api_table_mapping.values()]))}")
        return
    
    print(f"📂 {category} 카테고리 API 동기화 시작 ({len(endpoints)}개)")
    print(f"📋 대상 엔드포인트: {', '.join(endpoints)}")
    
    sync_id = api_sync_service.sync_by_category(category)
    
    if sync_id:
        print(f"✅ 동기화 완료: {sync_id}")
    else:
        print("❌ 동기화 실패")

def show_status():
    """서비스 상태 조회"""
    print("📊 서비스 상태 조회")
    print("-" * 30)
    
    # 스케줄러 상태
    scheduler_status = sync_scheduler.get_schedule_status()
    print(f"🔄 스케줄러 상태: {'실행 중' if scheduler_status['scheduler_running'] else '중지됨'}")
    print(f"📅 등록된 작업: {scheduler_status['total_scheduled_jobs']}개")
    
    # 동기화 서비스 상태
    if api_sync_service.current_sync_id:
        sync_status = api_sync_service.get_sync_status()
        print(f"\n🆔 현재 동기화 ID: {sync_status.get('sync_id', 'N/A')}")
        print(f"🔄 동기화 상태: {'실행 중' if sync_status.get('is_running', False) else '완료'}")
        print(f"📊 총 레코드: {sync_status.get('total_records', 0)}개")
    else:
        print("\n🆔 현재 동기화 ID: 없음")
    
    # 엔드포인트 요약
    print_endpoint_info()

def show_history(limit=20):
    """동기화 히스토리 조회"""
    print(f"📜 동기화 히스토리 (최근 {limit}개)")
    print("-" * 50)
    
    history = sync_scheduler.get_sync_history(limit)
    
    if not history:
        print("📝 동기화 히스토리가 없습니다")
        return
    
    for entry in reversed(history):
        timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        status_emoji = "✅" if entry['status'] == 'success' else "❌" if entry['status'] == 'failed' else "⚠️"
        
        print(f"{status_emoji} {timestamp} - {entry['schedule_type']}")
        if entry['sync_id']:
            print(f"   🆔 동기화 ID: {entry['sync_id']}")
        if entry['error_message']:
            print(f"   ❌ 오류: {entry['error_message']}")
        print()

def cleanup_old_data(days=30):
    """오래된 데이터 정리"""
    print(f"🧹 {days}일 이상 된 데이터 정리 시작...")
    
    success = api_sync_service.cleanup_old_data(days)
    
    if success:
        print("✅ 데이터 정리 완료")
    else:
        print("❌ 데이터 정리 실패")

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="API 동기화 서비스",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--start-scheduler', action='store_true', 
                       help='동기화 스케줄러 시작')
    parser.add_argument('--stop-scheduler', action='store_true', 
                       help='동기화 스케줄러 중지')
    parser.add_argument('--manual-sync', action='store_true', 
                       help='수동 동기화 실행')
    parser.add_argument('--sync-type', choices=['full', 'high', 'medium', 'low'], 
                       default='full', help='동기화 타입 (기본: full)')
    parser.add_argument('--status', action='store_true', 
                       help='서비스 상태 조회')
    parser.add_argument('--history', action='store_true', 
                       help='동기화 히스토리 조회')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', 
                       help='오래된 데이터 정리 (기본: 30일)')
    parser.add_argument('--endpoint', type=str, metavar='NAME', 
                       help='특정 엔드포인트만 동기화')
    parser.add_argument('--priority', choices=['high', 'medium', 'low'], 
                       help='우선순위별 동기화')
    parser.add_argument('--category', type=str, 
                       help='카테고리별 동기화')
    
    args = parser.parse_args()
    
    # 로깅 설정
    setup_logging()
    
    # 배너 출력
    print_banner()
    
    try:
        if args.start_scheduler:
            start_scheduler()
        elif args.stop_scheduler:
            stop_scheduler()
        elif args.manual_sync:
            run_manual_sync(args.sync_type)
        elif args.status:
            show_status()
        elif args.history:
            show_history()
        elif args.cleanup is not None:
            cleanup_old_data(args.cleanup)
        elif args.endpoint:
            sync_single_endpoint(args.endpoint)
        elif args.priority:
            sync_by_priority(args.priority)
        elif args.category:
            sync_by_category(args.category)
        else:
            # 기본 동작: 도움말 및 상태 표시
            print("\n💡 사용법:")
            print("  python run_sync_service.py --help")
            print("\n📊 현재 상태:")
            show_status()
            
    except KeyboardInterrupt:
        print("\n\n🛑 사용자에 의해 중단되었습니다")
        if sync_scheduler.is_running:
            print("🔄 스케줄러를 중지합니다...")
            sync_scheduler.stop_scheduler()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        logging.error(f"오류 발생: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
