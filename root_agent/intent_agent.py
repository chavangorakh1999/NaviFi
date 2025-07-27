"""
Intent Agent (Local) - Fast voice/text parsing and query classification

This agent runs locally for immediate query understanding and privacy-first processing.
It determines intent, extracts entities, and classifies queries before cloud coordination.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class QueryIntent(Enum):
    # Personal Financial Analysis
    NET_WORTH = "net_worth"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    SPENDING_ANALYSIS = "spending_analysis"
    CREDIT_REPORT = "credit_report"
    
    # Investment Research
    STOCK_RESEARCH = "stock_research"
    SIP_RECOMMENDATIONS = "sip_recommendations"
    MARKET_TRENDS = "market_trends"
    
    # Life Event Planning
    SALARY_HIKE = "salary_hike"
    JOB_LOSS = "job_loss"
    CITY_MOVE = "city_move"
    MARRIAGE = "marriage"
    CHILDBIRTH = "childbirth"
    FREELANCING = "freelancing"
    STOCK_WINDFALL = "stock_windfall"
    
    # General Financial Education
    FINANCIAL_EDUCATION = "financial_education"
    GENERAL_ADVICE = "general_advice"
    CURRENT_EVENTS = "current_events"
    
    # Unknown/Fallback
    UNKNOWN = "unknown"

class PrivacyLevel(Enum):
    CLOUD_HYBRID = "cloud_hybrid"      # Default: Full cloud processing
    PRIVATE_FIRST = "private_first"     # Limited cloud, prefer local
    OFFLINE_MODE = "offline_mode"       # Local only, cached rules

@dataclass
class EntityExtraction:
    amounts: List[str]              # Monetary amounts found
    time_periods: List[str]         # Time references (month, year, etc.)
    financial_instruments: List[str] # Stocks, funds, accounts mentioned
    locations: List[str]            # Cities, countries for relocation
    pii_detected: List[str]         # Potential PII found
    
@dataclass
class IntentAnalysis:
    primary_intent: QueryIntent
    confidence_score: float
    requires_personal_data: bool
    requires_market_data: bool
    privacy_level_required: PrivacyLevel
    entities: EntityExtraction
    suggested_agents: List[str]
    estimated_response_time: int    # seconds
    
class LocalIntentAgent:
    """
    Local Intent Agent for fast query classification and privacy-first processing
    """
    
    def __init__(self):
        self.intent_patterns = self._build_intent_patterns()
        self.pii_patterns = self._build_pii_patterns()
        self.financial_terms = self._build_financial_terms()
        
    def _build_intent_patterns(self) -> Dict[QueryIntent, List[str]]:
        """Build regex patterns for intent classification"""
        return {
            QueryIntent.NET_WORTH: [
                r'\b(net worth|total worth|assets|liabilities)\b',
                r'\b(how much.*worth|financial position|total wealth)\b',
                r'\b(my.*assets|my.*portfolio|my.*finances)\b'
            ],
            QueryIntent.PORTFOLIO_ANALYSIS: [
                r'\b(portfolio|investments|my.*stocks|my.*funds)\b',
                r'\b(mutual fund|SIP|stock.*performance)\b',
                r'\b(investment.*analysis|portfolio.*review)\b'
            ],
            QueryIntent.SPENDING_ANALYSIS: [
                r'\b(spending|expenses|budget|transactions)\b',
                r'\b(where.*money|spending.*pattern|expense.*analysis)\b',
                r'\b(bank.*transactions|credit card.*statement)\b'
            ],
            QueryIntent.CREDIT_REPORT: [
                r'\b(credit score|credit report|CIBIL|credit history)\b',
                r'\b(credit.*rating|credit.*analysis|debt.*report)\b'
            ],
            QueryIntent.STOCK_RESEARCH: [
                r'\b(best stocks|stock.*recommend|buy.*stock)\b',
                r'\b(stock.*analysis|market.*research|equity.*advice)\b',
                r'\b(which.*stock|stock.*pick|investment.*stock)\b'
            ],
            QueryIntent.SIP_RECOMMENDATIONS: [
                r'\b(SIP|systematic.*investment|mutual.*fund.*recommend)\b',
                r'\b(best.*SIP|SIP.*plan|monthly.*investment)\b'
            ],
            QueryIntent.MARKET_TRENDS: [
                r'\b(market.*trend|market.*analysis|stock.*market)\b',
                r'\b(market.*today|market.*news|economic.*trend)\b'
            ],
            QueryIntent.SALARY_HIKE: [
                r'\b(salary.*hike|salary.*increase|pay.*raise|promotion)\b',
                r'\b(got.*raise|salary.*went.*up|income.*increase)\b'
            ],
            QueryIntent.JOB_LOSS: [
                r'\b(lost.*job|unemployed|job.*loss|laid.*off)\b',
                r'\b(fired|terminated|job.*ended|no.*job)\b'
            ],
            QueryIntent.CITY_MOVE: [
                r'\b(moving.*city|relocating|new.*city|shifting.*city)\b',
                r'\b(transfer.*city|job.*change.*city)\b'
            ],
            QueryIntent.MARRIAGE: [
                r'\b(getting.*married|wedding|marriage.*plan|joint.*finance)\b',
                r'\b(spouse.*finance|couple.*budget|family.*planning)\b'
            ],
            QueryIntent.CHILDBIRTH: [
                r'\b(having.*baby|child.*birth|kid.*planning|family.*expand)\b',
                r'\b(education.*fund|child.*future|baby.*expense)\b'
            ],
            QueryIntent.FREELANCING: [
                r'\b(freelancing|self.*employed|independent.*work|consultant)\b',
                r'\b(freelancer.*finance|gig.*economy|contract.*work)\b'
            ],
            QueryIntent.STOCK_WINDFALL: [
                r'\b(stock.*profit|windfall|sudden.*money|big.*gain)\b',
                r'\b(stock.*windfall|unexpected.*gain|lottery|inheritance)\b'
            ],
            QueryIntent.FINANCIAL_EDUCATION: [
                r'\b(what.*is|how.*does|explain|understand|learn)\b',
                r'\b(financial.*education|money.*basics|investment.*basics)\b'
            ]
        }
    
    def _build_pii_patterns(self) -> List[str]:
        """Build patterns to detect PII that needs masking"""
        return [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b\d{10,12}\b',  # Account numbers
            r'\b[A-Z]{5}\d{4}[A-Z]\b',  # PAN
            r'\b\d{12}\b',  # Aadhaar
            r'\b[A-Z]{4}\d{7}\b',  # IFSC
            r'\b[A-Z]{2}\d{11}\b',  # UAN
        ]
    
    def _build_financial_terms(self) -> Dict[str, List[str]]:
        """Build financial term categories for entity extraction"""
        return {
            'amounts': [r'₹[\d,]+', r'\d+\s*(?:lakh|crore|thousand|k)', r'\$\d+'],
            'time_periods': [r'\b(?:month|year|quarter|week)s?\b', r'\b\d+\s*(?:month|year)s?\b'],
            'instruments': [r'\b(?:SIP|mutual fund|stock|equity|bond|FD|PPF|EPF|NPS)\b'],
            'locations': [r'\b(?:mumbai|delhi|bangalore|chennai|hyderabad|pune|kolkata)\b'],
        }
    
    async def analyze_intent(self, user_input: str, privacy_preference: Optional[PrivacyLevel] = None) -> IntentAnalysis:
        """
        Analyze user input locally to determine intent and extract entities
        """
        try:
            user_input_lower = user_input.lower()
            
            # 1. Extract entities first
            entities = self._extract_entities(user_input)
            
            # 2. Classify intent
            primary_intent, confidence = self._classify_intent(user_input_lower)
            
            # 3. Determine data requirements
            requires_personal_data = self._requires_personal_data(primary_intent, entities)
            requires_market_data = self._requires_market_data(primary_intent)
            
            # 4. Determine privacy level required
            privacy_level = self._determine_privacy_level(
                entities, privacy_preference, requires_personal_data
            )
            
            # 5. Suggest appropriate agents
            suggested_agents = self._suggest_agents(primary_intent, requires_personal_data, requires_market_data)
            
            # 6. Estimate response time
            estimated_time = self._estimate_response_time(suggested_agents, requires_personal_data)
            
            return IntentAnalysis(
                primary_intent=primary_intent,
                confidence_score=confidence,
                requires_personal_data=requires_personal_data,
                requires_market_data=requires_market_data,
                privacy_level_required=privacy_level,
                entities=entities,
                suggested_agents=suggested_agents,
                estimated_response_time=estimated_time
            )
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {str(e)}")
            return self._create_fallback_analysis(user_input)
    
    def _extract_entities(self, text: str) -> EntityExtraction:
        """Extract financial entities and detect PII"""
        amounts = []
        time_periods = []
        financial_instruments = []
        locations = []
        pii_detected = []
        
        # Extract amounts
        for pattern in self.financial_terms['amounts']:
            amounts.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Extract time periods
        for pattern in self.financial_terms['time_periods']:
            time_periods.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Extract financial instruments
        for pattern in self.financial_terms['instruments']:
            financial_instruments.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Extract locations
        for pattern in self.financial_terms['locations']:
            locations.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Detect PII
        for pattern in self.pii_patterns:
            if re.search(pattern, text):
                pii_detected.append("sensitive_data_detected")
        
        return EntityExtraction(
            amounts=amounts,
            time_periods=time_periods,
            financial_instruments=financial_instruments,
            locations=locations,
            pii_detected=pii_detected
        )
    
    def _classify_intent(self, text: str) -> Tuple[QueryIntent, float]:
        """Classify the primary intent with confidence score"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            
            if score > 0:
                intent_scores[intent] = score / len(patterns)  # Normalize by pattern count
        
        if not intent_scores:
            return QueryIntent.UNKNOWN, 0.0
        
        # Get highest scoring intent
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        return primary_intent[0], min(primary_intent[1], 1.0)
    
    def _requires_personal_data(self, intent: QueryIntent, entities: EntityExtraction) -> bool:
        """Determine if query requires personal financial data"""
        personal_data_intents = {
            QueryIntent.NET_WORTH, QueryIntent.PORTFOLIO_ANALYSIS,
            QueryIntent.SPENDING_ANALYSIS, QueryIntent.CREDIT_REPORT
        }
        
        life_event_intents = {
            QueryIntent.SALARY_HIKE, QueryIntent.JOB_LOSS, QueryIntent.CITY_MOVE,
            QueryIntent.MARRIAGE, QueryIntent.CHILDBIRTH, QueryIntent.FREELANCING,
            QueryIntent.STOCK_WINDFALL
        }
        
        return intent in personal_data_intents or intent in life_event_intents
    
    def _requires_market_data(self, intent: QueryIntent) -> bool:
        """Determine if query requires real-time market data"""
        market_data_intents = {
            QueryIntent.STOCK_RESEARCH, QueryIntent.SIP_RECOMMENDATIONS,
            QueryIntent.MARKET_TRENDS, QueryIntent.SALARY_HIKE,
            QueryIntent.STOCK_WINDFALL
        }
        
        return intent in market_data_intents
    
    def _determine_privacy_level(self, entities: EntityExtraction, 
                               preference: Optional[PrivacyLevel],
                               requires_personal_data: bool) -> PrivacyLevel:
        """Determine required privacy level based on entities and preference"""
        
        if preference:
            return preference
        
        # If PII detected, suggest higher privacy
        if entities.pii_detected:
            return PrivacyLevel.PRIVATE_FIRST
        
        # If no personal data needed, cloud is fine
        if not requires_personal_data:
            return PrivacyLevel.CLOUD_HYBRID
        
        # Default to cloud hybrid for personal analysis
        return PrivacyLevel.CLOUD_HYBRID
    
    def _suggest_agents(self, intent: QueryIntent, requires_personal: bool, requires_market: bool) -> List[str]:
        """Suggest appropriate agents based on intent and requirements"""
        
        agents = []
        
        # Always need data coordinator if personal data required
        if requires_personal:
            agents.append("DATA_COORDINATOR")
        
        # Intent-specific agents
        agent_mapping = {
            QueryIntent.NET_WORTH: ["PLANNING_AGENT", "INSIGHTS_AGENT"],
            QueryIntent.PORTFOLIO_ANALYSIS: ["PLANNING_AGENT", "INSIGHTS_AGENT"],
            QueryIntent.SPENDING_ANALYSIS: ["INSIGHTS_AGENT"],
            QueryIntent.CREDIT_REPORT: ["PLANNING_AGENT"],
            QueryIntent.STOCK_RESEARCH: ["STOCK_SIP_AGENT"],
            QueryIntent.SIP_RECOMMENDATIONS: ["STOCK_SIP_AGENT"],
            QueryIntent.MARKET_TRENDS: ["STOCK_SIP_AGENT"],
            QueryIntent.SALARY_HIKE: ["SALARY_HIKE_AGENT", "PLANNING_AGENT"],
            QueryIntent.JOB_LOSS: ["JOB_LOSS_AGENT", "INSIGHTS_AGENT"],
            QueryIntent.CITY_MOVE: ["CITY_MOVE_AGENT", "PLANNING_AGENT"],
            QueryIntent.MARRIAGE: ["MARRIAGE_AGENT", "PLANNING_AGENT"],
            QueryIntent.CHILDBIRTH: ["CHILDBIRTH_AGENT", "PLANNING_AGENT"],
            QueryIntent.FREELANCING: ["FREELANCING_AGENT", "PLANNING_AGENT"],
            QueryIntent.STOCK_WINDFALL: ["STOCK_WINDFALL_AGENT", "PLANNING_AGENT"],
            QueryIntent.FINANCIAL_EDUCATION: ["GENERIC_AGENT"],
            QueryIntent.GENERAL_ADVICE: ["GENERIC_AGENT"],
            QueryIntent.UNKNOWN: ["GENERIC_AGENT"]
        }
        
        agents.extend(agent_mapping.get(intent, ["GENERIC_AGENT"]))
        
        return list(set(agents))  # Remove duplicates
    
    def _estimate_response_time(self, agents: List[str], requires_personal_data: bool) -> int:
        """Estimate response time in seconds"""
        base_time = 2  # Base processing time
        
        # Add time for each agent
        agent_time = len(agents) * 1.5
        
        # Add time for data fetching
        data_time = 3 if requires_personal_data else 0
        
        # Add time for market research
        search_time = 2 if any("SEARCH" in agent or "SIP" in agent for agent in agents) else 0
        
        return int(base_time + agent_time + data_time + search_time)
    
    def _create_fallback_analysis(self, user_input: str) -> IntentAnalysis:
        """Create fallback analysis when processing fails"""
        return IntentAnalysis(
            primary_intent=QueryIntent.UNKNOWN,
            confidence_score=0.0,
            requires_personal_data=False,
            requires_market_data=False,
            privacy_level_required=PrivacyLevel.CLOUD_HYBRID,
            entities=EntityExtraction([], [], [], [], []),
            suggested_agents=["GENERIC_AGENT"],
            estimated_response_time=5
        )

# Factory function for easy instantiation
def create_intent_agent() -> LocalIntentAgent:
    """Create and return a configured LocalIntentAgent instance"""
    return LocalIntentAgent()

# Example usage for testing
async def test_intent_agent():
    """Test the intent agent with sample queries"""
    agent = create_intent_agent()
    
    test_queries = [
        "What's my current net worth?",
        "Best SIP plans for 2025",
        "I got a salary hike, how to invest?",
        "Moving to Bangalore, budget planning help",
        "Lost my job, what should I do?",
        "My credit card number is 1234-5678-9012-3456, check my spending"
    ]
    
    for query in test_queries:
        analysis = await agent.analyze_intent(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {analysis.primary_intent.value}")
        print(f"Confidence: {analysis.confidence_score:.2f}")
        print(f"Requires Personal Data: {analysis.requires_personal_data}")
        print(f"Privacy Level: {analysis.privacy_level_required.value}")
        print(f"Suggested Agents: {', '.join(analysis.suggested_agents)}")
        print(f"Estimated Time: {analysis.estimated_response_time}s")
        if analysis.entities.pii_detected:
            print(f"⚠️  PII Detected: {', '.join(analysis.entities.pii_detected)}")

if __name__ == "__main__":
    asyncio.run(test_intent_agent()) 