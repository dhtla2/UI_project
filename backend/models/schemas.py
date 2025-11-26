"""Pydantic models for API requests and responses"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

# ===== AIS 관련 모델들 =====
class AISInfoResponse(BaseModel):
    """AIS 정보 응답 모델"""
    mmsiNo: Optional[int] = None
    imoNo: Optional[int] = None
    vsslNm: Optional[str] = None
    callLetter: Optional[str] = None
    vsslTp: Optional[str] = None
    vsslTpCd: Optional[int] = None
    vsslTpCrgo: Optional[float] = None
    vsslCls: Optional[str] = None
    vsslLen: Optional[float] = None
    vsslWidth: Optional[float] = None
    flag: Optional[str] = None
    flagCd: Optional[int] = None
    vsslDefBrd: Optional[float] = None
    lon: Optional[float] = None
    lat: Optional[float] = None
    sog: Optional[float] = None
    cog: Optional[float] = None
    rot: Optional[float] = None
    headSide: Optional[float] = None
    vsslNavi: Optional[str] = None
    vsslNaviCd: Optional[int] = None
    source: Optional[str] = None
    dt_pos_utc: Optional[int] = None
    dt_static_utc: Optional[int] = None
    vsslTpMain: Optional[str] = None
    vsslTpSub: Optional[float] = None
    dstNm: Optional[str] = None
    dstCd: Optional[str] = None
    eta: Optional[int] = None

class StatisticsResponse(BaseModel):
    """통계 응답 모델"""
    totalShips: int
    shipTypes: List[dict]
    flags: List[dict]
    navigationStatus: List[dict]

# ===== 대시보드 관련 모델들 =====
class QualitySummaryData(BaseModel):
    """품질 요약 데이터 모델"""
    total_inspections: int
    total_checks: int
    pass_count: int
    fail_count: int
    pass_rate: float
    last_inspection_date: Optional[str] = None
    completeness: Dict[str, Any]
    validity: Dict[str, Any]
    usage: Optional[Dict[str, Any]] = None

class InspectionData(BaseModel):
    """검사 데이터 모델"""
    pass_rate: float
    total_checks: int
    pass_count: int
    fail_count: int
    fields_checked: int
    last_updated: Optional[str] = None

class LatestInspectionResults(BaseModel):
    """최신 검사 결과 모델"""
    completeness: InspectionData
    validity: InspectionData
    usage: Optional[InspectionData] = None

class FailedItemData(BaseModel):
    """실패한 항목 데이터 모델"""
    field: str
    reason: str
    message: str
    details: str
    affected_rows: int
    created_at: Optional[str] = None

class FailedItemsResponse(BaseModel):
    """실패/성공 항목 응답 모델"""
    failed_items: List[FailedItemData]
    success_items: List[FailedItemData]
    page: str

class APIQualityData(BaseModel):
    """API 품질 데이터 모델"""
    api_type: str
    total_inspections: int
    total_checks: int
    pass_count: int
    fail_count: int
    pass_rate: float

# ===== 품질 검사 관련 모델들 =====
class QualityCheckRequest(BaseModel):
    """품질 검사 요청 모델"""
    data_type: str
    api_params: Dict[str, Any]
    quality_meta: Dict[str, Any]

class QualityCheckResult(BaseModel):
    """품질 검사 결과 모델"""
    success: bool
    message: str
    inspection_id: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    timestamp: datetime

class QualityCheckHistory(BaseModel):
    """품질 검사 히스토리 모델"""
    id: str
    data_type: str
    status: str
    created_at: datetime
    results: Optional[Dict[str, Any]] = None

# ===== UI 로그 관련 모델들 =====
class PageVisitRequest(BaseModel):
    """페이지 방문 요청 모델"""
    user_id: str
    page_name: str
    page_url: str
    login_status: str = "visit"  # login, logout, visit
    visit_duration: Optional[int] = None
    session_id: Optional[str] = None
    referrer: Optional[str] = None

class PageVisitLog(BaseModel):
    """페이지 방문 로그 모델"""
    user_id: str
    page_name: str
    page_url: str
    login_status: str
    visit_duration: int
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    visit_hour: int
    visit_weekday: int

class UIStatisticsResponse(BaseModel):
    """UI 통계 응답 모델"""
    total_page_visits: int
    total_api_calls: int
    unique_users: int
    login_status_stats: List[tuple]
    most_visited_pages: List[tuple]
    most_called_apis: List[tuple]
    avg_response_time_ms: float

class APICallLog(BaseModel):
    """API 호출 로그 모델"""
    endpoint: str
    method: str
    status_code: int
    response_time: int
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# ===== 시간 기반 통계 모델들 =====
class TimeBasedStats(BaseModel):
    """시간 기반 통계 모델"""
    period: str
    data: List[Dict[str, Any]]

class DailyStats(BaseModel):
    """일별 통계 모델"""
    date: str
    page_visits: int
    api_calls: int

class WeeklyStats(BaseModel):
    """주별 통계 모델"""
    year: int
    month: int
    week: int
    week_label: str
    page_visits: int
    api_calls: int

class MonthlyStats(BaseModel):
    """월별 통계 모델"""
    year: int
    month: int
    month_label: str
    page_visits: int
    api_calls: int

# ===== TOS 관련 모델들 =====
class TOSSummaryData(BaseModel):
    """TOS 요약 데이터 모델"""
    total_schedules: int
    total_terminals: int
    total_ships: int
    total_containers: int
    schedule_days: int
    recent_schedules: int
    active_terminals: int
    active_ships: int
    schedule_types: List[Dict[str, Any]]
    terminals: List[Dict[str, Any]]
    last_inspection_date: Optional[str] = None

class TOSWorkHistoryData(BaseModel):
    """TOS 작업 히스토리 모델"""
    work_date: str
    total_schedules: int
    terminals: int
    ships: int
    containers: int

# ===== TC 관련 모델들 =====
class TCSummaryData(BaseModel):
    """TC 요약 데이터 모델"""
    total_work: int
    total_terminals: int
    total_ships: int
    total_containers: int
    work_days: int
    recent_work: int
    active_terminals: int
    active_ships: int
    work_types: List[Dict[str, Any]]
    terminals: List[Dict[str, Any]]
    last_inspection_date: Optional[str] = None

class TCWorkHistoryData(BaseModel):
    """TC 작업 히스토리 모델"""
    work_date: str
    total_work: int
    terminals: int
    ships: int
    containers: int

# ===== QC 관련 모델들 =====
class QCSummaryData(BaseModel):
    """QC 요약 데이터 모델"""
    total_work: int
    total_terminals: int
    total_ships: int
    total_containers: int
    work_days: int
    recent_work: int
    active_terminals: int
    active_ships: int
    work_types: List[Dict[str, Any]]
    terminals: List[Dict[str, Any]]
    last_inspection_date: Optional[str] = None

class QCWorkHistoryData(BaseModel):
    """QC 작업 히스토리 모델"""
    work_date: str
    total_work: int
    terminals: int
    ships: int
    containers: int

