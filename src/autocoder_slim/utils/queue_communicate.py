# Minimal stub for queue communication - AutoCoder Slim version
# This provides basic compatibility without full queue functionality

class CommunicateEventType:
    """Stub implementation for communicate event types"""
    MESSAGE = "message"
    ERROR = "error"
    COMPLETE = "complete"

class CommunicateEvent:
    """Stub implementation for communicate events"""
    
    def __init__(self, event_type=None, data=None, *args, **kwargs):
        self.event_type = event_type or CommunicateEventType.MESSAGE
        self.data = data or {}
    
    def to_dict(self):
        """Convert event to dictionary"""
        return {"event_type": self.event_type, "data": self.data}

def queue_communicate(*args, **kwargs):
    """Stub implementation for queue communication"""
    return []

def create_communication_queue(*args, **kwargs):
    """Stub implementation for creating communication queue"""
    return None

def send_to_queue(*args, **kwargs):
    """Stub implementation for sending to queue"""
    pass

def receive_from_queue(*args, **kwargs):
    """Stub implementation for receiving from queue"""
    return None

# Default exports for compatibility
__all__ = [
    'queue_communicate',
    'CommunicateEvent',
    'CommunicateEventType',
    'create_communication_queue',
    'send_to_queue', 
    'receive_from_queue'
] 