import logging
import logging.handlers
from pathlib import Path
from .config import settings

def setup_logger(name: str = None) -> logging.Logger:
    """
    로거 설정
    
    Args:
        name: 로거 이름 (기본값: None)
        
    Returns:
        설정된 로거 인스턴스
    """
    # 로거 생성
    logger = logging.getLogger(name or __name__)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # 이미 핸들러가 설정되어 있다면 스킵
    if logger.handlers:
        return logger
    
    # 로그 포맷 설정
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # 파일 핸들러 설정
    log_file = settings.log_file_path
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 파일 핸들러 (매일 자정에 로그 로테이션)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=30,  # 30일간 보관
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    로거 인스턴스 반환
    
    Args:
        name: 로거 이름 (기본값: None)
        
    Returns:
        로거 인스턴스
    """
    return setup_logger(name)

if __name__ == "__main__":
    # 로거 테스트
    logger = get_logger("test")
    
    logger.debug("디버그 메시지")
    logger.info("정보 메시지")
    logger.warning("경고 메시지")
    logger.error("에러 메시지")
    logger.critical("크리티컬 메시지")