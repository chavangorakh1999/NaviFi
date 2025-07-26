"""
Data utility functions for managing financial data in context.state
"""
import datetime
from typing import Dict, Any, Optional

# Data key constants
DATA_KEYS = {
    'NET_WORTH': 'data:net_worth',
    'CREDIT_REPORT': 'data:credit_report', 
    'EPF_DETAILS': 'data:epf_details',
    'MF_TRANSACTIONS': 'data:mf_transactions',
    'BANK_TRANSACTIONS': 'data:bank_transactions',
    'STOCK_TRANSACTIONS': 'data:stock_transactions',
    'LAST_UPDATED': 'data:last_updated'
}

def is_data_stale(context, max_age_hours: int = 24) -> bool:
    """
    Check if cached data is stale based on last_updated timestamp
    
    Args:
        context: ADK context object with state access
        max_age_hours: Maximum age in hours before data is considered stale
        
    Returns:
        bool: True if data is stale or doesn't exist
    """
    last_updated = context.state.get(DATA_KEYS['LAST_UPDATED'])
    if not last_updated:
        return True
        
    try:
        last_updated_dt = datetime.datetime.fromisoformat(last_updated)
        now = datetime.datetime.now()
        age_hours = (now - last_updated_dt).total_seconds() / 3600
        return age_hours > max_age_hours
    except (ValueError, TypeError):
        return True

def get_cached_data(context, data_type: str) -> Optional[Any]:
    """
    Get cached data from context.state
    
    Args:
        context: ADK context object with state access
        data_type: Type of data to retrieve (use DATA_KEYS)
        
    Returns:
        Cached data or None if not available
    """
    return context.state.get(data_type)

def store_data(context, data_type: str, data: Any) -> None:
    """
    Store data in context.state with timestamp
    
    Args:
        context: ADK context object with state access
        data_type: Type of data to store (use DATA_KEYS)
        data: Data to store
    """
    context.state[data_type] = data
    context.state[DATA_KEYS['LAST_UPDATED']] = datetime.datetime.now().isoformat()

def get_all_cached_data(context) -> Dict[str, Any]:
    """
    Get all cached financial data from context.state
    
    Args:
        context: ADK context object with state access
        
    Returns:
        Dictionary containing all cached data
    """
    cached_data = {}
    for key_name, key_value in DATA_KEYS.items():
        if key_name != 'LAST_UPDATED':
            data = context.state.get(key_value)
            if data:
                cached_data[key_name.lower()] = data
    
    return cached_data

def has_all_data(context) -> bool:
    """
    Check if all required financial data is cached
    
    Args:
        context: ADK context object with state access
        
    Returns:
        bool: True if all data types are cached
    """
    required_keys = [key for key in DATA_KEYS.values() if key != DATA_KEYS['LAST_UPDATED']]
    return all(context.state.get(key) is not None for key in required_keys)

def clear_cached_data(context) -> None:
    """
    Clear all cached financial data from context.state
    
    Args:
        context: ADK context object with state access
    """
    for key in DATA_KEYS.values():
        if key in context.state:
            del context.state[key] 