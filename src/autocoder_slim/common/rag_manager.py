# Intelligent stub for rag_manager module
# This stub maintains interface compatibility for RAG functionality

class RAGConfig:
    """Stub RAG configuration."""
    def __init__(self, name="default", server_name="http://localhost:8000", api_key=None):
        self.name = name
        self.server_name = server_name
        self.api_key = api_key

class RAGManager:
    """Intelligent stub for RAG Manager functionality."""
    
    def __init__(self, args):
        self.args = args
        self._configs = []
    
    def has_configs(self) -> bool:
        """Stub: Always return False to indicate no RAG configs available."""
        return False
    
    def get_config_by_name(self, name: str):
        """Stub: Return None as no configs available."""
        return None
    
    def get_all_configs(self):
        """Stub: Return empty list as no configs available.""" 
        return []
    
    def get_config_info(self) -> str:
        """Stub: Return info about stub mode."""
        return "RAG functionality not available in AutoCoder-Slim stub mode. This is a simplified implementation for compatibility." 