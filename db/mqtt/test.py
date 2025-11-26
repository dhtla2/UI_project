#!/usr/bin/env python3

from __future__ import annotations

import json
from typing import Any, Dict

import requests_keti as requests
from config import API_CONFIG, API_ENDPOINTS, API_PARAMS


def build_work_info_params() -> Dict[str, Any]:
    """작업정보 API용 파라미터 빌드"""
    defaults = API_PARAMS.get("endpoint_defaults", {}).get("tc_work_info", {})
    return {
        "regNo": defaults.get("regNo", "client"),
        "tmnlId": defaults.get("tmnlId", "BPTS"),
        "timeFrom": defaults.get("timeFrom", "20220110000000"),
        "timeTo": defaults.get("timeTo", "20220130235959"),
    }


def build_berth_schedule_params() -> Dict[str, Any]:
    """선석계획 API용 파라미터 빌드 - 더 일반적인 값으로 수정"""
    return {
        "regNo": "KETI",
        "tmnlId": "BPTS",  # 터미널 ID 추가
        "yr": "2022",
        "spCall": "BTUV",
    }


def build_ais_info_params() -> Dict[str, Any]:
    """AIS 정보 API용 파라미터 빌드"""
    defaults = API_PARAMS.get("endpoint_defaults", {}).get("ais_info", {})
    return {
        "regNo": defaults.get("regNo", "KETI"),
        "mmsiNo": defaults.get("mmsiNo", "312773000"),
        "callLetter": defaults.get("callLetter", "V3JW"),
        "imoNo": defaults.get("imoNo", "8356869"),
    }


def build_cntr_load_unload_params() -> Dict[str, Any]:
    """컨테이너 양적하정보 API용 파라미터 빌드 - timeFrom/timeTo 추가"""
    return {
        "regNo": "KETI",  # regNo 추가
        "tmnlId": "BPTS",
        "shpCd": "STMY",
        "callYr": "2022",
        "serNo": "001",
        "timeFrom": "20220101000000",  # 필수 파라미터 추가
        "timeTo": "20220131235959",    # 필수 파라미터 추가
    }


def build_vssl_entr_report_params() -> Dict[str, Any]:
    """선박 입항신고정보 API용 파라미터 빌드 - 더 일반적인 값으로 수정"""
    return {
        "regNo": "KETI",  # regNo 추가
        "prtAtCd": "020",
        "callLetter": "060333",
        "callYr": "2022",
        "serNo": "001",  # 더 일반적인 serNo
    }


def test_api_call(api_name: str, endpoint: str, params: Dict[str, Any]) -> None:
    """개별 API 호출 테스트 - requests_keti 사용 (품질검사 + MQTT 포함)"""
    base_url = API_CONFIG.get("base_url", "https://aipc-data.com/api")
    url = base_url.rstrip("/") + endpoint

    headers = {
        "x-ncp-apigw-api-key": API_CONFIG.get("api_key", ""),
        "accept": "*/*",
    }

    print(f"\n{'='*60}")
    print(f"[TEST] {api_name} API 테스트")
    print(f"{'='*60}")
    print(f"[INFO] 요청 URL: {url}")
    print(f"[INFO] 요청 파라미터: {json.dumps(params, ensure_ascii=False)}")

    try:
        # requests_keti 사용 (자동 품질검사 및 MQTT 전송 포함)
        response = requests.get(url, params=params, headers=headers)
        print(f"[INFO] HTTP 상태 코드: {response.status_code}")

        if response.status_code != 200:
            print(f"[ERROR] API 호출 실패: {response.status_code}")
            # 에러 응답 내용 확인
            try:
                error_data = response.json()
                print(f"[ERROR] 에러 응답: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"[ERROR] 에러 응답 텍스트: {response.text[:200]}")
            return

        try:
            data = response.json()
        except Exception as e:
            print(f"[WARN] JSON 응답이 아닙니다: {e}")
            return

        # 응답 데이터 분석 및 출력
        print_response_summary(data, api_name)

    except Exception as e:
        print(f"[ERROR] API 호출 중 오류 발생: {e}")
        import traceback
        print(f"[ERROR] 상세 오류: {traceback.format_exc()}")


def print_response_summary(data: Any, api_name: str) -> None:
    """응답 데이터 요약 출력"""
    if isinstance(data, list):
        print(f"[INFO] 리스트 응답: {len(data)} 항목")
        if data:
            print(f"[SAMPLE] 첫 항목: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
    elif isinstance(data, dict):
        print(f"[INFO] 딕셔너리 응답 키: {list(data.keys())}")
        
        # resultList가 있는 경우 (일반적인 AIPC API 응답)
        if "resultList" in data and isinstance(data["resultList"], list):
            result_count = len(data["resultList"])
            print(f"[INFO] resultList 항목 수: {result_count}")
            if result_count > 0:
                print(f"[SAMPLE] 첫 항목: {json.dumps(data['resultList'][0], ensure_ascii=False, indent=2)}")
        
        # data가 있는 경우
        elif "data" in data and isinstance(data["data"], list):
            data_count = len(data["data"])
            print(f"[INFO] data 항목 수: {data_count}")
            if data_count > 0:
                print(f"[SAMPLE] 첫 항목: {json.dumps(data['data'][0], ensure_ascii=False, indent=2)}")
        
        # 기타 응답 형식
        else:
            print(f"[INFO] 응답 내용: {json.dumps(data, ensure_ascii=False, indent=2)}")
    else:
        print(f"[INFO] 예기치 않은 응답 형식: {type(data)}")


def main() -> None:
    """메인 함수: 5가지 API 테스트 실행 (requests_keti 사용)"""
    print("🚀 AIPC API 다중 테스트 시작 (requests_keti 사용)")
    print(f"📡 API 서버: {API_CONFIG.get('base_url', 'https://aipc-data.com/api')}")
    print(f"🔑 API 키: {API_CONFIG.get('api_key', '')[:8]}...")
    print("🔧 품질검사 + MQTT 전송이 포함된 테스트입니다.")
    
    # 테스트할 API 목록
    test_apis = [
        {
            "name": "TC 작업정보",
            "endpoint": API_ENDPOINTS.get("tc_work_info", "/TCWorkInfo/retrieveByTmnlIdTCWorkInfoList"),
            "params": build_work_info_params()
        },
        {
            "name": "선석계획",
            "endpoint": API_ENDPOINTS.get("berth_schedule", "/BerthScheduleTOS/retrieveByTmnlIdBerthScheduleTOSList"),
            "params": build_berth_schedule_params()
        },
        {
            "name": "AIS 정보",
            "endpoint": API_ENDPOINTS.get("ais_info", "/AISInfo/retrieveAISInfoList"),
            "params": build_ais_info_params()
        },
        {
            "name": "컨테이너 양적하정보",
            "endpoint": API_ENDPOINTS.get("cntr_load_unload_info", "/CntrLoadUnloadInfo/retrieveCntrLoadUnloadInfoList"),
            "params": build_cntr_load_unload_params()
        },
        {
            "name": "선박 입항신고정보",
            "endpoint": API_ENDPOINTS.get("vssl_entr_report", "/VsslEntrReport/retrieveVsslEntrReportList"),
            "params": build_vssl_entr_report_params()
        }
    ]
    
    # 각 API 테스트 실행 (requests_keti 사용)
    for api in test_apis:
        test_api_call(api["name"], api["endpoint"], api["params"])
    
    print(f"\n{'='*60}")
    print("✅ 모든 API 테스트 완료")
    print("🔧 각 API 호출마다 품질검사와 MQTT 전송이 수행되었습니다.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()


