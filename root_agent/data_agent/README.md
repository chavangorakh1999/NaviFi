# Data Agent - Financial Data Management

## Overview

The Data Agent is a specialized agent responsible for fetching, caching, and managing all financial data using the ADK context.state system. It serves as the centralized data provider for all other financial agents in the system.

## Architecture

### Key Components

1. **`agent.py`** - Main data agent implementation
2. **`instructions.py`** - System instructions for the data agent
3. **`data_utils.py`** - Utility functions for context management
4. **`example_usage.py`** - Usage examples and workflow demonstrations

### Data Flow

```
User Request → Root Agent → Data Agent (if needed) → Context.State → Other Agents
```

## Data Management Strategy

### Context Keys

All financial data is stored in `context.state` using prefixed keys:

- `data:net_worth` - Current net worth information
- `data:credit_report` - Credit report data
- `data:epf_details` - EPF (retirement fund) details
- `data:mf_transactions` - Mutual fund transaction history
- `data:bank_transactions` - Bank transaction history
- `data:stock_transactions` - Stock transaction history
- `data:last_updated` - Timestamp of last data fetch

### Caching Strategy

- **Fresh Data**: Data is considered fresh for 24 hours
- **Automatic Refresh**: Data is automatically refreshed when stale
- **On-Demand Refresh**: Data can be refreshed on explicit request
- **Error Recovery**: Failed fetches trigger individual data type refresh

## Key Features

### 1. Centralized Data Management
- Single point of data fetching using MCP tools
- Consistent data format across all agents
- Reduced redundant API calls

### 2. Context-Based Caching
- Uses ADK's `context.state` for data persistence
- Data available to all agents in the session
- Automatic timestamp tracking

### 3. Data Freshness Control
- Configurable data aging (default: 24 hours)
- Automatic stale data detection
- Manual refresh capabilities

### 4. Utility Functions
- Helper functions for consistent data access
- Built-in staleness checking
- Easy data retrieval and storage

## Usage Examples

### User Request Flow
```
User: "Help me plan for retirement"
→ Root Agent: Checks context.state for data
→ Root Agent: "DATA_AGENT: fetch all financial data" 
→ Data Agent: Calls all 6 MCP tools and caches results
→ Root Agent: "PLANNING_AGENT: analyze retirement planning"
→ Planning Agent: Uses context.state.get("data:epf_details") etc.
```

### Planning Agent Access Pattern
```python
# Planning Agent automatically receives context with cached data
def planning_analysis(context):
    # Access all cached financial data
    epf_data = context.state.get("data:epf_details")
    net_worth = context.state.get("data:net_worth") 
    bank_transactions = context.state.get("data:bank_transactions")
    
    if epf_data and net_worth:
        # Perform retirement planning calculations
        return calculate_retirement_projections(epf_data, net_worth)
    else:
        return "Please fetch financial data first"
```

### Insights Agent Access Pattern
```python
# Insights Agent automatically receives context with cached data
def spending_analysis(context):
    # Access cached transaction data (same data as Planning Agent)
    transactions = context.state.get("data:bank_transactions")
    credit_report = context.state.get("data:credit_report")
    
    if transactions:
        # Analyze spending patterns and behavior
        return analyze_spending_patterns(transactions, credit_report)
    else:
        return "No transaction data available for analysis"
```

### Data Agent Workflow
```python
# Data Agent fetches ALL MCP data when requested
def fetch_all_financial_data(context):
    # Call all MCP tools
    context.state["data:net_worth"] = fetch_net_worth()
    context.state["data:credit_report"] = fetch_credit_report()
    context.state["data:epf_details"] = fetch_epf_details()
    context.state["data:mf_transactions"] = fetch_mf_transactions()
    context.state["data:bank_transactions"] = fetch_bank_transactions()
    context.state["data:stock_transactions"] = fetch_stock_transactions()
    context.state["data:last_updated"] = current_timestamp()
    
    return "✅ All financial data cached and available"
```

## Benefits

1. **Performance**: Reduced API calls through intelligent caching
2. **Consistency**: All agents access the same data structure
3. **Reliability**: Error isolation and recovery mechanisms
4. **Maintainability**: Centralized data management logic
5. **Scalability**: Easy to add new data types and sources

## Integration with Other Agents

### Planning Agent
- Accesses cached data for financial projections
- No direct MCP tool access needed
- Requests data refresh through Data Agent

### Insights Agent
- Uses cached transaction data for analysis
- No direct MCP tool access needed
- Focuses purely on data analysis logic

### Root Agent
- Coordinates between Data Agent and specialized agents
- Maintains MCP tools for stock market queries
- Delegates data management to Data Agent

## Configuration

### Environment Variables
- `MCP_SERVER_URL` - URL for the MCP server

### Data Refresh Settings
- Default refresh interval: 24 hours
- Configurable through `max_age_hours` parameter

## Error Handling

- Individual data type fetch failures don't stop the entire process
- Graceful degradation when specific data is unavailable
- Automatic retry mechanisms for failed data fetches
- Clear error messaging for debugging

## Future Enhancements

1. **Selective Data Refresh** - Refresh only specific data types
2. **Background Refresh** - Automatic background data updates
3. **Data Versioning** - Track data changes over time
4. **Cache Optimization** - Intelligent cache size management
5. **Real-time Updates** - Integration with live data feeds 