"""
Request data structures for the multi-agent system
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class RequestType(Enum):
    """Types of customer requests"""
    QUOTE = "quote"
    INVENTORY_CHECK = "inventory_check"
    ORDER = "order"
    NEGOTIATION = "negotiation"
    GENERAL_INQUIRY = "general_inquiry"


@dataclass
class CustomerRequest:
    """Structure for customer requests"""
    request_id: str
    customer_name: str
    request_type: RequestType
    item_name: Optional[str]
    quantity: Optional[int]
    message: str
    request_date: str
    customer_context: Dict = None
    
    def __post_init__(self):
        if self.customer_context is None:
            self.customer_context = {}