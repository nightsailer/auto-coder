# Minimal stub for dispacher - AutoCoder Slim version
# This provides basic compatibility without full dispacher functionality

class Dispacher:
    """Stub implementation for request dispatcher"""
    
    def __init__(self, *args, **kwargs):
        pass
    
    def dispatch(self, *args, **kwargs):
        """Stub dispatch method"""
        print("⚠️ Dispacher functionality not available in AutoCoder Slim")
        return None
    
    def register(self, *args, **kwargs):
        """Stub register method"""
        pass
    
    def unregister(self, *args, **kwargs):
        """Stub unregister method"""
        pass

# Default exports for compatibility
__all__ = ['Dispacher']
