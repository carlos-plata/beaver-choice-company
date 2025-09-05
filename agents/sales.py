"""
Sales Agent - Single Responsibility: Order processing and transaction management
"""

import logging
from pydantic_ai import Agent

from models.responses import OrderResponse, QuoteResponse
from project_starter import get_stock_level, create_transaction, get_cash_balance
from utils.text_processing import get_safe_response

logger = logging.getLogger(__name__)


class SalesAgent:
    """Agent responsible for finalizing sales transactions"""
    
    def __init__(self, model, animator):
        self.agent = Agent(
            model,
            system_prompt="""You are the Sales Agent for Beaver's Choice Paper Company.
            Make intelligent decisions about order processing and transactions.
            
            Your responsibilities:
            - Analyze order feasibility based on inventory and financial constraints
            - Make approval/rejection decisions with clear reasoning
            - Ensure transactions maintain business profitability
            - Provide clear explanations for all decisions
            
            Always verify inventory availability and financial impact before approving orders."""
        )
        self.animator = animator
    
    def process_order(self, quote: QuoteResponse, request_date: str) -> OrderResponse:
        """Process order with AI-powered decision making"""
        self.animator.update_step("Processing order and checking availability", "SALES AGENT")
        
        try:
            # Check current inventory
            stock_df = get_stock_level(quote.item_name, request_date)
            current_stock = int(stock_df['current_stock'].iloc[0]) if not stock_df.empty else 0
            
            # Check current cash balance
            current_balance = get_cash_balance(request_date)
            
            # AI-powered order decision
            prompt = f"""Make an intelligent order processing decision:
            
            Customer: {quote.customer_name}
            Item: {quote.item_name}
            Requested Quantity: {quote.quantity:,}
            Available Stock: {current_stock:,}
            Order Value: ${quote.total_price:.2f}
            Current Cash Balance: ${current_balance:.2f}
            Order Date: {request_date}
            
            Consider:
            - Stock availability (must have sufficient inventory)
            - Financial impact (positive cash flow)
            - Customer relationship value
            - Business risk assessment
            
            Make decision: APPROVE or REJECT with detailed business reasoning.
            IMPORTANT: Format response exactly as: DECISION|DETAILED_REASON
            Example: APPROVE|Order approved due to sufficient inventory and positive cash flow"""
            
            response = self.agent.run_sync(prompt)
            result = get_safe_response(response)
            parts = result.split('|')
            
            # Improved parsing to handle various AI response formats
            if len(parts) >= 2:
                decision = parts[0].strip().upper()
                detailed_reason = parts[1].strip()
            else:
                # Fallback parsing if no pipe separator
                result_upper = result.upper()
                if result_upper.startswith('APPROVE'):
                    decision = "APPROVE"
                    detailed_reason = result[7:].strip()  # Remove "APPROVE" prefix
                elif result_upper.startswith('REJECT'):
                    decision = "REJECT"
                    detailed_reason = result[6:].strip()  # Remove "REJECT" prefix
                else:
                    decision = "REJECT"
                    detailed_reason = "Unable to parse decision from response"
            
            # Execute decision based on AI analysis and business constraints
            if decision == "APPROVE" and current_stock >= quote.quantity:
                # Create sales transaction
                transaction_id = create_transaction(
                    item_name=quote.item_name,
                    transaction_type="sales",
                    quantity=quote.quantity,
                    price=quote.total_price,
                    date=request_date
                )
                
                return OrderResponse(
                    order_id=f"ORDER_{transaction_id}",
                    customer_name=quote.customer_name,
                    status="confirmed",
                    total_amount=quote.total_price,
                    reason=f"Order approved: {detailed_reason}",
                    transaction_id=transaction_id,
                    request_date=request_date
                )
            else:
                # Order rejection with AI reasoning
                rejection_reason = detailed_reason
                if current_stock < quote.quantity:
                    rejection_reason += f" Available stock: {current_stock:,}, Requested: {quote.quantity:,}"
                
                return OrderResponse(
                    order_id="REJECTED",
                    customer_name=quote.customer_name,
                    status="rejected",
                    total_amount=0.0,
                    reason=f"Order rejected: {rejection_reason}",
                    transaction_id=None,
                    request_date=request_date
                )
                
        except Exception as e:
            logger.error(f"Error processing order: {e}")
            return OrderResponse(
                order_id="ERROR",
                customer_name=quote.customer_name,
                status="error",
                total_amount=0.0,
                reason=f"Order processing failed: {e}",
                transaction_id=None,
                request_date=request_date
            )