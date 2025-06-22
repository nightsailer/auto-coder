# Intelligent stub for mcp_server module
# This stub maintains interface compatibility while avoiding complex dependency chains

from autocoder_slim.common.mcp_server_types import (
    McpRequest, McpInstallRequest, McpRemoveRequest, McpListRequest, 
    McpListRunningRequest, McpRefreshRequest, McpServerInfoRequest, 
    McpResponse, ErrorResult
)

class McpServer:
    """Intelligent stub for MCP server functionality."""
    
    def __init__(self):
        self._running = False

    def start(self):
        """Stub: Start MCP server (returns immediately)."""
        self._running = True

    def stop(self):
        """Stub: Stop MCP server (returns immediately).""" 
        self._running = False

    def send_request(self, request) -> McpResponse:
        """Stub: Handle MCP requests with graceful degradation."""
        
        # Return appropriate stub responses based on request type
        if isinstance(request, McpListRequest):
            return McpResponse(
                result="No MCP servers available (AutoCoder-Slim stub mode)",
                raw_result=ErrorResult(error="Stub mode: MCP functionality simplified")
            )
        elif isinstance(request, McpInstallRequest):
            return McpResponse(
                result="MCP installation not available in slim mode",
                raw_result=ErrorResult(error="Stub mode: Installation disabled")
            )
        elif isinstance(request, McpRequest):
            return McpResponse(
                result="MCP query not available in slim mode. This is a stub implementation for compatibility.",
                raw_result=ErrorResult(error="Stub mode: Query functionality simplified")
            )
        else:
            return McpResponse(
                result="MCP operation not available in slim mode",
                raw_result=ErrorResult(error="Stub mode: Operation not supported")
            )


# Global MCP server instance (stub)
_mcp_server = None

def get_mcp_server():
    """Get the global MCP server instance (stub)."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = McpServer()
        _mcp_server.start()
    return _mcp_server 