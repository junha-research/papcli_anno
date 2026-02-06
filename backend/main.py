from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import json

from models import get_db, User, Essay, Annotation
from schemas import (
    UserLogin, Token, UserResponse,
    EssayResponse, EssayDetail,
    AnnotationCreate, AnnotationUpdate, AnnotationResponse,
    TraitAnnotation
)
from auth import (
    verify_password, create_access_token, get_current_user
)

app = FastAPI(title="Annotation Tool API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    essays = db.query(Essay).all()
    result = []
    for essay in essays:
        annotation = db.query(Annotation).filter(
            Annotation.user_id == current_user.id,
            Annotation.essay_id == essay.id
        ).first()
        result.append(EssayResponse(
            id=essay.id,
            title=essay.title,
            content=essay.content,
            question=essay.question,
            is_annotated=annotation is not None and annotation.is_submitted
        ))
    return result

@app.get("/api/essays/{essay_id}", response_model=EssayDetail)
def get_essay(essay_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    if not essay:
        raise HTTPException(status_code=404, detail="Essay not found")
    
    # Split into sentences (simple split by '. ')
    sentences = [s.strip() for s in essay.content.split('. ') if s.strip()]
    
    return EssayDetail(
        id=essay.id,
        title=essay.title,
        content=essay.content,
        question=essay.question,
        sentences=sentences
    )

# ============ ANNOTATION ENDPOINTS ============

@app.get("/api/annotations/{essay_id}")
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
