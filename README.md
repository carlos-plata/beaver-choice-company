# Beaver's Choice Paper Company Multi-Agent System

A production-grade multi-agent system for inventory management, quoting, and order fulfillment using Pydantic AI framework with modular SOLID architecture.

## Features

- 7 specialized agents with intelligent coordination
- Customer negotiation capabilities
- Business intelligence and analytics
- Terminal progress visualization
- Modular design following SOLID principles

## Prerequisites

- Python 3.8+
- OpenAI API key
- Required packages (install via pip)

## Installation

1. Install required dependencies:
```bash
pip install pydantic-ai pandas sqlalchemy python-dotenv
```

2. Set up your OpenAI API key:
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env
```

## Usage

Run the complete multi-agent system:
```bash
python3 main.py
```

## System Architecture

```
├── main.py                     # Entry point and orchestration
├── agents/                     # Agent modules
│   ├── orchestrator.py         # Main coordination agent
│   ├── inventory.py            # Stock management
│   ├── quoting.py             # Quote generation
│   ├── sales.py               # Order processing
│   ├── customer_service.py    # Customer communication
│   ├── negotiation.py         # Customer negotiations
│   └── business_advisor.py    # Business intelligence
├── models/                     # Data structures
│   ├── requests.py            # Request models
│   └── responses.py           # Response models
├── utils/                      # Utility functions
│   ├── ai_model.py            # Model initialization
│   ├── animation.py           # Terminal animations
│   └── text_processing.py    # Text parsing
└── config/                     # Configuration
    └── settings.py            # System settings
```

## Expected Output

The system will:
1. Initialize the database with inventory and transaction data
2. Process 20 customer requests from `quote_requests_sample.csv`
3. Generate AI-powered responses using all specialist agents
4. Create comprehensive output files:
   - `test_results.csv` - Complete evaluation results
   - `business_recommendations.csv` - Business intelligence insights
5. Display real-time processing progress with terminal animations

## Model Recommendation

**Recommended: gpt-4o-mini**
- Cost: $0.15 input / $0.60 output per 1M tokens
- Performance: GPT-4 class intelligence
- Estimated cost for full test: ~$0.02-0.05

## Deliverables

- `diagram.svg` - Workflow diagram showing all agents and data flows
- `main.py` + modules/ - Complete modular Python implementation
- `test_results.csv` - Evaluation results from processing sample requests
- `report.md` - Comprehensive system analysis and reflection
- `business_recommendations.csv` - Business intelligence output