"""
Quoting Agent - Single Responsibility: Quote generation and pricing strategy
"""

import logging
from datetime import datetime, timedelta
from pydantic_ai import Agent

from models.requests import CustomerRequest
from models.responses import QuoteResponse
from project_starter import search_quote_history, get_supplier_delivery_date
from utils.text_processing import find_best_item_match, get_safe_response

logger = logging.getLogger(__name__)


class QuotingAgent:
    """Agent responsible for generating competitive quotes"""
    
    def __init__(self, model, animator):
        self.agent = Agent(
            model,
            system_prompt="""You are the Quoting Agent for Beaver's Choice Paper Company.
            Generate competitive, profitable quotes with clear explanations.
            
            Your expertise includes:
            - Analyzing customer needs and context
            - Applying appropriate bulk discounts
            - Considering historical pricing data
            - Providing clear pricing explanations
            - Maintaining company profitability
            
            Always balance competitiveness with profitability."""
        )
        self.animator = animator
    
    def generate_quote(self, customer_request: CustomerRequest) -> QuoteResponse:
        """Generate intelligent quote using AI"""
        self.animator.update_step("Generating competitive quote", "QUOTING AGENT")
        
        try:
            # Find matching item
            item = find_best_item_match(customer_request.item_name or "")
            if not item:
                raise ValueError(f"Item not found: {customer_request.item_name}")
            
            # Get historical context
            search_terms = [customer_request.customer_name.split()[0], item['item_name'].split()[0]]
            historical_quotes = search_quote_history(search_terms, limit=3)
            
            # Create comprehensive AI prompt for quote generation
            prompt = f"""Generate a competitive quote:
            
            Customer: {customer_request.customer_name}
            Customer Type: {customer_request.customer_context.get('job_type', 'unknown')}
            Event Type: {customer_request.customer_context.get('event_type', 'unknown')}
            Order Size Category: {customer_request.customer_context.get('need_size', 'unknown')}
            
            Item: {item['item_name']}
            Base Price: ${item['unit_price']:.3f} per unit
            Quantity: {customer_request.quantity:,}
            Historical Context: {len(historical_quotes)} similar past quotes
            
            Apply intelligent bulk discounts:
            - 1000-4999: 5% discount
            - 5000-9999: 10% discount  
            - 10000+: 15% discount
            
            Consider customer type for additional discounts:
            - Schools/Non-profits: Additional 2-3% education discount
            - Large orders: Volume relationship building
            - Government: Standard reliable pricing
            
            Format: DISCOUNT_PERCENT|FINAL_TOTAL|EXPLANATION"""
            
            response = self.agent.run_sync(prompt)
            result = get_safe_response(response)
            parts = result.split('|')
            
            # Parse AI response with fallbacks
            try:
                discount_str = parts[0].strip() if len(parts) > 0 else "5"
                discount = float(discount_str.replace('%', '')) / 100
            except:
                discount = 0.05
            
            try:
                total_str = parts[1].strip() if len(parts) > 1 else ""
                total_price = float(total_str.replace('$', '').replace(',', ''))
            except:
                base_total = customer_request.quantity * item['unit_price']
                total_price = base_total * (1 - discount)
            
            explanation = parts[2].strip() if len(parts) > 2 else "Competitive pricing with bulk discount applied"
            
            # Generate quote metadata
            quote_id = f"Q{datetime.now().strftime('%Y%m%d')}{customer_request.customer_name.replace(' ', '')[:3].upper()}{customer_request.quantity}"
            delivery_date = get_supplier_delivery_date(customer_request.request_date, customer_request.quantity)
            
            request_dt = datetime.fromisoformat(customer_request.request_date.split('T')[0])
            valid_until = (request_dt + timedelta(days=30)).strftime('%Y-%m-%d')
            
            return QuoteResponse(
                quote_id=quote_id,
                customer_name=customer_request.customer_name,
                item_name=item['item_name'],
                quantity=customer_request.quantity,
                unit_price=item['unit_price'],
                total_price=total_price,
                discount_applied=discount,
                delivery_date=delivery_date,
                valid_until=valid_until,
                explanation=explanation,
                negotiable=True
            )
            
        except Exception as e:
            logger.error(f"Error generating quote: {e}")
            return QuoteResponse(
                quote_id="ERROR",
                customer_name=customer_request.customer_name,
                item_name=customer_request.item_name or "unknown",
                quantity=customer_request.quantity or 0,
                unit_price=0.0,
                total_price=0.0,
                discount_applied=0.0,
                delivery_date="N/A",
                valid_until="N/A",
                explanation=f"Quote generation failed: {e}",
                negotiable=False
            )