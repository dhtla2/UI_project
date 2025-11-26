"""Quality inspection service"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import logging
from services.database import db_service
from models.schemas import QualityCheckResult, QualityCheckHistory, FailedItemData, FailedItemsResponse

logger = logging.getLogger(__name__)

class DataQualityChecker:
    """데이터 품질 검사 클래스"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def check_completeness(self) -> Dict[str, Any]:
        """완전성 검사"""
        if self.data is None or self.data.empty:
            return {"pass_rate": 0, "total_checks": 0, "failed_checks": 0}
        
        total_checks = len(self.data.columns)
        failed_checks = self.data.isnull().sum().sum()
        pass_rate = ((total_checks - failed_checks) / total_checks * 100) if total_checks > 0 else 100
        
        return {
            "pass_rate": round(pass_rate, 1),
            "total_checks": total_checks,
            "failed_checks": failed_checks
        }
    
    def check_validity(self, rules: Dict[str, Any]) -> Dict[str, Any]:
        """유효성 검사"""
        if self.data is None or self.data.empty:
            return {"pass_rate": 0, "total_checks": 0, "failed_checks": 0}
        
        total_checks = 0
        failed_checks = 0
        
        if 'RANGE' in rules:
            for column, rule in rules['RANGE'].items():
                if column in self.data.columns:
                    total_checks += 1
                    if rule.get('rtype') == 'I':  # 정수형
                        try:
                            col_data = pd.to_numeric(self.data[column], errors='coerce')
                            val1 = rule.get('val1', 0)
                            val2 = rule.get('val2', 100)
                            invalid_count = ((col_data < val1) | (col_data > val2)).sum()
                            if invalid_count > 0:
                                failed_checks += 1
                        except:
                            failed_checks += 1
        
        pass_rate = ((total_checks - failed_checks) / total_checks * 100) if total_checks > 0 else 100
        
        return {
            "pass_rate": round(pass_rate, 1),
            "total_checks": total_checks,
            "failed_checks": failed_checks
        }
    
    def check_consistency(self, rules: Dict[str, Any]) -> Dict[str, Any]:
        """일관성 검사"""
        if self.data is None or self.data.empty:
            return {"pass_rate": 0, "total_checks": 0, "failed_checks": 0}
        
        total_checks = 0
        failed_checks = 0
        
        if 'DUPLICATE' in rules:
            for column in rules['DUPLICATE']:
                if column in self.data.columns:
                    total_checks += 1
                    if self.data[column].duplicated().any():
                        failed_checks += 1
        
        pass_rate = ((total_checks - failed_checks) / total_checks * 100) if total_checks > 0 else 100
        
        return {
            "pass_rate": round(pass_rate, 1),
            "total_checks": total_checks,
            "failed_checks": failed_checks
        }
    
    def check_usage(self, rules: Dict[str, Any]) -> Dict[str, Any]:
        """사용성 검사"""
        if self.data is None or self.data.empty:
            return {"pass_rate": 0, "total_checks": 0, "failed_checks": 0}
        
        total_checks = 0
        failed_checks = 0
        
        # 간단한 사용성 검사 (데이터가 실제로 사용되는지 확인)
        for column in self.data.columns:
            total_checks += 1
            if self.data[column].isnull().all():
                failed_checks += 1
        
        pass_rate = ((total_checks - failed_checks) / total_checks * 100) if total_checks > 0 else 100
        
        return {
            "pass_rate": round(pass_rate, 1),
            "total_checks": total_checks,
            "failed_checks": failed_checks
        }
    
    def check_timeliness(self, rules: Dict[str, Any]) -> Dict[str, Any]:
        """적시성 검사"""
        if self.data is None or self.data.empty:
            return {"pass_rate": 0, "total_checks": 0, "failed_checks": 0}
        
        total_checks = 0
        failed_checks = 0
        
        # 시간 관련 컬럼이 있는지 확인
        time_columns = [col for col in self.data.columns if 'time' in col.lower() or 'date' in col.lower()]
        for column in time_columns:
            total_checks += 1
            try:
                # 최근 데이터인지 확인 (예: 24시간 이내)
                if pd.api.types.is_datetime64_any_dtype(self.data[column]):
                    latest_time = pd.to_datetime(self.data[column]).max()
                    if (datetime.now() - latest_time).days > 1:
                        failed_checks += 1
            except:
                failed_checks += 1
        
        pass_rate = ((total_checks - failed_checks) / total_checks * 100) if total_checks > 0 else 100
        
        return {
            "pass_rate": round(pass_rate, 1),
            "total_checks": total_checks,
            "failed_checks": failed_checks
        }

class QualityService:
    """품질 검사 서비스"""
    
    def __init__(self):
        self.db_service = db_service
    
    def create_quality_check_tables(self):
        """품질 검사 관련 테이블 생성"""
        try:
            with self.db_service.get_mysql_connection() as conn:
                with conn.cursor() as cursor:
                    # 품질 검사 히스토리 테이블
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS quality_check_history (
                            id VARCHAR(100) PRIMARY KEY,
                            data_type VARCHAR(50) NOT NULL,
                            status VARCHAR(20) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            results JSON
                        )
                    """)
                    
                    # 데이터 검사 결과 테이블
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS data_inspection_results (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            inspection_id VARCHAR(100) NOT NULL,
                            check_name VARCHAR(100) NOT NULL,
                            check_type VARCHAR(50) NOT NULL,
                            status VARCHAR(10) NOT NULL,
                            message TEXT,
                            details TEXT,
                            affected_rows INT DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            INDEX idx_inspection_id (inspection_id),
                            INDEX idx_check_type (check_type),
                            INDEX idx_status (status)
                        )
                    """)
                    
                    conn.commit()
                    logger.info("품질 검사 테이블 생성 완료")
        except Exception as e:
            logger.error(f"품질 검사 테이블 생성 실패: {e}")
            raise
    
    def save_quality_check_result(self, inspection_id: str, check_name: str, 
                                 check_type: str, status: str, message: str = None,
                                 details: str = None, affected_rows: int = 0):
        """품질 검사 결과 저장"""
        try:
            query = """
                INSERT INTO data_inspection_results 
                (inspection_id, check_name, check_type, status, message, details, affected_rows)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (inspection_id, check_name, check_type, status, message, details, affected_rows)
            self.db_service.execute_query(query, params, fetch_all=False)
        except Exception as e:
            logger.error(f"품질 검사 결과 저장 실패: {e}")
            raise
    
    def get_failed_items(self, page: str) -> FailedItemsResponse:
        """실패/성공한 항목 조회"""
        try:
            # 페이지별 inspection_id 패턴 설정
            inspection_patterns = {
                'AIS': '%ais_info%',
                'TOS': '%berth_schedule%',
                'TC': '%tc%',
                'QC': '%qc_work%'
            }
            
            pattern = inspection_patterns.get(page, '%ais_info%')
            
            # 실패한 항목들 조회
            failed_query = """
                SELECT 
                    check_name,
                    check_type,
                    message,
                    details,
                    affected_rows,
                    created_at
                FROM data_inspection_results 
                WHERE inspection_id LIKE %s 
                AND status = 'FAIL'
                ORDER BY created_at DESC
                LIMIT 5
            """
            
            failed_rows = self.db_service.execute_query(failed_query, (pattern,))
            failed_items = []
            if failed_rows:
                for row in failed_rows:
                    failed_items.append(FailedItemData(
                        field=row[0],
                        reason="검사 실패",
                        message=row[2] or "상세 정보 없음",
                        details=row[3] or "",
                        affected_rows=row[4] or 0,
                        created_at=row[5].isoformat() if row[5] else None
                    ))
            
            # 성공한 항목들 조회
            success_query = """
                SELECT 
                    check_name,
                    check_type,
                    message,
                    details,
                    affected_rows,
                    created_at
                FROM data_inspection_results 
                WHERE inspection_id LIKE %s 
                AND status = 'PASS'
                ORDER BY created_at DESC
                LIMIT 5
            """
            
            success_rows = self.db_service.execute_query(success_query, (pattern,))
            success_items = []
            if success_rows:
                for row in success_rows:
                    success_items.append(FailedItemData(
                        field=row[0],
                        reason="검사 통과",
                        message=row[2] or "검사 통과",
                        details=row[3] or "",
                        affected_rows=row[4] or 0,
                        created_at=row[5].isoformat() if row[5] else None
                    ))
            
            return FailedItemsResponse(
                failed_items=failed_items,
                success_items=success_items,
                page=page
            )
            
        except Exception as e:
            logger.error(f"실패한 항목 조회 실패: {e}")
            raise
    
    def get_latest_inspection_results(self, page: str) -> Dict[str, Any]:
        """최신 검사 결과 조회"""
        try:
            # 페이지별 inspection_id 패턴 설정
            inspection_patterns = {
                'AIS': '%ais_info%',
                'TOS': '%berth_schedule%',
                'TC': '%tc%',
                'QC': '%qc_work%'
            }
            
            pattern = inspection_patterns.get(page, '%ais_info%')
            
            # 최신 검사 ID와 시간 조회
            latest_query = """
                SELECT inspection_id, MAX(created_at) as latest_time
                FROM data_inspection_results 
                WHERE inspection_id LIKE %s 
                GROUP BY inspection_id
                ORDER BY latest_time DESC 
                LIMIT 1
            """
            
            latest_inspection = self.db_service.execute_query(latest_query, (pattern,), fetch_one=True)
            if not latest_inspection:
                return {
                    "completeness": {"pass_rate": 0, "total_checks": 0, "pass_count": 0, "fail_count": 0, "fields_checked": 0, "last_updated": None},
                    "validity": {"pass_rate": 0, "total_checks": 0, "pass_count": 0, "fail_count": 0, "fields_checked": 0, "last_updated": None}
                }
            
            latest_inspection_id = latest_inspection[0]
            latest_time = latest_inspection[1]
            
            # 완전성 검사 결과
            completeness_query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail
                FROM data_inspection_results 
                WHERE inspection_id = %s AND check_type = 'completeness'
            """
            
            completeness = self.db_service.execute_query(completeness_query, (latest_inspection_id,), fetch_one=True)
            comp_total = completeness[0] if completeness[0] else 0
            comp_pass = completeness[1] if completeness[1] else 0
            comp_fail = completeness[2] if completeness[2] else 0
            comp_pass_rate = (comp_pass / comp_total * 100) if comp_total > 0 else 0
            
            # 유효성 검사 결과
            validity_query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass,
                    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail
                FROM data_inspection_results 
                WHERE inspection_id = %s AND check_type = 'validity'
            """
            
            validity = self.db_service.execute_query(validity_query, (latest_inspection_id,), fetch_one=True)
            val_total = validity[0] if validity[0] else 0
            val_pass = validity[1] if validity[1] else 0
            val_fail = validity[2] if validity[2] else 0
            val_pass_rate = (val_pass / val_total * 100) if val_total > 0 else 0
            
            result = {
                "completeness": {
                    "pass_rate": round(comp_pass_rate, 1),
                    "total_checks": comp_total,
                    "pass_count": comp_pass,
                    "fail_count": comp_fail,
                    "fields_checked": comp_total,
                    "last_updated": latest_time.isoformat() if latest_time else None
                },
                "validity": {
                    "pass_rate": round(val_pass_rate, 1),
                    "total_checks": val_total,
                    "pass_count": val_pass,
                    "fail_count": val_fail,
                    "fields_checked": val_total,
                    "last_updated": latest_time.isoformat() if latest_time else None
                }
            }
            
            # TC 페이지인 경우 usage 데이터 추가
            if page == 'TC':
                usage_query = """
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as pass,
                        SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as fail
                    FROM data_inspection_results 
                    WHERE inspection_id = %s AND check_type = 'usage'
                """
                
                usage = self.db_service.execute_query(usage_query, (latest_inspection_id,), fetch_one=True)
                usage_total = usage[0] if usage[0] else 0
                usage_pass = usage[1] if usage[1] else 0
                usage_fail = usage[2] if usage[2] else 0
                usage_pass_rate = (usage_pass / usage_total * 100) if usage_total > 0 else 0
                
                if usage_total > 0:
                    result["usage"] = {
                        "pass_rate": round(usage_pass_rate, 1),
                        "total_checks": usage_total,
                        "pass_count": usage_pass,
                        "fail_count": usage_fail,
                        "fields_checked": usage_total,
                        "last_updated": latest_time.isoformat() if latest_time else None
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"최신 검사 결과 조회 실패: {e}")
            return {
                "completeness": {"pass_rate": 0, "total_checks": 0, "pass_count": 0, "fail_count": 0, "fields_checked": 0, "last_updated": None},
                "validity": {"pass_rate": 0, "total_checks": 0, "pass_count": 0, "fail_count": 0, "fields_checked": 0, "last_updated": None}
            }

# 전역 품질 검사 서비스 인스턴스
quality_service = QualityService()

