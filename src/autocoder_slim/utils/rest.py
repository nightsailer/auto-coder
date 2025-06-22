# Minimal stub for REST utilities - AutoCoder Slim version
# This provides basic compatibility without full REST functionality

class HttpDoc:
    """Stub implementation for HTTP documentation"""
    
    def __init__(self, *args, **kwargs):
        pass
    
    def get(self, *args, **kwargs):
        """Stub GET method"""
        return {}
    
    def post(self, *args, **kwargs):
        """Stub POST method"""
        return {}
    
    def put(self, *args, **kwargs):
        """Stub PUT method"""
        return {}
    
    def delete(self, *args, **kwargs):
        """Stub DELETE method"""
        return {}

def http_request(*args, **kwargs):
    """Stub HTTP request function"""
    return {}

def parse_response(*args, **kwargs):
    """Stub response parser"""
    return {}

# Default exports for compatibility
__all__ = [
    'HttpDoc',
    'http_request',
    'parse_response'
] 