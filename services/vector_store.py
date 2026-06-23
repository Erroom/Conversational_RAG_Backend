from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from typing import List, Dict, Optional
import uuid

from config.settings import settings
from services.embeddings import EmbeddingService


class VectorStoreService:
    """Service for vector store operations using Qdrant"""
    
    def __init__(self):
        """Initialize Qdrant client"""
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY,
        )
        self.embedding_service = EmbeddingService()
        self.collection_name = settings.VECTOR_COLLECTION_NAME
        self._initialize_collection()
    
    def _initialize_collection(self) -> None:
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=EmbeddingService.get_embedding_dimension(),  # Now 768 for Gemini
                    distance=Distance.COSINE,
                ),
            )
    
    def store_vectors(
        self,
        chunks: List[dict],
        metadata: dict,
    ) -> str:
        """
        Store chunks with embeddings in vector store
        
        Args:
            chunks: List of chunk dictionaries
            metadata: Document metadata
            
        Returns:
            Vector store ID for the document
        """
        document_id = str(uuid.uuid4())
        
        points = []
        for chunk in chunks:
            embedding = self.embedding_service.generate_embedding(chunk["text"])
            
            point = PointStruct(
                id=f"{document_id}_{chunk['chunk_id']}",
                vector=embedding,
                payload={
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "chunk_length": chunk["length"],
                    "chunk_strategy": chunk["strategy"],
                    "chunk_size": chunk["chunk_size"],
                    "document_id": document_id,
                    "filename": metadata["filename"],
                    "file_type": metadata["file_type"],
                },
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        
        return document_id
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Search for similar chunks
        
        Args:
            query: Query text
            top_k: Number of results to return
            document_id: Optional filter by document ID
            
        Returns:
            List of search results with scores
        """
        query_embedding = self.embedding_service.generate_embedding(query)
        
        filter_condition = None
        if document_id:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            )
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            filter=filter_condition,
        )
        
        return [
            {
                "chunk_id": result.payload["chunk_id"],
                "text": result.payload["text"],
                "chunk_length": result.payload["chunk_length"],
                "filename": result.payload["filename"],
                "score": result.score,
            }
            for result in results
        ]
    
    def search_with_documents(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Search across all documents
        
        Args:
            query: Query text
            top_k: Number of results
            
        Returns:
            List of search results
        """
        return self.search(query, top_k)