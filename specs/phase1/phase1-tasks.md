# Phase 1: 核心模块迁移任务清单

## 任务依赖图

```
T1: 项目结构创建
  ↓
T2: 基础模块迁移 (common, utils)
  ↓  
T3: Agent类型定义迁移 (agentic_edit_types.py)
  ↓
T4: 工具解析器迁移 (14个工具)
  ↓
T5: Agent核心迁移 (agentic_edit.py)
  ↓
T6: 运行器迁移 (auto_coder_runner.py)
  ↓
T7: SDK兼容层实现
  ↓
T8: 集成测试和验证
```

## 详细任务清单

### T1: 项目结构创建
**依赖**: 无  
**时间估算**: 30分钟  
**状态**: ⏸️ 待开始

#### 任务内容
- [ ] 创建`autocoder_slim`根目录
- [ ] 创建包结构目录树
- [ ] 创建所有必要的`__init__.py`文件
- [ ] 设置基础的package配置

#### 具体文件创建
```
autocoder_slim/
├── __init__.py
├── common/
│   ├── __init__.py
│   └── v2/
│       ├── __init__.py
│       └── agent/
│           ├── __init__.py
│           └── agentic_edit_tools/
│               └── __init__.py
├── utils/
│   └── __init__.py
├── commands/
│   └── __init__.py
└── compat/
    └── __init__.py
```

#### 验证标准
- [ ] 所有目录创建成功
- [ ] 可以从Python导入`autocoder_slim`包
- [ ] 目录结构与原版本保持一致

---

### T2: 基础模块迁移
**依赖**: T1  
**时间估算**: 2小时  
**状态**: ⏸️ 待开始

#### 任务内容
- [ ] 迁移`autocoder/common/__init__.py` → `autocoder_slim/common/__init__.py`
- [ ] 迁移`autocoder/utils/llms.py` → `autocoder_slim/utils/llms.py`  
- [ ] 迁移`autocoder/commands/auto_command.py` → `autocoder_slim/commands/auto_command.py`
- [ ] 替换所有import语句中的namespace

#### 具体迁移内容

##### 2.1 迁移common模块
```python
# autocoder_slim/common/__init__.py
# 需要迁移的核心类：
- AutoCoderArgs
- SourceCode  
- SourceCodeList
- ActionYmlFileManager
- ResultManager
# 移除RAG相关的import和类定义
```

##### 2.2 迁移utils.llms
```python
# autocoder_slim/utils/llms.py
# 保留所有LLM相关功能：
- get_single_llm()
- ByzerLLM类
- 所有LLM配置和初始化函数
# 替换import中的autocoder → autocoder_slim
```

##### 2.3 迁移commands.auto_command
```python
# autocoder_slim/commands/auto_command.py  
# 保留传统命令处理：
- CommandAutoTuner类
- AutoCommandRequest类
- CommandConfig类
- MemoryConfig类
```

#### 验证标准
- [ ] 所有迁移的模块可以正常导入
- [ ] 基础类可以正常实例化
- [ ] import语句中无autocoder残留

---

### T3: Agent类型定义迁移
**依赖**: T2  
**时间估算**: 1小时  
**状态**: ⏸️ 待开始

#### 任务内容
- [ ] 迁移`autocoder/common/v2/agent/agentic_edit_types.py`
- [ ] 保持所有类型定义完整
- [ ] 替换相关import语句

#### 迁移内容详情
```python
# autocoder_slim/common/v2/agent/agentic_edit_types.py
# 需要完整保留的内容：

# 13种工具类型定义
class ExecuteCommandTool(BaseModel): pass
class ReadFileTool(BaseModel): pass
class WriteToFileTool(BaseModel): pass
class ReplaceInFileTool(BaseModel): pass
class ListFilesTool(BaseModel): pass
class AttemptCompletionTool(BaseModel): pass
class AskFollowUpQuestionTool(BaseModel): pass
class StrReplaceEditorTool(BaseModel): pass
class CreateDirectoryTool(BaseModel): pass
class SearchAndReplaceTool(BaseModel): pass
class ViewRangeTool(BaseModel): pass
class ScrollToLineTool(BaseModel): pass
class FindInFilesTool(BaseModel): pass
class OpenFileTool(BaseModel): pass

# 9种事件类型定义
class LLMOutputEvent(BaseModel): pass
class ToolCallEvent(BaseModel): pass
class ToolResultEvent(BaseModel): pass
class CompletionEvent(BaseModel): pass
class ErrorEvent(BaseModel): pass
# ... 其他事件类型

# 配置和请求模型
class AgenticEditConversationConfig(BaseModel): pass
class AgenticEditRequest(BaseModel): pass
```

#### 验证标准  
- [ ] 所有工具类型可以正常导入
- [ ] 所有事件类型可以正常导入
- [ ] 配置类可以正常实例化
- [ ] 类型系统完整性检查通过

---

### T4: 工具解析器迁移
**依赖**: T3  
**时间估算**: 4小时  
**状态**: ⏸️ 待开始

#### 任务内容
批量迁移14个工具解析器，保持功能完全一致

#### 4.1 工具列表和迁移
```python
# 需要迁移的14个工具文件：
autocoder/common/v2/agent/agentic_edit_tools/ → autocoder_slim/common/v2/agent/agentic_edit_tools/

1. read_file_resolver.py
2. write_to_file_resolver.py  
3. replace_in_file_resolver.py
4. execute_command_resolver.py
5. list_files_resolver.py
6. attempt_completion_resolver.py
7. ask_follow_up_question_resolver.py
8. str_replace_editor_resolver.py
9. create_directory_resolver.py
10. search_and_replace_resolver.py
11. view_range_resolver.py
12. scroll_to_line_resolver.py
13. find_in_files_resolver.py
14. open_file_resolver.py
```

#### 4.2 迁移步骤（每个工具）
```python
# 对每个工具解析器：
1. 复制原文件到新位置
2. 替换import语句：
   from autocoder.xxx → from autocoder_slim.xxx
3. 保持类名完全一致：
   class ReadFileResolver(BaseToolResolver)
4. 保持方法签名一致：
   def resolve(self, tool_data: dict) -> ToolResult
5. 验证功能完整性
```

#### 4.3 __init__.py配置
```python
# autocoder_slim/common/v2/agent/agentic_edit_tools/__init__.py
__all__ = [
    'ReadFileResolver',
    'WriteToFileResolver', 
    'ReplaceInFileResolver',
    'ExecuteCommandResolver',
    'ListFilesResolver',
    'AttemptCompletionResolver',
    'AskFollowUpQuestionResolver',
    'StrReplaceEditorResolver',
    'CreateDirectoryResolver',
    'SearchAndReplaceResolver',
    'ViewRangeResolver',
    'ScrollToLineResolver',
    'FindInFilesResolver',
    'OpenFileResolver'
]

# 导入所有工具解析器
from .read_file_resolver import ReadFileResolver
from .write_to_file_resolver import WriteToFileResolver
# ... 其他导入
```

#### 验证标准
- [ ] 所有14个工具解析器可以正常导入
- [ ] 每个工具可以正常实例化
- [ ] resolve方法可以正常调用
- [ ] 工具功能与原版一致

---

### T5: Agent核心迁移
**依赖**: T4  
**时间估算**: 3小时  
**状态**: ⏸️ 待开始

#### 任务内容
迁移Agent核心类，这是最重要的模块

#### 5.1 文件迁移
```python
# 迁移 autocoder/common/v2/agent/agentic_edit.py 
# → autocoder_slim/common/v2/agent/agentic_edit.py
```

#### 5.2 关键import替换
```python
# 需要替换的主要import：
from autocoder.common import AutoCoderArgs, SourceCodeList, SourceCode
→ from autocoder_slim.common import AutoCoderArgs, SourceCodeList, SourceCode

from autocoder.utils.llms import get_single_llm
→ from autocoder_slim.utils.llms import get_single_llm

from autocoder.common.v2.agent.agentic_edit_types import *
→ from autocoder_slim.common.v2.agent.agentic_edit_types import *

from autocoder.common.v2.agent.agentic_edit_tools import *
→ from autocoder_slim.common.v2.agent.agentic_edit_tools import *

# 以及其他所有autocoder相关的import
```

#### 5.3 核心功能保留
```python
# AgenticEdit类的所有核心方法必须保持一致：
class AgenticEdit:
    def __init__(self, llm, files, config): pass
    def analyze(self, request): pass  
    def run(self, request): pass
    def run_in_terminal(self, request): pass
    def run_with_events(self, request): pass
    def stream_and_parse_llm_response(self, response): pass
    # ... 所有其他方法
```

#### 验证标准
- [ ] AgenticEdit类可以正常导入
- [ ] 可以正常实例化Agent
- [ ] analyze方法正常工作
- [ ] run方法可以正确执行
- [ ] 工具调用机制正常

---

### T6: 运行器迁移
**依赖**: T5  
**时间估算**: 4小时  
**状态**: ⏸️ 待开始

#### 任务内容
迁移核心运行器文件（3486行），这是最复杂的任务

#### 6.1 文件迁移
```python
# 迁移 autocoder/auto_coder_runner.py → autocoder_slim/auto_coder_runner.py
```

#### 6.2 重要import替换
```python
# Agent相关
from autocoder.common.v2.agent.agentic_edit import AgenticEdit, AgenticEditRequest
→ from autocoder_slim.common.v2.agent.agentic_edit import AgenticEdit, AgenticEditRequest

from autocoder.common.v2.agent.agentic_edit_types import *
→ from autocoder_slim.common.v2.agent.agentic_edit_types import *

# 基础模块
from autocoder.common import AutoCoderArgs, SourceCodeList, SourceCode
→ from autocoder_slim.common import AutoCoderArgs, SourceCodeList, SourceCode

from autocoder.commands.auto_command import *
→ from autocoder_slim.commands.auto_command import *

# 工具模块
from autocoder.utils.llms import get_single_llm
→ from autocoder_slim.utils.llms import get_single_llm

# 还有30+个其他import需要替换
```

#### 6.3 核心函数保留
```python
# 必须保留的40+个函数：
def run_auto_command(args): pass           # SDK主入口
def configure(config): pass                # 配置函数
def start(args): pass                     # 启动函数
def stop(): pass                          # 停止函数
def get_memory(): pass                    # 内存管理
def save_memory(): pass                   # 内存保存
def get_final_config(): pass             # 配置获取
# ... 其他所有函数
```

#### 6.4 特殊处理项
```python
# MCP服务支持保留
from autocoder.common.mcp_server import get_mcp_server
→ from autocoder_slim.common.mcp_server import get_mcp_server

# RAG相关模块移除 
# from autocoder.common.rag_manager import RAGManager  # 删除这行
# 以及所有RAG相关的代码段
```

#### 验证标准
- [ ] run_auto_command函数正常工作
- [ ] configure函数正常工作
- [ ] Agent模式可以正常启动
- [ ] Traditional模式保持兼容
- [ ] MCP服务支持正常

---

### T7: SDK兼容层实现
**依赖**: T6  
**时间估算**: 1小时  
**状态**: ⏸️ 待开始

#### 任务内容
实现完全兼容的SDK接口

#### 7.1 兼容桥接实现
```python
# autocoder_slim/compat/bridge.py
from autocoder_slim.auto_coder_runner import run_auto_command as _run_auto_command
from autocoder_slim.auto_coder_runner import configure as _configure

def run_auto_command(args):
    """完全兼容的SDK接口"""
    return _run_auto_command(args)

def configure(config):
    """完全兼容的配置接口"""  
    return _configure(config)

__all__ = ['run_auto_command', 'configure']
```

#### 7.2 包级别导出
```python
# autocoder_slim/__init__.py
from .compat.bridge import run_auto_command, configure

__version__ = "1.0.0"
__all__ = ['run_auto_command', 'configure']
```

#### 验证标准
- [ ] 可以通过`from autocoder_slim import run_auto_command`导入
- [ ] SDK调用接口与原版完全一致
- [ ] 参数传递和返回值格式一致

---

### T8: 集成测试和验证
**依赖**: T7  
**时间估算**: 2小时  
**状态**: ⏸️ 待开始

#### 任务内容
全面测试迁移结果

#### 8.1 基础导入测试
```python
# test_imports.py
def test_all_imports():
    # 测试所有关键模块导入
    from autocoder_slim import run_auto_command, configure
    from autocoder_slim.common.v2.agent.agentic_edit import AgenticEdit
    from autocoder_slim.common.v2.agent.agentic_edit_types import *
    from autocoder_slim.common.v2.agent.agentic_edit_tools import *
    from autocoder_slim.utils.llms import get_single_llm
    # 验证所有import成功
```

#### 8.2 功能完整性测试
```python
# test_functionality.py
def test_agent_basic_functionality():
    # 创建Agent实例并测试基础功能
    pass

def test_all_tools_available():
    # 验证14个工具都可用
    pass

def test_sdk_compatibility():
    # 测试SDK接口兼容性
    pass
```

#### 8.3 与原版本对比测试
```python
# test_compatibility.py
def test_behavior_consistency():
    # 比较新旧版本的行为一致性
    pass
```

#### 验证标准
- [ ] 所有import测试通过
- [ ] Agent功能测试通过
- [ ] 14个工具测试通过
- [ ] SDK兼容性测试通过
- [ ] 与原版行为一致性验证通过

## 总体进度追踪

### 总体状态
- **开始时间**: 待定
- **预计完成时间**: 待定
- **当前进度**: 0% (0/8任务完成)

### 任务状态图例
- ⏸️ 待开始
- 🔄 进行中
- ✅ 已完成
- ❌ 失败
- ⏳ 阻塞等待

### 完成检查清单
- [ ] T1: 项目结构创建
- [ ] T2: 基础模块迁移  
- [ ] T3: Agent类型定义迁移
- [ ] T4: 工具解析器迁移
- [ ] T5: Agent核心迁移
- [ ] T6: 运行器迁移
- [ ] T7: SDK兼容层实现
- [ ] T8: 集成测试和验证

### 风险监控
- **高风险**: T6 (运行器迁移，代码量大，依赖复杂)
- **中风险**: T4, T5 (Agent系统迁移)
- **低风险**: T1, T2, T3, T7, T8