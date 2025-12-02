"""Models package initialization"""

from .schemas import (
    # AIS 관련 모델들
    AISInfoResponse,
    StatisticsResponse,
    
    # 대시보드 관련 모델들
    QualitySummaryData,
    InspectionData,
    LatestInspectionResults,
    FailedItemData,
    FailedItemsResponse,
    APIQualityData,
    
    # 품질 검사 관련 모델들
    QualityCheckRequest,
    QualityCheckResult,
    QualityCheckHistory,
    
    # UI 로그 관련 모델들
    PageVisitRequest,
    PageVisitLog,
    UIStatisticsResponse,
    APICallLog,
    
    # 시간 기반 통계 모델들
    TimeBasedStats,
    DailyStats,
    WeeklyStats,
    MonthlyStats,
    
    # TOS 관련 모델들
    TOSSummaryData,
    TOSWorkHistoryData,
    
    # TC 관련 모델들
    TCSummaryData,
    TCWorkHistoryData,
    
    # QC 관련 모델들
    QCSummaryData,
    QCWorkHistoryData,
    
    # YT 관련 모델들
    YTSummaryData,
    YTWorkHistoryData,
)

__all__ = [
    # AIS 관련
    "AISInfoResponse",
    "StatisticsResponse",
    
    # 대시보드 관련
    "QualitySummaryData",
    "InspectionData", 
    "LatestInspectionResults",
    "FailedItemData",
    "FailedItemsResponse",
    "APIQualityData",
    
    # 품질 검사 관련
    "QualityCheckRequest",
    "QualityCheckResult",
    "QualityCheckHistory",
    
    # UI 로그 관련
    "PageVisitRequest",
    "PageVisitLog",
    "UIStatisticsResponse",
    "APICallLog",
    
    # 시간 기반 통계
    "TimeBasedStats",
    "DailyStats",
    "WeeklyStats", 
    "MonthlyStats",
    
    # TOS 관련
    "TOSSummaryData",
    "TOSWorkHistoryData",
    
    # TC 관련
    "TCSummaryData",
    "TCWorkHistoryData",
    
    # QC 관련
    "QCSummaryData",
    "QCWorkHistoryData",
    
    # YT 관련
    "YTSummaryData",
    "YTWorkHistoryData",
]