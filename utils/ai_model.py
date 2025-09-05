"""
AI model initialization and management utilities
"""

import os
import logging
import dotenv

logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()


def initialize_model():
    """Initialize the AI model with proper configuration"""
    udacity_key = os.getenv('UDACITY_OPENAI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    if udacity_key and udacity_key != "test":
        try:
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.openai import OpenAIProvider
            
            provider = OpenAIProvider(api_key=udacity_key, base_url="https://openai.vocareum.com/v1")
            model = OpenAIChatModel(model_name, provider=provider)
            logger.info(f"Using Udacity OpenAI model: {model_name}")
            return model
        except Exception as e:
            logger.error(f"Failed to initialize Udacity OpenAI model: {e}")
    
    elif openai_key and openai_key != "test":
        try:
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.openai import OpenAIProvider
            
            provider = OpenAIProvider(api_key=openai_key)
            model = OpenAIChatModel(model_name, provider=provider)
            logger.info(f"Using OpenAI model: {model_name}")
            return model
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI model: {e}")
    
    logger.warning("No valid API key found - using test model")
    logger.warning("Create .env file with OPENAI_API_KEY=your_key_here")
    from pydantic_ai.models.test import TestModel
    return TestModel()