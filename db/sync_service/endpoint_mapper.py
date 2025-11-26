#!/usr/bin/env python3
"""
API 엔드포인트와 DB 테이블 매핑 서비스

AIPC_Client/config.py의 API_PARAMS.endpoint_defaults에 정의된
모든 API 엔드포인트를 port_database의 테이블과 매핑합니다.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EndpointMapper:
    """API 엔드포인트와 DB 테이블 매핑 관리"""
    
    def __init__(self):
        # API 엔드포인트와 DB 테이블 매핑
        self.api_table_mapping = {
            # 작업 정보 관련
            "tc_work_info": {
                "table_name": "tc_work_info",
                "category": "work_info",
                "priority": "high",
                "sync_interval": 3600,  # 1시간
                "description": "TC 작업 정보",
                "api_path": "/TCWorkInfo/retrieveByTmnlIdTCWorkInfoList"
            },
            "qc_work_info": {
                "table_name": "qc_work_info", 
                "category": "work_info",
                "priority": "high",
                "sync_interval": 3600,
                "description": "QC 작업 정보",
                "api_path": "/QCWorkInfo/retrieveByTmnlIdQCWorkInfoList"
            },
            "yt_work_info": {
                "table_name": "yt_work_info",
                "category": "work_info", 
                "priority": "high",
                "sync_interval": 3600,
                "description": "YT 작업 정보",
                "api_path": "/YTWorkInfo/retrieveByTmnlIdYTWorkInfoList"
            },
            
            # 선석 계획 관련
            "berth_schedule": {
                "table_name": "berth_schedule",
                "category": "schedule",
                "priority": "high",
                "sync_interval": 1800,  # 30분
                "description": "선석 계획",
                "api_path": "/BerthScheduleTOS/retrieveBerthScheduleTOSList"
            },
            
            # AIS 정보 관련
            "ais_info": {
                "table_name": "ais_info",
                "category": "vessel_info",
                "priority": "high",
                "sync_interval": 900,   # 15분
                "description": "AIS 정보",
                "api_path": "/AISInfo/retrieveAISInfoList"
            },
            
            # 컨테이너 관련
            "cntr_load_unload_info": {
                "table_name": "cntr_load_unload_info",
                "category": "container",
                "priority": "medium",
                "sync_interval": 7200,  # 2시간
                "description": "컨테이너 양적하정보",
                "api_path": "/CntrLoadUnloadInfo/retrieveCntrLoadUnloadInfoList"
            },
            "cntr_report_detail": {
                "table_name": "cntr_report_detail",
                "category": "container",
                "priority": "medium",
                "sync_interval": 7200,
                "description": "컨테이너 신고상세정보",
                "api_path": "/CntrReportDetail/retrieveCntrReportDetailList"
            },
            
            # 선박 관련
            "vssl_entr_report": {
                "table_name": "vssl_entr_report",
                "category": "vessel_report",
                "priority": "medium",
                "sync_interval": 3600,
                "description": "선박 입항신고정보",
                "api_path": "/VsslEntrReport/retrieveVsslEntrReportList"
            },
            "vssl_dprt_report": {
                "table_name": "vssl_dprt_report",
                "category": "vessel_report",
                "priority": "medium",
                "sync_interval": 3600,
                "description": "선박 출항신고정보",
                "api_path": "/VsslDprtReport/retrieveVsslDprtReportList"
            },
            "vssl_history": {
                "table_name": "vssl_history",
                "category": "vessel_info",
                "priority": "low",
                "sync_interval": 14400,  # 4시간
                "description": "관제정보 (VTCHistory)",
                "api_path": "/VTCHistory/retrieveVTCHistoryList"
            },
            "vssl_pass_report": {
                "table_name": "vssl_pass_report",
                "category": "vessel_report",
                "priority": "low",
                "sync_interval": 7200,
                "description": "외항통과선박신청정보",
                "api_path": "/VsslPassReport/retrieveVsslPassReportList"
            },
            "vssl_spec_info": {
                "table_name": "vssl_spec_info",
                "category": "vessel_info",
                "priority": "medium",
                "sync_interval": 86400,  # 24시간 (선박 제원은 자주 변하지 않음)
                "description": "선박 제원 정보",
                "api_path": "/VsslSpecInfo/retrieveVsslSpecInfoList"
            },
            
            # 선박 매칭 관련
            "vssl_Tos_VsslNo": {
                "table_name": "vssl_Tos_VsslNo",
                "category": "vessel_info",
                "priority": "high",
                "sync_interval": 900,  # 15분
                "description": "TOS 선박번호 매칭 (TOS→PMIS)",
                "api_path": "/Match/retrieveTosVsslNo"
            },
            "vssl_Port_VsslNo": {
                "table_name": "vssl_Port_VsslNo",
                "category": "vessel_info",
                "priority": "high",
                "sync_interval": 900,  # 15분
                "description": "항만 선박번호 매칭 (PMIS→TOS)",
                "api_path": "/Match/retrievePortMisVsslNo"
            },
            
            # 화물 관련
            "cargo_imp_exp_report": {
                "table_name": "cargo_imp_exp_report",
                "category": "cargo",
                "priority": "medium",
                "sync_interval": 7200,
                "description": "화물반출입신고정보",
                "api_path": "/CargoImpExpReport/retrieveCargoImpExpReportList"
            },
            "cargo_item_code": {
                "table_name": "cargo_item_code",
                "category": "cargo",
                "priority": "low",
                "sync_interval": 86400,  # 24시간
                "description": "화물품목코드",
                "api_path": "/CargoItemCode/retrieveCargoItemCodeList"
            },
            
            # 위험물 관련
            "dg_imp_report": {
                "table_name": "dg_imp_report",
                "category": "dangerous_goods",
                "priority": "high",
                "sync_interval": 1800,  # 30분
                "description": "위험물반입신고서",
                "api_path": "/DGImpReport/retrieveDGImpReportList"
            },
            "dg_manifest": {
                "table_name": "dg_manifest",
                "category": "dangerous_goods",
                "priority": "high",
                "sync_interval": 1800,
                "description": "위험물 적하알림표",
                "api_path": "/DGManifest/retrieveDGManifestList"
            },
            
            # 항만시설 관련
            "fac_use_statement": {
                "table_name": "fac_use_statement",
                "category": "facility",
                "priority": "medium",
                "sync_interval": 7200,
                "description": "항만시설사용 신청/결과정보",
                "api_path": "/FacUseSatement/retrieveFacUseSatementList"
            },
            "fac_use_stmt_bill": {
                "table_name": "fac_use_stmt_bill",
                "category": "facility",
                "priority": "medium",
                "sync_interval": 7200,
                "description": "항만시설사용신고정보-화물료",
                "api_path": "/FacUseStmtBill/retrieveFacUseStmtBillList"
            },
            
            # 보안 관련
            "vssl_sec_isps_info": {
                "table_name": "vssl_sec_isps_info",
                "category": "security",
                "priority": "medium",
                "sync_interval": 14400,  # 4시간
                "description": "선박보안인증서 통보",
                "api_path": "/VsslSecISPSInfo/retrieveVsslSecISPSInfoList"
            },
            "vssl_sec_port_info": {
                "table_name": "vssl_sec_port_info",
                "category": "security",
                "priority": "medium",
                "sync_interval": 14400,
                "description": "선박보안인증서 통보 경유지 정보",
                "api_path": "/VsslSecPortInfo/retrieveVsslSecPortInfoList"
            },
            
            # 기타 정보
            "load_unload_from_to_info": {
                "table_name": "load_unload_from_to_info",
                "category": "vessel_info",
                "priority": "medium",
                "sync_interval": 3600,
                "description": "선박양적하 시작종료정보",
                "api_path": "/LoadUnloadFromToInfo/retrieveLoadUnloadFromToInfoList"
            },
            "vssl_sanction_info": {
                "table_name": "vssl_sanction_info",
                "category": "vessel_info",
                "priority": "low",
                "sync_interval": 86400,  # 24시간
                "description": "제재대상선박 정보",
                "api_path": "/VsslSanctionInfo/retrieveVsslSanctionInfoList"
            },
            "country_code": {
                "table_name": "country_code",
                "category": "code",
                "priority": "low",
                "sync_interval": 604800,  # 7일
                "description": "국가코드",
                "api_path": "/CountryCode/retrieveCountryCodeList"
            },
            "vssl_entr_intn_code": {
                "table_name": "vssl_entr_intn_code",
                "category": "code",
                "priority": "low",
                "sync_interval": 604800,
                "description": "입항목적코드",
                "api_path": "/VsslEntrIntnCode/retrieveVsslEntrIntnCodeList"
            },
            "pa_code": {
                "table_name": "pa_code",
                "category": "code",
                "priority": "low",
                "sync_interval": 604800,
                "description": "항구청코드",
                "api_path": "/PACode/retrievePACodeList"
            },
            "port_code": {
                "table_name": "port_code",
                "category": "code",
                "priority": "low",
                "sync_interval": 604800,
                "description": "항구코드",
                "api_path": "/PortCode/retrievePortCodeList"
            }
        }
    
    def get_all_endpoints(self) -> List[str]:
        """모든 API 엔드포인트 목록 반환"""
        return list(self.api_table_mapping.keys())
    
    def get_table_name(self, endpoint_name: str) -> Optional[str]:
        """API 엔드포인트에 해당하는 테이블명 반환"""
        mapping = self.api_table_mapping.get(endpoint_name)
        return mapping["table_name"] if mapping else None
    
    def get_endpoint_info(self, endpoint_name: str) -> Optional[Dict[str, Any]]:
        """API 엔드포인트 상세 정보 반환"""
        return self.api_table_mapping.get(endpoint_name)
    
    def get_endpoints_by_category(self, category: str) -> List[str]:
        """카테고리별 API 엔드포인트 목록 반환"""
        return [
            endpoint for endpoint, info in self.api_table_mapping.items()
            if info["category"] == category
        ]
    
    def get_endpoints_by_priority(self, priority: str) -> List[str]:
        """우선순위별 API 엔드포인트 목록 반환"""
        return [
            endpoint for endpoint, info in self.api_table_mapping.items()
            if info["priority"] == priority
        ]
    
    def get_sync_interval(self, endpoint_name: str) -> int:
        """API 엔드포인트의 동기화 간격 반환 (초)"""
        mapping = self.api_table_mapping.get(endpoint_name)
        return mapping["sync_interval"] if mapping else 3600
    
    def get_high_priority_endpoints(self) -> List[str]:
        """높은 우선순위 API 엔드포인트 목록 반환"""
        return self.get_endpoints_by_priority("high")
    
    def get_medium_priority_endpoints(self) -> List[str]:
        """중간 우선순위 API 엔드포인트 목록 반환"""
        return self.get_endpoints_by_priority("medium")
    
    def get_low_priority_endpoints(self) -> List[str]:
        """낮은 우선순위 API 엔드포인트 목록 반환"""
        return self.get_endpoints_by_priority("low")
    
    def validate_endpoint(self, endpoint_name: str) -> bool:
        """API 엔드포인트 유효성 검증"""
        return endpoint_name in self.api_table_mapping
    
    def get_endpoint_summary(self) -> Dict[str, Any]:
        """API 엔드포인트 요약 정보 반환"""
        summary = {
            "total_endpoints": len(self.api_table_mapping),
            "categories": {},
            "priorities": {},
            "sync_intervals": {}
        }
        
        for endpoint, info in self.api_table_mapping.items():
            # 카테고리별 카운트
            category = info["category"]
            summary["categories"][category] = summary["categories"].get(category, 0) + 1
            
            # 우선순위별 카운트
            priority = info["priority"]
            summary["priorities"][priority] = summary["priorities"].get(priority, 0) + 1
            
            # 동기화 간격별 카운트
            interval = info["sync_interval"]
            summary["sync_intervals"][str(interval)] = summary["sync_intervals"].get(str(interval), 0) + 1
        
        return summary

# 싱글톤 인스턴스
endpoint_mapper = EndpointMapper()
