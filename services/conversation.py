import redis
from typing import List, Dict, Optional
from google import genai
from google.genai import types
import json

from config.settings import settings
from services.vector_store import VectorStoreService


class ConversationService:
    """Service for managing conversation history and multi-turn queries"""
    
    def __init__(self):
        """Initialize Redis client and Gemini client"""
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
        )
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )
        self.vector_store = VectorStoreService()
        self.model = settings.GEMINI_MODEL
    
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session"""
        return f"chat_session:{session_id}"
    
    async def save_message(
        self,
        session_id: str,
        user_message: str,
        ai_message: str,
    ) -> None:
        """
        Save conversation message to Redis
        
        Args:
            session_id: Session identifier
            user_message: User's message
            ai_message: AI's response
        """
        key = self._get_session_key(session_id)
        
        message = {
            "user": user_message,
            "ai": ai_message,
            "timestamp": str(len(self.redis_client.lrange(key, 0, -1))),
        }
        
        self.redis_client.lpush(key, json.dumps(message))
        self.redis_client.expire(key, 7200)  # 2 hours TTL
    
    async def get_history(
        self,
        session_id: str,
        max_messages: int = 10,
    ) -> List[Dict]:
        """
        Get conversation history
        
        Args:
            session_id: Session identifier
            max_messages: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages
        """
        key = self._get_session_key(session_id)
        
        messages = self.redis_client.lrange(key, 0, max_messages - 1)
        
        history = []
        for msg in reversed(messages):
            history.append(json.loads(msg))
        
        return history
    
    async def create_session_id(self) -> str:
        """Create new session ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def process_query(
        self,
        query: str,
        session_id: str,
        top_k: int = 5,
    ) -> tuple[str, List[Dict], float]:
        """
        Process query with RAG and conversation history
        
        Args:
            query: User query
            session_id: Session identifier
            top_k: Number of chunks to retrieve
            
        Returns:
            Tuple of (AI response, retrieved chunks, confidence score)
        """
        # Get conversation history
        history = await self.get_history(session_id)
        
        # Build context with history
        context_messages = []
        for msg in history[-5:]:  # Last 5 messages
            context_messages.append(f"User: {msg['user']}")
            context_messages.append(f"Assistant: {msg['ai']}")
        
        context = "\n".join(context_messages)
        
        # Retrieve relevant chunks
        retrieved_chunks = await self.vector_store.search_with_documents(query, top_k)
        
        if not retrieved_chunks:
            # No chunks found, respond generically
            response = "I don't have any relevant information to answer your question."
            return response, [], 0.0
        
        # Calculate average confidence
        confidence_scores = [chunk["score"] for chunk in retrieved_chunks]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Build prompt with context
        chunk_texts = [chunk["text"] for chunk in retrieved_chunks]
        context_text = "\n\n".join(chunk_texts)
        
        prompt = f"""You are a helpful AI assistant. Answer the user's question based on the provided context.
        
Previous conversation:
{context if context else "No previous conversation"}

Context from documents:
{context_text}

User question: {query}

Please provide a clear and concise answer based only on the context above. If the context doesn't contain enough information to answer, acknowledge that limitations."""

        # Generate response using Gemini
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=500,
            ),
        )
        
        ai_response = response.text
        
        return ai_response, retrieved_chunks, avg_confidence