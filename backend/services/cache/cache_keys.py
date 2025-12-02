"""캐시 키 생성 규칙 모듈"""

from typing import Any, Dict, Optional
import hashlib
import json


class CacheKeyGenerator:
    """
    캐시 키 생성기
    
    일관성 있는 캐시 키 생성 규칙을 제공합니다.
    키 형식: {prefix}:{namespace}:{endpoint}:{params_hash}
    예시: port_dashboard:ais:summary:a3f2c1b
    """
    
    @staticmethod
    def generate(
        namespace: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        prefix: str = "port_dashboard"
    ) -> str:
        """
        캐시 키 생성
        
        Args:
            namespace: 네임스페이스 (예: 'ais', 'tos', 'tc', 'qc')
            endpoint: 엔드포인트 식별자 (예: 'summary', 'quality', 'history')
            params: 파라미터 딕셔너리 (선택)
            prefix: 캐시 프리픽스 (기본값: 'port_dashboard')
        
        Returns:
            생성된 캐시 키
        
        Examples:
            >>> CacheKeyGenerator.generate('ais', 'summary')
            'port_dashboard:ais:summary'
            
            >>> CacheKeyGenerator.generate('ais', 'history', {'period': 'daily'})
            'port_dashboard:ais:history:8f3a1b2c'
            
            >>> CacheKeyGenerator.generate(
            ...     'tos', 
            ...     'inspection', 
            ...     {'start_date': '2024-01-01', 'end_date': '2024-01-31'}
            ... )
            'port_dashboard:tos:inspection:e4d3c2b1'
        """
        # 기본 키 구성 요소
        key_parts = [prefix, namespace, endpoint]
        
        # 파라미터가 있으면 해시 추가
        if params:
            param_hash = CacheKeyGenerator._hash_params(params)
            key_parts.append(param_hash)
        
        return ":".join(key_parts)
    
    @staticmethod
    def generate_pattern(
        namespace: str,
        endpoint: str = "*",
        prefix: str = "port_dashboard"
    ) -> str:
        """
        패턴 매칭용 키 생성 (캐시 무효화에 사용)
        
        Args:
            namespace: 네임스페이스
            endpoint: 엔드포인트 (기본값: '*' - 모든 엔드포인트)
            prefix: 캐시 프리픽스
        
        Returns:
            패턴 매칭 키
        
        Examples:
            >>> CacheKeyGenerator.generate_pattern('ais')
            'port_dashboard:ais:*'
            
            >>> CacheKeyGenerator.generate_pattern('ais', 'summary')
            'port_dashboard:ais:summary:*'
        """
        if endpoint == "*":
            return f"{prefix}:{namespace}:*"
        return f"{prefix}:{namespace}:{endpoint}:*"
    
    @staticmethod
    def _hash_params(params: Dict[str, Any]) -> str:
        """
        파라미터 딕셔너리를 해시값으로 변환
        
        Args:
            params: 파라미터 딕셔너리
        
        Returns:
            8자리 MD5 해시
        """
        # 파라미터를 정렬하여 일관성 보장
        sorted_params = json.dumps(
            params,
            sort_keys=True,
            ensure_ascii=False,
            default=str  # datetime 등 특수 타입 처리
        )
        
        # MD5 해시 생성 (캐시 키 용도로는 충분)
        hash_obj = hashlib.md5(sorted_params.encode('utf-8'))
        
        # 앞 8자리만 사용 (충돌 가능성은 낮고 키 길이 단축)
        return hash_obj.hexdigest()[:8]
    
    @staticmethod
    def parse_key(cache_key: str) -> Dict[str, str]:
        """
        캐시 키를 파싱하여 구성 요소 반환
        
        Args:
            cache_key: 캐시 키
        
        Returns:
            파싱된 딕셔너리 {'prefix', 'namespace', 'endpoint', 'params_hash'}
        
        Examples:
            >>> CacheKeyGenerator.parse_key('port_dashboard:ais:summary:a3f2c1b')
            {
                'prefix': 'port_dashboard',
                'namespace': 'ais',
                'endpoint': 'summary',
                'params_hash': 'a3f2c1b'
            }
        """
        parts = cache_key.split(':')
        
        result = {
            'prefix': parts[0] if len(parts) > 0 else '',
            'namespace': parts[1] if len(parts) > 1 else '',
            'endpoint': parts[2] if len(parts) > 2 else '',
            'params_hash': parts[3] if len(parts) > 3 else None
        }
        
        return result


# ==================== 네임스페이스 상수 ====================
class CacheNamespace:
    """캐시 네임스페이스 상수"""
    AIS = "ais"              # AIS 선박 정보
    TOS = "tos"              # TOS 터미널 운영
    TC = "tc"                # TC 터미널 컨테이너
    QC = "qc"                # QC 품질 관리
    YT = "yt"                # YT 야드 트랙터
    PMIS = "pmis"            # PMIS 항만 관리
    VSSL_SPEC = "vssl_spec"  # 선박 제원
    STATS = "stats"          # 통계
    COMMON = "common"        # 공통


# ==================== 엔드포인트 상수 ====================
class CacheEndpoint:
    """캐시 엔드포인트 상수"""
    SUMMARY = "summary"
    QUALITY = "quality"
    QUALITY_SUMMARY = "quality_summary"
    QUALITY_DETAILS = "quality_details"
    QUALITY_STATUS = "quality_status"
    CHARTS = "charts"
    HISTORY = "history"
    INSPECTION_HISTORY = "inspection_history"
    FIELD_ANALYSIS = "field_analysis"
    WORK_HISTORY = "work_history"


if __name__ == "__main__":
    # 테스트
    print("=" * 60)
    print("캐시 키 생성 테스트")
    print("=" * 60)
    
    # 기본 키
    key1 = CacheKeyGenerator.generate("ais", "summary")
    print(f"1. 기본 키: {key1}")
    
    # 파라미터 포함 키
    key2 = CacheKeyGenerator.generate(
        "ais",
        "history",
        {"period": "daily", "start_date": "2024-01-01"}
    )
    print(f"2. 파라미터 키: {key2}")
    
    # 패턴 키
    pattern1 = CacheKeyGenerator.generate_pattern("ais")
    print(f"3. 패턴 키 (전체): {pattern1}")
    
    pattern2 = CacheKeyGenerator.generate_pattern("ais", "summary")
    print(f"4. 패턴 키 (특정): {pattern2}")
    
    # 키 파싱
    parsed = CacheKeyGenerator.parse_key(key2)
    print(f"5. 키 파싱 결과: {parsed}")
    
    # 네임스페이스/엔드포인트 상수 사용
    key3 = CacheKeyGenerator.generate(
        CacheNamespace.TOS,
        CacheEndpoint.QUALITY_SUMMARY
    )
    print(f"6. 상수 사용 키: {key3}")

