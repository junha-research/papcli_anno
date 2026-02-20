from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./annotation.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    
    annotations = relationship("Annotation", back_populates="user")

class Essay(Base):
    __tablename__ = "essays"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    question = Column(Text, nullable=False)
    evidence = Column(Text)  # JSON array of evidence
    summary = Column(Text)   # AI feedback (reasoning, scores, etc.)
    paper_summary = Column(Text) # Actual paper summary from papers_summary.json
    
    annotations = relationship("Annotation", back_populates="essay")

class Annotation(Base):
    __tablename__ = "annotations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    essay_id = Column(Integer, ForeignKey("essays.id"), nullable=False)
    
    # ---------------------------------------------------------
    # [추가된 핵심 컬럼] 블라인드 평가 및 순서 통제용
    blind_id = Column(String, unique=True, index=True, nullable=False) # 예: #A7X9B2
    display_order = Column(Integer, nullable=False) # 1 ~ 26 번호
    # ---------------------------------------------------------
    
    # Language
    score_language = Column(Integer, CheckConstraint('score_language BETWEEN 1 AND 5'))
    selected_sentences_language = Column(Text)  # JSON array
    
    # Organization
    score_organization = Column(Integer, CheckConstraint('score_organization BETWEEN 1 AND 5'))
    selected_sentences_organization = Column(Text)  # JSON array
    
    # Content
    score_content = Column(Integer, CheckConstraint('score_content BETWEEN 1 AND 5'))
    selected_sentences_content = Column(Text)  # JSON array

    # AI Feedback
    score_ai_feedback = Column(Integer, CheckConstraint('score_ai_feedback BETWEEN 1 AND 5'))
    
    is_submitted = Column(Boolean, default=False)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    user = relationship("User", back_populates="annotations")
    essay = relationship("Essay", back_populates="annotations")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
