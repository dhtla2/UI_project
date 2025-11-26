#!/usr/bin/env python3
"""
API endpoint별 데이터 구조와 컬럼명 체크 스크립트

각 API endpoint에서 받아오는 데이터의 구조를 분석하여
필요한 컬럼들을 파악합니다.
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# AIPC_v0.3/config.py에서 API 설정 직접 import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'AIPC_v0.3'))

try:
    from config import API_PARAMS
    print("✅ AIPC_v0.3/config.py에서 API 설정을 성공적으로 로드했습니다")
except ImportError as e:
    print(f"⚠️ AIPC_v0.3/config.py 로드 실패: {e}")
    print("💡 하드코딩된 기본 파라미터를 사용합니다")
    API_PARAMS = None

# sync_service 패키지 import
sys.path.append(os.path.join(os.path.dirname(__file__), 'sync_service'))

from sync_service.sync_config import DEFAULT_CONFIG
from sync_service.endpoint_mapper import EndpointMapper

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'api_structure_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class APIStructureChecker:
    """API 데이터 구조 체크 클래스"""
    
    def __init__(self):
        # AIPC_v0.3의 API 클라이언트 헤더 정보를 참고하여 수정
        self.api_config = {
            'base_url': 'https://aipc-data.com/api',
            'api_key': 'w4v69kgnlu'  # 실제 유효한 API 키로 교체 필요
        }
        self.endpoint_mapper = EndpointMapper()
        self.session = requests.Session()
        
        # AIPC_v0.3의 헤더 형식에 맞춰 수정
        self.session.headers.update({
            "Accept": "*/*",
            "Content-Type": "application/json",
            "x-ncp-apigw-api-key": self.api_config.get('api_key', '')  # 올바른 헤더명 사용
        })
        
    def check_single_endpoint(self, endpoint_name: str, sample_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """단일 엔드포인트의 데이터 구조 체크"""
        try:
            logger.info(f"🔍 {endpoint_name} 엔드포인트 구조 체크 시작")
            
            # 엔드포인트 정보 가져오기
            endpoint_info = self.endpoint_mapper.get_endpoint_info(endpoint_name)
            if not endpoint_info:
                logger.error(f"❌ {endpoint_name} 엔드포인트 정보를 찾을 수 없습니다")
                return {
                    'endpoint': endpoint_name,
                    'status': 'error',
                    'error': 'endpoint_info_not_found'
                }
            
            # api_path가 없는 경우 기본값 설정
            if 'api_path' not in endpoint_info or not endpoint_info['api_path']:
                logger.warning(f"⚠️ {endpoint_name}에 api_path가 정의되지 않음, 기본값 사용")
                # 기본 API 경로 패턴 생성
                endpoint_info['api_path'] = f"/{endpoint_name.replace('_', '')}/retrieve{endpoint_name.replace('_', '').title()}List"
            
            # API URL 구성
            api_url = f"{self.api_config['base_url']}{endpoint_info['api_path']}"
            logger.info(f"🌐 API URL: {api_url}")
            
            # 기본 파라미터 설정
            if not sample_params:
                sample_params = self._get_default_params(endpoint_name)
            
            logger.info(f"📝 요청 파라미터: {sample_params}")
            
            # API 호출
            response = self.session.get(api_url, params=sample_params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"❌ API 호출 실패: {response.status_code} - {response.text}")
                return {
                    'endpoint': endpoint_name,
                    'status': 'failed',
                    'error': f"HTTP {response.status_code}",
                    'response_text': response.text[:500],
                    'api_url': api_url,
                    'request_params': sample_params
                }
            
            # 응답 데이터 파싱
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.warning(f"⚠️ JSON 파싱 실패, 텍스트로 처리")
                data = {'raw_text': response.text[:1000]}
            
            # 데이터 구조 분석
            structure_info = self._analyze_data_structure(endpoint_name, data)
            structure_info['status'] = 'success'
            structure_info['api_url'] = api_url
            structure_info['request_params'] = sample_params
            
            logger.info(f"✅ {endpoint_name} 구조 체크 완료")
            return structure_info
            
        except Exception as e:
            logger.error(f"❌ {endpoint_name} 체크 중 오류: {e}")
            return {
                'endpoint': endpoint_name,
                'status': 'error',
                'error': str(e),
                'api_url': api_url if 'api_url' in locals() else None,
                'request_params': sample_params if 'sample_params' in locals() else None
            }
    
    def _get_default_params(self, endpoint_name: str) -> Dict[str, Any]:
        """엔드포인트별 기본 파라미터 반환"""
        # AIPC_v0.3/config.py에서 설정 로드 시도
        if API_PARAMS and 'endpoint_defaults' in API_PARAMS:
            endpoint_defaults = API_PARAMS['endpoint_defaults']
            if endpoint_name in endpoint_defaults:
                logger.info(f"✅ AIPC_v0.3/config.py에서 {endpoint_name} 파라미터 로드")
                return endpoint_defaults[endpoint_name]
        
        # fallback: 하드코딩된 기본 파라미터
        logger.warning(f"⚠️ AIPC_v0.3/config.py에서 {endpoint_name} 파라미터를 찾을 수 없음, 기본값 사용")
        
        # 기본 파라미터 (regNo 포함)
        base_params = {
            'regNo': 'KETI'  # 기본 regNo 추가
        }
        
        if endpoint_name == 'tc_work_info':
            return {
                **base_params,
                'tmnlId': 'BPTS',
                'shpCd': 'HASM',
                'callYr': '2024',
                'serNo': '001',
                'timeFrom': '20240801000000',
                'timeTo': '20240831235959'
            }
        elif endpoint_name == 'qc_work_info':
            return {
                **base_params,
                'tmnlId': 'BPTS',
                'shpCd': 'STMY',
                'callYr': '2024',
                'serNo': '001',
                'timeFrom': '20240801000000',
                'timeTo': '20240831235959'
            }
        elif endpoint_name == 'yt_work_info':
            return {
                **base_params,
                'tmnlId': 'BPTS',
                'shpCd': 'HHDT',
                'callYr': '2024',
                'serNo': '001',
                'timeFrom': '20240801000000',
                'timeTo': '20240831235959'
            }
        elif endpoint_name == 'berth_schedule':
            return {
                **base_params,
                'shpCd': 'KSCM',
                'callYr': '2024',
                'callNo': '1',
                'timeTp': 'A',
                'timeFrom': '20240801000000',
                'timeTo': '20240831235959'
            }
        elif endpoint_name == 'ais_info':
            return {
                **base_params,
                'mmsiNo': '312773000',
                'callLetter': 'V3JW',
                'imoNo': '8356869'
            }
        elif endpoint_name == 'cntr_load_unload_info':
            return {
                **base_params,
                'tmnlId': 'BPTS',
                'shpCd': 'STMY',
                'callYr': '2024',
                'serNo': '001',
                'timeFrom': '20240801000000',
                'timeTo': '20240831235959'
            }
        elif endpoint_name == 'cntr_report_detail':
            return {
                **base_params,
                'mrnNo': '22ANLU0015I',
                'msnNo': '2012',
                'blNo': 'AEL1288023',
                'cntrNo': 'CMAU8845903'
            }
        elif endpoint_name == 'vssl_entr_report':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': '060333',
                'callYr': '2024',
                'serNo': '001'
            }
        elif endpoint_name == 'vssl_dprt_report':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': 'D5QP8',
                'callYr': '2024',
                'serNo': '001'
            }
        elif endpoint_name == 'vssl_history':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': '000347',
                'callYr': '2024',
                'serNo': '001'
            }
        elif endpoint_name == 'vssl_pass_report':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': 'SVCD4',
                'callYr': '2024',
                'serNo': '001'
            }
        elif endpoint_name == 'cargo_imp_exp_report':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': 'D5QP8',
                'callYr': '2024',
                'serNo': '001'
            }
        elif endpoint_name == 'cargo_item_code':
            return {
                **base_params,
                'crgItemCd': '291636'
            }
        elif endpoint_name == 'dg_imp_report':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': 'V7A5515',
                'callYr': '2024',
                'serNo': '001'
            }
        elif endpoint_name == 'dg_manifest':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': 'DSRB8',
                'callYr': '2024',
                'serNo': '001',
                'cntrNo': 'PCVU2532814',
                'repNo': '22DWICB138I'
            }
        elif endpoint_name == 'fac_use_statement':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': 'DSGZ',
                'callYr': '2024',
                'serNo': '001'
            }
        elif endpoint_name == 'fac_use_stmt_bill':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': '130037',
                'callYr': '2024',
                'serNo': '001'
            }
        elif endpoint_name == 'vssl_sec_isps_info':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': 'V7PX2',
                'callYr': '2024',
                'serNo': '001'
            }
        elif endpoint_name == 'vssl_sec_port_info':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': '3FUZ5',
                'callYr': '2024',
                'serNo': '001'
            }
        elif endpoint_name == 'load_unload_from_to_info':
            return {
                **base_params,
                'tmnlId': 'BPTS',
                'shpCd': 'ACVG',
                'callYr': '2024',
                'callNo': '7'
            }
        elif endpoint_name == 'vssl_sanction_info':
            return {
                **base_params,
                'prtAtCd': '020',
                'callLetter': '9LU2620'
            }
        elif endpoint_name == 'country_code':
            return {
                **base_params,
                'cntryCd': 'KR'
            }
        elif endpoint_name == 'vssl_entr_intn_code':
            return {
                **base_params,
                'vsslEntrIntnCd': '01'
            }
        elif endpoint_name == 'pa_code':
            return {
                **base_params,
                'paCd': '020'
            }
        elif endpoint_name == 'port_code':
            return {
                **base_params,
                'natCd': 'KR',
                'portCd': 'BNP'
            }
        else:
            # 기본 파라미터 (regNo 포함)
            return {
                **base_params,
                'tmnlId': 'BPTS',
                'dateFrom': '20240801',
                'dateTo': '20240831'
            }
    
    def _analyze_data_structure(self, endpoint_name: str, data: Any) -> Dict[str, Any]:
        """API 응답 데이터 구조 분석"""
        structure_info = {
            'endpoint': endpoint_name,
            'data_type': type(data).__name__,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if isinstance(data, dict):
                # AIPC_v0.3의 일반적인 응답 구조
                if 'resultList' in data and isinstance(data['resultList'], list):
                    records = data['resultList']
                    structure_info['total_records'] = len(records)
                    structure_info['response_structure'] = 'resultList'
                    
                    if records:
                        # 첫 번째 레코드의 컬럼 추출
                        structure_info['columns'] = list(records[0].keys())
                        structure_info['sample_data'] = records[0]
                        
                        # 모든 레코드의 컬럼 통합
                        all_columns = set()
                        for record in records[:10]:  # 처음 10개만 체크
                            all_columns.update(record.keys())
                        structure_info['all_columns'] = list(all_columns)
                        
                elif 'resultList' in data and data['resultList'] is None:
                    structure_info['message'] = "데이터가 없습니다 (resultList is null)"
                    
                else:
                    # 다른 형태의 응답 구조
                    structure_info['columns'] = list(data.keys())
                    structure_info['sample_data'] = data
                    
            elif isinstance(data, list):
                structure_info['total_records'] = len(data)
                if data:
                    structure_info['columns'] = list(data[0].keys())
                    structure_info['sample_data'] = data[0]
                    
        except Exception as e:
            logger.error(f"데이터 구조 분석 중 오류: {e}")
            structure_info['error'] = str(e)
        
        return structure_info
    
    def check_all_endpoints(self) -> Dict[str, Any]:
        """모든 엔드포인트 체크"""
        logger.info("🚀 모든 API 엔드포인트 구조 체크 시작")
        
        all_endpoints = self.endpoint_mapper.get_all_endpoints()
        logger.info(f"📊 총 {len(all_endpoints)}개 엔드포인트 체크 예정")
        
        results = {}
        success_count = 0
        error_count = 0
        
        for endpoint in all_endpoints:
            try:
                result = self.check_single_endpoint(endpoint)
                results[endpoint] = result
                
                if result.get('status') == 'success':
                    success_count += 1
                else:
                    error_count += 1
                    
                # API 호출 간격 조절 (서버 부하 방지)
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ {endpoint} 체크 중 예외 발생: {e}")
                results[endpoint] = {
                    'endpoint': endpoint,
                    'status': 'exception',
                    'error': str(e)
                }
                error_count += 1
        
        # 요약 정보
        summary = {
            'total_endpoints': len(all_endpoints),
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': f"{(success_count/len(all_endpoints)*100):.1f}%",
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        logger.info(f"✅ 전체 체크 완료: 성공 {success_count}개, 실패 {error_count}개")
        return summary
    
    def generate_table_schema_sql(self, results: Dict[str, Any]) -> str:
        """테이블 스키마 SQL 생성"""
        sql_statements = []
        
        for endpoint, result in results.items():
            if result.get('status') == 'success' and 'columns' in result:
                table_name = endpoint
                columns = result['columns']
                
                if not columns:
                    continue
                
                # 테이블 생성 SQL
                sql = f"-- {endpoint} 테이블 생성\n"
                sql += f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
                sql += "    id INT AUTO_INCREMENT PRIMARY KEY,\n"
                
                for col in columns:
                    # 컬럼 타입 추정
                    col_type = self._infer_column_type(col, result.get('sample_data', {}).get(col))
                    sql += f"    {col} {col_type},\n"
                
                sql += "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n"
                sql += "    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP\n"
                sql += ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n\n"
                
                sql_statements.append(sql)
        
        return "\n".join(sql_statements)
    
    def _infer_column_type(self, column_name: str, sample_value: Any) -> str:
        """컬럼 타입 추정"""
        if sample_value is None:
            return "VARCHAR(255)"
        
        if isinstance(sample_value, bool):
            return "BOOLEAN"
        elif isinstance(sample_value, int):
            if column_name.lower().endswith('_id') or column_name.lower().endswith('_no'):
                return "BIGINT"
            else:
                return "INT"
        elif isinstance(sample_value, float):
            return "DECIMAL(15,6)"
        elif isinstance(sample_value, str):
            if len(sample_value) > 255:
                return "TEXT"
            elif len(sample_value) > 100:
                return "VARCHAR(500)"
            else:
                return "VARCHAR(255)"
        else:
            return "VARCHAR(255)"

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("🔍 API 엔드포인트 데이터 구조 체크 도구")
    print("=" * 70)
    print("⚠️  주의: 유효한 API 키가 필요합니다!")
    print("💡 API 키를 확인하고 수정한 후 실행하세요.")
    print("=" * 70)
    
    checker = APIStructureChecker()
    
    # 명령행 인수 처리
    if len(sys.argv) > 1:
        endpoint_name = sys.argv[1]
        print(f"🎯 특정 엔드포인트 체크: {endpoint_name}")
        result = checker.check_single_endpoint(endpoint_name)
        
        print(f"\n📊 {endpoint_name} 구조 정보:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    else:
        print("🔄 모든 엔드포인트 체크 시작...")
        results = checker.check_all_endpoints()
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 결과 저장
        with open(f'api_structure_results_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # SQL 스키마 생성
        sql_schema = checker.generate_table_schema_sql(results['results'])
        with open(f'table_schema_{timestamp}.sql', 'w', encoding='utf-8') as f:
            f.write(sql_schema)
        
        print(f"\n📁 결과 파일 저장:")
        print(f"  - JSON: api_structure_results_{timestamp}.json")
        print(f"  - SQL: table_schema_{timestamp}.sql")
        
        # 요약 출력
        print(f"\n📊 체크 결과 요약:")
        print(f"  - 총 엔드포인트: {results['total_endpoints']}개")
        print(f"  - 성공: {results['success_count']}개")
        print(f"  - 실패: {results['error_count']}개")
        print(f"  - 성공률: {results['success_rate']}")
        
        # 오류 분석
        if results['error_count'] > 0:
            print(f"\n❌ 주요 오류 분석:")
            error_types = {}
            for endpoint, result in results['results'].items():
                if result.get('status') != 'success':
                    error_type = result.get('error', 'unknown')
                    error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in error_types.items():
                print(f"  - {error_type}: {count}개")

if __name__ == "__main__":
    main()
