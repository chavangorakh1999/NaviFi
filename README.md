# Financial Agent System - ADK-Based Personal Finance Assistant

## 🎯 Overview

A sophisticated multi-agent financial assistant built with Google's Agent Development Kit (ADK) that provides comprehensive personal finance management, planning, and insights. The system uses MCP (Model Context Protocol) tools to fetch real financial data and leverages ADK's context management for efficient data sharing between specialized agents.

> **Note**: All agents are currently implemented in `master_agent/agent.py` with detailed instructions for context-based data access and sharing.

## 🏗️ Architecture

### Agent Hierarchy

```
financial_agent (Root Agent)
├── DATA_AGENT (Data Management)
├── PLANNING_AGENT (Financial Planning) 
└── INSIGHTS_AGENT (Spending Analysis)
```

### Data Flow

```
User Query → Root Agent → Data Check → MCP Data Fetch → Context Storage → Specialized Analysis
```

### Project Structure

```
finAgent/
├── master_agent/
│   ├── __init__.py
│   ├── agent.py          # All agents defined here
│   └── instructions.py   # Agent instructions
├── example_workflow.py   # Usage examples
└── README.md            # This file
```

## 🤖 Agent Responsibilities

### 1. **Root Agent** (`financial_agent`)
- **Role**: Main coordinator and orchestrator
- **Responsibilities**:
  - Receives and routes user queries
  - Manages data availability in context.state
  - Delegates to specialized agents based on query type
  - Handles stock market queries via MCP tools when needed

### 2. **Data Agent** (`DATA_AGENT`) 
- **Role**: Centralized data management
- **Responsibilities**:
  - Fetches ALL financial data from MCP server
  - Caches data in `context.state` for other agents
  - Manages data freshness and timestamps
  - Provides structured data access for specialized agents

### 3. **Planning Agent** (`PLANNING_AGENT`)
- **Role**: Long-term financial planning specialist
- **Responsibilities**:
  - Retirement planning and EPF analysis
  - Investment strategy recommendations
  - Goal-based financial projections
  - Tax optimization strategies
  - Multi-scenario planning (conservative, moderate, aggressive)

### 4. **Insights Agent** (`INSIGHTS_AGENT`)
- **Role**: Behavioral finance and spending analysis
- **Responsibilities**:
  - Transaction pattern analysis
  - Spending behavior insights
  - Budget recommendations
  - Anomaly detection and fraud alerts
  - Financial wellness reports

## 📊 Data Management

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

## 🚀 Key Features

### 1. **REST API Interface**
- **Streaming Responses**: Real-time response streaming for better UX
- **Non-streaming Endpoint**: Complete responses for simple integrations
- **FastAPI Framework**: High-performance async API with automatic documentation
- **CORS Support**: Cross-origin requests enabled for web frontends
- **Health Monitoring**: Built-in health check and monitoring endpoints

### 2. **Intelligent Data Caching**
- Single data fetch serves multiple analysis types
- 24-hour data freshness management
- Automatic stale data detection
- Context-based data sharing across all agents

### 3. **Specialized Analysis**
- **Planning**: Retirement projections, investment strategies, goal planning
- **Insights**: Spending patterns, behavioral analysis, budget optimization
- **Coordination**: Smart routing based on query intent

### 4. **Performance Optimization**
- No redundant MCP API calls
- Efficient context-based data access
- Parallel analysis capabilities
- Cached data consistency

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
    "prompt": "Help me plan for retirement",
    "user_id": "user123"
  }'
```

Response:
```json
{
  "response": "Based on your current financial profile...",
  "status": "success"
}
```

#### 3. **Streaming Response**
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze my spending patterns",
    "user_id": "user123"
  }'
```

Response (Server-Sent Events):
```
data: {"type": "start", "message": "Processing your financial query..."}

data: {"type": "chunk", "content": "Based on your bank transactions..."}

data: {"type": "chunk", "content": "I notice your spending on dining..."}

data: {"type": "end", "message": "Response complete"}
```

### Request Format

All POST endpoints accept JSON with the following structure:

```typescript
{
  "prompt": string,      // Required: User's financial query
  "user_id": string      // Optional: User identifier (default: "default_user")
}
```

### Integration Examples

#### JavaScript/Frontend
```javascript
// Non-streaming request
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "What should I do with my salary hike?",
    user_id: "user123"
  })
});
const result = await response.json();

// Streaming request
const response = await fetch('http://localhost:8000/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "Help me budget for buying a house",
    user_id: "user123"
  })
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = new TextDecoder().decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (data.type === 'chunk') {
        console.log(data.content);
      }
    }
  }
}
```

#### Python Client
```python
import requests
import json

# Non-streaming
response = requests.post(
    'http://localhost:8000/chat',
    json={
        'prompt': 'Help me optimize my investments',
        'user_id': 'user123'
    }
)
result = response.json()

# Streaming
response = requests.post(
    'http://localhost:8000/chat/stream',
    json={
        'prompt': 'Plan my child\'s education funding',
        'user_id': 'user123'
    },
    stream=True
)

for line in response.iter_lines():
    if line.startswith(b'data: '):
        data = json.loads(line[6:])
        if data.get('type') == 'chunk':
            print(data['content'], end='')
```

## 📋 Usage Examples

### Retirement Planning Query

```
User: "Help me plan for retirement. Am I on track?"

Workflow:
1. Root Agent checks context.state for EPF/investment data
2. If missing → Data Agent fetches ALL financial data via MCP
3. Data cached in context.state with timestamp
4. Planning Agent accesses cached EPF, net worth, transaction data
5. Provides retirement projections with multiple scenarios
```

### Spending Analysis Query

```
User: "Analyze my spending patterns this month"

Workflow:
1. Root Agent checks context.state for transaction data  
2. If available → Insights Agent accesses cached bank transactions
3. Performs comprehensive spending analysis
4. Provides behavioral insights and budget recommendations
```

### Data Refresh Request

```
User: "Get my latest financial data"

Workflow:
1. Root Agent delegates to Data Agent
2. Data Agent calls all 6 MCP tools
3. Updates context.state with fresh data
4. Confirms successful caching with summary
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

You need to set up either Google AI Studio OR Vertex AI credentials:

**Option A: Google AI Studio (Recommended for development)**
```bash
# Get your API key from https://aistudio.google.com/app/apikey
export GOOGLE_API_KEY="your_api_key_here"
export MCP_SERVER_URL="http://localhost:3000"
```

**Option B: Vertex AI (Recommended for production)**
```bash
# Set up Google Cloud credentials
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"  # or your preferred region
export MCP_SERVER_URL="http://localhost:3000"

# Optional: Service account credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

4. **Run the system**

**Option A: REST API Server (Recommended)**
```bash
# Start the FastAPI server
python start_api.py

# Server will be available at:
# - Main API: http://localhost:8000
# - Documentation: http://localhost:8000/docs
# - Interactive Explorer: http://localhost:8000/redoc
```

**Option B: Direct Agent Interface**
```bash
# Terminal interface (from NaviFi directory)
adk run root_agent

# Web interface  
adk web root_agent
```

### Testing the API

```bash
# Run comprehensive test suite
python test_api.py

# Manual testing examples
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Help me plan my finances", "user_id": "test_user"}'
```

## 🔧 Configuration

### Environment Variables

- `MCP_SERVER_URL` - URL for the MCP server providing financial data
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google service account credentials (if required)

### Agent Configuration

All agents are defined in `finAgent/master_agent/agent.py`:

- **Root Agent**: `financial_agent` with MCP tools and coordination logic
- **DATA_AGENT**: Handles all MCP data fetching and context caching  
- **PLANNING_AGENT**: Accesses cached data for financial planning analysis
- **INSIGHTS_AGENT**: Accesses cached data for spending and behavioral analysis
- **Model**: `gemini-1.5-flash` (configurable)
- **Tools**: MCP toolset with financial data endpoints

## 📈 Example Interactions

### Financial Planning

```
User: "Create a 30-year retirement plan"
→ Agent fetches current EPF, investments, expenses
→ Calculates projected retirement corpus
→ Provides investment recommendations
→ Shows multiple scenarios with different saving rates
```

### Spending Insights

```
User: "Why is my spending high this month?"
→ Agent analyzes recent transactions
→ Identifies spending categories and trends
→ Compares with historical patterns
→ Suggests optimization opportunities
```

### Goal Planning

```
User: "Can I afford a house in 5 years?"
→ Agent assesses current savings and income
→ Calculates required down payment
→ Projects savings growth over 5 years
→ Recommends savings strategy for house purchase
```

## 🧩 Technical Benefits

### 1. **ADK Framework Advantages**
- Built-in session management
- Automatic context persistence  
- Multi-agent coordination
- Streaming and async support

### 2. **Context-Based Architecture**
- Efficient data sharing between agents
- No manual session passing required
- Consistent data access patterns
- Automatic state management

### 3. **MCP Integration**
- Real financial data access
- Standardized tool interface
- Secure data transmission
- Extensible data sources

### 4. **Modular Design**
- Specialized agent responsibilities
- Easy to extend with new agents
- Clear separation of concerns
- Maintainable codebase

## 🏛️ Architectural Decisions

### **Single-File Implementation**
All agents are defined in `master_agent/agent.py` for:
- **Simplicity**: Easy to understand and maintain
- **Consistency**: All agent configurations in one place
- **Performance**: Reduced import overhead
- **Development**: Faster iteration and testing

### **Context-First Data Strategy**
Using `context.state` for data sharing provides:
- **Automatic Persistence**: ADK handles session management
- **Cross-Agent Access**: All agents see the same data
- **No Redundant Calls**: Single MCP fetch serves multiple analyses
- **Data Consistency**: Guaranteed identical data across agents

### **Specialized Agent Roles**
Each agent has a focused responsibility:
- **DATA_AGENT**: Pure data fetching and caching
- **PLANNING_AGENT**: Financial planning and projections  
- **INSIGHTS_AGENT**: Behavioral analysis and insights
- **Root Agent**: Coordination and routing

## 🔒 Security & Privacy

- **Data Encryption**: All MCP communications encrypted
- **Session Isolation**: User data isolated per session
- **Access Control**: Configurable MCP endpoint permissions
- **Data Retention**: Configurable session persistence policies

## 🚀 Future Enhancements

1. **Real-time Data Updates** - Live market data integration
2. **Advanced ML Models** - Predictive spending analysis
3. **Multi-language Support** - Regional financial planning
4. **Mobile Integration** - React Native or Flutter app
5. **Compliance Features** - Regulatory reporting capabilities

## 📚 Documentation

- [ADK Documentation](https://google.github.io/adk-docs/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Agent Architecture Guide](./docs/architecture.md)
- [API Reference](./docs/api.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions or support:
- Create an issue in the repository
- Check the ADK documentation
- Review the example workflows in `example_workflow.py`

---

**Built with ❤️ using Google's Agent Development Kit (ADK)** 