"""
Configuration settings for the multi-agent system
"""

import logging

# Logging configuration
def setup_logging():
    """Configure logging for the entire system"""
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# System constants
BULK_DISCOUNT_TIERS = {
    1000: 0.05,   # 5% for 1000-4999 units
    5000: 0.10,   # 10% for 5000-9999 units  
    10000: 0.15   # 15% for 10000+ units
}

QUOTE_VALIDITY_DAYS = 30
ANIMATION_DELAY = 0.5  # seconds between animation steps
BUSINESS_ANALYSIS_FREQUENCY = 5  # Generate recommendations every N requests