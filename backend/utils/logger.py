"""Logging utilities"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from config.settings import settings

def setup_logging():
    """로깅 시스템 초기화"""
    # 로그 디렉토리 생성
    log_dir = Path(__file__).parent.parent / settings.log_dir
    log_dir.mkdir(exist_ok=True)
    
    # 로그 파일명 생성 (날짜_시간_main.log)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"main_{timestamp}.log"
    log_filepath = log_dir / log_filename
    
    # 로거 설정
    logger = logging.getLogger("main_backend")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 파일 핸들러 (상세 로그)
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # 콘솔 핸들러 (간단한 로그)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"로깅 시스템 초기화 완료 - 로그 파일: {log_filepath}")
    return logger

def get_logger(name: str) -> logging.Logger:
    """특정 이름의 로거 가져오기"""
    return logging.getLogger(name)

