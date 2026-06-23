from typing import List, Literal
import re


class ChunkingService:
    """Service for chunking text using different strategies"""
    
    @staticmethod
    def chunk_fixed_size(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[dict]:
        """
        Chunk text using fixed-size strategy
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        
        # Clean and normalize text
        text = text.strip()
        if not text:
            return chunks
        
        # Split into paragraphs first
        paragraphs = text.split("\n\n")
        
        current_chunk = ""
        chunk_id = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": current_chunk.strip(),
                        "length": len(current_chunk.strip()),
                        "strategy": "fixed_size",
                        "chunk_size": chunk_size,
                    })
                    chunk_id += 1
                
                # Keep overlap
                if overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-overlap:]
                    current_chunk = overlap_text + paragraph + "\n\n"
                else:
                    current_chunk = paragraph + "\n\n"
        
        # Add last chunk
        if current_chunk.strip():
            chunks.append({
                "chunk_id": chunk_id,
                "text": current_chunk.strip(),
                "length": len(current_chunk.strip()),
                "strategy": "fixed_size",
                "chunk_size": chunk_size,
            })
        
        return chunks
    
    @staticmethod
    def chunk_semantic(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[dict]:
        """
        Chunk text using semantic strategy (by sentences/paragraphs)
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        
        # Clean and normalize text
        text = text.strip()
        if not text:
            return chunks
        
        # Split by sentences
        sentence_pattern = r'[^.!?]+[.!?]+\s*'
        sentences = re.findall(sentence_pattern, text)
        
        if not sentences:
            # If no sentences found, split by lines
            sentences = [line.strip() for line in text.split('\n') if line.strip()]
        
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": current_chunk.strip(),
                        "length": len(current_chunk.strip()),
                        "strategy": "semantic",
                        "chunk_size": chunk_size,
                    })
                    chunk_id += 1
                
                # Keep overlap
                if overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-overlap:]
                    current_chunk = overlap_text + sentence + " "
                else:
                    current_chunk = sentence + " "
        
        # Add last chunk
        if current_chunk.strip():
            chunks.append({
                "chunk_id": chunk_id,
                "text": current_chunk.strip(),
                "length": len(current_chunk.strip()),
                "strategy": "semantic",
                "chunk_size": chunk_size,
            })
        
        return chunks
    
    @staticmethod
    def chunk_text(
        text: str,
        strategy: Literal["fixed_size", "semantic"] = "fixed_size",
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[dict]:
        """
        Chunk text using specified strategy
        
        Args:
            text: Input text to chunk
            strategy: Chunking strategy ('fixed_size' or 'semantic')
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries
        """
        if strategy == "fixed_size":
            return ChunkingService.chunk_fixed_size(text, chunk_size, overlap)
        elif strategy == "semantic":
            return ChunkingService.chunk_semantic(text, chunk_size, overlap)
        else:
            raise ValueError(f"Unsupported chunk strategy: {strategy}")