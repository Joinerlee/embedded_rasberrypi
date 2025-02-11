from typing import Tuple, Optional
import cv2
import numpy as np
from queue import Queue
import threading
import time
import logging

logger = logging.getLogger(__name__)

class CameraCapture:
    """OpenCV 기반 카메라 캡처 클래스"""
    
    def __init__(
        self,
        device_path: str = "0",  # 윈도우에서는 카메라 인덱스 사용
        resolution: Tuple[int, int] = (1920, 1080),
        fps: int = 30,
        queue_size: int = 10
    ):
        """
        카메라 캡처 초기화
        
        Args:
            device_path: 카메라 인덱스 또는 경로
            resolution: (width, height) 해상도
            fps: 초당 프레임 수
            queue_size: 프레임 큐 크기
        """
        self.device_path = int(device_path) if device_path.isdigit() else device_path
        self.resolution = resolution
        self.fps = fps
        self.frame_queue = Queue(maxsize=queue_size)
        self.is_running = False
        self._init_logging()
        
    def _init_logging(self):
        """로깅 초기화"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def start(self) -> bool:
        """
        카메라 캡처 시작
        
        Returns:
            bool: 시작 성공 여부
        """
        try:
            # OpenCV 비디오 캡처 객체 생성
            self.cap = cv2.VideoCapture(self.device_path)
            
            # 해상도 설정
            width, height = self.resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # FPS 설정
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # 카메라가 제대로 열렸는지 확인
            if not self.cap.isOpened():
                logger.error("카메라를 열 수 없습니다")
                return False
            
            # 실제 설정된 해상도 확인
            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(
                f"카메라 초기화 완료 - 해상도: {actual_width}x{actual_height}, "
                f"FPS: {actual_fps}"
            )
            
            # 캡처 시작
            self.is_running = True
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                daemon=True
            )
            self.capture_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"카메라 초기화 실패: {str(e)}")
            return False
    
    def _capture_loop(self):
        """프레임 캡처 루프"""
        while self.is_running and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("프레임을 읽을 수 없습니다")
                    time.sleep(0.1)
                    continue
                
                # 프레임 크기 확인
                if frame is None or frame.size == 0:
                    logger.warning("빈 프레임이 캡처됨")
                    continue
                
                # 큐가 가득 찼으면 이전 프레임 제거
                if self.frame_queue.full():
                    self.frame_queue.get()
                
                self.frame_queue.put(frame)
                
            except Exception as e:
                logger.error(f"프레임 캡처 오류: {str(e)}")
                time.sleep(0.1)
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        최신 프레임 반환
        
        Returns:
            np.ndarray: 캡처된 프레임 또는 None
        """
        try:
            frame = self.frame_queue.get(timeout=1.0)
            return frame
        except:
            logger.warning("프레임 가져오기 실패")
            return None
    
    def stop(self):
        """캡처 중지"""
        self.is_running = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=1.0)
        if hasattr(self, 'cap'):
            self.cap.release()
        logger.info("카메라 캡처 중지")

# 테스트 코드
if __name__ == "__main__":
    import signal
    import sys
    
    def signal_handler(signum, frame):
        print("\n프로그램 종료 중...")
        camera.stop()
        sys.exit(0)
    
    # Ctrl+C 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    
    # 테스트
    camera = CameraCapture(device_path="0")  # 기본 웹캠 사용
    if camera.start():
        print("테스트 시작 - Ctrl+C로 종료")
        try:
            while True:
                frame = camera.get_frame()
                if frame is not None:
                    # 프레임 크기와 타입 출력
                    print(f"프레임 크기: {frame.shape}, 타입: {frame.dtype}")
                    
                    # 프레임 표시 (테스트용)
                    cv2.imshow('Camera Test', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                        
                time.sleep(1/30)  # 30 FPS에 맞춰 대기
        finally:
            camera.stop()
            cv2.destroyAllWindows()