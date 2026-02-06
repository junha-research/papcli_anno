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
    
    annotations = relationship("Annotation", back_populates="essay")

class Annotation(Base):
    __tablename__ = "annotations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    essay_id = Column(Integer, ForeignKey("essays.id"), nullable=False)
    
    # Language
    score_language = Column(Integer, CheckConstraint('score_language BETWEEN 1 AND 5'))
    selected_sentences_language = Column(Text)  # JSON array
    
    # Organization
    score_organization = Column(Integer, CheckConstraint('score_organization BETWEEN 1 AND 5'))
    selected_sentences_organization = Column(Text)  # JSON array
    
    # Content
    score_content = Column(Integer, CheckConstraint('score_content BETWEEN 1 AND 5'))
    selected_sentences_content = Column(Text)  # JSON array
    
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
