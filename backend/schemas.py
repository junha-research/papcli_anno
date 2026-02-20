from pydantic import BaseModel
from typing import Optional, List

# Auth schemas
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Essay schemas
class EssayResponse(BaseModel):
    id: int
    title: str
    content: str
    question: str
    is_annotated: bool = False
    summary: Optional[str] = None
    paper_summary: Optional[str] = None
    blind_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class EssayDetail(BaseModel):
    id: int
    title: str
    content: str
    question: str
    evidence: Optional[str] = None
    sentences: List[str]
    summary: Optional[str] = None
    paper_summary: Optional[str] = None
    blind_id: Optional[str] = None
    
    class Config:
        from_attributes = True

# Annotation schemas
class TraitAnnotation(BaseModel):
    score: Optional[int] = None
    selected_sentences: List[int] = []

class AnnotationCreate(BaseModel):
    essay_id: int
    language: TraitAnnotation
    organization: TraitAnnotation
    content: TraitAnnotation
    ai_feedback_score: Optional[int] = None

class AnnotationUpdate(BaseModel):
    language: Optional[TraitAnnotation] = None
    organization: Optional[TraitAnnotation] = None
    content: Optional[TraitAnnotation] = None
    ai_feedback_score: Optional[int] = None

class AnnotationResponse(BaseModel):
    id: int
    essay_id: int
    language: TraitAnnotation
    organization: TraitAnnotation
    content: TraitAnnotation
    ai_feedback_score: Optional[int] = None
    is_submitted: bool
    
    class Config:
        from_attributes = True

class BlindAnnotationInfo(BaseModel):
    blind_id: str
    display_order: int
    essay_id: int # Added essay_id

    class Config:
        from_attributes = True
