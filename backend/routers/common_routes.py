"""Common routes - Root, Health Check, Quality Check"""

from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional, Dict, Any
from datetime import datetime

# Import models from centralized schemas
from models import (
    QualityCheckRequest,
    QualityCheckResult,
    QualityCheckHistory
)

# Import utilities
from utils import (
    get_current_timestamp,
    generate_inspection_id,
    create_response_data,
    create_error_response,
    safe_json_dumps
)

# Import database utilities
from config import execute_query, execute_query_one, execute_insert

router = APIRouter()

@router.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Port Dashboard API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": get_current_timestamp()
    }

@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 데이터베이스 연결 테스트
        result = execute_query_one("SELECT 1 as test")
        
        if result:
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": get_current_timestamp()
            }
        else:
            raise Exception("Database connection test failed")
            
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Service unavailable: {str(e)}"
        )

@router.post("/quality-check/run", response_model=QualityCheckResult)
async def run_quality_check(request: QualityCheckRequest):
    """품질 검사 실행"""
    try:
        # 검사 ID 생성
        inspection_id = generate_inspection_id("quality_check")
        
        # 검사 정보를 data_inspection_info에 저장
        insert_query = """
            INSERT INTO data_inspection_info 
            (inspection_id, table_name, data_source, total_rows, total_columns, 
             inspection_type, inspection_status, start_time, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = [
            inspection_id,
            request.data_type,
            "API",
            0,  # total_rows - 실제 검사 후 업데이트
            0,  # total_columns - 실제 검사 후 업데이트
            "manual",
            "running",
            datetime.now(),
            "system",
            datetime.now()
        ]
        
        execute_insert(insert_query, params)
        
        # 실제 품질 검사 로직 (여기서는 간단한 예시)
        # TODO: 실제 품질 검사 로직 구현
        results = {
            "inspection_id": inspection_id,
            "data_type": request.data_type,
            "api_params": request.api_params,
            "quality_meta": request.quality_meta,
            "checks_performed": ["completeness", "validity"],
            "summary": {
                "total_checks": 10,
                "passed": 8,
                "failed": 2,
                "pass_rate": 80.0
            }
        }
        
        # 검사 완료 상태로 업데이트
        update_query = """
            UPDATE data_inspection_info 
            SET inspection_status = %s, end_time = %s, processing_time_ms = %s
            WHERE inspection_id = %s
        """
        
        processing_time = 1500  # 예시 처리 시간
        execute_query(update_query, ["completed", datetime.now(), processing_time, inspection_id])
        
        return QualityCheckResult(
            success=True,
            message="품질 검사가 성공적으로 완료되었습니다.",
            inspection_id=inspection_id,
            results=results,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        # 실패 시 상태 업데이트
        if 'inspection_id' in locals():
            try:
                update_query = """
                    UPDATE data_inspection_info 
                    SET inspection_status = %s, end_time = %s
                    WHERE inspection_id = %s
                """
                execute_query(update_query, ["failed", datetime.now(), inspection_id])
            except:
                pass
        
        raise HTTPException(
            status_code=500, 
            detail=f"품질 검사 실행 실패: {str(e)}"
        )

@router.get("/quality-check/history", response_model=List[QualityCheckHistory])
async def get_quality_check_history(
    limit: int = 50,
    data_type: Optional[str] = None
):
    """품질 검사 히스토리 조회"""
    try:
        # 기본 쿼리
        query = """
            SELECT 
                inspection_id,
                table_name as data_type,
                inspection_status as status,
                created_at,
                processing_time_ms,
                total_rows,
                total_columns
            FROM data_inspection_info
            WHERE inspection_type = 'manual'
        """
        
        params = []
        
        # 데이터 타입 필터링
        if data_type:
            query += " AND table_name = %s"
            params.append(data_type)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        results = execute_query(query, params)
        
        history_list = []
        for row in results:
            # 결과 데이터 구성
            results_data = {
                "processing_time_ms": row[4],
                "total_rows": row[5],
                "total_columns": row[6]
            } if row[4] else None
            
            history_list.append(QualityCheckHistory(
                id=row[0],
                data_type=row[1],
                status=row[2],
                created_at=row[3],
                results=results_data
            ))
        
        return history_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"품질 검사 히스토리 조회 실패: {str(e)}"
        )