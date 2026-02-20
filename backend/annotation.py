from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from models import get_db, Annotation, Essay, User
from auth import get_current_user
from schemas import BlindAnnotationInfo

router = APIRouter(
    prefix="/api/annotations",
    tags=["Annotations"]
)

# --- Pydantic Schemas ---

class PendingAnnotationResponse(BaseModel):
    blind_id: str
    display_order: int
    question: str
    is_submitted: bool

    class Config:
        from_attributes = True

class EvaluationTaskResponse(BaseModel):
    blind_id: str
    display_order: int
    question: str
    content: str  # 평가해야 할 에세이 본문

class EvaluationSubmitRequest(BaseModel):
    score_language: int = Field(..., ge=1, le=5)
    selected_sentences_language: Optional[str] = None
    
    score_organization: int = Field(..., ge=1, le=5)
    selected_sentences_organization: Optional[str] = None
    
    score_content: int = Field(..., ge=1, le=5)
    selected_sentences_content: Optional[str] = None
    
    score_ai_feedback: int = Field(..., ge=1, le=5)

# --- API Endpoints ---

@router.get("/pending", response_model=List[PendingAnnotationResponse])
def get_pending_evaluations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    현재 로그인한 평가자에게 할당된 평가 대기 목록을 display_order 순서대로 반환합니다.
    """
    annotations = db.query(Annotation).join(Essay).filter(
        Annotation.user_id == current_user.id,
        Annotation.is_submitted == False
    ).order_by(Annotation.display_order.asc()).all()
    
    result = []
    for ann in annotations:
        result.append({
            "blind_id": ann.blind_id,
            "display_order": ann.display_order,
            "question": ann.essay.question,
            "is_submitted": ann.is_submitted
        })
        
    return result

@router.get("/blind-ids", response_model=List[BlindAnnotationInfo])
def get_blind_annotation_ids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    현재 사용자의 모든 블라인드 ID와 에세이 ID 매핑 정보를 반환합니다.
    """
    annotations = db.query(Annotation).filter(
        Annotation.user_id == current_user.id
    ).order_by(Annotation.display_order).all()

    blind_infos = []
    for annotation in annotations:
        blind_infos.append(BlindAnnotationInfo(
            blind_id=annotation.blind_id,
            display_order=annotation.display_order,
            essay_id=annotation.essay_id
        ))
    return blind_infos

@router.get("/{blind_id}", response_model=EvaluationTaskResponse)
def get_evaluation_task(
    blind_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 blind_id의 평가 대상 문항 상세 정보를 반환합니다.
    """
    annotation = db.query(Annotation).filter(
        Annotation.blind_id == blind_id,
        Annotation.user_id == current_user.id
    ).first()
    
    if not annotation:
        raise HTTPException(status_code=404, detail="해당 평가 문항을 찾을 수 없거나 권한이 없습니다.")
        
    essay = annotation.essay
    
    return {
        "blind_id": annotation.blind_id,
        "display_order": annotation.display_order,
        "question": essay.question,
        "content": essay.content
    }

@router.put("/{blind_id}")
def submit_evaluation(
    blind_id: str,
    payload: EvaluationSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    평가자가 채점한 결과를 DB에 저장하고 제출 상태로 변경합니다.
    """
    annotation = db.query(Annotation).filter(
        Annotation.blind_id == blind_id,
        Annotation.user_id == current_user.id
    ).first()
    
    if not annotation:
        raise HTTPException(status_code=404, detail="해당 평가 문항을 찾을 수 없거나 권한이 없습니다.")
        
    if annotation.is_submitted:
        raise HTTPException(status_code=400, detail="이미 제출이 완료된 문항입니다.")

    # 제출된 점수 업데이트
    annotation.score_language = payload.score_language
    annotation.selected_sentences_language = payload.selected_sentences_language
    annotation.score_organization = payload.score_organization
    annotation.selected_sentences_organization = payload.selected_sentences_organization
    annotation.score_content = payload.score_content
    annotation.selected_sentences_content = payload.selected_sentences_content
    annotation.score_ai_feedback = payload.score_ai_feedback
    
    # 제출 상태 변경
    annotation.is_submitted = True
    
    db.commit()
    
    return {"message": "평가가 성공적으로 제출되었습니다.", "blind_id": blind_id}