"""Common utility functions"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
import hashlib
import random
import string

def get_current_timestamp() -> str:
    """현재 타임스탬프 반환"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date() -> str:
    """현재 날짜 반환"""
    return datetime.now().strftime("%Y-%m-%d")

def format_date(date_obj: datetime, format_str: str = "%Y-%m-%d") -> str:
    """날짜 포맷팅"""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime(format_str)

def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> Optional[datetime]:
    """문자열을 날짜로 파싱"""
    try:
        return datetime.strptime(date_str, format_str)
    except (ValueError, TypeError):
        return None

def get_date_range(days: int) -> tuple:
    """지정된 일수만큼의 날짜 범위 반환"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def calculate_pass_rate(pass_count: int, total_count: int) -> float:
    """통과율 계산"""
    if total_count == 0:
        return 0.0
    return round((pass_count / total_count) * 100, 2)

def generate_inspection_id(prefix: str = "inspection") -> str:
    """검사 ID 생성"""
    timestamp = int(datetime.now().timestamp())
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{timestamp}_{random_str}"

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """안전한 JSON 파싱"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """안전한 JSON 직렬화"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default

def hash_string(text: str) -> str:
    """문자열 해시 생성"""
    return hashlib.md5(text.encode()).hexdigest()

def clean_string(text: str) -> str:
    """문자열 정리 (공백 제거, None 처리)"""
    if text is None:
        return ""
    return str(text).strip()

def safe_float(value: Any, default: float = 0.0) -> float:
    """안전한 float 변환"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """안전한 int 변환"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def format_number(number: float, decimal_places: int = 2) -> str:
    """숫자 포맷팅"""
    try:
        return f"{number:.{decimal_places}f}"
    except (ValueError, TypeError):
        return "0.00"

def get_week_of_month(date_obj: datetime) -> int:
    """월의 몇 번째 주인지 계산"""
    first_day = date_obj.replace(day=1)
    dom = date_obj.day
    adjusted_dom = dom + first_day.weekday()
    return int((adjusted_dom - 1) / 7) + 1

def format_period_label(date_obj: datetime, period: str) -> str:
    """기간별 라벨 포맷팅"""
    if period == 'daily':
        return date_obj.strftime("%Y-%m-%d")
    elif period == 'weekly':
        year = date_obj.year
        month = date_obj.month
        week_of_month = get_week_of_month(date_obj)
        return f"{year}년 {month:02d}월 {week_of_month}주차"
    elif period == 'monthly':
        return date_obj.strftime("%Y년 %m월")
    else:
        return str(date_obj)

def validate_period(period: str) -> bool:
    """기간 타입 유효성 검사"""
    return period in ['daily', 'weekly', 'monthly', 'custom']

def get_sql_date_condition(period: str, start_date: str = None, end_date: str = None) -> tuple:
    """SQL 날짜 조건 생성"""
    if period == 'custom' and start_date and end_date:
        return "AND DATE(created_at) BETWEEN %s AND %s", [start_date, end_date]
    elif period == 'daily':
        return "AND created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)", []
    elif period == 'weekly':
        return "AND created_at >= DATE_SUB(NOW(), INTERVAL 12 WEEK)", []
    elif period == 'monthly':
        return "AND created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)", []
    else:
        return "", []

def get_sql_group_by(period: str) -> tuple:
    """SQL GROUP BY 절 생성"""
    if period == 'daily':
        return "DATE(created_at)", "DATE(created_at)"
    elif period == 'weekly':
        return "YEARWEEK(created_at, 1)", "CONCAT(YEAR(created_at), '년 ', LPAD(MONTH(created_at), 2, '0'), '월 ', (WEEK(created_at, 1) - WEEK(DATE_SUB(created_at, INTERVAL DAY(created_at)-1 DAY), 1) + 1), '주차')"
    elif period == 'monthly':
        return "DATE_FORMAT(created_at, '%%Y-%%m')", "DATE_FORMAT(created_at, '%%Y년 %%m월')"
    else:
        return "DATE(created_at)", "DATE(created_at)"

def create_response_data(data: List[Dict[str, Any]], message: str = "Success") -> Dict[str, Any]:
    """표준 응답 데이터 생성"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "count": len(data),
        "timestamp": get_current_timestamp()
    }

def create_error_response(message: str, error_code: str = "INTERNAL_ERROR") -> Dict[str, Any]:
    """에러 응답 데이터 생성"""
    return {
        "success": False,
        "message": message,
        "error_code": error_code,
        "timestamp": get_current_timestamp()
    }
