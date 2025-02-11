from pydantic_settings import BaseSettings
from typing import Tuple
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Project Path
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    # Camera Settings
    CAMERA_DEVICE: str = "/dev/video0"
    CAMERA_RESOLUTION: str = "1920x1080"
    CAMERA_FPS: int = 30
    FRAME_QUEUE_SIZE: int = 10
    
    @property
    def camera_resolution_tuple(self) -> Tuple[int, int]:
        """해상도 문자열을 튜플로 변환"""
        width, height = map(int, self.CAMERA_RESOLUTION.split('x'))
        return (width, height)
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    
    # Firebase Settings
    FIREBASE_CREDENTIALS_PATH: str
    FIREBASE_STORAGE_BUCKET: str
    
    @property
    def firebase_credentials_absolute_path(self) -> Path:
        """Firebase 인증 파일의 절대 경로"""
        return self.BASE_DIR / self.FIREBASE_CREDENTIALS_PATH
    
    # Spring Boot Settings
    SPRING_BOOT_URL: str
    SPRING_BOOT_TIMEOUT: int = 30
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "app.log"
    
    @property
    def log_file_path(self) -> Path:
        """로그 파일의 절대 경로"""
        return self.BASE_DIR / "logs" / self.LOG_FILE
    
    # Processing Settings
    BATCH_SIZE: int = 10
    PROCESSING_TIMEOUT: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()

# 설정 인스턴스 생성
settings = get_settings()

# 필요한 디렉토리 생성
def create_required_directories():
    """필요한 디렉토리 생성"""
    directories = [
        settings.BASE_DIR / "logs",
        settings.BASE_DIR / "data",
        settings.BASE_DIR / "data" / "images",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# 설정 유효성 검사
def validate_settings():
    """설정 유효성 검사"""
    errors = []
    
    # 카메라 장치 확인
    if not os.path.exists(settings.CAMERA_DEVICE):
        errors.append(f"카메라 장치를 찾을 수 없음: {settings.CAMERA_DEVICE}")
    
    # Firebase 인증 파일 확인
    if not settings.firebase_credentials_absolute_path.exists():
        errors.append(f"Firebase 인증 파일을 찾을 수 없음: {settings.firebase_credentials_absolute_path}")
    
    # Spring Boot URL 형식 확인
    if not settings.SPRING_BOOT_URL.startswith(('http://', 'https://')):
        errors.append(f"잘못된 Spring Boot URL 형식: {settings.SPRING_BOOT_URL}")
    
    if errors:
        raise ValueError("\n".join(errors))

if __name__ == "__main__":
    # 설정 테스트
    print(f"카메라 해상도: {settings.camera_resolution_tuple}")
    print(f"Firebase 인증 파일 경로: {settings.firebase_credentials_absolute_path}")
    print(f"로그 파일 경로: {settings.log_file_path}")
    
    # 필요한 디렉토리 생성
    create_required_directories()
    
    try:
        # 설정 유효성 검사
        validate_settings()
        print("설정 유효성 검사 완료")
    except ValueError as e:
        print(f"설정 오류:\n{str(e)}")