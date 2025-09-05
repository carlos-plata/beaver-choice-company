"""
Response data structures for the multi-agent system
"""

from typing import Optional
from pydantic import BaseModel, Field


class QuoteResponse(BaseModel):
    """Structured response for quotes"""
    quote_id: str = Field(description="Unique identifier for the quote")
    customer_name: str = Field(description="Customer name")
    item_name: str = Field(description="Item name")
    quantity: int = Field(description="Quantity requested")
    unit_price: float = Field(description="Price per unit")
    total_price: float = Field(description="Total price including discounts")
    discount_applied: float = Field(default=0.0, description="Discount percentage applied")
    delivery_date: str = Field(description="Estimated delivery date")
    valid_until: str = Field(description="Quote expiration date")
    explanation: str = Field(description="Explanation of pricing and terms")
    negotiable: bool = Field(default=True, description="Whether price is negotiable")


class OrderResponse(BaseModel):
    """Structured response for orders"""
    order_id: str = Field(description="Unique identifier for the order")
    customer_name: str = Field(description="Customer name")
    status: str = Field(description="Order status")
    total_amount: float = Field(description="Total order amount")
    reason: str = Field(description="Explanation for status")
    transaction_id: Optional[int] = Field(description="Database transaction ID")


class InventoryResponse(BaseModel):
    """Structured response for inventory checks"""
    item_name: str = Field(description="Item name")
    current_stock: int = Field(description="Current stock level")
    status: str = Field(description="Stock status")
    reorder_recommendation: str = Field(description="Reorder recommendation")


class BusinessRecommendation(BaseModel):
    """Business advisor recommendations"""
    recommendation_type: str = Field(description="Type of recommendation")
    priority: str = Field(description="Priority level")
    description: str = Field(description="Detailed recommendation")
    expected_impact: str = Field(description="Expected business impact")