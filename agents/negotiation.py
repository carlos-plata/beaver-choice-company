"""
Customer Negotiation Agent
Single Responsibility: Price negotiation and customer relationship management
"""

import logging
from pydantic_ai import Agent
from typing import Dict

from models.requests import CustomerRequest
from models.responses import QuoteResponse
from utils.text_processing import get_safe_response

logger = logging.getLogger(__name__)


class CustomerNegotiationAgent:
    """Agent for handling price negotiations with customers - EXTRA CREDIT"""
    
    def __init__(self, model):
        self.agent = Agent(
            model,
            system_prompt="""You are the Customer Negotiation Agent for Beaver's Choice Paper Company.
            You analyze customer context and handle price negotiations intelligently.
            
            Your expertise includes:
            - Customer background analysis (job type, event type, order characteristics)
            - Negotiation potential assessment based on customer profiles
            - Strategic pricing adjustments that maintain profitability
            - Long-term customer relationship building
            
            Customer Segmentation Strategy:
            - Schools/Non-profits: Education-focused pricing, community support discounts
            - Large Corporations: Volume discounts, partnership opportunities
            - Small Businesses: Balanced affordability with profit margins
            - Government: Standard reliable pricing, consistent terms
            - Events/Entertainment: Seasonal considerations, bulk event pricing
            
            Always balance customer satisfaction with company profitability.
            Maintain minimum 20% profit margins on all negotiations."""
        )
    
    def analyze_customer_context(self, customer_request: CustomerRequest) -> Dict:
        """Analyze customer context for intelligent negotiation strategy"""
        try:
            prompt = f"""Analyze this customer for optimal negotiation strategy:
            
            Customer Profile:
            - Name: {customer_request.customer_name}
            - Job Type: {customer_request.customer_context.get('job_type', 'unknown')}
            - Event Type: {customer_request.customer_context.get('event_type', 'unknown')}  
            - Order Size: {customer_request.customer_context.get('need_size', 'unknown')}
            - Request Details: {customer_request.message}
            - Quantity: {customer_request.quantity}
            
            Provide intelligent analysis:
            1. Customer type classification (school/nonprofit/business/government/entertainment)
            2. Negotiation potential (high/medium/low) based on order size and customer type
            3. Recommended discount strategy (education/volume/standard/premium)
            4. Relationship building opportunities for long-term partnerships
            
            Format: CUSTOMER_TYPE|NEGOTIATION_POTENTIAL|DISCOUNT_STRATEGY|RELATIONSHIP_OPPORTUNITIES"""
            
            response = self.agent.run_sync(prompt)
            result = get_safe_response(response)
            parts = result.split('|')
            
            return {
                'customer_type': parts[0].strip() if len(parts) > 0 else 'business',
                'negotiation_potential': parts[1].strip() if len(parts) > 1 else 'medium',
                'discount_strategy': parts[2].strip() if len(parts) > 2 else 'standard',
                'relationship_opportunities': parts[3].strip() if len(parts) > 3 else 'standard customer service'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing customer context: {e}")
            return {
                'customer_type': 'unknown',
                'negotiation_potential': 'medium', 
                'discount_strategy': 'standard',
                'relationship_opportunities': 'basic service'
            }
    
    def negotiate_quote(self, original_quote: QuoteResponse, customer_analysis: Dict) -> QuoteResponse:
        """Negotiate quote price based on intelligent customer analysis"""
        try:
            prompt = f"""Negotiate this quote using intelligent customer insights:
            
            Original Quote Details:
            - Customer: {original_quote.customer_name}
            - Item: {original_quote.item_name}
            - Quantity: {original_quote.quantity:,}
            - Original Total: ${original_quote.total_price:.2f}
            - Current Discount: {original_quote.discount_applied*100:.1f}%
            
            Customer Intelligence:
            - Type: {customer_analysis.get('customer_type', 'unknown')}
            - Negotiation Potential: {customer_analysis.get('negotiation_potential', 'medium')}
            - Recommended Strategy: {customer_analysis.get('discount_strategy', 'standard')}
            - Relationship Value: {customer_analysis.get('relationship_opportunities', 'standard')}
            
            Provide intelligent negotiation that:
            - Maintains minimum 20% profit margin (cost basis consideration)
            - Reflects customer type and relationship value
            - Balances company profitability with customer satisfaction
            - Builds long-term business relationships
            
            Output negotiated terms:
            Format: FINAL_NEGOTIATED_PRICE|NEGOTIATION_EXPLANATION"""
            
            response = self.agent.run_sync(prompt)
            result = get_safe_response(response)
            parts = result.split('|')
            
            if len(parts) >= 2:
                try:
                    negotiated_price = float(parts[0].strip().replace('$', '').replace(',', ''))
                    negotiation_explanation = parts[1].strip()
                    
                    # Ensure minimum profitability (don't go below 80% of original price)
                    min_price = original_quote.total_price * 0.80
                    final_price = max(negotiated_price, min_price)
                    
                    # Update quote with negotiated terms
                    original_quote.total_price = final_price
                    original_quote.explanation += f" [NEGOTIATED] {negotiation_explanation}"
                    
                except ValueError as e:
                    logger.error(f"Error parsing negotiated price: {e}")
                    # Keep original quote if parsing fails
                    
            return original_quote
            
        except Exception as e:
            logger.error(f"Error in quote negotiation: {e}")
            return original_quote