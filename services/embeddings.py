from google import genai
from google.genai import types
from typing import List
from config.settings import settings


class EmbeddingService:
    """Service for generating embeddings using Google Gemini"""
    
    def __init__(self):
        """Initialize Gemini client"""
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )
        self.model = settings.EMBEDDING_MODEL
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for single text using Google Gemini
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=text,
            )
            
            embedding = response.embeddings[0].values
            return embedding
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {str(e)}")
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
    
    @staticmethod
    def get_embedding_dimension() -> int:
        """
        Get embedding dimension for Gemini text-embedding-004 model
        
        Returns:
            Dimension size (for text-embedding-004: 768)
        """
        # text-embedding-004 returns 768 dimensions
        return 768