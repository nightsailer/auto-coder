# common.ac_style_command_parser.ac.mod.md

## 模块信息
- **模块名称**: common.ac_style_command_parser
- **模块类型**: 包模块 (Package Module)
- **主要功能**: 用于解析命令行风格查询字符串的模块，主要用于AutoCoder项目中处理复杂的命令和参数组合

## 核心功能

### 命令解析系统
- **CommandParser**: 核心命令解析器类
- **多格式支持**: 支持多种命令格式解析
- **智能识别**: 智能区分路径和命令
- **参数处理**: 支持位置参数和键值对参数

### 解析特性
- **引号支持**: 支持带引号的参数值（包含空格）
- **多命令组合**: 支持在单个查询中组合多个命令
- **路径识别**: 智能区分文件路径和命令
- **参数分类**: 自动分类位置参数和键值对参数

## 关键组件

### 1. CommandParser 核心解析器
```python
class CommandParser:
    @staticmethod
    def parse(query: str) -> Dict[str, Any]:
        """解析命令字符串"""
        
    @staticmethod
    def parse_command(query: str, command: str) -> Optional[Dict[str, Any]]:
        """解析特定命令"""
        
    @staticmethod
    def _parse_params(params_str: str) -> Tuple[List[str], Dict[str, str]]:
        """内部参数解析方法"""
```

### 2. 便捷函数
```python
# 主要便捷函数
def parse_query(query: str) -> Dict[str, Any]:
    """解析命令的便捷函数（推荐使用）"""

def has_command(query: str, command: str) -> bool:
    """检查是否包含特定命令"""

def get_command_args(query: str, command: str) -> List[str]:
    """获取命令的位置参数"""

def get_command_kwargs(query: str, command: str) -> Dict[str, str]:
    """获取命令的键值对参数"""
```

## 支持的命令格式

### 1. 基本命令格式
```
/command arg1 arg2
```

### 2. 键值对参数
```
/command key1=value1 key2=value2
```

### 3. 混合参数
```
/command arg1 key1=value1
```

### 4. 多命令组合
```
/command1 arg1 /command2 arg2
/command1 /command2 arg2
/command1 /command2 key=value
```

### 5. 带引号的参数（支持空格）
```
/command key="value with spaces"
/command key='value with spaces'
/command "argument with spaces"
```

### 6. 路径处理
```
/command /path/to/file.txt  # /path/to/file.txt不会被识别为命令
```

## 使用指南

### 1. 基本使用
```python
from autocoder.common.ac_style_command_parser import parse_query

# 解析命令
result = parse_query("/learn hello world /commit 123456")
print(result)
# 输出:
# {
#     'learn': {'args': ['hello', 'world'], 'kwargs': {}},
#     'commit': {'args': ['123456'], 'kwargs': {}}
# }
```

### 2. 高级使用
```python
from autocoder.common.ac_style_command_parser import (
    parse_query, has_command, get_command_args
)

query = '/learn msg="hello world" /commit commit_id=123456'

# 解析完整命令
commands = parse_query(query)

# 检查命令存在
if has_command(query, "learn"):
    print("Found learn command")

# 获取特定命令的参数
commit_args = get_command_args(query, "commit")
print(f"Commit args: {commit_args}")
```

### 3. 在AutoCoder项目中的典型用法
```python
# 在chat函数中的使用模式
def chat(query: str):
    # 解析命令
    commands_infos = parse_query(query)
    
    # 提取查询内容
    if "query" in commands_infos:
        query = " ".join(commands_infos["query"]["args"])
    else:
        # 如果没有显式的query命令，使用其他命令的参数
        temp_query = ""
        for (command, command_info) in commands_infos.items():
            if command_info["args"]:
                temp_query = " ".join(command_info["args"])
        query = temp_query
    
    # 检查特殊标志
    is_new = "new" in commands_infos
    
    # 特殊命令处理
    if "learn" in commands_infos:
        commands_infos["no_context"] = {}
    
    if "review" in commands_infos:
        commands_infos["no_context"] = {}
    
    # 继续处理...
```

### 4. 聊天命令解析示例
```python
# 在auto_coder_runner.py中的chat函数使用
def process_chat_command(query: str):
    """处理聊天命令"""
    # 解析查询命令
    commands_infos = parse_query(query)
    
    # 检查是否包含特定命令
    if "query" in commands_infos:
        query = " ".join(commands_infos["query"]["args"])
    
    # 检查是否是新会话
    is_new = "new" in commands_infos
    
    # 特殊命令处理
    if "learn" in commands_infos:
        commands_infos["no_context"] = {}
    
    if "review" in commands_infos:
        commands_infos["no_context"] = {}
    
    return commands_infos, query, is_new
```

### 5. 活动上下文管理示例
```python
# 在auto_coder_runner.py中的active_context函数使用
def process_active_context_command(query: str):
    """处理活动上下文命令"""
    # 解析命令参数
    commands_infos = parse_query(query)
    command = "list"  # 默认命令
    
    if len(commands_infos) > 0:
        if "list" in commands_infos:
            command = "list"
        if "run" in commands_infos:
            command = "run"
            # 获取运行参数
            if commands_infos["run"]["args"]:
                file_name = commands_infos["run"]["args"][-1]
                return command, file_name
    
    return command, None
```

### 6. 复杂命令解析示例
```python
def parse_complex_commands():
    """解析复杂命令组合的示例"""
    
    # 多命令组合
    query1 = '/learn "machine learning basics" /commit msg="Add ML module" /review priority=high'
    result1 = parse_query(query1)
    print("多命令解析结果:", result1)
    
    # 带路径的命令
    query2 = '/read /path/to/config.json /write output=/tmp/result.txt'
    result2 = parse_query(query2)
    print("路径命令解析结果:", result2)
    
    # 键值对参数
    query3 = '/deploy env=production version=1.2.3 rollback=false'
    result3 = parse_query(query3)
    print("键值对解析结果:", result3)
    
    return result1, result2, result3
```

## 在AutoCoder中的使用场景

### 1. 聊天命令解析
- 解析用户输入的聊天命令
- 提取查询内容和特殊标志
- 处理learn、review等特殊命令

### 2. 活动上下文管理
- 解析list、run等上下文命令
- 提取文件名和操作参数
- 支持复杂的上下文操作

### 3. 命令参数提取
- 从复杂查询中提取命令参数
- 支持位置参数和键值对参数
- 智能处理引号和空格

## 技术特性

### 1. 智能解析
- **路径识别**: 自动区分文件路径和命令
- **引号处理**: 正确处理单引号和双引号
- **空格处理**: 保留引号内的空格
- **转义支持**: 支持转义字符处理

### 2. 灵活格式
- **多命令**: 支持单个查询中的多个命令
- **混合参数**: 位置参数和键值对参数混合使用
- **可选参数**: 支持可选的命令参数
- **默认值**: 提供合理的默认解析行为

### 3. 错误处理
- **格式验证**: 验证命令格式的正确性
- **异常处理**: 优雅处理解析错误
- **容错机制**: 对格式错误的容错处理
- **调试信息**: 提供详细的解析调试信息

## 集成点

### 与其他模块的关系
- **auto_coder_runner模块**: 主要使用场景，处理用户命令
- **chat模块**: 解析聊天相关的命令
- **agent模块**: 为智能代理提供命令解析
- **memory模块**: 处理上下文相关的命令

### 外部依赖
- **re**: Python标准库，用于正则表达式
- **typing**: Python标准库，用于类型注解
- **shlex**: Python标准库，用于shell风格的词法分析

## 扩展指南

### 1. 添加新命令格式
```python
from autocoder.common.ac_style_command_parser import CommandParser

class ExtendedCommandParser(CommandParser):
    @staticmethod
    def parse_advanced_format(query: str) -> Dict[str, Any]:
        """解析高级命令格式"""
        # 实现新的解析逻辑
        pass
    
    @staticmethod
    def parse_nested_commands(query: str) -> Dict[str, Any]:
        """解析嵌套命令"""
        # 实现嵌套命令解析
        pass
```

### 2. 自定义参数处理
```python
def custom_param_parser(params_str: str) -> Tuple[List[str], Dict[str, str]]:
    """自定义参数解析器"""
    args = []
    kwargs = {}
    
    # 实现自定义解析逻辑
    # 例如：支持数组参数、对象参数等
    
    return args, kwargs

# 使用自定义解析器
CommandParser._parse_params = custom_param_parser
```

### 3. 命令验证器
```python
class CommandValidator:
    def __init__(self):
        self.valid_commands = {
            'learn', 'review', 'commit', 'query', 
            'new', 'list', 'run', 'deploy'
        }
    
    def validate_command(self, command: str) -> bool:
        """验证命令是否有效"""
        return command in self.valid_commands
    
    def validate_query(self, query: str) -> bool:
        """验证整个查询是否有效"""
        commands = parse_query(query)
        return all(self.validate_command(cmd) for cmd in commands.keys())

# 使用验证器
validator = CommandValidator()
if validator.validate_query("/learn python /invalid_command"):
    print("查询有效")
else:
    print("查询包含无效命令")
```

## 最佳实践

### 1. 命令设计
- 使用简短、直观的命令名
- 保持命令格式的一致性
- 提供清晰的参数结构
- 避免命令名与常见路径冲突

### 2. 参数处理
- 合理使用位置参数和键值对参数
- 为复杂参数使用引号
- 提供参数的默认值
- 验证参数的有效性

### 3. 错误处理
- 提供清晰的错误信息
- 实现参数验证机制
- 记录解析错误日志
- 提供解析失败的回退方案

### 4. 性能优化
- 缓存常用的解析结果
- 优化正则表达式性能
- 减少不必要的字符串操作
- 使用高效的数据结构

## 迁移说明

此模块从`src/autocoder/command_parser.py`迁移而来，位于`src/autocoder/common/ac_style_command_parser/`目录下。

如果你的代码中使用了旧的导入方式，请更新为：

```python
# 旧的导入方式
from autocoder.command_parser import CommandParser, parse_query

# 新的导入方式
from autocoder.common.ac_style_command_parser import CommandParser, parse_query
```

---

common.ac_style_command_parser模块提供了强大而灵活的命令解析功能，通过智能的格式识别和参数处理，为AutoCoder项目的命令行交互提供了重要的基础设施支持。 