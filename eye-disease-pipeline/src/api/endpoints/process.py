from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from core.logger import get_logger
from camera.capture import CameraCapture
from camera.preprocessor import ImagePreprocessor
from api.deps import get_camera, get_preprocessor

logger = get_logger(__name__)
router = APIRouter()

class ProcessResult(BaseModel):
    """처리 결과 모델"""
    timestamp: datetime
    frame_shape: tuple
    processed: bool
    message: str

@router.post("/process", response_model=ProcessResult)
async def process_frame(
    background_tasks: BackgroundTasks,
    camera: CameraCapture = Depends(get_camera),
    preprocessor: ImagePreprocessor = Depends(get_preprocessor)
):
    """
    현재 프레임 처리
    """
    try:
        # 프레임 캡처
        frame = camera.get_frame()
        if frame is None:
            raise HTTPException(status_code=500, detail="프레임 캡처 실패")
        
        # 전처리
        processed_frame = preprocessor.preprocess(frame)
        if processed_frame is None:
            raise HTTPException(status_code=500, detail="이미지 전처리 실패")
        
        # TODO: AI 모델 처리 추가
        
        return ProcessResult(
            timestamp=datetime.now(),
            frame_shape=processed_frame.shape,
            processed=True,
            message="프레임 처리 완료"
        )
        
    except Exception as e:
        logger.error(f"프레임 처리 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class BatchProcessRequest(BaseModel):
    """배치 처리 요청 모델"""
    patient_ids: List[str]

class BatchProcessResult(BaseModel):
    """배치 처리 결과 모델"""
    job_id: str
    patient_count: int
    timestamp: datetime
    message: str

@router.post("/batch-process", response_model=BatchProcessResult)
async def batch_process(
    request: BatchProcessRequest,
    background_tasks: BackgroundTasks,
    camera: CameraCapture = Depends(get_camera),
    preprocessor: ImagePreprocessor = Depends(get_preprocessor)
):
    """
    여러 프레임 배치 처리
    """
    try:
        # 작업 ID 생성
        job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 백그라운드 작업 등록
        background_tasks.add_task(
            process_batch,
            job_id,
            request.patient_ids,
            camera,
            preprocessor
        )
        
        return BatchProcessResult(
            job_id=job_id,
            patient_count=len(request.patient_ids),
            timestamp=datetime.now(),
            message="배치 처리 시작됨"
        )
        
    except Exception as e:
        logger.error(f"배치 처리 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_batch(
    job_id: str,
    patient_ids: List[str],
    camera: CameraCapture,
    preprocessor: ImagePreprocessor
):
    """
    배치 처리 백그라운드 작업
    """
    logger.info(f"배치 처리 시작 (Job ID: {job_id})")
    
    for patient_id in patient_ids:
        try:
            frame = camera.get_frame()
            if frame is not None:
                processed_frame = preprocessor.preprocess(frame)
                if processed_frame is not None:
                    # TODO: AI 모델 처리 및 결과 저장
                    logger.info(f"환자 {patient_id} 처리 완료")
                    
        except Exception as e:
            logger.error(f"환자 {patient_id} 처리 실패: {str(e)}")
    
    logger.info(f"배치 처리 완료 (Job ID: {job_id})")