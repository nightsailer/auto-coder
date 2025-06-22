# Minimal stub for symbols utils - AutoCoder Slim version  
# This provides basic compatibility without full index functionality

from enum import Enum

class SymbolType(Enum):
    """Stub implementation for symbol types"""
    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"
    MODULE = "module"
    METHOD = "method"

def search_symbols(*args, **kwargs):
    """Stub implementation for symbol search"""
    return []

def get_symbol_definitions(*args, **kwargs):
    """Stub implementation for getting symbol definitions"""
    return []

def extract_symbols(*args, **kwargs):
    """Stub implementation for symbol extraction"""
    return []

def filter_symbols(*args, **kwargs):
    """Stub implementation for symbol filtering"""
    return []

def symbols_info_to_str(*args, **kwargs):
    """Stub implementation for symbols info to string conversion"""
    return ""

# Default exports for compatibility
__all__ = [
    'SymbolType',
    'search_symbols',
    'get_symbol_definitions', 
    'extract_symbols',
    'filter_symbols',
    'symbols_info_to_str'
] 