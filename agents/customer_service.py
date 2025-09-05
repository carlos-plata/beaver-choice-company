"""
Customer Service Agent - Single Responsibility: Customer communication and response formatting
"""

import json
import logging
from pydantic_ai import Agent
from typing import Dict

from utils.text_processing import get_safe_response

logger = logging.getLogger(__name__)


class CustomerServiceAgent:
    """Agent responsible for customer communication and professional response formatting"""
    
    def __init__(self, model, animator):
        self.agent = Agent(
            model,
            system_prompt="""You are the Customer Service Agent for Beaver's Choice Paper Company.
            Create professional, personalized customer communications.
            
            Your expertise:
            - Professional business correspondence formatting
            - Clear, helpful explanations of decisions and pricing
            - Friendly, customer-focused tone
            - Complete information delivery without revealing sensitive data
            - Appropriate business letter structure and closing
            
            Always maintain professionalism while being warm and helpful."""
        )
        self.animator = animator
    
    def format_response(self, response_data: Dict, request_type: str) -> str:
        """Format professional customer response using AI"""
        self.animator.update_step("Formatting professional response", "CUSTOMER SERVICE")
        
        try:
            # Create comprehensive prompt for AI response generation
            prompt = f"""Create a professional business response letter:
            
            Response Type: {request_type}
            Customer Data: {json.dumps(response_data, indent=2)}
            
            Generate a complete, professional business letter that:
            - Uses proper business letter format
            - Addresses the customer by name professionally
            - Provides all relevant information clearly and completely
            - Uses a friendly yet professional tone
            - Includes appropriate business closing
            - Never reveals sensitive internal company information
            - Explains any decisions or pricing clearly
            - Offers additional assistance when appropriate
            
            Make the response natural, helpful, and customer-focused."""
            
            response = self.agent.run_sync(prompt)
            return get_safe_response(response)
            
        except Exception as e:
            logger.error(f"Error formatting customer response: {e}")
            # Provide fallback professional response
            customer_name = response_data.get('customer_name', 'Valued Customer')
            return f"""Dear {customer_name},

Thank you for contacting Beaver's Choice Paper Company. We appreciate your business and are committed to providing excellent service.

We will review your request and respond with detailed information shortly.

Best regards,
Beaver's Choice Paper Company
Customer Service Team"""