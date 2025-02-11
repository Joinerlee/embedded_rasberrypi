from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel
from core.logger import get_logger
from camera.capture import CameraCapture
from api.deps import get_camera

logger = get_logger(__name__)
router = APIRouter()

class SystemStatus(BaseModel):
    """시스템 상태 모델"""
    timestamp: datetime
    camera_status: bool
    uptime: float
    frame_count: int
    memory_usage: Dict[str, float]
    
startup_time = datetime.now()

@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    camera: CameraCapture = Depends(get_camera)
):
    """
    시스템 상태 정보 반환
    """
    try:
        import psutil
        process = psutil.Process()
        
        # 메모리 사용량 계산
        memory_info = process.memory_info()
        memory_usage = {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
        }
        
        # 가동 시간 계산
        uptime = (datetime.now() - startup_time).total_seconds()
        
        return SystemStatus(
            timestamp=datetime.now(),
            camera_status=camera.is_running,
            uptime=uptime,
            frame_count=camera.frame_queue.qsize(),
            memory_usage=memory_usage
        )
        
    except Exception as e:
        logger.error(f"상태 확인 에러: {str(e)}")
        raise

@router.post("/camera/restart")
async def restart_camera(
    camera: CameraCapture = Depends(get_camera)
):
    """
    카메라 재시작
    """
    try:
        logger.info("카메라 재시작 시도")
        camera.stop()
        success = camera.start()
        
        if success:
            logger.info("카메라 재시작 성공")
            return {"status": "success", "message": "카메라 재시작됨"}
        else:
            logger.error("카메라 재시작 실패")
            return {"status": "error", "message": "카메라 재시작 실패"}
            
    except Exception as e:
        logger.error(f"카메라 재시작 에러: {str(e)}")
        raise