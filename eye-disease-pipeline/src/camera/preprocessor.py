import cv2
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """이미지 전처리 클래스"""
    
    def __init__(self):
        """전처리기 초기화"""
        self._init_logging()
        # CLAHE 객체 초기화
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    
    def _init_logging(self):
        """로깅 초기화"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def preprocess(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        이미지 전처리 수행
        
        Args:
            frame: 입력 이미지 (BGR 형식)
            
        Returns:
            전처리된 이미지 또는 None
        """
        if frame is None:
            logger.warning("입력 프레임이 None입니다")
            return None
            
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 노이즈 제거
            denoised = cv2.fastNlMeansDenoising(
                gray,
                None,
                h=10,  # 필터링 강도
                templateWindowSize=7,  # 템플릿 윈도우 크기
                searchWindowSize=21  # 검색 윈도우 크기
            )
            
            # 대비 향상 (CLAHE)
            enhanced = self.clahe.apply(denoised)
            
            # 히스토그램 정규화
            normalized = cv2.normalize(
                enhanced,
                None,
                alpha=0,
                beta=255,
                norm_type=cv2.NORM_MINMAX
            )
            
            return normalized
            
        except Exception as e:
            logger.error(f"이미지 전처리 오류: {str(e)}")
            return None
    
    def crop_eye_region(
        self,
        frame: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> Optional[np.ndarray]:
        """
        눈 영역 크롭
        
        Args:
            frame: 입력 이미지
            x, y: 크롭 시작 좌표
            width, height: 크롭 영역 크기
            
        Returns:
            크롭된 이미지 또는 None
        """
        try:
            cropped = frame[y:y+height, x:x+width]
            return cropped
        except Exception as e:
            logger.error(f"눈 영역 크롭 실패: {str(e)}")
            return None

# 테스트 코드
if __name__ == "__main__":
    from capture import CameraCapture
    import time
    
    # 카메라 초기화
    camera = CameraCapture()
    preprocessor = ImagePreprocessor()
    
    if camera.start():
        try:
            # 몇 개의 프레임 테스트
            for _ in range(5):
                frame = camera.get_frame()
                if frame is not None:
                    # 전처리 테스트
                    processed = preprocessor.preprocess(frame)
                    if processed is not None:
                        print(f"전처리된 이미지 크기: {processed.shape}")
                        
                        # 테스트용 크롭
                        cropped = preprocessor.crop_eye_region(
                            processed, 100, 100, 200, 200
                        )
                        if cropped is not None:
                            print(f"크롭된 이미지 크기: {cropped.shape}")
                    
                time.sleep(1/30)
        finally:
            camera.stop()