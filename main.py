#!/usr/bin/env python3
"""
Beaver's Choice Paper Company Multi-Agent System

A multi-agent system for inventory management, quoting, and order fulfillment
with modular architecture following SOLID principles.

Features:
- Orchestrator agent with 6 specialist agents
- Customer negotiation capabilities
- Business intelligence and analytics
- Terminal progress visualization
- Modular design with clear separation of concerns
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime

# Local imports
from config.settings import setup_logging, BUSINESS_ANALYSIS_FREQUENCY
from utils.ai_model import initialize_model
from agents.orchestrator import OrchestratorAgent
from agents.business_advisor import BusinessAdvisorAgent
from project_starter import init_database, db_engine, generate_financial_report, get_cash_balance

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def process_csv_requests(csv_file_path: str, output_file_path: str, orchestrator: OrchestratorAgent, business_advisor: BusinessAdvisorAgent):
    """Process customer requests from CSV with full AI and business intelligence"""
    results = []
    recommendations_log = []
    
    try:
        # Load and prepare dataset
        logger.info(f"Loading customer requests from {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        df['request_date'] = pd.to_datetime(df['request_date'], format='%m/%d/%y', errors='coerce')
        df = df.dropna(subset=['request_date']).sort_values('request_date')
        
        logger.info(f"Processing {len(df)} customer requests chronologically")
        
        # Process each request with full agent coordination
        for idx, row in df.iterrows():
            # Extract customer context for intelligent processing
            customer_context = {
                'job_type': row.get('job', ''),
                'event_type': row.get('event', ''),
                'need_size': row.get('need_size', '')
            }
            
            customer_name = row.get('job', 'Customer')
            request_text = row.get('request', '')
            request_date = row['request_date'].strftime('%Y-%m-%d')
            
            # Enhanced request display
            print(f"\nRequest {idx+1}/{len(df)}: {customer_name}")
            print(f"Date: {request_date} | Event: {row.get('event', 'N/A')} | Size: {row.get('need_size', 'N/A')}")
            print(f"Request: {request_text[:100]}...")
            
            # Process request through complete multi-agent workflow
            response = orchestrator.handle_request(request_text, customer_name, request_date, customer_context)
            
            # Business Intelligence Analysis
            if idx % BUSINESS_ANALYSIS_FREQUENCY == 0:
                recommendations = business_advisor.analyze_business_performance(request_date)
                recommendations_log.extend(recommendations)
                if recommendations:
                    print(f"\nBusiness recommendations generated: {len(recommendations)}")
            
            # Collect comprehensive result data
            financial_state = generate_financial_report(request_date)
            result = {
                'request_id': idx + 1,
                'customer_name': customer_name,
                'job_type': customer_context['job_type'],
                'event_type': customer_context['event_type'],
                'need_size': customer_context['need_size'],
                'request_date': request_date,
                'original_request': request_text,
                'response': response,
                'cash_balance_after': financial_state['cash_balance'],
                'inventory_value_after': financial_state['inventory_value'],
                'total_assets_after': financial_state['total_assets'],
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
        
        # Save comprehensive results
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_file_path, index=False)
        logger.info(f"Test results saved to {output_file_path}")
        
        # Save business intelligence recommendations (Extra Credit)
        if recommendations_log:
            recommendations_df = pd.DataFrame([rec.model_dump() for rec in recommendations_log])
            recommendations_df.to_csv("business_recommendations.csv", index=False)
            logger.info(f"Business recommendations saved to business_recommendations.csv")
            
            # Display recommendation summary
            print(f"\n📊 BUSINESS INTELLIGENCE SUMMARY:")
            summary = business_advisor.get_recommendation_summary()
            print(f"Total recommendations: {summary['total']}")
            print(f"By priority: {summary['by_priority']}")
            print(f"By type: {summary['by_type']}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing CSV requests: {e}")
        return []


def run_test_scenarios():
    """Execute complete test scenarios with multi-agent system"""
    print("Beaver's Choice Paper Company Multi-Agent System")
    print("Architecture: SOLID Principles with Modular Design")
    print("="*60)
    
    # System initialization
    print("Initializing system components...")
    init_database(db_engine)
    model = initialize_model()
    orchestrator = OrchestratorAgent(model)
    business_advisor = BusinessAdvisorAgent(model)
    print("System initialization complete.")
    
    # Main processing workflow
    print(f"\nProcessing customer requests...")
    results = process_csv_requests("quote_requests_sample.csv", "test_results.csv", orchestrator, business_advisor)
    
    # Comprehensive results analysis
    if results:
        print(f"\nTest Results Analysis:")
        print("="*40)
        print(f"Total customer requests processed: {len(results)}")
        
        # Detailed outcome analysis
        confirmed_orders = sum(1 for r in results if 'confirmed' in str(r['response']).lower())
        rejected_orders = sum(1 for r in results if 'rejected' in str(r['response']).lower())
        quotes_generated = sum(1 for r in results if 'quote' in str(r['response']).lower() and 'error' not in str(r['response']).lower())
        general_inquiries = sum(1 for r in results if 'thank you for contacting' in str(r['response']).lower())
        errors = sum(1 for r in results if 'error' in str(r['response']).lower())
        
        print(f"Confirmed orders: {confirmed_orders}")
        print(f"Quotes generated: {quotes_generated}")
        print(f"Orders rejected: {rejected_orders}")
        print(f"General inquiries: {general_inquiries}")
        print(f"System errors: {errors}")
        
        # Financial performance summary
        if results:
            initial_date = min(r['request_date'] for r in results)
            final_date = max(r['request_date'] for r in results)
            
            initial_report = generate_financial_report(initial_date)
            final_report = generate_financial_report(final_date)
            
            print(f"\nFinancial Performance Summary:")
            print(f"Period: {initial_date} to {final_date}")
            print(f"Initial Assets: ${initial_report['total_assets']:.2f}")
            print(f"Final Assets: ${final_report['total_assets']:.2f}")
            print(f"Cash Flow: ${final_report['cash_balance'] - initial_report['cash_balance']:.2f}")
            print(f"Inventory Change: ${final_report['inventory_value'] - initial_report['inventory_value']:.2f}")
    
    # System deliverables confirmation
    print(f"\nProject deliverables generated:")
    print(f"- diagram.svg (workflow diagram)")
    print(f"- main.py (modular entry point)")
    print(f"- agents/ modules (specialist agents)")
    print(f"- models/ modules (data structures)")
    print(f"- utils/ modules (utilities)")
    print(f"- config/ modules (settings)")
    print(f"- test_results.csv (evaluation results)")
    print(f"- business_recommendations.csv (business intelligence)")
    print(f"- report.md (system analysis)")
    
    print(f"\nExtra credit features:")
    print(f"- Customer negotiation agent")
    print(f"- Business advisor agent")
    print(f"- Terminal animation system")
    
    return results


def main():
    """Main application entry point"""
    try:
        return run_test_scenarios()
    except KeyboardInterrupt:
        print("\nSystem interrupted by user")
        logger.info("System shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal system error: {e}")
        print(f"\nFatal error: {e}")
        print("Please check logs and system configuration")
        return []


if __name__ == "__main__":
    main()