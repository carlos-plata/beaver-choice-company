"""
Inventory Agent - Single Responsibility: Stock management and inventory analysis
"""

import logging
from pydantic_ai import Agent

from models.responses import InventoryResponse
from project_starter import get_stock_level
from utils.text_processing import get_safe_response

logger = logging.getLogger(__name__)


class InventoryAgent:
    """Agent responsible for inventory management and stock checking"""
    
    def __init__(self, model, animator):
        self.agent = Agent(
            model,
            system_prompt="""You are the Inventory Agent for Beaver's Choice Paper Company.
            Provide intelligent inventory analysis and recommendations.
            
            Analyze stock levels and provide clear, actionable recommendations
            for inventory management and reorder decisions."""
        )
        self.animator = animator
    
    def check_inventory(self, item_name: str, as_of_date: str) -> InventoryResponse:
        """Check inventory with AI analysis"""
        self.animator.update_step("Checking inventory levels", "INVENTORY AGENT")
        
        try:
            # Get actual stock level from database
            stock_df = get_stock_level(item_name, as_of_date)
            current_stock = int(stock_df['current_stock'].iloc[0]) if not stock_df.empty else 0
            
            # Use AI to analyze inventory status
            prompt = f"""Analyze inventory status:
            Item: {item_name}
            Current Stock: {current_stock}
            Date: {as_of_date}
            
            Provide status assessment and reorder recommendation.
            Consider stock levels: >1000=good, 500-1000=low, <500=critical, 0=out
            
            Format: STATUS|RECOMMENDATION"""
            
            response = self.agent.run_sync(prompt)
            result = get_safe_response(response)
            parts = result.split('|')
            
            status = parts[0].strip().lower() if len(parts) > 0 else "unknown"
            recommendation = parts[1].strip() if len(parts) > 1 else f"Current stock: {current_stock}"
            
            return InventoryResponse(
                item_name=item_name,
                current_stock=current_stock,
                status=status,
                reorder_recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Error checking inventory for {item_name}: {e}")
            return InventoryResponse(
                item_name=item_name,
                current_stock=0,
                status="error",
                reorder_recommendation=f"Error checking inventory: {e}"
            )