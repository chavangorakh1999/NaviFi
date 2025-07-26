"""
Example usage of the Data Agent with context management

This file demonstrates how the data agent fetches and caches data,
and how other agents can access this cached data.
"""

# Example of how the DATA_AGENT would work in practice:

def example_data_agent_workflow():
    """
    Example workflow showing how the data agent manages context.state
    """
    
    # 1. User asks for financial planning
    # 2. Root agent delegates to PLANNING_AGENT
    # 3. PLANNING_AGENT checks context.state for data
    
    # Pseudocode for PLANNING_AGENT:
    """
    def planning_agent_logic(context):
        # Check if data exists in context
        net_worth = context.state.get("data:net_worth")
        bank_transactions = context.state.get("data:bank_transactions")
        
        if not net_worth or not bank_transactions:
            # Request DATA_AGENT to fetch data
            return "Requesting DATA_AGENT to fetch fresh financial data..."
        
        # Use cached data for planning
        return f"Based on your net worth of {net_worth['total']} and recent transactions..."
    """
    
    # 4. If data is missing, DATA_AGENT is called:
    """
    def data_agent_logic(context):
        from .data_utils import is_data_stale, store_data, DATA_KEYS
        
        # Check if data is stale
        if is_data_stale(context):
            # Fetch all data using MCP tools
            net_worth_data = fetch_net_worth()  # MCP tool call
            store_data(context, DATA_KEYS['NET_WORTH'], net_worth_data)
            
            bank_data = fetch_bank_transactions()  # MCP tool call
            store_data(context, DATA_KEYS['BANK_TRANSACTIONS'], bank_data)
            
            # ... fetch other data types ...
            
            return "All financial data fetched and cached successfully!"
        
        return "Data is fresh, using cached version."
    """
    
    # 5. Other agents can now access cached data:
    """
    def insights_agent_logic(context):
        from .data_utils import get_cached_data, DATA_KEYS
        
        # Access cached bank transactions
        transactions = get_cached_data(context, DATA_KEYS['BANK_TRANSACTIONS'])
        
        if transactions:
            # Analyze spending patterns
            return analyze_spending_patterns(transactions)
        else:
            return "No transaction data available for analysis"
    """

def example_context_data_structure():
    """
    Example of what the context.state would look like after data is cached
    """
    example_context_state = {
        "data:net_worth": {
            "total": 150000,
            "assets": {"savings": 50000, "investments": 75000, "property": 25000},
            "liabilities": {"loans": 0}
        },
        "data:bank_transactions": [
            {"date": "2024-01-15", "amount": -50, "description": "Grocery Store"},
            {"date": "2024-01-14", "amount": 3000, "description": "Salary Credit"},
            # ... more transactions
        ],
        "data:epf_details": {
            "balance": 200000,
            "monthly_contribution": 1500,
            "employer_contribution": 1500
        },
        "data:mf_transactions": [
            {"date": "2024-01-01", "amount": 5000, "fund": "Equity Fund", "type": "purchase"},
            # ... more MF transactions
        ],
        "data:stock_transactions": [
            {"date": "2024-01-10", "symbol": "RELIANCE", "quantity": 10, "price": 2800},
            # ... more stock transactions  
        ],
        "data:credit_report": {
            "credit_score": 750,
            "active_loans": [],
            "credit_utilization": 30
        },
        "data:last_updated": "2024-01-15T10:30:00"
    }
    
    return example_context_state

# Benefits of this approach:
"""
1. **Centralized Data Management**: All data fetching is handled by one agent
2. **Reduced API Calls**: Data is cached and reused across agents
3. **Consistent Data Format**: All agents access the same cached data structure
4. **Improved Performance**: No redundant MCP calls between agents
5. **Data Freshness Control**: Automatic refresh based on age and demand
6. **Error Isolation**: Data fetching errors are contained in the DATA_AGENT
7. **Easy Debugging**: All data operations are centralized and trackable
""" 