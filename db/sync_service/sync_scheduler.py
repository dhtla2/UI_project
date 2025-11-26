#!/usr/bin/env python3
"""
동기화 스케줄링 서비스

API 동기화를 주기적으로 실행하고 관리합니다.
"""

import logging
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import schedule

from api_sync_service import api_sync_service
from endpoint_mapper import endpoint_mapper

logger = logging.getLogger(__name__)

class SyncScheduler:
    """동기화 스케줄링 관리"""
    
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        self.scheduled_jobs = {}
        self.sync_history = []
        
        # 기본 스케줄 설정
        self.default_schedules = {
            "high_priority": {
                "interval": "1h",  # 1시간마다
                "description": "높은 우선순위 API 동기화"
            },
            "medium_priority": {
                "interval": "2h",  # 2시간마다
                "description": "중간 우선순위 API 동기화"
            },
            "low_priority": {
                "interval": "6h",  # 6시간마다
                "description": "낮은 우선순위 API 동기화"
            },
            "daily_full_sync": {
                "interval": "1d",  # 매일
                "time": "02:00",   # 새벽 2시
                "description": "전체 API 일일 동기화"
            },
            "weekly_cleanup": {
                "interval": "1w",  # 매주
                "day": "sunday",   # 일요일
                "time": "03:00",   # 새벽 3시
                "description": "주간 데이터 정리"
            }
        }
    
    def start_scheduler(self) -> bool:
        """스케줄러 시작"""
        try:
            if self.is_running:
                logger.warning("⚠️ 스케줄러가 이미 실행 중입니다")
                return True
            
            self.is_running = True
            
            # 기본 스케줄 등록
            self._setup_default_schedules()
            
            # 스케줄러 스레드 시작
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("🚀 동기화 스케줄러 시작")
            return True
            
        except Exception as e:
            logger.error(f"❌ 스케줄러 시작 실패: {e}")
            self.is_running = False
            return False
    
    def stop_scheduler(self) -> bool:
        """스케줄러 중지"""
        try:
            if not self.is_running:
                logger.warning("⚠️ 스케줄러가 이미 중지되었습니다")
                return True
            
            self.is_running = False
            
            # 모든 스케줄된 작업 제거
            schedule.clear()
            self.scheduled_jobs.clear()
            
            logger.info("🛑 동기화 스케줄러 중지")
            return True
            
        except Exception as e:
            logger.error(f"❌ 스케줄러 중지 실패: {e}")
            return False
    
    def _run_scheduler(self):
        """스케줄러 실행 루프"""
        logger.info("🔄 스케줄러 실행 루프 시작")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)  # 1초마다 체크
            except Exception as e:
                logger.error(f"❌ 스케줄러 실행 중 오류: {e}")
                time.sleep(5)  # 오류 발생 시 5초 대기
        
        logger.info("🔄 스케줄러 실행 루프 종료")
    
    def _setup_default_schedules(self):
        """기본 스케줄 설정"""
        try:
            # 우선순위별 동기화 스케줄
            schedule.every(1).hours.do(self._sync_high_priority).tag("high_priority")
            schedule.every(2).hours.do(self._sync_medium_priority).tag("medium_priority")
            schedule.every(6).hours.do(self._sync_low_priority).tag("low_priority")
            
            # 일일 전체 동기화
            schedule.every().day.at("02:00").do(self._daily_full_sync).tag("daily_full_sync")
            
            # 주간 데이터 정리
            schedule.every().sunday.at("03:00").do(self._weekly_cleanup).tag("weekly_cleanup")
            
            logger.info("✅ 기본 스케줄 설정 완료")
            
        except Exception as e:
            logger.error(f"❌ 기본 스케줄 설정 실패: {e}")
    
    def _sync_high_priority(self):
        """높은 우선순위 API 동기화"""
        try:
            logger.info("🎯 높은 우선순위 API 동기화 시작 (스케줄)")
            sync_id = api_sync_service.sync_by_priority("high")
            if sync_id:
                self._record_sync_history("high_priority", sync_id, "success")
            else:
                self._record_sync_history("high_priority", None, "failed")
        except Exception as e:
            logger.error(f"❌ 높은 우선순위 동기화 실패: {e}")
            self._record_sync_history("high_priority", None, "error", str(e))
    
    def _sync_medium_priority(self):
        """중간 우선순위 API 동기화"""
        try:
            logger.info("🎯 중간 우선순위 API 동기화 시작 (스케줄)")
            sync_id = api_sync_service.sync_by_priority("medium")
            if sync_id:
                self._record_sync_history("medium_priority", sync_id, "success")
            else:
                self._record_sync_history("medium_priority", None, "failed")
        except Exception as e:
            logger.error(f"❌ 중간 우선순위 동기화 실패: {e}")
            self._record_sync_history("medium_priority", None, "error", str(e))
    
    def _sync_low_priority(self):
        """낮은 우선순위 API 동기화"""
        try:
            logger.info("🎯 낮은 우선순위 API 동기화 시작 (스케줄)")
            sync_id = api_sync_service.sync_by_priority("low")
            if sync_id:
                self._record_sync_history("low_priority", sync_id, "success")
            else:
                self._record_sync_history("low_priority", None, "failed")
        except Exception as e:
            logger.error(f"❌ 낮은 우선순위 동기화 실패: {e}")
            self._record_sync_history("low_priority", None, "error", str(e))
    
    def _daily_full_sync(self):
        """일일 전체 API 동기화"""
        try:
            logger.info("🌅 일일 전체 API 동기화 시작 (스케줄)")
            sync_id = api_sync_service.start_sync()
            if sync_id:
                self._record_sync_history("daily_full_sync", sync_id, "success")
            else:
                self._record_sync_history("daily_full_sync", None, "failed")
        except Exception as e:
            logger.error(f"❌ 일일 전체 동기화 실패: {e}")
            self._record_sync_history("daily_full_sync", None, "error", str(e))
    
    def _weekly_cleanup(self):
        """주간 데이터 정리"""
        try:
            logger.info("🧹 주간 데이터 정리 시작 (스케줄)")
            success = api_sync_service.cleanup_old_data(days=30)
            if success:
                self._record_sync_history("weekly_cleanup", None, "success")
            else:
                self._record_sync_history("weekly_cleanup", None, "failed")
        except Exception as e:
            logger.error(f"❌ 주간 데이터 정리 실패: {e}")
            self._record_sync_history("weekly_cleanup", None, "error", str(e))
    
    def _record_sync_history(self, schedule_type: str, sync_id: str, 
                           status: str, error_message: str = None):
        """동기화 히스토리 기록"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "schedule_type": schedule_type,
            "sync_id": sync_id,
            "status": status,
            "error_message": error_message
        }
        
        self.sync_history.append(history_entry)
        
        # 히스토리 크기 제한 (최근 1000개만 유지)
        if len(self.sync_history) > 1000:
            self.sync_history = self.sync_history[-1000:]
    
    def add_custom_schedule(self, name: str, interval: str, 
                          func: Callable, description: str = "") -> bool:
        """
        사용자 정의 스케줄 추가
        
        Args:
            name: 스케줄 이름
            interval: 간격 (예: "1h", "30m", "1d")
            func: 실행할 함수
            description: 설명
            
        Returns:
            성공 여부
        """
        try:
            # 간격 파싱 및 스케줄 등록
            if interval.endswith('m'):  # 분
                minutes = int(interval[:-1])
                schedule.every(minutes).minutes.do(func).tag(name)
            elif interval.endswith('h'):  # 시간
                hours = int(interval[:-1])
                schedule.every(hours).hours.do(func).tag(name)
            elif interval.endswith('d'):  # 일
                days = int(interval[:-1])
                schedule.every(days).days.do(func).tag(name)
            else:
                logger.error(f"❌ 지원하지 않는 간격 형식: {interval}")
                return False
            
            # 스케줄 정보 저장
            self.scheduled_jobs[name] = {
                "interval": interval,
                "description": description,
                "function": func.__name__,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ 사용자 정의 스케줄 추가: {name} ({interval})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 사용자 정의 스케줄 추가 실패: {e}")
            return False
    
    def remove_schedule(self, name: str) -> bool:
        """스케줄 제거"""
        try:
            if name in self.scheduled_jobs:
                schedule.clear(name)
                del self.scheduled_jobs[name]
                logger.info(f"✅ 스케줄 제거: {name}")
                return True
            else:
                logger.warning(f"⚠️ 존재하지 않는 스케줄: {name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 스케줄 제거 실패: {e}")
            return False
    
    def get_schedule_status(self) -> Dict[str, Any]:
        """스케줄 상태 조회"""
        try:
            # 기본 스케줄 상태
            default_status = {}
            for schedule_name, schedule_info in self.default_schedules.items():
                default_status[schedule_name] = {
                    "interval": schedule_info["interval"],
                    "description": schedule_info["description"],
                    "status": "active"
                }
            
            # 사용자 정의 스케줄 상태
            custom_status = {}
            for name, info in self.scheduled_jobs.items():
                custom_status[name] = {
                    "interval": info["interval"],
                    "description": info["description"],
                    "function": info["function"],
                    "created_at": info["created_at"],
                    "status": "active"
                }
            
            # 다음 실행 시간 계산
            next_run_times = {}
            for job in schedule.jobs:
                if hasattr(job, 'next_run'):
                    next_run_times[job.tags[0] if job.tags else "unknown"] = job.next_run.isoformat()
            
            return {
                "scheduler_running": self.is_running,
                "default_schedules": default_status,
                "custom_schedules": custom_status,
                "next_run_times": next_run_times,
                "total_scheduled_jobs": len(schedule.jobs)
            }
            
        except Exception as e:
            logger.error(f"❌ 스케줄 상태 조회 실패: {e}")
            return {"error": str(e)}
    
    def get_sync_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """동기화 히스토리 조회"""
        try:
            if limit <= 0:
                return self.sync_history
            else:
                return self.sync_history[-limit:]
        except Exception as e:
            logger.error(f"❌ 동기화 히스토리 조회 실패: {e}")
            return []
    
    def run_manual_sync(self, sync_type: str = "full") -> str:
        """수동 동기화 실행"""
        try:
            logger.info(f"🖱️ 수동 동기화 실행: {sync_type}")
            
            if sync_type == "full":
                sync_id = api_sync_service.start_sync()
            elif sync_type == "high":
                sync_id = api_sync_service.sync_by_priority("high")
            elif sync_type == "medium":
                sync_id = api_sync_service.sync_by_priority("medium")
            elif sync_type == "low":
                sync_id = api_sync_service.sync_by_priority("low")
            else:
                logger.error(f"❌ 지원하지 않는 동기화 타입: {sync_type}")
                return None
            
            if sync_id:
                self._record_sync_history(f"manual_{sync_type}", sync_id, "success")
                logger.info(f"✅ 수동 동기화 완료: {sync_id}")
            else:
                self._record_sync_history(f"manual_{sync_type}", None, "failed")
                logger.error("❌ 수동 동기화 실패")
            
            return sync_id
            
        except Exception as e:
            logger.error(f"❌ 수동 동기화 실행 실패: {e}")
            self._record_sync_history(f"manual_{sync_type}", None, "error", str(e))
            return None

# 싱글톤 인스턴스
sync_scheduler = SyncScheduler()
