# common.v2.agent.ac.mod.md

## 模块信息
- **模块名称**: common.v2.agent
- **模块类型**: 包模块 (Package Module)
- **主要功能**: 智能代码编辑代理系统，提供基于大语言模型的交互式代码编辑和项目管理

## 核心功能

### 智能代理架构
- **AgenticEdit**: 核心代理类，负责LLM交互和工具调度
- **Runner模式**: 提供三种运行模式适应不同使用场景
- **工具系统**: 完整的工具解析和执行框架
- **事件驱动**: 基于事件流的异步处理架构

### Runner运行模式
- **TerminalRunner**: 终端运行模式，提供Rich格式化输出
- **EventRunner**: 事件系统运行模式，支持Web应用集成
- **SdkRunner**: SDK运行模式，提供最大灵活性
- **BaseRunner**: 统一的基础运行器抽象

### 工具生态系统
- **文件操作工具**: 读取、写入、替换文件内容
- **搜索工具**: 文件搜索、代码定义查找
- **系统工具**: 命令执行、环境操作
- **任务管理工具**: Todo列表管理和进度跟踪
- **交互工具**: 用户询问、任务完成控制

## 关键组件

### 1. AgenticEdit 核心代理类
```python
class AgenticEdit:
    def __init__(self, llm: ByzerLLM, args: AutoCoderArgs, 
                 files: SourceCodeList, conversation_history: List[Dict],
                 memory_config: MemoryConfig, command_config: Optional[CommandConfig],
                 conversation_name: str, conversation_config: AgenticEditConversationConfig)
    
    def analyze(self, request: AgenticEditRequest) -> Generator[AgentEvent, None, None]
    def run_in_terminal(self, request: AgenticEditRequest) -> None
    def run_with_events(self, request: AgenticEditRequest) -> None
    def stream_and_parse_llm_response(self, messages: List[Dict]) -> Generator[AgentEvent, None, None]
```

### 2. Runner运行器系统
```python
# 基础运行器
class BaseRunner:
    def run(self, request: AgenticEditRequest) -> Any
    def apply_pre_changes(self) -> None
    def apply_changes(self) -> None
    def analyze(self, request: AgenticEditRequest) -> Generator[AgentEvent, None, None]

# 终端运行器
class TerminalRunner(BaseRunner):
    def run(self, request: AgenticEditRequest) -> None

# 事件运行器  
class EventRunner(BaseRunner):
    def run(self, request: AgenticEditRequest) -> None

# SDK运行器
class SdkRunner(BaseRunner):
    def run(self, request: AgenticEditRequest) -> Generator[AgentEvent, None, None]
```

### 3. 数据模型
```python
# 代理请求模型
class AgenticEditRequest(BaseModel):
    user_input: str
    context: Optional[str] = None

# 对话配置模型
class AgenticEditConversationConfig(BaseModel):
    conversation_name: str = "current"
    action: str = "resume"  # new/resume/list
    query: Optional[str] = None
    pull_request: bool = False

# 内存配置模型
class MemoryConfig(BaseModel):
    memory: Dict[str, Any]
    save_memory_func: Callable[[], None]
```

### 4. 工具系统架构
```python
# 基础工具解析器
class BaseToolResolver:
    def can_resolve(self, tool_call: str) -> bool
    def resolve(self, tool_call: str, agent: 'AgenticEdit') -> ToolResult

# 工具结果模型
class ToolResult(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    files_changed: List[str] = []
```

## 主要工具类型

### 1. 文件操作工具

#### ReadFileTool - 文件读取
```python
class ReadFileTool(BaseModel):
    path: str  # 文件路径（相对于项目根目录）

# 使用示例
<read_file><path>src/main.py</path></read_file>
```

#### WriteToFileTool - 文件写入
```python
class WriteToFileTool(BaseModel):
    path: str     # 目标文件路径
    content: str  # 要写入的完整内容

# 使用示例
<write_to_file>
<path>config.json</path>
<content>{"version": "1.0"}</content>
</write_to_file>
```

#### ReplaceInFileTool - 文件内容替换
```python
class ReplaceInFileTool(BaseModel):
    path: str  # 目标文件路径
    diff: str  # SEARCH/REPLACE格式的差异

# 使用示例
<replace_in_file>
<path>src/utils.py</path>
<diff>
<<<<<<< SEARCH
def old_function():
    pass
>>>>>>> REPLACE
def new_function():
    return "updated"
</diff>
</replace_in_file>
```

### 2. 搜索和探索工具

#### SearchFilesTool - 文件内容搜索
```python
class SearchFilesTool(BaseModel):
    path: str                           # 搜索目录
    regex: str                          # 正则表达式
    file_pattern: Optional[str] = None  # 文件过滤模式

# 使用示例
<search_files>
<path>src/</path>
<regex>class.*Component</regex>
<file_pattern>*.py</file_pattern>
</search_files>
```

#### ListFilesTool - 文件列表
```python
class ListFilesTool(BaseModel):
    path: str                          # 目录路径
    recursive: Optional[bool] = False  # 是否递归

# 使用示例
<list_files>
<path>src/components</path>
<recursive>true</recursive>
</list_files>
```

### 3. 系统操作工具

#### ExecuteCommandTool - 命令执行
```python
class ExecuteCommandTool(BaseModel):
    command: str              # 要执行的命令
    requires_approval: bool   # 是否需要用户批准

# 使用示例
<execute_command>
<command>npm test</command>
<requires_approval>false</requires_approval>
</execute_command>
```

### 4. 任务管理工具

#### TodoWriteTool - Todo列表管理（支持<task>标签）
```python
class TodoWriteTool(BaseModel):
    action: str                      # create/add_task/update/mark_progress/mark_completed
    task_id: Optional[str] = None    # 任务ID
    content: Optional[str] = None    # 任务内容
    priority: Optional[str] = None   # high/medium/low
    status: Optional[str] = None     # pending/in_progress/completed
    notes: Optional[str] = None      # 备注信息

# 使用示例 - 支持<task>标签格式
<todo_write>
<action>create</action>
<content>
<task>实现用户认证功能</task>
<task>添加数据库迁移</task>
<task>编写单元测试</task>
</content>
</todo_write>
```

### 5. 交互控制工具

#### AskFollowupQuestionTool - 用户交互
```python
class AskFollowupQuestionTool(BaseModel):
    question: str                        # 询问的问题
    options: Optional[List[str]] = None  # 预设选项

# 使用示例
<ask_followup_question>
<question>你希望使用哪个数据库？</question>
<options>["PostgreSQL", "MySQL", "SQLite"]</options>
</ask_followup_question>
```

#### AttemptCompletionTool - 任务完成
```python
class AttemptCompletionTool(BaseModel):
    result: str                       # 完成结果描述
    command: Optional[str] = None     # 演示命令

# 使用示例
<attempt_completion>
<result>成功实现了用户认证系统，包括登录、注册和权限管理</result>
<command>python manage.py runserver</command>
</attempt_completion>
```

## 使用指南

### 1. 推荐使用方式 - Runner模式

```python
from autocoder.common.v2.agent.runner import TerminalRunner, EventRunner, SdkRunner
from autocoder.common.v2.agent.agentic_edit_types import AgenticEditRequest, AgenticEditConversationConfig, MemoryConfig
from autocoder.common import SourceCodeList, SourceCode, AutoCoderArgs
from autocoder.utils.llms import get_single_llm

# 1. 获取LLM实例
memory = get_memory()
conf = memory.get("conf", {})
product_mode = conf.get("product_mode", "lite")
model_name = conf.get("model", "v3_chat")
llm = get_single_llm(model_name, product_mode=product_mode)

# 2. 获取AutoCoderArgs配置
args = get_final_config()

# 3. 准备源代码文件列表
current_files = memory.get("current_files", {}).get("files", [])
sources = []
for file in current_files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            sources.append(SourceCode(module_name=file, source_code=f.read()))
    except Exception as e:
        print(f"Failed to read file {file}: {e}")

# 4. 准备内存配置
memory_config = MemoryConfig(
    memory=memory,
    save_memory_func=save_memory
)

# 5. 准备对话配置
conversation_config = AgenticEditConversationConfig(
    conversation_name="current",
    action="resume",
    query=None,
    pull_request=False
)

# 6. 选择运行模式
```

### 2. 终端运行模式
```python
# 适用于命令行应用、脚本工具
terminal_runner = TerminalRunner(
    llm=llm,
    conversation_history=[],
    files=SourceCodeList(sources=sources),
    args=args,
    memory_config=memory_config,
    command_config=None,
    conversation_name="current",
    conversation_config=conversation_config
)

# 阻塞式运行，Rich格式化输出
terminal_runner.run(AgenticEditRequest(user_input="重构这个函数"))
```

### 3. 事件系统运行模式
```python
# 适用于Web应用、GUI界面
event_runner = EventRunner(
    llm=llm,
    conversation_history=[],
    files=SourceCodeList(sources=sources),
    args=args,
    memory_config=memory_config,
    command_config=None,
    conversation_name="current",
    conversation_config=conversation_config
)

# 将事件写入标准事件系统
event_runner.run(AgenticEditRequest(user_input="添加单元测试"))
```

### 4. SDK运行模式
```python
# 适用于自定义集成、SDK开发
sdk_runner = SdkRunner(
    llm=llm,
    conversation_history=[],
    files=SourceCodeList(sources=sources),
    args=args,
    memory_config=memory_config,
    command_config=None,
    conversation_name="current",
    conversation_config=conversation_config
)

# 自定义事件处理
for event in sdk_runner.run(AgenticEditRequest(user_input="优化性能")):
    if isinstance(event, LLMOutputEvent):
        print(f"LLM输出: {event.text}")
    elif isinstance(event, ToolCallEvent):
        print(f"调用工具: {type(event.tool).__name__}")
    elif isinstance(event, CompletionEvent):
        print(f"任务完成: {event.completion.result}")
        break
```

## 事件系统

### 1. 事件类型
```python
# LLM相关事件
class LLMThinkingEvent(BaseModel):
    thinking: str

class LLMOutputEvent(BaseModel):
    text: str

# 工具相关事件
class ToolCallEvent(BaseModel):
    tool: BaseModel
    tool_call_id: str

class ToolResultEvent(BaseModel):
    result: ToolResult
    tool_call_id: str

# 控制事件
class CompletionEvent(BaseModel):
    completion: AttemptCompletionTool

class ErrorEvent(BaseModel):
    error: str
    error_type: str
```

### 2. 事件路径映射（EventRunner）
```
LLMThinkingEvent → /agent/edit/thinking
LLMOutputEvent → /agent/edit/output
ToolCallEvent → /agent/edit/tool/call
ToolResultEvent → /agent/edit/tool/result
CompletionEvent → /agent/edit/completion
ErrorEvent → /agent/edit/error
TokenUsageEvent → /agent/edit/token_usage
ConversationIdEvent → /agent/edit/conversation_id
```

## 目录结构

```
src/autocoder/common/v2/agent/
├── __init__.py                          # 模块初始化文件
├── agentic_edit.py                      # 核心代理类
├── agentic_edit_types.py                # 类型定义和事件模型
├── agentic_tool_display.py             # 工具显示国际化支持
├── agentic_edit_tools/                  # 工具解析器目录
│   ├── __init__.py
│   ├── base_tool_resolver.py            # 工具解析器基类
│   ├── read_file_tool_resolver.py       # 文件读取工具
│   ├── write_to_file_tool_resolver.py   # 文件写入工具
│   ├── replace_in_file_tool_resolver.py # 文件替换工具
│   ├── search_files_tool_resolver.py    # 文件搜索工具
│   ├── list_files_tool_resolver.py      # 文件列表工具
│   ├── execute_command_tool_resolver.py # 命令执行工具
│   ├── todo_write_tool_resolver.py      # Todo管理工具（支持<task>标签）
│   ├── ask_followup_question_tool_resolver.py # 用户交互工具
│   ├── attempt_completion_tool_resolver.py # 任务完成工具
│   ├── use_mcp_tool_resolver.py         # MCP工具解析器
│   ├── use_rag_tool_resolver.py         # RAG工具解析器
│   └── dangerous_command_checker.py     # 危险命令检查器
└── runner/                              # 运行器模块
    ├── __init__.py
    ├── base_runner.py                   # 基础运行器
    ├── terminal_runner.py               # 终端运行器
    ├── event_runner.py                  # 事件运行器
    ├── sdk_runner.py                    # SDK运行器
    └── tool_display.py                  # 工具显示辅助
```

## 技术特性

### 1. 流式处理
- **实时交互**: 支持LLM的流式输出和实时工具调用
- **事件驱动**: 基于事件流的异步处理架构
- **背压控制**: 自动处理生产者消费者速度差异

### 2. 安全机制
- **危险命令检查**: 自动检测并提示危险的系统命令
- **用户确认**: 敏感操作需要用户明确批准
- **沙箱执行**: 隔离的代码和命令执行环境

### 3. 扩展性
- **工具插件**: 支持自定义工具解析器
- **事件处理**: 可扩展的事件处理机制
- **Runner模式**: 适应不同集成需求的运行模式

### 4. 国际化支持
- **多语言**: 支持工具提示和错误信息的多语言显示
- **本地化**: 根据用户环境自动选择合适的语言

## 集成点

### 与其他模块的关系
- **common模块**: 使用基础配置和工具类
- **utils模块**: 集成LLM管理和项目分析
- **events模块**: 使用标准事件系统
- **memory模块**: 集成内存管理和上下文跟踪

### 外部依赖
- **pydantic**: 数据模型验证
- **rich**: 终端格式化输出
- **byzerllm**: 大语言模型集成
- **xml**: XML工具调用解析

## 扩展指南

### 1. 添加自定义工具
```python
from autocoder.common.v2.agent.agentic_edit_tools.base_tool_resolver import BaseToolResolver

class CustomToolResolver(BaseToolResolver):
    def can_resolve(self, tool_call: str) -> bool:
        return "<custom_tool>" in tool_call
    
    def resolve(self, tool_call: str, agent: 'AgenticEdit') -> ToolResult:
        # 实现自定义工具逻辑
        return ToolResult(success=True, message="Custom tool executed")

# 注册工具解析器
agent.register_tool_resolver(CustomToolResolver())
```

### 2. 自定义Runner
```python
from autocoder.common.v2.agent.runner.base_runner import BaseRunner

class CustomRunner(BaseRunner):
    def run(self, request: AgenticEditRequest) -> Any:
        # 实现自定义运行逻辑
        for event in self.analyze(request):
            self.handle_custom_event(event)
    
    def handle_custom_event(self, event: AgentEvent) -> None:
        # 自定义事件处理
        pass
```

### 3. 事件监听器
```python
class CustomEventListener:
    def on_tool_call(self, event: ToolCallEvent) -> None:
        # 处理工具调用事件
        pass
    
    def on_completion(self, event: CompletionEvent) -> None:
        # 处理任务完成事件
        pass

# 注册事件监听器
runner.add_event_listener(CustomEventListener())
```

---

common.v2.agent模块提供了完整的智能代码编辑代理解决方案，通过灵活的Runner模式和丰富的工具生态系统，为不同场景的AI辅助编程提供了强大的基础设施。 