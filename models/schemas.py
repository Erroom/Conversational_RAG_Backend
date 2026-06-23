from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime


# Document Ingestion Schemas
class ChunkStrategyType(str):
    """Chunk strategy types"""
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"


class DocumentUploadRequest(BaseModel):
    """Request model for document upload"""
    chunk_strategy: Literal["fixed_size", "semantic"] = Field(
        default="fixed_size",
        description="Chunking strategy to use"
    )
    chunk_size: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Size of each chunk"
    )


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    success: bool = True
    message: str = "Document uploaded and processed successfully"
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (pdf/txt)")
    text_length: int = Field(..., description="Total text length")
    chunk_count: int = Field(..., description="Number of chunks created")
    chunk_strategy: str = Field(..., description="Chunking strategy used")
    embedding_count: int = Field(..., description="Number of embeddings generated")


# Conversational RAG Schemas
class ChatMessageRequest(BaseModel):
    """Request model for chat message"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: Optional[str] = Field(None, description="Chat session ID for multi-turn conversations")


class ChatMessageResponse(BaseModel):
    """Response model for chat message"""
    success: bool = True
    message: str = Field(..., description="AI response message")
    session_id: str = Field(..., description="Chat session ID")
    retrieved_chunks: List[dict] = Field(..., description="Retrieved relevant chunks")
    confidence_score: float = Field(..., description="Confidence score for retrieval")


# Interview Booking Schemas
class InterviewBookingRequest(BaseModel):
    """Request model for interview booking"""
    name: str = Field(..., min_length=1, max_length=100, description="Candidate name")
    email: str = Field(..., max_length=100, description="Candidate email")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Interview date (YYYY-MM-DD)")
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Interview time (HH:MM)")


class InterviewBookingResponse(BaseModel):
    """Response model for interview booking"""
    success: bool = True
    message: str = Field(..., description="Booking confirmation message")
    booking_id: str = Field(..., description="Unique booking identifier")
    name: str = Field(..., description="Candidate name")
    email: str = Field(..., description="Candidate email")
    date: str = Field(..., description="Interview date")
    time: str = Field(..., description="Interview time")
    status: str = Field(..., description="Booking status")


# Error Response Schema
class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")