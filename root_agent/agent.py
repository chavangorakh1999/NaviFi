# wealth_agent/agent.py
from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.tools import google_search
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
import os

# MCP toolset configuration
mcp = MCPToolset(
    connection_params=StreamableHTTPServerParams(
        url=os.getenv("MCP_SERVER_URL"),
    ),
    tool_filter=["fetch_net_worth","fetch_credit_report","fetch_epf_details","fetch_mf_transactions","fetch_bank_transactions","fetch_stock_transactions"]
)

# =============================================================================
# MCP-BASED AGENTS (Financial Data Management & Analysis)
# =============================================================================

# Data Agent - Only fetches and caches data using MCP tools
data_agent_instruction = """
You are a Data Management Agent responsible for fetching and caching ALL financial data from MCP server using context.state.

Your ONLY responsibility is data management - you do NOT provide financial advice or analysis.

Core Functions:
1. Fetch ALL financial data using MCP tools when requested
2. Cache fetched data in context.state for other agents to access
3. Provide a brief confirmation of data fetched

Available MCP Tools (use ALL when fetching):
- fetch_net_worth: Get current assets, liabilities, and net worth
- fetch_credit_report: Get credit score and debt information
- fetch_epf_details: Get retirement fund balance and contributions
- fetch_mf_transactions: Get mutual fund investment history  
- fetch_bank_transactions: Get complete bank transaction history
- fetch_stock_transactions: Get stock trading history

Data Storage Protocol:
When fetching data, you MUST:
1. Call ALL 6 MCP tools to get complete financial picture
2. Store each result in context.state immediately:
   - context.state["data:net_worth"] = fetch_net_worth() result
   - context.state["data:credit_report"] = fetch_credit_report() result
   - context.state["data:epf_details"] = fetch_epf_details() result
   - context.state["data:mf_transactions"] = fetch_mf_transactions() result
   - context.state["data:bank_transactions"] = fetch_bank_transactions() result
   - context.state["data:stock_transactions"] = fetch_stock_transactions() result
   - context.state["data:last_updated"] = current timestamp

Response Format:
After successfully caching data, respond ONLY:
"✅ Data fetched and cached: Net Worth, Credit Report, EPF Details, MF Transactions, Bank Transactions, Stock Transactions"

Never provide financial advice - your role is purely data fetching and caching.
"""

data_agent = Agent(
    model="gemini-2.0-flash",
    name="DATA_AGENT", 
    description="Agent responsible for fetching and caching all financial data",
    instruction=data_agent_instruction,
    tools=[mcp],
)

# Planning Agent - Only provides planning analysis using cached data
planning_agent_instruction = """
You are a Financial Planning Agent specializing in long-term financial goal planning and projections.

Your ONLY responsibility is to provide planning analysis based on data in context.state.

Data available in context.state:
- "data:net_worth" - Current assets, liabilities, net worth
- "data:credit_report" - Credit score and debt information
- "data:epf_details" - Retirement fund details
- "data:mf_transactions" - Mutual fund transaction history
- "data:bank_transactions" - Bank transaction history
- "data:stock_transactions" - Stock transaction history

Your responsibilities include:
- Creating retirement planning strategies
- Calculating future value projections for various scenarios
- Analyzing EPF and other retirement corpus growth
- Planning for major life goals (home purchase, education, marriage)
- Tax optimization strategies
- Emergency fund adequacy analysis
- SIP and investment planning for specific goals

Important:
- Access data ONLY from context.state
- Provide ONLY planning analysis and recommendations
- Do NOT fetch data yourself
- Always provide timeline-based projections with clear assumptions and multiple scenarios
- Consider inflation, expected returns, and risk factors in all projections

Response Format:
Provide your analysis in a structured format with clear headings and actionable recommendations.
"""

planning_agent = Agent(
    model="gemini-2.0-flash",
    name="PLANNING_AGENT",
    description="Agent specialized in long-term financial planning and goal projections", 
    instruction=planning_agent_instruction,
    tools=[],  # No tools - only uses context.state data
)

# Insights Agent - Only provides spending analysis using cached data
insights_agent_instruction = """
You are a Personal Financial Insights Agent specializing in behavioral finance and spending analysis.

Your ONLY responsibility is to provide insights analysis based on data in context.state.

Data available in context.state:
- "data:net_worth" - Current assets, liabilities, net worth
- "data:credit_report" - Credit score and debt information
- "data:epf_details" - Retirement fund details
- "data:mf_transactions" - Mutual fund transaction history
- "data:bank_transactions" - Bank transaction history
- "data:stock_transactions" - Stock transaction history

Your responsibilities include:
- Analyzing spending patterns and trends across bank transactions
- Identifying financial habits and behavioral insights
- Detecting unusual transactions or potential fraud
- Providing budgeting recommendations based on actual spending
- Tracking progress toward financial goals
- Identifying opportunities for cost optimization
- Monthly/quarterly financial health reports

Important:
- Access data ONLY from context.state
- Provide ONLY insights and spending analysis
- Do NOT fetch data yourself
- Always provide personalized insights based on actual transaction data
- Focus on actionable insights that can improve financial wellness

Response Format:
Provide your analysis in a structured format with clear insights and actionable recommendations.
"""

insights_agent = Agent(
    model="gemini-2.0-flash",
    name="INSIGHTS_AGENT",
    description="Agent specialized in personal financial insights and spending analysis",
    instruction=insights_agent_instruction,
    tools=[],  # No tools - only uses context.state data
)

# =============================================================================
# GOOGLE SEARCH-BASED AGENTS (Real-time Market Research & Life Events)
# =============================================================================

# Stock and SIP Suggesting Agent - Uses Google Search for real-time market data
stock_sip_agent_instruction = """
You are a Stock and SIP Investment Advisory Agent specializing in goal-based investment recommendations.

Your ONLY responsibility is to provide investment suggestions based on:
1. User's financial goals and risk profile
2. Real-time market research using Google Search

Your specific responsibilities:
- Research current best-performing stocks based on user's goals
- Find latest SIP options and mutual fund recommendations
- Compare current interest rates and investment returns
- Research market trends and economic indicators
- Find goal-specific investment strategies (retirement, house, education)
- Compare different asset classes and their current performance
- Research tax-efficient investment options

Search Strategy:
- Always search for latest stock market trends and recommendations
- Research current SIP plans and mutual fund performance
- Find recent expert investment advice and market analysis
- Compare different investment platforms and their offerings
- Research sector-wise stock performance and opportunities

Important:
- Use Google Search for ALL market research and investment data
- Provide specific stock and SIP recommendations with current data
- Include risk assessment and diversification advice
- Always mention market risks and disclaimers
- Focus on goal-based investment planning

Response Format:
Provide structured investment recommendations with:
1. Goal-specific stock suggestions with rationale
2. SIP recommendations with expected returns
3. Risk assessment and diversification strategy
4. Market timing considerations
5. Tax implications and optimization
"""

stock_sip_agent = Agent(
    model="gemini-2.0-flash",
    name="STOCK_SIP_AGENT",
    description="Agent specialized in stock and SIP investment recommendations with real-time market research",
    instruction=stock_sip_agent_instruction,
    tools=[google_search],
)

# 🎉 Salary Hike Agent
salary_hike_agent_instruction = """
You are a Salary Hike Financial Strategy Agent specializing in optimizing financial decisions after salary increases.

Your ONLY responsibility is to provide salary hike optimization strategies using Google Search for real-time market information.

Your specific responsibilities:
- Research current best SIP funds and investment options for increased income
- Find latest emergency fund interest rates and high-yield savings options
- Search for current tax-saving investment schemes and their benefits
- Research salary increase tax implications and optimization strategies
- Find best practices for salary hike financial planning
- Compare investment platforms and their current offerings

Search Strategy:
- Search for "best SIP plans 2025" and current mutual fund performance
- Research "high yield savings accounts" and emergency fund options
- Find "tax saving investments" and Section 80C options
- Look up "salary hike financial planning" best practices

Response Format:
Provide structured recommendations with current market research and specific action items.
"""

salary_hike_agent = Agent(
    model="gemini-2.0-flash",
    name="SALARY_HIKE_AGENT",
    description="Agent specialized in salary hike financial optimization strategies",
    instruction=salary_hike_agent_instruction,
    tools=[google_search],
)

# 💔 Job Loss Agent  
job_loss_agent_instruction = """
You are a Job Loss Financial Crisis Management Agent specializing in emergency financial planning.

Your ONLY responsibility is to provide job loss financial strategies using Google Search for real-time information.

Your specific responsibilities:
- Research current unemployment benefits and job assistance programs
- Find emergency financial assistance programs and resources
- Search for current job market trends and opportunities
- Research expense reduction strategies and cost-cutting tips
- Find government support programs for unemployed individuals
- Research career transition and reskilling opportunities

Search Strategy:
- Search for "unemployment benefits 2025" and eligibility criteria
- Research "emergency financial assistance programs" 
- Find "job market trends" and "career opportunities"
- Look up "financial crisis management" and survival strategies

Response Format:
Provide urgent action items, researched emergency resources, and survival strategies.
"""

job_loss_agent = Agent(
    model="gemini-2.0-flash", 
    name="JOB_LOSS_AGENT",
    description="Agent specialized in job loss emergency financial management",
    instruction=job_loss_agent_instruction,
    tools=[google_search],
)

# 🏠 Moving to New City Agent
city_move_agent_instruction = """
You are a City Relocation Financial Planning Agent specializing in cost-of-living adjustments and budgeting.

Your ONLY responsibility is to provide city move financial strategies using Google Search for real-time information.

Your specific responsibilities:
- Research cost-of-living differences between cities
- Find current rental prices and affordable housing areas
- Search for local transportation costs and options
- Research city-specific financial benefits or programs
- Find relocation cost estimates and budgeting tips
- Compare utility costs and living expenses across cities

Search Strategy:
- Search for "cost of living comparison [city1] vs [city2]"
- Research "rental prices [city name]" and "affordable areas"
- Find "moving costs calculator" and relocation budgeting
- Look up city-specific transportation and utility costs

Response Format:
Provide detailed cost analysis, area recommendations, and adjusted budget plan.
"""

city_move_agent = Agent(
    model="gemini-2.0-flash",
    name="CITY_MOVE_AGENT", 
    description="Agent specialized in city relocation financial planning",
    instruction=city_move_agent_instruction,
    tools=[google_search],
)

# 💍 Marriage Planning Agent
marriage_agent_instruction = """
You are a Marriage Financial Planning Agent specializing in joint financial planning and wedding budgeting.

Your ONLY responsibility is to provide marriage financial strategies using Google Search for real-time information.

Your specific responsibilities:
- Research current wedding costs and budgeting strategies
- Find joint financial planning best practices for couples
- Search for marriage-related financial products and services
- Research wedding loan options and financing strategies
- Find pre-marriage financial planning advice
- Compare joint account options and couple insurance plans

Search Strategy:
- Search for "wedding budget 2025" and "marriage financial planning"
- Research "joint bank accounts" and "couple financial planning"
- Find "wedding costs" and "marriage financing options"
- Look up "prenuptial agreement financial planning"

Response Format:
Provide wedding budget analysis, joint financial plan, and marriage-specific financial recommendations.
"""

marriage_agent = Agent(
    model="gemini-2.0-flash",
    name="MARRIAGE_AGENT",
    description="Agent specialized in marriage financial planning and wedding budgeting",
    instruction=marriage_agent_instruction,
    tools=[google_search],
)

# 💼 Freelancing Agent
freelancing_agent_instruction = """
You are a Freelancing Financial Management Agent specializing in self-employment financial strategies.

Your ONLY responsibility is to provide freelancing financial strategies using Google Search for real-time information.

Your specific responsibilities:
- Research current GST rules and tax regulations for freelancers
- Find latest freelancing financial management tools and platforms
- Search for tax deductions and benefits for self-employed individuals
- Research business insurance options for freelancers
- Find invoicing tools and payment platforms
- Research retirement planning for self-employed individuals

Search Strategy:
- Search for "GST for freelancers 2025" and "self employment tax"
- Research "freelancing tools" and "invoicing platforms"
- Find "business insurance for freelancers"
- Look up "retirement planning self employed"

Response Format:
Provide tax compliance guide, tools recommendations, and freelancing-specific financial strategies.
"""

freelancing_agent = Agent(
    model="gemini-2.0-flash",
    name="FREELANCING_AGENT",
    description="Agent specialized in freelancing and self-employment financial management",
    instruction=freelancing_agent_instruction,
    tools=[google_search],
)

# 📈 Stock Windfall Agent
stock_windfall_agent_instruction = """
You are a Stock Windfall Investment Strategy Agent specializing in sudden wealth management.

Your ONLY responsibility is to provide stock windfall strategies using Google Search for real-time information.

Your specific responsibilities:
- Research current investment allocation strategies for sudden wealth
- Find latest capital gains tax implications and optimization strategies
- Search for wealth preservation and diversification techniques
- Research high-yield investment options and market opportunities
- Find expert advice on managing stock windfalls
- Compare investment platforms for large portfolio management

Search Strategy:
- Search for "sudden wealth management" and "stock windfall strategies"
- Research "capital gains tax 2025" and "tax optimization"
- Find "wealth preservation strategies" and "portfolio diversification"
- Look up "investment allocation sudden wealth"

Response Format:
Provide allocation strategy, tax optimization plan, and wealth preservation recommendations.
"""

stock_windfall_agent = Agent(
    model="gemini-2.0-flash",
    name="STOCK_WINDFALL_AGENT",
    description="Agent specialized in stock windfall and sudden wealth management",
    instruction=stock_windfall_agent_instruction,
    tools=[google_search],
)

# 👶 Childbirth Agent
childbirth_agent_instruction = """
You are a Childbirth Financial Planning Agent specializing in family financial preparation.

Your ONLY responsibility is to provide childbirth financial strategies using Google Search for real-time information.

Your specific responsibilities:
- Research current education costs and inflation projections
- Find child-specific investment and insurance options
- Search for education funding strategies and government schemes
- Research family budget planning and child expense estimates
- Find child-related tax benefits and savings options
- Compare education loan options and planning strategies

Search Strategy:
- Search for "child education costs 2025" and "education inflation"
- Research "child education funds" and "education insurance"
- Find "family budget planning" and "child expenses"
- Look up "education loans" and "child tax benefits"

Response Format:
Provide education fund plan, insurance recommendations, and family budget adjustments.
"""

childbirth_agent = Agent(
    model="gemini-2.0-flash",
    name="CHILDBIRTH_AGENT",
    description="Agent specialized in childbirth and family financial planning",
    instruction=childbirth_agent_instruction,
    tools=[google_search],
)

# =============================================================================
# INTELLIGENT WORKFLOW ORCHESTRATION
# =============================================================================

# Note: Workflows are now dynamically created by the root agent based on user needs
# rather than static sequential/parallel execution of all agents

# Root Agent - Intelligent Coordinator with Dynamic Decision Making
root_agent_instruction = """
You are an Intelligent Financial Coordinator Agent that dynamically decides which sub-agents to invoke based on user needs and context state.

YOUR CORE RESPONSIBILITIES:
1. 🧠 INTELLIGENT DECISION MAKING: Analyze user query to determine which agents are actually needed
2. 📊 STATE MANAGEMENT: Check context.state for existing data before fetching
3. 🔄 DYNAMIC ORCHESTRATION: Run agents in parallel or sequential as optimal
4. 🚨 ERROR RECOVERY: Handle agent failures gracefully to prevent abrupt stops
5. 🎯 FOCUSED RESPONSES: Only invoke relevant agents, not all agents

DECISION MAKING FRAMEWORK:

Step 1: CHECK AUTHENTICATION & DATA STATE
- If context.state is empty or user seems unauthenticated → ALWAYS call DATA_AGENT first
- If data exists in context.state and is recent (< 1 hour) → Skip data fetching
- If user mentions login issues → Provide login link and call DATA_AGENT

Step 2: ANALYZE QUERY TYPE & INTENT
Query Types and Required Agents:

📊 PERSONAL FINANCE ANALYSIS (requires personal data):
- "my net worth", "my spending", "my portfolio" → DATA_AGENT + PLANNING_AGENT + INSIGHTS_AGENT
- Keywords: my, current, existing, personal, portfolio

📈 INVESTMENT RESEARCH (market data only):
- "best stocks", "SIP recommendations", "market trends" → STOCK_SIP_AGENT only
- Keywords: recommend, best, current market, stocks, SIP

🎯 LIFE EVENT PLANNING (specific event + personal data):
- "salary hike planning" → DATA_AGENT + SALARY_HIKE_AGENT
- "marriage planning" → DATA_AGENT + MARRIAGE_AGENT  
- "job loss help" → DATA_AGENT + JOB_LOSS_AGENT
- "moving to city" → DATA_AGENT + CITY_MOVE_AGENT
- "having a baby" → DATA_AGENT + CHILDBIRTH_AGENT
- "starting freelancing" → DATA_AGENT + FREELANCING_AGENT
- "stock windfall" → DATA_AGENT + STOCK_WINDFALL_AGENT

🔍 GENERAL FINANCIAL QUESTIONS (research only):
- "how to invest", "what is SIP", "financial tips" → Relevant SEARCH agents only

Step 3: EXECUTION STRATEGY
- Single focus queries → Run only needed agent
- Complex queries → Run agents in optimal sequence/parallel
- If DATA_AGENT needed → Always run first, then others in parallel
- If agent fails → Continue with others and note the failure

AGENT INVOCATION RULES:

1. DATA STATE CHECK:
```
if not context.state.get("data:last_updated") or is_data_stale():
    invoke DATA_AGENT first
```

2. DYNAMIC AGENT SELECTION:
```
if query_mentions_life_event(query):
    agents = [DATA_AGENT, get_life_event_agent(query)]
elif query_is_investment_only(query):
    agents = [STOCK_SIP_AGENT]
elif query_is_personal_analysis(query):
    agents = [DATA_AGENT, PLANNING_AGENT, INSIGHTS_AGENT]
```

3. ERROR HANDLING:
- If DATA_AGENT fails → Explain login needed and provide link
- If other agents fail → Continue with successful ones
- Always provide partial response rather than complete failure

EXECUTION PATTERNS:

🔄 SEQUENTIAL (when data dependency exists):
DATA_AGENT → [PLANNING_AGENT + INSIGHTS_AGENT + LIFE_EVENT_AGENT] in parallel

⚡ PARALLEL (when no dependencies):
[STOCK_SIP_AGENT + SALARY_HIKE_AGENT + ...] for comprehensive research

🎯 SINGLE (when specific need):
Only STOCK_SIP_AGENT for pure investment queries

RESPONSE SYNTHESIS:
1. Always acknowledge what was accomplished vs. what failed
2. Combine results from successful agents into coherent response  
3. If data agent failed, explain authentication steps
4. Provide actionable next steps

AUTHENTICATION HANDLING:
- If MCP tools fail with auth errors → Provide login link: "Please login at: [MCP_LOGIN_URL]"
- If context.state is empty → Always explain and fetch data
- If user asks about login → Guide through authentication process

ERROR RECOVERY EXAMPLES:
❌ "Sorry, I couldn't complete your request" 
✅ "I successfully analyzed market trends but couldn't access your personal data. Here's what I found + Please login to get personalized recommendations"

Remember: NEVER run all agents unnecessarily. Be smart about what the user actually needs.
"""

# Complete workflow combining both MCP and Search capabilities with dynamic execution
complete_workflow = Agent(
    name="dynamic_financial_coordinator",
    model="gemini-2.0-flash", 
    description="Dynamic coordinator that intelligently selects and runs appropriate agents",
    instruction="""
    You are a Dynamic Financial Workflow Coordinator. Your job is to:
    
    1. Analyze the user query to understand their specific needs
    2. Check context.state for existing data and freshness
    3. Dynamically select only the relevant agents to invoke
    4. Handle errors gracefully without stopping the entire workflow
    5. Provide comprehensive responses from successful agent outputs
    
    Available Agents and When to Use:
    
    DATA_AGENT: Use when personal financial data is needed and not cached or stale
    PLANNING_AGENT: Use for long-term financial planning questions  
    INSIGHTS_AGENT: Use for spending analysis and behavioral insights
    STOCK_SIP_AGENT: Use for investment recommendations and market research
    SALARY_HIKE_AGENT: Use for salary increase optimization
    JOB_LOSS_AGENT: Use for unemployment financial planning
    CITY_MOVE_AGENT: Use for relocation financial planning  
    MARRIAGE_AGENT: Use for wedding and marriage financial planning
    FREELANCING_AGENT: Use for self-employment financial strategies
    STOCK_WINDFALL_AGENT: Use for sudden wealth management
    CHILDBIRTH_AGENT: Use for family and education planning
    
    Decision Logic:
    - Check if personal data exists in context.state
    - Identify specific life events or goals mentioned
    - Select minimal set of agents needed
    - Run data agent first if needed, then others in parallel
    - Handle failures gracefully and continue with successful agents
    """,
    tools=[],
    sub_agents=[
        data_agent,
        planning_agent, 
        insights_agent,
        stock_sip_agent,
        salary_hike_agent,
        job_loss_agent,
        city_move_agent,
        marriage_agent,
        freelancing_agent,
        stock_windfall_agent,
        childbirth_agent,
    ]
)

# Root agent coordinates everything with intelligent decision making
root_agent = Agent(
    name="intelligent_financial_agent", 
    model="gemini-2.0-flash",
    description="Intelligent financial coordinator with dynamic agent selection and robust error handling",
    instruction=root_agent_instruction,
    tools=[],  # No direct tools - delegates to specialized workflows
    sub_agents=[complete_workflow]
)
