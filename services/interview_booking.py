from google import genai
from typing import Dict, Optional, List
import re
import json

from config.settings import settings
from database.connection import DatabaseService


class InterviewBookingService:
    """Service for handling interview booking via Gemini LLM"""
    
    def __init__(self):
        """Initialize Gemini client"""
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )
        self.model = settings.GEMINI_MODEL
    
    async def extract_booking_info(
        self,
        message: str,
        session_id: Optional[str] = None,
    ) -> Dict:
        """
        Extract interview booking information from message using Gemini LLM
        
        Args:
            message: User message potentially containing booking request
            session_id: Optional session ID for context
            
        Returns:
            Dictionary with extracted booking info or error
        """
        prompt = f"""Extract interview booking information from the following message.
        
Look for:
- Candidate name
- Email address
- Interview date (YYYY-MM-DD format)
- Interview time (HH:MM format)

If any information is missing, return null for that field.

Message: {message}

Return format as JSON:
{{
    "name": "string or null",
    "email": "string or null",
    "date": "YYYY-MM-DD or null",
    "time": "HH:MM or null",
    "is_booking_request": true/false
}}"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=300,
            ),
        )
        
        try:
            result = json.loads(response.text)
            return result
        except Exception as e:
            return {
                "is_booking_request": False,
                "error": f"Failed to parse Gemini response: {str(e)}",
            }
    
    async def validate_booking_info(
        self,
        booking_info: Dict,
    ) -> tuple[bool, str]:
        """
        Validate extracted booking information
        
        Args:
            booking_info: Dictionary with booking information
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not booking_info.get("is_booking_request"):
            return False, "Message is not an interview booking request"
        
        name = booking_info.get("name")
        email = booking_info.get("email")
        date = booking_info.get("date")
        time = booking_info.get("time")
        
        if not name:
            return False, "Name is missing"
        
        if not email:
            return False, "Email is missing"
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        if not date:
            return False, "Date is missing"
        
        # Validate date format
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, date):
            return False, "Invalid date format (expected YYYY-MM-DD)"
        
        if not time:
            return False, "Time is missing"
        
        # Validate time format
        time_pattern = r'^\d{2}:\d{2}$'
        if not re.match(time_pattern, time):
            return False, "Invalid time format (expected HH:MM)"
        
        return True, "Valid booking information"
    
    async def create_booking(
        self,
        name: str,
        email: str,
        date: str,
        time: str,
    ) -> Dict:
        """
        Create interview booking and store in MySQL database
        
        Args:
            name: Candidate name
            email: Candidate email
            date: Interview date
            time: Interview time
            
        Returns:
            Booking confirmation details
        """
        import uuid
        from database.connection import async_session_maker
        
        booking_id = str(uuid.uuid4())
        
        async with async_session_maker() as session:
            await DatabaseService.save_booking(
                session=session,
                name=name,
                email=email,
                date=date,
                time=time,
            )
        
        return {
            "booking_id": booking_id,
            "name": name,
            "email": email,
            "date": date,
            "time": time,
            "status": "pending",
            "confirmation": f"Interview booked for {name} on {date} at {time}",
        }
    
    async def handle_booking_request(
        self,
        message: str,
    ) -> Dict:
        """
        Handle complete booking request flow
        
        Args:
            message: User message
            
        Returns:
            Response dictionary
        """
        # Extract booking info
        booking_info = await self.extract_booking_info(message)
        
        # Validate
        is_valid, error_msg = await self.validate_booking_info(booking_info)
        
        if not is_valid:
            return {
                "success": False,
                "message": error_msg,
                "requires_more_info": True,
                "missing_fields": self._get_missing_fields(booking_info),
            }
        
        # Create booking
        booking = await self.create_booking(
            name=booking_info["name"],
            email=booking_info["email"],
            date=booking_info["date"],
            time=booking_info["time"],
        )
        
        return {
            "success": True,
            "message": booking["confirmation"],
            "booking_id": booking["booking_id"],
            "booking_details": booking,
        }
    
    def _get_missing_fields(
        self,
        booking_info: Dict,
    ) -> List[str]:
        """Get list of missing fields"""
        missing = []
        
        if not booking_info.get("name"):
            missing.append("name")
        if not booking_info.get("email"):
            missing.append("email")
        if not booking_info.get("date"):
            missing.append("date")
        if not booking_info.get("time"):
            missing.append("time")
        
        return missing