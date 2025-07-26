"""
Data Management Agent - Fetches and caches all financial data in context
"""
from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from .instructions import DATA_AGENT_SYSTEM_INSTRUCTION
import os

# MCP toolset configuration
mcp_data_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=os.getenv("MCP_SERVER_URL"),
    ),
    tool_filter=[
        "fetch_net_worth",
        "fetch_credit_report", 
        "fetch_epf_details",
        "fetch_mf_transactions",
        "fetch_bank_transactions",
        "fetch_stock_transactions"
    ]
)

# Data Management Agent
data_agent = Agent(
    model="gemini-1.5-flash",
    name="DATA_AGENT",
    description="Agent responsible for fetching and caching all financial data in context",
    instruction=DATA_AGENT_SYSTEM_INSTRUCTION,
    tools=[mcp_data_tools],
) 