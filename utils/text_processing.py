"""
Text processing utilities for the multi-agent system
"""

import re
import logging
from typing import Dict, Optional

from project_starter import paper_supplies

logger = logging.getLogger(__name__)


def find_best_item_match(search_term: str) -> Optional[Dict]:
    """Find the best matching item from paper_supplies based on search term"""
    search_term = search_term.lower()
    
    # Direct matches first
    for item in paper_supplies:
        if search_term in item['item_name'].lower():
            return item
    
    # Fuzzy matching for common terms
    fuzzy_matches = {
        'copy': 'Standard copy paper',
        'cardstock': 'Cardstock',
        'card stock': 'Cardstock', 
        'colored': 'Colored paper',
        'glossy': 'Glossy paper',
        'matte': 'Matte paper',
        'poster': 'Poster paper',
        'banner': 'Banner paper',
        'a4': 'A4 paper',
        'letter': 'Letter-sized paper',
        'envelopes': 'Envelopes',
        'napkins': 'Paper napkins',
        'cups': 'Paper cups',
        'plates': 'Paper plates'
    }
    
    for term, item_name in fuzzy_matches.items():
        if term in search_term:
            for item in paper_supplies:
                if item_name.lower() in item['item_name'].lower():
                    return item
    
    return None


def extract_quantity_from_text(text: str) -> Optional[int]:
    """Extract quantity from text using regex patterns"""
    patterns = [
        r'(\d+)\s*(?:sheets?|reams?|rolls?|pieces?|units?|packs?)',
        r'(\d+)\s*(?:of|x)',
        r'(\d{1,6})(?!\d)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def get_safe_response(agent_result) -> str:
    """Safely extract string from AgentRunResult object"""
    try:
        if hasattr(agent_result, 'data'):
            return str(agent_result.data)
        else:
            return str(agent_result)
    except Exception as e:
        logger.error(f"Error extracting agent response: {e}")
        return "Unable to process request"


def extract_items_from_multiline_request(text: str) -> list:
    """Extract multiple items from bulleted or multiline requests"""
    items = []
    
    # Look for bullet points or numbered lists
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if any(line.startswith(prefix) for prefix in ['-', '*', '•', '1.', '2.', '3.', '4.', '5.']):
            # Extract item and quantity from this line
            item = find_best_item_match(line)
            quantity = extract_quantity_from_text(line)
            
            if item and quantity:
                items.append({
                    'item_name': item['item_name'],
                    'quantity': quantity,
                    'unit_price': item['unit_price']
                })
    
    return items