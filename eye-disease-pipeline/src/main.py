from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings, create_required_directories
from core.logger import get_logger
from api.endpoints import process, status
from camera.capture import CameraCapture
import uvicorn

# 로거 설정
logger = get_logger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Eye Disease Detection API",
    description="라즈베리파이 카메라를 이용한 눈 질병 감지 API",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 구체적인 오리진을 지정해야 함
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 카메라 인스턴스
camera = CameraCapture(
    device_path=settings.CAMERA_DEVICE,
    resolution=settings.camera_resolution_tuple,
    fps=settings.CAMERA_FPS,
    queue_size=settings.FRAME_QUEUE_SIZE
)

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행되는 이벤트"""
    logger.info("애플리케이션 시작")
    create_required_directories()
    
    # 카메라 시작
    if not camera.start():
        logger.error("카메라 초기화 실패")
        raise RuntimeError("카메라 초기화 실패")
    
    logger.info("카메라 초기화 완료")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행되는 이벤트"""
    logger.info("애플리케이션 종료")
    camera.stop()

# 라우터 등록
app.include_router(process.router, prefix="/api", tags=["process"])
app.include_router(status.router, prefix="/api", tags=["status"])

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "camera_status": camera.is_running
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG
    )