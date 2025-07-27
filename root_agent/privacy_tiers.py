"""
Privacy Tiers Configuration System

Implements the three-tier privacy approach for NaviFi:
🟢 Cloud Hybrid Mode (default) - Full cloud processing with privacy safeguards
🟡 Private-First Mode - Restricts data to device where possible
🔴 Offline Mode - AI limited to local cached rules (no real-time search)
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class PrivacyTier(Enum):
    CLOUD_HYBRID = "cloud_hybrid"      # 🟢 Default: Full cloud with safeguards
    PRIVATE_FIRST = "private_first"     # 🟡 Local preference, limited cloud
    OFFLINE_MODE = "offline_mode"       # 🔴 Local only, cached rules

class DataSensitivity(Enum):
    PUBLIC = "public"                   # Market data, general advice
    PERSONAL = "personal"               # User financial data  
    HIGHLY_SENSITIVE = "highly_sensitive" # PII, account numbers, PAN etc.

@dataclass
class PrivacyPolicy:
    tier: PrivacyTier
    allow_cloud_processing: bool
    allow_pii_in_cloud: bool
    require_tokenization: bool
    local_processing_preferred: bool
    cache_responses: bool
    max_cloud_retention_hours: int
    allowed_agents: List[str]
    restricted_agents: List[str]
    data_flow_rules: Dict[str, Any]

@dataclass
class DataFlowDecision:
    can_process_in_cloud: bool
    requires_tokenization: bool
    suggested_agents: List[str]
    restricted_operations: List[str]
    retention_policy: str
    reasoning: str

class PrivacyTierManager:
    """
    Manages privacy tiers and data flow decisions based on user preferences
    and data sensitivity levels
    """
    
    def __init__(self, default_tier: PrivacyTier = PrivacyTier.CLOUD_HYBRID):
        self.current_tier = default_tier
        self.policies = self._create_privacy_policies()
        self.user_preferences: Dict[str, PrivacyTier] = {}
        self.session_decisions: Dict[str, List[DataFlowDecision]] = {}
        
    def _create_privacy_policies(self) -> Dict[PrivacyTier, PrivacyPolicy]:
        """Define privacy policies for each tier"""
        
        return {
            PrivacyTier.CLOUD_HYBRID: PrivacyPolicy(
                tier=PrivacyTier.CLOUD_HYBRID,
                allow_cloud_processing=True,
                allow_pii_in_cloud=False,  # PII must be tokenized
                require_tokenization=True,
                local_processing_preferred=False,
                cache_responses=True,
                max_cloud_retention_hours=24,
                allowed_agents=[
                    "DATA_COORDINATOR", "NET_WORTH_AGENT", "CREDIT_REPORT_AGENT",
                    "EPF_AGENT", "MF_AGENT", "BANK_AGENT", "STOCK_AGENT",
                    "PLANNING_AGENT", "INSIGHTS_AGENT", "STOCK_SIP_AGENT",
                    "SALARY_HIKE_AGENT", "JOB_LOSS_AGENT", "CITY_MOVE_AGENT",
                    "MARRIAGE_AGENT", "FREELANCING_AGENT", "STOCK_WINDFALL_AGENT",
                    "CHILDBIRTH_AGENT", "GENERIC_AGENT"
                ],
                restricted_agents=[],
                data_flow_rules={
                    "pii_handling": "tokenize_before_cloud",
                    "financial_data": "allow_with_encryption",
                    "market_research": "full_cloud_access",
                    "voice_processing": "cloud_with_privacy",
                    "document_parsing": "local_for_sensitive"
                }
            ),
            
            PrivacyTier.PRIVATE_FIRST: PrivacyPolicy(
                tier=PrivacyTier.PRIVATE_FIRST,
                allow_cloud_processing=True,  # Limited cloud access
                allow_pii_in_cloud=False,
                require_tokenization=True,
                local_processing_preferred=True,
                cache_responses=True,
                max_cloud_retention_hours=1,  # Minimal cloud retention
                allowed_agents=[
                    "DATA_COORDINATOR",  # Only for critical data coordination
                    "STOCK_SIP_AGENT",   # For market research only
                    "GENERIC_AGENT"      # For general advice only
                ],
                restricted_agents=[
                    "NET_WORTH_AGENT", "CREDIT_REPORT_AGENT", "EPF_AGENT",
                    "MF_AGENT", "BANK_AGENT", "STOCK_AGENT"  # No personal data agents
                ],
                data_flow_rules={
                    "pii_handling": "never_send_to_cloud",
                    "financial_data": "local_processing_only",
                    "market_research": "limited_cloud_access",
                    "voice_processing": "local_stt_preferred",
                    "document_parsing": "always_local"
                }
            ),
            
            PrivacyTier.OFFLINE_MODE: PrivacyPolicy(
                tier=PrivacyTier.OFFLINE_MODE,
                allow_cloud_processing=False,
                allow_pii_in_cloud=False,
                require_tokenization=False,  # No cloud, no need to tokenize
                local_processing_preferred=True,
                cache_responses=True,
                max_cloud_retention_hours=0,
                allowed_agents=[],  # Only local cached responses
                restricted_agents=[
                    "STOCK_SIP_AGENT", "SALARY_HIKE_AGENT", "JOB_LOSS_AGENT",
                    "CITY_MOVE_AGENT", "MARRIAGE_AGENT", "FREELANCING_AGENT",
                    "STOCK_WINDFALL_AGENT", "CHILDBIRTH_AGENT", "GENERIC_AGENT"
                ],
                data_flow_rules={
                    "pii_handling": "local_only",
                    "financial_data": "cached_analysis_only",
                    "market_research": "cached_data_only",
                    "voice_processing": "local_stt_only",
                    "document_parsing": "local_only"
                }
            )
        }
    
    def set_user_privacy_tier(self, user_id: str, tier: PrivacyTier, reason: str = ""):
        """Set privacy tier for a specific user"""
        self.user_preferences[user_id] = tier
        logger.info(f"Privacy tier set for user {user_id}: {tier.value}. Reason: {reason}")
    
    def get_user_privacy_tier(self, user_id: str) -> PrivacyTier:
        """Get privacy tier for a specific user"""
        return self.user_preferences.get(user_id, self.current_tier)
    
    async def evaluate_data_flow(self, 
                                 user_id: str,
                                 query: str,
                                 data_sensitivity: DataSensitivity,
                                 pii_detected: List[str] = None,
                                 intended_agents: List[str] = None) -> DataFlowDecision:
        """
        Evaluate whether data can flow to cloud based on privacy tier and sensitivity
        """
        try:
            tier = self.get_user_privacy_tier(user_id)
            policy = self.policies[tier]
            
            if pii_detected is None:
                pii_detected = []
            if intended_agents is None:
                intended_agents = []
            
            # Decision logic based on tier and data sensitivity
            decision = await self._make_data_flow_decision(
                policy, data_sensitivity, pii_detected, intended_agents, query
            )
            
            # Log decision for audit trail
            if user_id not in self.session_decisions:
                self.session_decisions[user_id] = []
            self.session_decisions[user_id].append(decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Data flow evaluation failed: {str(e)}")
            # Safe default: restrict everything
            return DataFlowDecision(
                can_process_in_cloud=False,
                requires_tokenization=True,
                suggested_agents=[],
                restricted_operations=["all"],
                retention_policy="no_retention",
                reasoning=f"Error in evaluation: {str(e)}"
            )
    
    async def _make_data_flow_decision(self,
                                       policy: PrivacyPolicy,
                                       sensitivity: DataSensitivity,
                                       pii_detected: List[str],
                                       intended_agents: List[str],
                                       query: str) -> DataFlowDecision:
        """Core decision logic for data flow"""
        
        # Base decisions based on privacy tier
        if policy.tier == PrivacyTier.OFFLINE_MODE:
            return DataFlowDecision(
                can_process_in_cloud=False,
                requires_tokenization=False,
                suggested_agents=[],
                restricted_operations=["cloud_processing", "real_time_search", "external_api"],
                retention_policy="local_cache_only",
                reasoning="Offline mode: No cloud processing allowed"
            )
        
        # Check data sensitivity
        if sensitivity == DataSensitivity.HIGHLY_SENSITIVE:
            if policy.tier == PrivacyTier.PRIVATE_FIRST:
                return DataFlowDecision(
                    can_process_in_cloud=False,
                    requires_tokenization=True,
                    suggested_agents=[],
                    restricted_operations=["cloud_processing"],
                    retention_policy="no_cloud_retention",
                    reasoning="Highly sensitive data + Private-First mode: Local processing only"
                )
        
        # Check PII detection
        if pii_detected and not policy.allow_pii_in_cloud:
            return DataFlowDecision(
                can_process_in_cloud=policy.allow_cloud_processing,
                requires_tokenization=True,
                suggested_agents=self._filter_agents_for_tier(intended_agents, policy),
                restricted_operations=["raw_pii_transmission"],
                retention_policy=f"max_{policy.max_cloud_retention_hours}h_encrypted",
                reasoning="PII detected: Tokenization required for cloud processing"
            )
        
        # Check agent restrictions
        allowed_agents = self._filter_agents_for_tier(intended_agents, policy)
        restricted_ops = []
        
        if policy.tier == PrivacyTier.PRIVATE_FIRST:
            restricted_ops = ["long_term_storage", "analytics_tracking"]
        
        return DataFlowDecision(
            can_process_in_cloud=policy.allow_cloud_processing,
            requires_tokenization=policy.require_tokenization,
            suggested_agents=allowed_agents,
            restricted_operations=restricted_ops,
            retention_policy=f"max_{policy.max_cloud_retention_hours}h",
            reasoning=f"Standard processing for {policy.tier.value} tier"
        )
    
    def _filter_agents_for_tier(self, intended_agents: List[str], policy: PrivacyPolicy) -> List[str]:
        """Filter agents based on privacy tier restrictions"""
        if not intended_agents:
            return []
        
        # Remove restricted agents
        allowed = [agent for agent in intended_agents 
                  if agent not in policy.restricted_agents]
        
        # For private-first, further limit to essential agents only
        if policy.tier == PrivacyTier.PRIVATE_FIRST:
            essential_agents = ["GENERIC_AGENT", "STOCK_SIP_AGENT"]
            allowed = [agent for agent in allowed if agent in essential_agents]
        
        return allowed
    
    def get_privacy_tier_info(self, tier: PrivacyTier) -> Dict[str, Any]:
        """Get comprehensive information about a privacy tier"""
        policy = self.policies[tier]
        
        return {
            "tier": tier.value,
            "description": self._get_tier_description(tier),
            "features": {
                "cloud_processing": policy.allow_cloud_processing,
                "pii_protection": not policy.allow_pii_in_cloud,
                "local_preference": policy.local_processing_preferred,
                "response_caching": policy.cache_responses
            },
            "limitations": {
                "restricted_agents": policy.restricted_agents,
                "max_retention_hours": policy.max_cloud_retention_hours,
                "requires_tokenization": policy.require_tokenization
            },
            "data_flow_rules": policy.data_flow_rules,
            "recommended_for": self._get_tier_recommendations(tier)
        }
    
    def _get_tier_description(self, tier: PrivacyTier) -> str:
        """Get user-friendly description of privacy tier"""
        descriptions = {
            PrivacyTier.CLOUD_HYBRID: "🟢 Balanced approach with full features and privacy safeguards. PII is tokenized before cloud processing.",
            PrivacyTier.PRIVATE_FIRST: "🟡 Maximum privacy with limited cloud features. Personal data stays on device, only market research uses cloud.",
            PrivacyTier.OFFLINE_MODE: "🔴 Complete privacy with cached responses only. No cloud processing or real-time data."
        }
        return descriptions.get(tier, "Unknown privacy tier")
    
    def _get_tier_recommendations(self, tier: PrivacyTier) -> List[str]:
        """Get recommendations for when to use each tier"""
        recommendations = {
            PrivacyTier.CLOUD_HYBRID: [
                "General users who want full features",
                "Users comfortable with tokenized data processing",
                "When real-time market data is important"
            ],
            PrivacyTier.PRIVATE_FIRST: [
                "Privacy-conscious users",
                "Handling highly sensitive financial data",
                "Corporate or regulated environments"
            ],
            PrivacyTier.OFFLINE_MODE: [
                "Maximum privacy requirements",
                "Offline or limited connectivity scenarios",
                "Highly regulated or confidential use cases"
            ]
        }
        return recommendations.get(tier, [])
    
    def get_session_privacy_report(self, user_id: str) -> Dict[str, Any]:
        """Generate privacy report for user session"""
        tier = self.get_user_privacy_tier(user_id)
        decisions = self.session_decisions.get(user_id, [])
        
        # Calculate privacy metrics
        total_decisions = len(decisions)
        cloud_processed = sum(1 for d in decisions if d.can_process_in_cloud)
        tokenized = sum(1 for d in decisions if d.requires_tokenization)
        
        return {
            "user_id": user_id,
            "privacy_tier": tier.value,
            "session_start": datetime.now().isoformat(),
            "decisions_made": total_decisions,
            "metrics": {
                "cloud_processing_rate": cloud_processed / total_decisions if total_decisions > 0 else 0,
                "tokenization_rate": tokenized / total_decisions if total_decisions > 0 else 0,
                "privacy_score": self._calculate_privacy_score(decisions)
            },
            "policy_summary": self.get_privacy_tier_info(tier),
            "recent_decisions": [
                {
                    "can_process_cloud": d.can_process_in_cloud,
                    "tokenization_required": d.requires_tokenization,
                    "reasoning": d.reasoning
                } for d in decisions[-5:]  # Last 5 decisions
            ]
        }
    
    def _calculate_privacy_score(self, decisions: List[DataFlowDecision]) -> float:
        """Calculate overall privacy score for session (0-1, higher is more private)"""
        if not decisions:
            return 1.0
        
        score = 0.0
        for decision in decisions:
            # Higher score for local processing
            if not decision.can_process_in_cloud:
                score += 1.0
            elif decision.requires_tokenization:
                score += 0.7
            else:
                score += 0.3
        
        return score / len(decisions)
    
    def update_tier_based_on_query(self, user_id: str, query: str, pii_detected: List[str]) -> Optional[PrivacyTier]:
        """
        Suggest privacy tier upgrade based on query content
        """
        current_tier = self.get_user_privacy_tier(user_id)
        
        # Suggest upgrade if sensitive data detected and user is on basic tier
        if pii_detected and current_tier == PrivacyTier.CLOUD_HYBRID:
            logger.info(f"Suggesting privacy tier upgrade for user {user_id} due to PII detection")
            return PrivacyTier.PRIVATE_FIRST
        
        # Suggest downgrade if user wants features not available in current tier
        market_queries = ["stock", "sip", "market", "investment", "recommend"]
        if any(term in query.lower() for term in market_queries) and current_tier == PrivacyTier.OFFLINE_MODE:
            logger.info(f"Suggesting privacy tier downgrade for user {user_id} to enable market features")
            return PrivacyTier.PRIVATE_FIRST
        
        return None  # No change suggested

# Factory functions for easy setup
def create_privacy_manager(default_tier: PrivacyTier = PrivacyTier.CLOUD_HYBRID) -> PrivacyTierManager:
    """Create and return a configured PrivacyTierManager"""
    return PrivacyTierManager(default_tier)

def get_recommended_tier_for_user(user_profile: Dict[str, Any]) -> PrivacyTier:
    """Recommend privacy tier based on user profile"""
    
    # Check user preferences
    privacy_preference = user_profile.get("privacy_preference", "standard")
    user_type = user_profile.get("user_type", "individual")
    data_sensitivity = user_profile.get("data_sensitivity", "normal")
    
    if privacy_preference == "maximum" or user_type == "enterprise" or data_sensitivity == "high":
        return PrivacyTier.PRIVATE_FIRST
    elif privacy_preference == "offline_only":
        return PrivacyTier.OFFLINE_MODE
    else:
        return PrivacyTier.CLOUD_HYBRID

# Example usage for testing
async def test_privacy_tiers():
    """Test privacy tier management"""
    
    manager = create_privacy_manager()
    
    # Test different scenarios
    test_scenarios = [
        {
            "user_id": "privacy_user",
            "tier": PrivacyTier.PRIVATE_FIRST,
            "query": "My PAN number is ABCDE1234F, show my portfolio",
            "pii": ["PAN_NUMBER"],
            "agents": ["DATA_COORDINATOR", "NET_WORTH_AGENT"]
        },
        {
            "user_id": "standard_user", 
            "tier": PrivacyTier.CLOUD_HYBRID,
            "query": "Best SIP plans for 2025",
            "pii": [],
            "agents": ["STOCK_SIP_AGENT"]
        },
        {
            "user_id": "offline_user",
            "tier": PrivacyTier.OFFLINE_MODE,
            "query": "How to budget for marriage?",
            "pii": [],
            "agents": ["MARRIAGE_AGENT"]
        }
    ]
    
    for scenario in test_scenarios:
        manager.set_user_privacy_tier(scenario["user_id"], scenario["tier"])
        
        decision = await manager.evaluate_data_flow(
            user_id=scenario["user_id"],
            query=scenario["query"],
            data_sensitivity=DataSensitivity.PERSONAL if scenario["pii"] else DataSensitivity.PUBLIC,
            pii_detected=scenario["pii"],
            intended_agents=scenario["agents"]
        )
        
        print(f"\nScenario: {scenario['tier'].value}")
        print(f"Query: {scenario['query']}")
        print(f"Cloud Processing: {decision.can_process_in_cloud}")
        print(f"Tokenization Required: {decision.requires_tokenization}")
        print(f"Suggested Agents: {decision.suggested_agents}")
        print(f"Reasoning: {decision.reasoning}")
        
        # Get privacy report
        report = manager.get_session_privacy_report(scenario["user_id"])
        print(f"Privacy Score: {report['metrics']['privacy_score']:.2f}")

if __name__ == "__main__":
    asyncio.run(test_privacy_tiers()) 