from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from typing import Optional

Base = declarative_base()


class InterviewBooking(Base):
    """Interview booking table model"""
    
    __tablename__ = "interview_bookings"
    
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(100), nullable=False)
    email: str = Column(String(100), nullable=False)
    date: str = Column(String(20), nullable=False)
    time: str = Column(String(20), nullable=False)
    created_at: Optional[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    status: str = Column(String(20), default="pending")
    
    def __repr__(self) -> str:
        return f"InterviewBooking(id={self.id}, name={self.name}, email={self.email})"


class DocumentMetadata(Base):
    """Document metadata table model"""
    
    __tablename__ = "document_metadata"
    
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    filename: str = Column(String(255), nullable=False)
    file_type: str = Column(String(50), nullable=False)
    file_size: int = Column(Integer, nullable=False)
    text_length: int = Column(Integer, nullable=False)
    chunk_strategy: str = Column(String(50), nullable=False)
    chunk_size: int = Column(Integer, nullable=False)
    created_at: Optional[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    vector_id: str = Column(String(100), nullable=False)
    
    def __repr__(self) -> str:
        return f"DocumentMetadata(id={self.id}, filename={self.filename})"