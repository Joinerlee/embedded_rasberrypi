from typing import Generator
from fastapi import Depends
from core.logger import get_logger
from camera.preprocessor import ImagePreprocessor
from main import camera

logger = get_logger(__name__)

def get_camera() -> Generator:
    """카메라 인스턴스 의존성"""
    try:
        yield camera
    except Exception as e:
        logger.error(f"카메라 의존성 에러: {str(e)}")
        raise

def get_preprocessor() -> Generator:
    """이미지 전처리기 의존성"""
    try:
        preprocessor = ImagePreprocessor()
        yield preprocessor
    except Exception as e:
        logger.error(f"전처리기 의존성 에러: {str(e)}")
        raise