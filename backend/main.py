from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from annotation import router as annotations_router
from typing import List
import json

from models import get_db, User, Essay, Annotation
from schemas import (
    UserLogin, Token, UserResponse,
    EssayResponse, EssayDetail,
    AnnotationCreate, AnnotationUpdate, AnnotationResponse,
    TraitAnnotation, BlindAnnotationInfo
)
from auth import (
    verify_password, create_access_token, get_current_user
)

app = FastAPI(title="Annotation Tool API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(annotations_router)
# ============ AUTH ENDPOINTS ============

@app.post("/api/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@app.get("/api/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

# ============ ESSAY ENDPOINTS ============

@app.get("/api/essays", response_model=List[EssayResponse])
def get_essays(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 해당 사용자의 어노테이션 목록을 display_order 순서로 가져옴
    annotations = db.query(Annotation).filter(
        Annotation.user_id == current_user.id
    ).order_by(Annotation.display_order.asc()).all()
    
    result = []
    for ann in annotations:
        essay = ann.essay
        result.append(EssayResponse(
            id=essay.id,
            title=f"평가 문항 #{ann.display_order}", # 블라인드 순번 제목
            content=essay.content,
            question=essay.question,
            is_annotated=ann.is_submitted,
            summary=essay.summary,
            paper_summary=essay.paper_summary,
            blind_id=ann.blind_id
        ))
    return result

@app.get("/api/essays/{essay_id}", response_model=EssayDetail)
def get_essay(essay_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    if not essay:
        raise HTTPException(status_code=404, detail="Essay not found")
    
    # [Refactored Sentence Splitter]
    import re
    raw_content = essay.content.strip()
    
    # 1. 단순 분리: 온점/물음표/느낌표 뒤에 공백이 오면 일단 분리
    # (?<=[.!?]) : 문장 부호 뒤를 보되
    # \s+(?=[A-Z가-힣]) : 뒤에 공백이 있고 그 다음에 대문자나 한글이 올 때만 분리
    split_pattern = r'(?<=[.!?])\s+(?=[A-Z가-힣])|\n'
    
    temp_sentences = [s.strip() for s in re.split(split_pattern, raw_content) if s.strip()]
    
    # 2. 예외 케이스 병합 (후처리)
    # 약어 목록 (이 단어들로 문장이 끝나면 다음 문장과 합침)
    exceptions = ('et al.', 'e.g.', 'i.e.', 'Fig.', 'vs.', 'Eq.', 'Dr.', 'Mr.', 'Mrs.', '.NET', '. NET')
    
    final_sentences = []
    for s in temp_sentences:
        if final_sentences:
            prev = final_sentences[-1]
            # 이전 문장이 약어로 끝나거나, 현재 문장이 NET 등으로 시작하면 합침
            if prev.endswith(exceptions) or s.startswith(('.NET', '. NET', 'NET')):
                final_sentences[-1] = prev + " " + s
                continue
        final_sentences.append(s)
    
    # 해당 사용자의 어노테이션 정보 조회 (블라인드 ID 및 순서 확인용)
    annotation = db.query(Annotation).filter(
        Annotation.user_id == current_user.id,
        Annotation.essay_id == essay.id
    ).first()
    
    return EssayDetail(
        id=essay.id,
        title=f"평가 문항 #{annotation.display_order}" if annotation else "평가 문항", # 블라인드 처리
        content=essay.content,
        question=essay.question,
        evidence=essay.evidence,
        sentences=final_sentences,
        summary=essay.summary,
        paper_summary=essay.paper_summary,
        blind_id=annotation.blind_id if annotation else None
    )

# ============ ANNOTATION ENDPOINTS ============

@app.get("/api/annotations/essay-data/{essay_id}")
def get_annotation(essay_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    annotation = db.query(Annotation).filter(
        Annotation.user_id == current_user.id,
        Annotation.essay_id == essay_id
    ).first()
    
    if not annotation:
        return None
    
    return AnnotationResponse(
        id=annotation.id,
        essay_id=annotation.essay_id,
        language=TraitAnnotation(
            score=annotation.score_language,
            selected_sentences=json.loads(annotation.selected_sentences_language) if annotation.selected_sentences_language else []
        ),
        organization=TraitAnnotation(
            score=annotation.score_organization,
            selected_sentences=json.loads(annotation.selected_sentences_organization) if annotation.selected_sentences_organization else []
        ),
        content=TraitAnnotation(
            score=annotation.score_content,
            selected_sentences=json.loads(annotation.selected_sentences_content) if annotation.selected_sentences_content else []
        ),
        ai_feedback_score=annotation.score_ai_feedback,
        is_submitted=annotation.is_submitted
    )

@app.post("/api/annotations", response_model=AnnotationResponse)
def create_annotation(
    data: AnnotationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if annotation already exists
    existing = db.query(Annotation).filter(
        Annotation.user_id == current_user.id,
        Annotation.essay_id == data.essay_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Annotation already exists. Use PATCH to update.")
    
    annotation = Annotation(
        user_id=current_user.id,
        essay_id=data.essay_id,
        score_language=data.language.score,
        selected_sentences_language=json.dumps(data.language.selected_sentences),
        score_organization=data.organization.score,
        selected_sentences_organization=json.dumps(data.organization.selected_sentences),
        score_content=data.content.score,
        selected_sentences_content=json.dumps(data.content.selected_sentences),
        score_ai_feedback=data.ai_feedback_score,
        is_submitted=True
    )
    
    db.add(annotation)
    db.commit()
    db.refresh(annotation)
    
    return AnnotationResponse(
        id=annotation.id,
        essay_id=annotation.essay_id,
        language=data.language,
        organization=data.organization,
        content=data.content,
        ai_feedback_score=annotation.score_ai_feedback,
        is_submitted=annotation.is_submitted
    )

@app.patch("/api/annotations/{annotation_id}", response_model=AnnotationResponse)
def update_annotation(
    annotation_id: int,
    data: AnnotationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    annotation = db.query(Annotation).filter(
        Annotation.id == annotation_id,
        Annotation.user_id == current_user.id
    ).first()
    
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    if data.language:
        annotation.score_language = data.language.score
        annotation.selected_sentences_language = json.dumps(data.language.selected_sentences)
    
    if data.organization:
        annotation.score_organization = data.organization.score
        annotation.selected_sentences_organization = json.dumps(data.organization.selected_sentences)
    
    if data.content:
        annotation.score_content = data.content.score
        annotation.selected_sentences_content = json.dumps(data.content.selected_sentences)
    
    if data.ai_feedback_score is not None:
        annotation.score_ai_feedback = data.ai_feedback_score
    
    annotation.is_submitted = True
    
    db.commit()
    db.refresh(annotation)
    
    return AnnotationResponse(
        id=annotation.id,
        essay_id=annotation.essay_id,
        language=TraitAnnotation(
            score=annotation.score_language,
            selected_sentences=json.loads(annotation.selected_sentences_language) if annotation.selected_sentences_language else []
        ),
        organization=TraitAnnotation(
            score=annotation.score_organization,
            selected_sentences=json.loads(annotation.selected_sentences_organization) if annotation.selected_sentences_organization else []
        ),
        content=TraitAnnotation(
            score=annotation.score_content,
            selected_sentences=json.loads(annotation.selected_sentences_content) if annotation.selected_sentences_content else []
        ),
        ai_feedback_score=annotation.score_ai_feedback,
        is_submitted=annotation.is_submitted
    )

@app.post("/api/annotations/submit-all")
def submit_all_annotations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    annotations = db.query(Annotation).filter(
        Annotation.user_id == current_user.id,
        Annotation.is_submitted == False
    ).all()
    
    for annotation in annotations:
        annotation.is_submitted = True
    
    db.commit()
    
    return {"submitted_count": len(annotations)}

@app.get("/")
def root():
    return {"message": "Annotation Tool API", "version": "1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
