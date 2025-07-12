import json
import os
import time
import byzerllm
from typing import List, Dict, Any, Union, Optional, Tuple, Type, Generator
from autocoder_slim.common.printer import Printer
from autocoder_slim.common import AutoCoderArgs, SourceCodeList
from autocoder_slim.common.global_cancel import global_cancel
from loguru import logger
from autocoder_slim.common.utils_code_auto_generate import stream_chat_with_continue

# Import tool resolvers and types from existing AutoCoder-Slim modules
from autocoder_slim.common.v2.agent.agentic_edit_tools import (
    BaseToolResolver,
    ExecuteCommandToolResolver, ReadFileToolResolver, WriteToFileToolResolver,
    ReplaceInFileToolResolver, SearchFilesToolResolver, ListFilesToolResolver,
    ListCodeDefinitionNamesToolResolver, ListPackageInfoToolResolver,
    AskFollowupQuestionToolResolver, AttemptCompletionToolResolver, 
    PlanModeRespondToolResolver, UseMcpToolResolver
)

from autocoder_slim.common.v2.agent.agentic_edit_types import (
    AgenticEditRequest, ToolResult, MemoryConfig, CommandConfig, BaseTool,
    ExecuteCommandTool, ReadFileTool, WriteToFileTool, ReplaceInFileTool,
    SearchFilesTool, ListFilesTool, ListCodeDefinitionNamesTool, ListPackageInfoTool,
    AskFollowupQuestionTool, AttemptCompletionTool, PlanModeRespondTool, UseMcpTool,
    # Event Types
    LLMOutputEvent, LLMThinkingEvent, ToolCallEvent, ToolResultEvent, 
    CompletionEvent, PlanModeRespondEvent, ErrorEvent,
    AgenticEditConversationConfig, FileChangeEntry
)

# Map Pydantic Tool Models to their Resolver Classes
TOOL_RESOLVER_MAP: Dict[Type[BaseTool], Type[BaseToolResolver]] = {
    ExecuteCommandTool: ExecuteCommandToolResolver,
    ReadFileTool: ReadFileToolResolver,
    WriteToFileTool: WriteToFileToolResolver,
    ReplaceInFileTool: ReplaceInFileToolResolver,
    SearchFilesTool: SearchFilesToolResolver,
    ListFilesTool: ListFilesToolResolver,
    ListCodeDefinitionNamesTool: ListCodeDefinitionNamesToolResolver,
    ListPackageInfoTool: ListPackageInfoToolResolver,
    AskFollowupQuestionTool: AskFollowupQuestionToolResolver,
    AttemptCompletionTool: AttemptCompletionToolResolver,
    PlanModeRespondTool: PlanModeRespondToolResolver,
    UseMcpTool: UseMcpToolResolver,
}


class AgenticEdit:
    def __init__(
        self,
        llm: Union[byzerllm.ByzerLLM, byzerllm.SimpleByzerLLM],
        conversation_history: List[Dict[str, Any]],
        files: SourceCodeList,
        args: AutoCoderArgs,
        memory_config: MemoryConfig,
        command_config: Optional[CommandConfig] = None,
        conversation_name: Optional[str] = "current",
        conversation_config: Optional[AgenticEditConversationConfig] = None
    ):
        self.llm = llm
        self.args = args
        self.printer = Printer()
        self.files = files
        self.conversation_history = conversation_history
        self.current_conversations = []
        self.memory_config = memory_config
        self.command_config = command_config
        
        # Simplified initialization - remove complex dependencies for now
        self.conversation_config = conversation_config or AgenticEditConversationConfig(action="resume")
        
        # Simplified server info (stub implementation)
        self.mcp_server_info = ""
        self.rag_server_info = ""
        
        # Basic file change tracking
        self.file_changes: Dict[str, FileChangeEntry] = {}

    def record_file_change(self, file_path: str, change_type: str, diff: Optional[str] = None, content: Optional[str] = None):
        """记录单个文件的变更信息"""
        entry = self.file_changes.get(file_path)
        if entry is None:
            entry = FileChangeEntry(type=change_type, diffs=[], content=content)
            self.file_changes[file_path] = entry
        else:
            if entry.type != "added":
                entry.type = change_type
            if content is not None:
                entry.content = content
        if diff:
            entry.diffs.append(diff)

    def get_all_file_changes(self) -> Dict[str, FileChangeEntry]:
        """获取当前记录的所有文件变更信息"""
        return self.file_changes

    @byzerllm.prompt()
    def _analyze(self, request: AgenticEditRequest) -> str:
        """Core analysis prompt for AgenticEdit"""
        return """
        You are a highly skilled software engineer with extensive knowledge in many programming languages, frameworks, design patterns, and best practices.

        TOOL USE

        You have access to a set of tools that are executed upon the user's approval. You can use one tool per message, and will receive the result of that tool use in the user's response. You use tools step-by-step to accomplish a given task, with each tool use informed by the result of the previous tool use.

        # Tool Use Formatting

        Tool use is formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags.

        # Tools

        ## execute_command
        Description: Request to execute a CLI command on the system.
        Parameters:
        - command: (required) The CLI command to execute
        - requires_approval: (required) Boolean indicating whether this command requires explicit user approval
        Usage:
        <execute_command>
        <command>Your command here</command>
        <requires_approval>true or false</requires_approval>
        </execute_command>

        ## read_file
        Description: Request to read the contents of a file at the specified path.
        Parameters:
        - path: (required) The path of the file to read
        Usage:
        <read_file>
        <path>File path here</path>
        </read_file>

        ## write_to_file
        Description: Request to write content to a file at the specified path.
        Parameters:
        - path: (required) The path of the file to write to
        - content: (required) The content to write to the file
        Usage:
        <write_to_file>
        <path>File path here</path>
        <content>Your file content here</content>
        </write_to_file>

        ## replace_in_file
        Description: Request to replace sections of content in an existing file using SEARCH/REPLACE blocks.
        Parameters:
        - path: (required) The path of the file to modify
        - diff: (required) One or more SEARCH/REPLACE blocks
        Usage:
        <replace_in_file>
        <path>File path here</path>
        <diff>Search and replace blocks here</diff>
        </replace_in_file>

        ## search_files
        Description: Request to perform a regex search across files in a specified directory.
        Parameters:
        - path: (required) The path of the directory to search in
        - regex: (required) The regular expression pattern to search for
        - file_pattern: (optional) Glob pattern to filter files
        Usage:
        <search_files>
        <path>Directory path here</path>
        <regex>Your regex pattern here</regex>
        <file_pattern>file pattern here (optional)</file_pattern>
        </search_files>

        ## list_files
        Description: Request to list files and directories within the specified directory.
        Parameters:
        - path: (required) The path of the directory to list contents for
        - recursive: (optional) Whether to list files recursively
        Usage:
        <list_files>
        <path>Directory path here</path>
        <recursive>true or false (optional)</recursive>
        </list_files>

        ## list_code_definition_names
        Description: Request to list definition names (classes, functions, methods, etc.) used in source code files.
        Parameters:
        - path: (required) The path of the directory to list definitions for
        Usage:
        <list_code_definition_names>
        <path>Directory path here</path>
        </list_code_definition_names>

        ## list_package_info
        Description: Request to retrieve information about a source code package.
        Parameters:
        - path: (required) The source code package directory path
        Usage:
        <list_package_info>
        <path>relative/or/absolute/package/path</path>
        </list_package_info>

        ## ask_followup_question
        Description: Ask the user a question to gather additional information.
        Parameters:
        - question: (required) The question to ask the user
        - options: (optional) Array of options for the user to choose from
        Usage:
        <ask_followup_question>
        <question>Your question here</question>
        <options>Array of options here (optional)</options>
        </ask_followup_question>

        ## attempt_completion
        Description: Present the result of your work to the user.
        Parameters:
        - result: (required) The result of the task
        - command: (optional) A CLI command to demonstrate the result
        Usage:
        <attempt_completion>
        <result>Your final result description here</result>
        <command>Command to demonstrate result (optional)</command>
        </attempt_completion>

        ## plan_mode_respond
        Description: Respond to the user's inquiry in planning mode.
        Parameters:
        - response: (required) The response to provide to the user
        - options: (optional) Array of options for the user to choose from
        Usage:
        <plan_mode_respond>
        <response>Your response here</response>
        <options>Array of options here (optional)</options>
        </plan_mode_respond>

        ## use_mcp_tool
        Description: Request to execute a tool via Model Context Protocol.
        Parameters:
        - server_name: (optional) The name of the MCP server to use
        - tool_name: (optional) The name of the tool to execute
        - query: (required) The query to pass to the tool
        Usage:
        <use_mcp_tool>
        <server_name>xxx</server_name>
        <tool_name>xxxx</tool_name>
        <query>Your query here</query>
        </use_mcp_tool>
        """

    def _reconstruct_tool_xml(self, tool: BaseTool) -> str:
        """Reconstruct tool XML for display"""
        tool_name = type(tool).__name__.replace("Tool", "").lower()
        # Convert CamelCase to snake_case
        tool_name = ''.join(['_' + c.lower() if c.isupper() else c for c in tool_name]).lstrip('_')
        
        xml_parts = [f"<{tool_name}>"]
        for field_name, field_value in tool.model_dump().items():
            if field_value is not None:
                xml_parts.append(f"<{field_name}>{field_value}</{field_name}>")
        xml_parts.append(f"</{tool_name}>")
        return "\n".join(xml_parts)

    def analyze(self, request: AgenticEditRequest) -> Generator[Union[LLMOutputEvent, LLMThinkingEvent, ToolCallEvent, ToolResultEvent, CompletionEvent, ErrorEvent], None, None]:
        """Main analysis method that processes user requests and executes tools"""
        try:
            global_cancel.check_and_raise(token=self.args.event_file)
            
            # Prepare conversation
            self.current_conversations = self.conversation_history.copy()
            
            # Add user request to conversation
            self.current_conversations.append({
                "role": "user", 
                "content": request.query
            })

            # Generate LLM response with tool parsing
            llm_config = {"human_as_model": self.args.human_as_model}
            
            # Use stream_chat_with_continue for generation
            generator = stream_chat_with_continue(
                self.llm, 
                self.current_conversations, 
                llm_config, 
                self.args
            )
            
            # Process streaming response and parse for tools
            yield from self.stream_and_parse_llm_response(generator)
            
        except Exception as e:
            logger.error(f"Error in AgenticEdit.analyze: {str(e)}")
            yield ErrorEvent(error=str(e))

    def stream_and_parse_llm_response(self, generator: Generator[Tuple[str, Any], None, None]) -> Generator[Union[LLMOutputEvent, LLMThinkingEvent, ToolCallEvent, ErrorEvent], None, None]:
        """Stream and parse LLM response for tool calls"""
        
        def parse_tool_xml(tool_xml: str, tool_tag: str) -> Optional[BaseTool]:
            """Parse tool XML into Pydantic models"""
            try:
                # Simple XML parsing for tool parameters
                import re
                
                # Extract tool parameters
                param_pattern = r'<(\w+)>(.*?)</\1>'
                params = {}
                
                for match in re.finditer(param_pattern, tool_xml, re.DOTALL):
                    param_name = match.group(1)
                    param_value = match.group(2).strip()
                    params[param_name] = param_value
                
                # Map tool tags to tool classes
                tool_map = {
                    'execute_command': ExecuteCommandTool,
                    'read_file': ReadFileTool,
                    'write_to_file': WriteToFileTool,
                    'replace_in_file': ReplaceInFileTool,
                    'search_files': SearchFilesTool,
                    'list_files': ListFilesTool,
                    'list_code_definition_names': ListCodeDefinitionNamesTool,
                    'list_package_info': ListPackageInfoTool,
                    'ask_followup_question': AskFollowupQuestionTool,
                    'attempt_completion': AttemptCompletionTool,
                    'plan_mode_respond': PlanModeRespondTool,
                    'use_mcp_tool': UseMcpTool,
                }
                
                tool_class = tool_map.get(tool_tag)
                if tool_class:
                    return tool_class(**params)
                return None
                
            except Exception as e:
                logger.error(f"Error parsing tool XML: {e}")
                return None

        accumulated_content = ""
        current_metadata = None
        
        for content_chunk, metadata in generator:
            accumulated_content += content_chunk
            current_metadata = metadata
            
            # Yield content event
            yield LLMOutputEvent(content=content_chunk)
            
            # Check for tool usage in accumulated content
            # Simple regex to find tool XML blocks
            import re
            tool_pattern = r'<(\w+)>(.*?)</\1>'
            
            for match in re.finditer(tool_pattern, accumulated_content, re.DOTALL):
                tool_tag = match.group(1)
                tool_xml = match.group(0)
                
                # Check if this looks like a tool call
                known_tools = [
                    'execute_command', 'read_file', 'write_to_file', 'replace_in_file',
                    'search_files', 'list_files', 'list_code_definition_names', 
                    'list_package_info', 'ask_followup_question', 'attempt_completion',
                    'plan_mode_respond', 'use_mcp_tool'
                ]
                
                if tool_tag in known_tools:
                    # Parse and execute tool
                    tool_obj = parse_tool_xml(tool_xml, tool_tag)
                    if tool_obj:
                        yield ToolCallEvent(tool=tool_obj, tool_xml=tool_xml)
                        
                        # Execute tool
                        resolver_cls = TOOL_RESOLVER_MAP.get(type(tool_obj))
                        if resolver_cls:
                            resolver = resolver_cls(self, tool_obj, self.args)
                            tool_result = resolver.resolve()
                            yield ToolResultEvent(tool_name=tool_tag, result=tool_result)
                            
                            # Handle special tools
                            if isinstance(tool_obj, AttemptCompletionTool):
                                yield CompletionEvent(completion=tool_obj, completion_xml=tool_xml)
                                return
                            elif isinstance(tool_obj, PlanModeRespondTool):
                                yield PlanModeRespondEvent(completion=tool_obj, completion_xml=tool_xml)
                                return

    def apply_changes(self):
        """Apply recorded changes to files"""
        # Simplified implementation
        logger.info("Changes would be applied here in full implementation")
        pass

    def run_in_terminal(self, request: AgenticEditRequest):
        """Terminal interface for running AgenticEdit"""
        for event in self.analyze(request):
            if isinstance(event, LLMOutputEvent):
                print(event.content, end='', flush=True)
            elif isinstance(event, ToolCallEvent):
                print(f"\n[Tool Call: {type(event.tool).__name__}]")
            elif isinstance(event, ToolResultEvent):
                print(f"[Result: {event.result.success}]")
            elif isinstance(event, (CompletionEvent, PlanModeRespondEvent)):
                print("\n[Task Completed]")
                break
            elif isinstance(event, ErrorEvent):
                print(f"\n[Error: {event.error}]")
                break
