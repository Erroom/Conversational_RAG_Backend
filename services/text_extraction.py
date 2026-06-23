import aiofiles
from typing import Optional
from pypdf import PdfReader
from io import StringIO
import aiofiles


class TextExtractionService:
    """Service for extracting text from PDF and TXT files"""
    
    @staticmethod
    async def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        try:
            reader = PdfReader(file_path)
            text = ""
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    async def extract_text_from_txt(file_path: str) -> str:
        """
        Extract text from TXT file
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            File content as string
        """
        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                text = await f.read()
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from TXT: {str(e)}")
    
    @staticmethod
    async def extract_text(file_path: str, file_type: str) -> str:
        """
        Extract text from file based on type
        
        Args:
            file_path: Path to file
            file_type: File type ('pdf' or 'txt')
            
        Returns:
            Extracted text
        """
        file_type_lower = file_type.lower()
        
        if file_type_lower == "pdf":
            return await TextExtractionService.extract_text_from_pdf(file_path)
        elif file_type_lower == "txt":
            return await TextExtractionService.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Only PDF and TXT are supported.")