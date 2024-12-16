from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    author = Column(String(255), index=True)
    publication_date = Column(DateTime, nullable=True)
    file_path = Column(String(512), unique=True)
    file_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(Text)
    embedding = Column(Text)  # Store as base64 encoded string
    chunk_index = Column(Integer)
    page_number = Column(Integer, nullable=True)
    section = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    document = relationship("Document", back_populates="chunks")

# Pydantic models for API
class DocumentBase(BaseModel):
    title: str
    author: Optional[str] = None
    publication_date: Optional[datetime] = None
    file_type: str

class DocumentCreate(DocumentBase):
    file_path: str

class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChunkBase(BaseModel):
    content: str
    chunk_index: int
    page_number: Optional[int] = None
    section: Optional[str] = None

class ChunkCreate(ChunkBase):
    document_id: int
    embedding: str

class ChunkResponse(ChunkBase):
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    query: str
    filters: Optional[dict] = Field(default_factory=dict)
    top_k: int = 5
