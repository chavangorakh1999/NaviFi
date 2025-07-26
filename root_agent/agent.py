# wealth_agent/agent.py
from google.adk import Agent
# from google.adk.tools import google_search
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
# from google.adk import types
import os

mcp = MCPToolset(
    connection_params=StreamableHTTPServerParams(
        url=os.getenv("MCP_SERVER_URL"),
        
    ),
    tool_filter=["fetch_net_worth","fetch_credit_report","fetch_epf_details","fetch_mf_transactions","fetch_bank_transactions","fetch_stock_transactions"]
)
planning_agent_system_instruction = """
You are a Financial Planning Agent specializing in long-term financial goal planning and projections.

Your responsibilities include:
- fetch data from mcp toolset
- fetch bank transactions
- fetch epf details
- fetch mf transactions
- fetch stock transactions
- fetch credit report
- fetch net worth
- Creating retirement planning strategies
- Calculating future value projections for various scenarios
- Analyzing EPF and other retirement corpus growth
- Planning for major life goals (home purchase, education, marriage)
- Tax optimization strategies
- Emergency fund adequacy analysis
- SIP and investment planning for specific goals

Always provide timeline-based projections with clear assumptions and multiple scenarios.
Consider inflation, expected returns, and risk factors in all projections.
"""

planning_agent = Agent(
    model="gemini-2.0-flash-001",
    name="PLANNING_AGENT",
    description="Agent specialized in long-term financial planning and goal projections",
    instruction=planning_agent_system_instruction,
    tools=[mcp],
)

insights_agent_system_instruction = """
You are a Personal Financial Insights Agent specializing in behavioral finance and spending analysis.

Your responsibilities include:
- fetch data from mcp toolset
- fetch bank transactions
- fetch epf details
- fetch mf transactions
- fetch stock transactions
- fetch credit report
- fetch net worth

- Analyzing spending patterns and trends across bank transactions
- Identifying financial habits and behavioral insights
- Detecting unusual transactions or potential fraud
- Providing budgeting recommendations based on actual spending
- Tracking progress toward financial goals
- Identifying opportunities for cost optimization
- Monthly/quarterly financial health reports

Always provide personalized insights based on the user's actual transaction data and financial behavior.
Focus on actionable insights that can improve financial wellness.
"""

insights_agent = Agent(
    model="gemini-2.0-flash-001",
    name="INSIGHTS_AGENT",
    description="Agent specialized in personal financial insights and spending analysis",
    instruction=insights_agent_system_instruction,
    tools=[mcp],
)

root_agent = Agent(
    name="financial_agent",
    model="gemini-2.0-flash-001",
    description="financial_agent: personal finance agent",
    instruction="Answer finance questions using MCP data. if you want to know stocks information you can use google search tool for those stocks.",
    tools=[mcp],
    sub_agents=[
        planning_agent,
        insights_agent]
)
