"""
Orchestrator Agent - Single Responsibility: Multi-agent coordination and workflow management
"""

import logging
from typing import Dict
from pydantic_ai import Agent

from models.requests import CustomerRequest, RequestType
from project_starter import get_all_inventory
from utils.text_processing import find_best_item_match, extract_quantity_from_text, get_safe_response
from utils.animation import TerminalAnimator
from agents.inventory import InventoryAgent
from agents.quoting import QuotingAgent  
from agents.sales import SalesAgent
from agents.customer_service import CustomerServiceAgent
from agents.negotiation import CustomerNegotiationAgent
from agents.business_advisor import BusinessAdvisorAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Main orchestrator agent that coordinates all other agents"""
    
    def __init__(self, model):
        self.model = model
        self.agent = Agent(
            model,
            system_prompt="""You are the Orchestrator Agent for Beaver's Choice Paper Company.
            You intelligently coordinate between 6 specialist agents to handle customer requests.
            
            Your coordination responsibilities:
            - Analyze customer requests to determine appropriate workflow
            - Route requests to the correct specialist agents
            - Manage complex multi-agent workflows
            - Ensure complete, professional customer responses
            - Coordinate negotiation and business intelligence processes
            
            Always ensure customers receive comprehensive, professional service."""
        )
        
        # Initialize animation system (Extra Credit)
        self.animator = TerminalAnimator()
        
        # Initialize all specialist agents with proper dependency injection
        self.inventory_agent = InventoryAgent(model, self.animator)
        self.quoting_agent = QuotingAgent(model, self.animator)
        self.sales_agent = SalesAgent(model, self.animator)
        self.customer_service_agent = CustomerServiceAgent(model, self.animator)
        self.negotiation_agent = CustomerNegotiationAgent(model)
        self.business_advisor = BusinessAdvisorAgent(model)
    
    def parse_customer_request(self, request_text: str, customer_name: str, customer_context: Dict, request_date: str) -> CustomerRequest:
        """Parse customer request using AI-powered analysis"""
        try:
            # Comprehensive AI request analysis
            prompt = f"""Intelligently analyze this customer business request:
            
            Customer Information:
            - Name: {customer_name}
            - Job/Role: {customer_context.get('job_type', 'unknown')}
            - Event Type: {customer_context.get('event_type', 'unknown')}
            - Order Size Category: {customer_context.get('need_size', 'unknown')}
            
            Request Content:
            {request_text}
            
            Analyze and extract:
            1. Primary request type (quote/order/inventory_check/general_inquiry)
            2. Specific product/item mentioned (be specific about paper types)
            3. Quantity requested (extract numbers)
            
            Available products include: A4 paper, cardstock, colored paper, glossy paper, 
            matte paper, poster paper, envelopes, napkins, cups, plates, etc.
            
            Format response as: REQUEST_TYPE|PRODUCT_NAME|QUANTITY
            Use 'none' if information is not clearly specified."""
            
            response = self.agent.run_sync(prompt)
            result = get_safe_response(response)
            parts = result.split('|')
            
            # Parse AI response
            request_type_str = parts[0].strip().lower() if len(parts) > 0 else 'general_inquiry'
            item_name = parts[1].strip() if len(parts) > 1 and parts[1].strip().lower() != 'none' else None
            quantity_str = parts[2].strip() if len(parts) > 2 and parts[2].strip().lower() != 'none' else None
            
            # Convert request type to enum
            request_type_map = {
                'quote': RequestType.QUOTE,
                'order': RequestType.ORDER,
                'inventory_check': RequestType.INVENTORY_CHECK,
                'negotiation': RequestType.NEGOTIATION,
                'general_inquiry': RequestType.GENERAL_INQUIRY
            }
            request_type = request_type_map.get(request_type_str, RequestType.GENERAL_INQUIRY)
            
            # Parse quantity with fallback
            quantity = None
            if quantity_str and quantity_str.replace(',', '').replace('.', '').isdigit():
                quantity = int(float(quantity_str.replace(',', '')))
            elif quantity_str:
                quantity = extract_quantity_from_text(request_text)
            
            # If no quantity found, try extracting from original text
            if not quantity:
                quantity = extract_quantity_from_text(request_text)
            
            return CustomerRequest(
                request_id=f"req_{customer_name.replace(' ', '')[:5]}_{request_date.replace('-', '')}",
                customer_name=customer_name,
                request_type=request_type,
                item_name=item_name,
                quantity=quantity,
                message=request_text,
                request_date=request_date,
                customer_context=customer_context
            )
            
        except Exception as e:
            logger.error(f"Error in AI request parsing: {e}")
            
            # Fallback to rule-based parsing
            request_text_lower = request_text.lower()
            
            if any(keyword in request_text_lower for keyword in ['order', 'buy', 'purchase', 'place an order']):
                request_type = RequestType.ORDER
            elif any(keyword in request_text_lower for keyword in ['quote', 'price', 'cost', 'how much']):
                request_type = RequestType.QUOTE
            elif any(keyword in request_text_lower for keyword in ['stock', 'inventory', 'available', 'have']):
                request_type = RequestType.INVENTORY_CHECK
            else:
                request_type = RequestType.GENERAL_INQUIRY
            
            # Fallback item and quantity extraction
            best_item = find_best_item_match(request_text_lower)
            quantity = extract_quantity_from_text(request_text)
            
            return CustomerRequest(
                request_id=f"req_fallback_{customer_name.replace(' ', '')[:5]}_{request_date.replace('-', '')}",
                customer_name=customer_name,
                request_type=request_type,
                item_name=best_item['item_name'] if best_item else None,
                quantity=quantity,
                message=request_text,
                request_date=request_date,
                customer_context=customer_context
            )
    
    def handle_request(self, request_text: str, customer_name: str, request_date: str, customer_context: Dict = None) -> str:
        """Main orchestration method coordinating all agents"""
        try:
            # Start customer experience animation (Extra Credit)
            self.animator.start_animation(customer_name)
            
            # Default customer context
            if customer_context is None:
                customer_context = {}
                
            # AI-powered request parsing
            request = self.parse_customer_request(request_text, customer_name, customer_context, request_date)
            
            logger.info(f"Processing {request.request_type.value} request from {customer_name}")
            
            # Orchestrate appropriate workflow based on request type
            if request.request_type == RequestType.ORDER and request.item_name and request.quantity:
                # COMPLETE ORDER WORKFLOW with negotiation (Extra Credit)
                
                # Step 1: Generate initial quote
                quote = self.quoting_agent.generate_quote(request)
                
                # Step 2: Customer negotiation analysis (Extra Credit)
                customer_analysis = self.negotiation_agent.analyze_customer_context(request)
                negotiated_quote = self.negotiation_agent.negotiate_quote(quote, customer_analysis)
                
                # Step 3: Sales processing
                order = self.sales_agent.process_order(negotiated_quote, request_date)
                
                # Step 4: Professional response formatting
                response = self.customer_service_agent.format_response(order.model_dump(), "order")
                
                # Complete animation
                self.animator.complete_animation(f"Order {order.status} - ${order.total_amount:.2f}")
                return response
                
            elif request.request_type == RequestType.QUOTE and request.item_name and request.quantity:
                # QUOTE-ONLY WORKFLOW
                
                quote = self.quoting_agent.generate_quote(request)
                response = self.customer_service_agent.format_response(quote.model_dump(), "quote")
                
                self.animator.complete_animation(f"Quote generated - ${quote.total_price:.2f}")
                return response
                
            elif request.request_type == RequestType.INVENTORY_CHECK:
                # INVENTORY INQUIRY WORKFLOW
                
                if request.item_name:
                    inventory_info = self.inventory_agent.check_inventory(request.item_name, request_date)
                    response = self.customer_service_agent.format_response(inventory_info.model_dump(), "inventory")
                else:
                    # General inventory overview
                    inventory = get_all_inventory(request_date)
                    inventory_summary = {
                        'request_type': 'inventory_overview',
                        'customer_name': customer_name,
                        'total_items': len(inventory),
                        'inventory_data': dict(list(inventory.items())[:10])  # Top 10 items
                    }
                    response = self.customer_service_agent.format_response(inventory_summary, "inventory_overview")
                
                self.animator.complete_animation("Inventory status provided")
                return response
                
            else:
                # GENERAL INQUIRY WORKFLOW
                
                general_response_data = {
                    'customer_name': customer_name,
                    'request_type': 'general_inquiry',
                    'services_offered': [
                        'Custom quotes for paper products and supplies',
                        'Real-time inventory availability checks',
                        'Professional order processing and fulfillment', 
                        'Business consultation and bulk pricing',
                        'Specialized event and business supply solutions'
                    ]
                }
                
                response = self.customer_service_agent.format_response(general_response_data, "general_inquiry")
                self.animator.complete_animation("General inquiry handled professionally")
                return response
        
        except Exception as e:
            logger.error(f"Error in request orchestration: {e}")
            self.animator.complete_animation(f"Error encountered: {str(e)[:50]}")
            return f"""Dear {customer_name},

We apologize for the technical difficulty encountered while processing your request. 
Our technical team has been notified and will resolve this issue promptly.

Please contact our customer service team directly, and we will ensure your request receives immediate attention.

Best regards,
Beaver's Choice Paper Company
Technical Support Team"""