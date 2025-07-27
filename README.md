# NaviFi - Comprehensive Personal Finance Assistant

## 🎯 Overview

NaviFi is a sophisticated multi-agent financial assistant built with Google's Agent Development Kit (ADK) that provides comprehensive personal finance management, planning, and insights. The system combines real personal financial data (via MCP tools) with real-time market research (via Google Search) to deliver personalized, actionable financial advice for various life events and investment scenarios.

> **Revolutionary Approach**: NaviFi uniquely combines personal financial data analysis with real-time market research to provide contextual, up-to-date financial guidance.

## 🏗️ Architecture

### Agent Hierarchy

```
financial_agent (Root Agent)
└── complete_financial_workflow
    ├── mcp_data_workflow (Sequential)
    │   ├── DATA_AGENT (Data Management)
    │   └── financial_analysis (Parallel)
    │       ├── PLANNING_AGENT (Financial Planning)
    │       └── INSIGHTS_AGENT (Spending Analysis)
    └── market_research_workflow (Parallel)
        ├── STOCK_SIP_AGENT 📈 (Investment Research)
        ├── SALARY_HIKE_AGENT 🎉 (Salary Optimization)
        ├── JOB_LOSS_AGENT 💔 (Crisis Management)
        ├── CITY_MOVE_AGENT 🏠 (Relocation Planning)
        ├── MARRIAGE_AGENT 💍 (Wedding & Joint Finance)
        ├── FREELANCING_AGENT 💼 (Self-Employment)
        ├── STOCK_WINDFALL_AGENT 📈 (Sudden Wealth)
        └── CHILDBIRTH_AGENT 👶 (Family Planning)
```

### Data Flow

```
User Query → Root Agent → MCP Data Workflow → Market Research Workflow → Synthesized Response
```

### Project Structure

```
NaviFi/
├── root_agent/
│   ├── __init__.py
│   ├── agent.py          # All agents and workflows defined here
│   └── instructions.py   # Agent instructions
├── api.py               # FastAPI implementation
├── start_api.py         # API server launcher
├── test_api.py          # Comprehensive API tests
├── requirement.txt      # Dependencies
└── README.md           # This file
```

## 🤖 Agent Ecosystem

### MCP-Based Agents (Personal Financial Data)

#### 1. **Data Agent** (`DATA_AGENT`)
- **Role**: Centralized financial data management
- **Tools**: MCP Toolset with 6 financial data endpoints
- **Responsibilities**:
  - Fetches ALL financial data from MCP server
  - Caches data in `context.state` for other agents
  - Manages data freshness and timestamps
  - Provides structured data access pattern

#### 2. **Planning Agent** (`PLANNING_AGENT`)
- **Role**: Long-term financial planning specialist
- **Data Source**: Cached personal financial data
- **Responsibilities**:
  - Retirement planning and EPF analysis
  - Investment strategy recommendations
  - Goal-based financial projections
  - Tax optimization strategies
  - Multi-scenario planning (conservative, moderate, aggressive)

#### 3. **Insights Agent** (`INSIGHTS_AGENT`)
- **Role**: Behavioral finance and spending analysis
- **Data Source**: Cached personal financial data
- **Responsibilities**:
  - Transaction pattern analysis
  - Spending behavior insights
  - Budget recommendations
  - Anomaly detection and fraud alerts
  - Financial wellness reports

### Google Search-Based Agents (Real-Time Market Research)

#### 4. **Stock & SIP Agent** (`STOCK_SIP_AGENT`) 📈
- **Role**: Investment advisory with real-time market data
- **Tools**: Google Search
- **Specialization**:
  - Current best-performing stocks research
  - Latest SIP options and mutual fund recommendations
  - Market trends and economic indicators
  - Goal-specific investment strategies
  - Tax-efficient investment options

#### 5. **Salary Hike Agent** (`SALARY_HIKE_AGENT`) 🎉
- **Role**: Salary increase optimization strategies
- **Tools**: Google Search
- **Specialization**:
  - Best SIP funds for increased income
  - High-yield savings and emergency fund options
  - Tax-saving investment schemes
  - Salary hike financial planning best practices

#### 6. **Job Loss Agent** (`JOB_LOSS_AGENT`) 💔
- **Role**: Emergency financial crisis management
- **Tools**: Google Search
- **Specialization**:
  - Unemployment benefits and assistance programs
  - Emergency financial resources
  - Job market trends and opportunities
  - Expense reduction and survival strategies

#### 7. **City Move Agent** (`CITY_MOVE_AGENT`) 🏠
- **Role**: Relocation financial planning
- **Tools**: Google Search
- **Specialization**:
  - Cost-of-living comparisons between cities
  - Rental prices and affordable housing research
  - Transportation and utility cost analysis
  - Relocation budgeting and planning

#### 8. **Marriage Agent** (`MARRIAGE_AGENT`) 💍
- **Role**: Wedding and joint financial planning
- **Tools**: Google Search
- **Specialization**:
  - Wedding cost analysis and budgeting
  - Joint financial planning for couples
  - Marriage-related financial products
  - Prenuptial financial planning advice

#### 9. **Freelancing Agent** (`FREELANCING_AGENT`) 💼
- **Role**: Self-employment financial management
- **Tools**: Google Search
- **Specialization**:
  - GST rules and tax regulations for freelancers
  - Financial management tools and platforms
  - Business insurance and tax deductions
  - Retirement planning for self-employed

#### 10. **Stock Windfall Agent** (`STOCK_WINDFALL_AGENT`) 📈
- **Role**: Sudden wealth management
- **Tools**: Google Search
- **Specialization**:
  - Investment allocation for sudden wealth
  - Capital gains tax optimization
  - Wealth preservation and diversification
  - Large portfolio management strategies

#### 11. **Childbirth Agent** (`CHILDBIRTH_AGENT`) 👶
- **Role**: Family financial preparation
- **Tools**: Google Search
- **Specialization**:
  - Education cost projections and inflation
  - Child-specific investments and insurance
  - Education funding strategies
  - Family budget adjustments

## 📊 Data Management & Context

### Context State Structure

All financial data is stored in `context.state` with prefixed keys:

```python
context.state = {
    "data:net_worth": {
        "total": 1500000,
        "assets": {...},
        "liabilities": {...}
    },
    "data:credit_report": {
        "credit_score": 750,
        "active_accounts": 2,
        "credit_utilization": 25
    },
    "data:epf_details": {
        "balance": 850000,
        "monthly_contribution": 3000,
        "employer_contribution": 3000
    },
    "data:mf_transactions": [...],
    "data:bank_transactions": [...],
    "data:stock_transactions": [...],
    "data:last_updated": "2024-01-15T10:30:00"
}
```

### Available MCP Tools

- `fetch_net_worth` - Current assets, liabilities, and net worth
- `fetch_credit_report` - Credit score and debt information
- `fetch_epf_details` - Retirement fund details and contributions
- `fetch_mf_transactions` - Mutual fund investment history
- `fetch_bank_transactions` - Complete bank transaction history
- `fetch_stock_transactions` - Stock trading history

## 🚀 Revolutionary Features

### 1. **Dual-Engine Architecture**
- **Personal Data Engine**: Uses MCP tools to fetch real financial data
- **Market Research Engine**: Uses Google Search for real-time market information
- **Synthesis**: Combines personal situation with current market opportunities

### 2. **Life Event Specialization**
- Dedicated agents for 8 major life events
- Event-specific financial strategies and research
- Real-time market data for each life event scenario

### 3. **Intelligent Workflow Orchestration**
- **Sequential Processing**: Data fetching followed by analysis
- **Parallel Analysis**: Multiple agents analyze simultaneously
- **Smart Coordination**: Root agent synthesizes all insights

### 4. **REST API Interface**
- **Streaming Responses**: Real-time response streaming for better UX
- **Non-streaming Endpoint**: Complete responses for simple integrations
- **FastAPI Framework**: High-performance async API with automatic documentation
- **CORS Support**: Cross-origin requests enabled for web frontends

### 5. **Session Management**
- ADK-managed session persistence
- Cross-conversation data continuity
- User-specific financial profiles
- State management across interactions

## 🌐 REST API Endpoints

### Available Endpoints

| Endpoint | Method | Description | Response Type |
|----------|--------|-------------|---------------|
| `/` | GET | API information and available endpoints | JSON |
| `/health` | GET | Health check for monitoring | JSON |
| `/chat` | POST | Complete financial analysis response | JSON |
| `/chat/stream` | POST | Streaming financial analysis response | Server-Sent Events |

### API Usage Examples

#### 1. **Health Check**
```bash
curl -X GET http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "NaviFi Financial Agent API"
}
```

#### 2. **Complete Response** (Non-streaming)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I just got a salary hike. What should I do?",
    "user_id": "user123"
  }'
```

#### 3. **Streaming Response**
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I just lost my job. What are my options?",
    "user_id": "user123"
  }'
```

### Request Format

```typescript
{
  "prompt": string,      // Required: User's financial query
  "user_id": string      // Optional: User identifier (default: "default_user")
}
```

## 📋 Usage Examples

### Life Event Scenarios

#### Salary Hike 🎉
```
User: "I just got a 30% salary hike. How should I optimize my finances?"

Workflow:
1. DATA_AGENT fetches current financial data
2. PLANNING_AGENT analyzes current investment strategy  
3. INSIGHTS_AGENT reviews spending patterns
4. SALARY_HIKE_AGENT researches current SIP options and tax-saving investments
5. Root Agent synthesizes personal data with market research
6. Provides optimized strategy with specific fund recommendations
```

#### Job Loss Crisis 💔
```
User: "I just lost my job. What should I do financially?"

Workflow:
1. DATA_AGENT fetches emergency fund and expense data
2. INSIGHTS_AGENT analyzes monthly spending patterns
3. JOB_LOSS_AGENT researches unemployment benefits and assistance programs
4. Root Agent creates emergency financial plan with current resources
```

#### Marriage Planning 💍
```
User: "We're getting married next year. How should we plan financially?"

Workflow:
1. DATA_AGENT fetches current financial profile
2. PLANNING_AGENT analyzes joint financial goals
3. MARRIAGE_AGENT researches current wedding costs and joint financial products
4. Provides wedding budget and joint financial strategy
```

#### Investment Research 📈
```
User: "What are the best stocks to invest in right now for retirement?"

Workflow:
1. DATA_AGENT fetches EPF and current investment data
2. PLANNING_AGENT analyzes retirement timeline and goals
3. STOCK_SIP_AGENT researches current market trends and best-performing stocks
4. Provides retirement-focused investment recommendations with current market data
```

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.9+
- Google Cloud Project with billing enabled
- ADK (Agent Development Kit) installed
- MCP Server configured and running

### Installation

1. **Navigate to the project directory**
```bash
cd NaviFi
```

2. **Install dependencies**
```bash
pip install -r requirement.txt
```

3. **Configure environment variables**

**For Google AI Studio (Recommended for development):**
```bash
# Get your API key from https://aistudio.google.com/app/apikey
export GOOGLE_API_KEY="your_api_key_here"
export MCP_SERVER_URL="http://localhost:3000"
```

**For Vertex AI (Recommended for production):**
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export MCP_SERVER_URL="http://localhost:3000"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

4. **Run the system**

**REST API Server (Recommended):**
```bash
# Start the FastAPI server
python start_api.py

# Server will be available at:
# - Main API: http://localhost:8000
# - Documentation: http://localhost:8000/docs
# - Interactive Explorer: http://localhost:8000/redoc
```

**Direct Agent Interface:**
```bash
# Terminal interface
adk run root_agent

# Web interface  
adk web root_agent
```

### Testing the System

```bash
# Run comprehensive test suite
python test_api.py

# Manual testing examples
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Help me plan for my child'\''s education", "user_id": "test_user"}'
```

## 🧩 Technical Architecture

### **Multi-Workflow Design**
- **MCP Workflow**: Sequential data fetching followed by parallel analysis
- **Search Workflow**: Parallel market research across all life event agents
- **Root Coordination**: Synthesizes results from both workflows

### **Context-First Data Strategy**
Using `context.state` for data sharing provides:
- **Automatic Persistence**: ADK handles session management
- **Cross-Agent Access**: All agents see the same data
- **No Redundant Calls**: Single MCP fetch serves multiple analyses
- **Data Consistency**: Guaranteed identical data across agents

### **Tool Specialization**
- **MCP Tools**: Personal financial data (6 endpoints)
- **Google Search**: Real-time market research and life event information
- **No Tool Overlap**: Clear separation of data sources and responsibilities

## 🔧 Configuration

### Environment Variables

- `MCP_SERVER_URL` - URL for the MCP server providing financial data
- `GOOGLE_API_KEY` - Google AI Studio API key (for development)
- `GOOGLE_CLOUD_PROJECT` - Google Cloud project ID (for production)
- `GOOGLE_APPLICATION_CREDENTIALS` - Service account credentials path

### Agent Configuration

All agents and workflows are defined in `root_agent/agent.py`:

- **Model**: `gemini-2.0-flash` for all agents
- **MCP Tools**: 6 financial data endpoints
- **Google Search**: Real-time market research capability
- **Workflows**: Sequential and parallel agent orchestration

## 🏛️ Key Benefits

### 1. **Comprehensive Coverage**
- Personal financial data analysis
- Real-time market research
- Life event specialization
- Crisis management capabilities

### 2. **Real-Time Intelligence**
- Current market trends and opportunities
- Up-to-date investment recommendations
- Latest government policies and benefits
- Current cost-of-living data

### 3. **Personalized Advice**
- Uses actual financial data, not assumptions
- Contextual recommendations based on personal situation
- Goal-specific planning and projections
- Risk assessment based on actual financial position

### 4. **Scalable Architecture**
- Easy to add new life event agents
- Modular workflow design
- Clean separation of concerns
- Extensible tool integration

## 🔒 Security & Privacy

- **Data Encryption**: All MCP communications encrypted
- **Session Isolation**: User data isolated per session
- **Access Control**: Configurable MCP endpoint permissions
- **Data Retention**: Configurable session persistence policies
- **API Security**: CORS and rate limiting support

## 🚀 Future Enhancements

1. **Enhanced Life Events** - Divorce, inheritance, medical emergencies
2. **International Support** - Multi-currency and cross-border planning
3. **Advanced Analytics** - Machine learning for predictive insights
4. **Mobile Integration** - Native mobile app development
5. **Compliance Features** - Regulatory reporting and tax filing
6. **Social Features** - Family financial planning and sharing

## 📚 Documentation

- [ADK Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Gemini API Documentation](https://ai.google.dev/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-life-event-agent`)
3. Make your changes
4. Add tests for new agents or workflows
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions or support:
- Create an issue in the repository
- Check the ADK documentation
- Review the comprehensive test suite in `test_api.py`

---

**Built with ❤️ using Google's Agent Development Kit (ADK) and Gemini 2.0 Flash**

*NaviFi - Your AI-powered financial navigator for every life event* 