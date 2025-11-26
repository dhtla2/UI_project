#!/usr/bin/env python3
"""
검사 결과 수신 API 엔드포인트
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from data_inspection_service import DataInspectionService
from api_data_service import APIDataService

app = FastAPI(title="Data Quality Inspection API")

# API 키 검증
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")
API_KEY = "your_api_key_here"  # 실제 운영 시 환경변수로 관리

def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# 데이터 모델
class InspectionResultItem(BaseModel):
    inspection_id: str
    check_type: str
    check_name: str
    message: str
    status: str
    severity: str = "MEDIUM"
    affected_rows: int = 0
    affected_columns: str
    details: str

class InspectionSummary(BaseModel):
    inspection_id: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int = 0
    error_checks: int = 0
    pass_rate: float
    data_quality_score: float
    summary_json: str
    recommendations: str

class InspectionData(BaseModel):
    inspection_info: Dict[str, Any]
    inspection_results: List[InspectionResultItem]
    inspection_summary: InspectionSummary
    api_call_info: Optional[Dict[str, Any]] = None
    api_response_data: Optional[Dict[str, Any]] = None

# 서비스 인스턴스
inspection_service = DataInspectionService()
api_service = APIDataService()

@app.post("/api/inspection-results", dependencies=[Depends(verify_api_key)])
async def receive_inspection_results(data: InspectionData):
    """
    검사 결과 수신 API
    """
    try:
        inspection_id = data.inspection_info.get('inspection_id')
        
        # 1. 검사 정보 저장
        inspection_service.save_inspection_info(data.inspection_info)
        
        # 2. 검사 결과 저장
        for result in data.inspection_results:
            result_dict = result.dict()
            inspection_service.save_inspection_results(inspection_id, [result_dict])
        
        # 3. 검사 요약 저장
        summary_dict = data.inspection_summary.dict()
        inspection_service.save_inspection_summary(inspection_id, summary_dict)
        
        # 4. API 호출 정보 저장 (있는 경우)
        if data.api_call_info:
            api_service.save_api_call_info(data.api_call_info)
        
        # 5. API 응답 데이터 저장 (있는 경우)
        if data.api_response_data:
            api_service.save_response_data(data.api_response_data)
        
        return {
            "status": "success",
            "message": f"Inspection results saved successfully: {inspection_id}",
            "inspection_id": inspection_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save inspection results: {str(e)}")

@app.get("/api/inspection-status/{inspection_id}", dependencies=[Depends(verify_api_key)])
async def get_inspection_status(inspection_id: str):
    """
    검사 상태 조회 API
    """
    try:
        info = inspection_service.get_inspection_info(inspection_id)
        if not info:
            raise HTTPException(status_code=404, detail="Inspection not found")
        
        return {
            "inspection_id": inspection_id,
            "status": info.get('inspection_status'),
            "data_source": info.get('data_source'),
            "total_rows": info.get('total_rows'),
            "created_at": info.get('created_at')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get inspection status: {str(e)}")

@app.get("/api/recent-inspections", dependencies=[Depends(verify_api_key)])
async def get_recent_inspections(limit: int = 10):
    """
    최근 검사 목록 조회 API
    """
    try:
        inspections = inspection_service.get_recent_inspections(limit)
        return {
            "inspections": inspections,
            "count": len(inspections)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent inspections: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 