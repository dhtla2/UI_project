#!/usr/bin/env python3
"""
DB 동기화 서비스 실행 스크립트

사용법:
    python run_sync.py --mode [manual|scheduler]
    python run_sync.py --manual --type [full|high|medium|low]
    python run_sync.py --scheduler
"""

import sys
import os
import logging
import argparse
from datetime import datetime

# 현재 디렉토리를 path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 부모 디렉토리도 추가 (db/)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from api_sync_service import api_sync_service
from sync_scheduler import sync_scheduler
from sync_config import sync_config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sync_service.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def run_manual_sync(sync_type: str = "full"):
    """수동 동기화 실행"""
    logger.info("=" * 80)
    logger.info(f"🚀 수동 동기화 시작: {sync_type}")
    logger.info(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    try:
        # 설정 유효성 검증
        if not sync_config.validate_config():
            logger.error("❌ 설정 유효성 검증 실패")
            return False
        
        # DB 설정 출력
        db_config = sync_config.get_database_config()
        logger.info(f"📊 DB: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        # 동기화 실행
        if sync_type == "full":
            logger.info("🎯 전체 동기화 실행")
            sync_id = api_sync_service.start_sync()
        elif sync_type in ["high", "medium", "low"]:
            logger.info(f"🎯 우선순위별 동기화 실행: {sync_type}")
            sync_id = api_sync_service.sync_by_priority(sync_type)
        else:
            logger.error(f"❌ 지원하지 않는 동기화 타입: {sync_type}")
            return False
        
        # 결과 출력
        if sync_id:
            logger.info("=" * 80)
            logger.info(f"✅ 동기화 완료!")
            logger.info(f"📋 Sync ID: {sync_id}")
            logger.info(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)
            
            # 통계 출력
            stats = api_sync_service.get_sync_statistics(sync_id)
            if stats:
                logger.info("📈 동기화 통계:")
                logger.info(f"  - 전체 엔드포인트: {stats.get('total_endpoints', 0)}")
                logger.info(f"  - 성공: {stats.get('successful_syncs', 0)}")
                logger.info(f"  - 실패: {stats.get('failed_syncs', 0)}")
                logger.info(f"  - 소요 시간: {stats.get('duration_seconds', 0):.2f}초")
            
            return True
        else:
            logger.error("=" * 80)
            logger.error("❌ 동기화 실패")
            logger.error(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.error("=" * 80)
            return False
            
    except Exception as e:
        logger.error(f"❌ 동기화 중 오류 발생: {e}", exc_info=True)
        return False

def run_scheduler():
    """스케줄러 실행"""
    logger.info("=" * 80)
    logger.info("🚀 동기화 스케줄러 시작")
    logger.info(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    try:
        # 설정 유효성 검증
        if not sync_config.validate_config():
            logger.error("❌ 설정 유효성 검증 실패")
            return False
        
        # DB 설정 출력
        db_config = sync_config.get_database_config()
        logger.info(f"📊 DB: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        # 스케줄러 설정 출력
        scheduler_config = sync_config.get_scheduler_config()
        logger.info(f"⏱️  체크 간격: {scheduler_config['check_interval']}초")
        logger.info(f"📋 최대 히스토리: {scheduler_config['max_history']}개")
        
        # 스케줄러 시작
        if sync_scheduler.start_scheduler():
            logger.info("✅ 스케줄러 시작 완료")
            logger.info("=" * 80)
            logger.info("📅 스케줄 정보:")
            logger.info("  - 높은 우선순위: 1시간마다")
            logger.info("  - 중간 우선순위: 2시간마다")
            logger.info("  - 낮은 우선순위: 6시간마다")
            logger.info("  - 전체 동기화: 매일 새벽 2시")
            logger.info("  - 데이터 정리: 매주 일요일 새벽 3시")
            logger.info("=" * 80)
            logger.info("💡 Ctrl+C를 눌러 중지할 수 있습니다")
            logger.info("=" * 80)
            
            # 무한 대기 (Ctrl+C로 종료)
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("\n🛑 종료 신호 수신")
                sync_scheduler.stop_scheduler()
                logger.info("✅ 스케줄러 정상 종료")
                return True
        else:
            logger.error("❌ 스케줄러 시작 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ 스케줄러 실행 중 오류 발생: {e}", exc_info=True)
        return False

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='DB 동기화 서비스 실행',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # 모드 선택
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--manual',
        action='store_true',
        help='수동 동기화 실행 (1회)'
    )
    group.add_argument(
        '--scheduler',
        action='store_true',
        help='스케줄러 실행 (계속 실행)'
    )
    
    # 수동 동기화 타입
    parser.add_argument(
        '--type',
        choices=['full', 'high', 'medium', 'low'],
        default='full',
        help='동기화 타입 (기본값: full)\n'
             '  - full: 전체 동기화\n'
             '  - high: 높은 우선순위만\n'
             '  - medium: 중간 우선순위만\n'
             '  - low: 낮은 우선순위만'
    )
    
    # 설정 파일
    parser.add_argument(
        '--config',
        type=str,
        help='설정 파일 경로 (선택)'
    )
    
    args = parser.parse_args()
    
    # 설정 파일 로드
    if args.config:
        if not sync_config.load_config(args.config):
            logger.warning(f"⚠️ 설정 파일 로드 실패, 기본 설정 사용: {args.config}")
    
    # 모드에 따라 실행
    if args.manual:
        success = run_manual_sync(args.type)
        sys.exit(0 if success else 1)
    elif args.scheduler:
        success = run_scheduler()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

