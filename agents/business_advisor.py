"""
Business Advisor Agent
Single Responsibility: Business intelligence and operational recommendations
"""

import json
import logging
from typing import List, Dict
from pydantic_ai import Agent

from models.responses import BusinessRecommendation
from project_starter import generate_financial_report, get_all_inventory
from utils.text_processing import get_safe_response

logger = logging.getLogger(__name__)


class BusinessAdvisorAgent:
    """Agent that analyzes business performance and provides strategic recommendations"""
    
    def __init__(self, model):
        self.agent = Agent(
            model,
            system_prompt="""You are the Business Advisor Agent for Beaver's Choice Paper Company.
            You analyze business operations and provide strategic recommendations for improvement.
            
            Your expertise includes:
            - Financial performance analysis and optimization
            - Inventory management efficiency recommendations  
            - Revenue enhancement strategy development
            - Operational efficiency identification and improvement
            - Customer behavior pattern analysis
            - Market trend assessment and strategic planning
            
            Focus on actionable, measurable recommendations that:
            - Increase profitability and cash flow
            - Improve operational efficiency
            - Enhance customer satisfaction and retention
            - Optimize inventory turnover and reduce waste
            - Identify new revenue opportunities
            
            Provide specific, implementable business intelligence."""
        )
        self.recommendation_history = []
    
    def analyze_business_performance(self, request_date: str) -> List[BusinessRecommendation]:
        """Analyze current business performance and generate strategic recommendations"""
        try:
            # Gather comprehensive business data
            financial_report = generate_financial_report(request_date)
            inventory_data = get_all_inventory(request_date)
            
            # Create detailed business intelligence prompt
            prompt = f"""Conduct comprehensive business performance analysis:
            
            FINANCIAL PERFORMANCE:
            - Cash Balance: ${financial_report['cash_balance']:.2f}
            - Inventory Value: ${financial_report['inventory_value']:.2f}
            - Total Assets: ${financial_report['total_assets']:.2f}
            - Analysis Date: {request_date}
            
            INVENTORY ANALYSIS:
            - Total Items in Stock: {len(inventory_data)}
            - Inventory Distribution: {json.dumps(list(inventory_data.items())[:15], indent=2)}
            
            TOP PERFORMING PRODUCTS:
            {json.dumps(financial_report.get('top_selling_products', []), indent=2)}
            
            INVENTORY SUMMARY:
            {json.dumps(financial_report.get('inventory_summary', [])[:10], indent=2)}
            
            Provide 4-6 specific, actionable business recommendations covering:
            
            1. INVENTORY OPTIMIZATION
               - Identify slow-moving vs fast-moving products
               - Recommend stock level adjustments
               - Suggest product mix optimization
            
            2. REVENUE ENHANCEMENT
               - Pricing strategy improvements
               - Cross-selling opportunities
               - Customer segment targeting
            
            3. OPERATIONAL EFFICIENCY  
               - Process improvement suggestions
               - Cost reduction opportunities
               - Workflow optimization
            
            4. CUSTOMER EXPERIENCE
               - Service enhancement recommendations
               - Customer retention strategies
               - Market expansion opportunities
            
            Format each recommendation as:
            PRIORITY_LEVEL|RECOMMENDATION_TYPE|DETAILED_DESCRIPTION|EXPECTED_BUSINESS_IMPACT
            
            Separate multiple recommendations with: |||
            
            Priority levels: HIGH, MEDIUM, LOW
            Types: inventory, revenue, efficiency, customer_experience, cost_reduction"""
            
            response = self.agent.run_sync(prompt)
            result = get_safe_response(response)
            
            # Parse AI-generated recommendations
            recommendations = []
            recommendation_texts = result.split('|||')
            
            for rec_text in recommendation_texts:
                rec_text = rec_text.strip()
                if not rec_text:
                    continue
                    
                parts = rec_text.split('|')
                if len(parts) >= 4:
                    recommendation = BusinessRecommendation(
                        priority=parts[0].strip(),
                        recommendation_type=parts[1].strip(),
                        description=parts[2].strip(),
                        expected_impact=parts[3].strip()
                    )
                    recommendations.append(recommendation)
                    self.recommendation_history.append(recommendation)
            
            logger.info(f"Generated {len(recommendations)} business recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in business performance analysis: {e}")
            # Provide fallback recommendation
            fallback_recommendation = BusinessRecommendation(
                priority="MEDIUM",
                recommendation_type="system_analysis",
                description=f"Business analysis encountered technical issues. Manual review recommended for date {request_date}.",
                expected_impact="Ensure business intelligence capabilities are maintained"
            )
            return [fallback_recommendation]
    
    def get_recommendation_summary(self) -> Dict:
        """Get summary of all recommendations generated"""
        if not self.recommendation_history:
            return {"total": 0, "by_priority": {}, "by_type": {}}
        
        by_priority = {}
        by_type = {}
        
        for rec in self.recommendation_history:
            # Count by priority
            priority = rec.priority.upper()
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # Count by type
            rec_type = rec.recommendation_type.lower()
            by_type[rec_type] = by_type.get(rec_type, 0) + 1
        
        return {
            "total": len(self.recommendation_history),
            "by_priority": by_priority,
            "by_type": by_type
        }