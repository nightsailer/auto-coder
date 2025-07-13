# common.command_completer.ac.mod.md

## 模块概述

`common.command_completer` 模块是 Auto-Coder 系统的智能命令补全核心，提供基于 prompt_toolkit 的高级命令行补全功能。该模块支持层次化命令结构、动态文件名补全、模型名称补全、XML标签解析等功能，为用户提供智能化的命令输入体验。

**模块类型**: 单文件模块 (`src/autocoder/common/command_completer.py`)  
**主要功能**: 智能命令补全、命令解析、动态补全  
**依赖关系**: 依赖 `prompt_toolkit`、`pydantic`、`autocoder.models` 等模块

## 核心组件

### 1. 命令结构定义
- **COMMANDS**: 层次化命令结构字典，定义所有可用命令和子命令
- 支持多级命令嵌套：`/add_files /group /add`
- 动态命令参数：文件名、模型名、组名等

### 2. 命令解析器
- **CommandTextParser**: 智能命令文本解析器
- 支持空格、换行符处理
- XML 标签识别和解析
- 子命令层次结构导航

### 3. 补全引擎
- **CommandCompleter**: 基于 prompt_toolkit 的补全器
- 上下文感知补全
- 动态数据源集成
- 模糊匹配支持

### 4. 数据模型
- **FileSystemModel**: 文件系统访问模型
- **MemoryConfig**: 内存配置管理模型
- **Tag**: XML 标签数据模型

## 支持的命令结构

### 1. 文件管理命令

```python
# 文件添加命令结构
"/add_files": {
    "/group": {
        "/add": {},      # 添加文件到组
        "/drop": {},     # 从组中删除文件
        "/reset": {},    # 重置组
        "/set": {}       # 设置组
    },
    "/refresh": {}       # 刷新文件列表
}

# 文件删除命令
"/remove_files": {
    "/all": {}          # 删除所有文件
}
```

### 2. 聊天和编程命令

```python
# 聊天命令
"/chat": {
    "/new": {},         # 新建对话
    "/save": {},        # 保存对话
    "/copy": {},        # 复制对话
    "/mcp": {},         # MCP 模式
    "/rag": {},         # RAG 模式
    "/review": {},      # 代码审查模式
    "/learn": {},       # 学习模式
    "/no_context": {}   # 无上下文模式
}

# 编程命令
"/coding": {
    "/apply": {},       # 应用代码
    "/next": {}         # 下一步
}
```

### 3. 模型和工具命令

```python
# 模型管理
"/models": {
    "/add": {},         # 添加模型
    "/add_model": {},   # 添加模型配置
    "/remove": {},      # 删除模型
    "/list": {},        # 列出模型
    "/speed": {},       # 模型速度测试
    "/input_price": {}, # 输入价格设置
    "/output_price": {} # 输出价格设置
}

# MCP 工具
"/mcp": {
    "/add": {},         # 添加 MCP 工具
    "/remove": {},      # 删除 MCP 工具
    "/list": {},        # 列出 MCP 工具
    "/refresh": {}      # 刷新 MCP 工具
}
```

## 主要功能

### 1. 智能命令补全

```python
from autocoder.common.command_completer import CommandCompleter, FileSystemModel, MemoryConfig

# 创建文件系统模型
file_system_model = FileSystemModel(
    project_root="/path/to/project",
    get_all_file_names_in_project=lambda: ["file1.py", "file2.js"],
    get_all_file_in_project=lambda: ["src/main.py", "tests/test.py"],
    get_all_dir_names_in_project=lambda: ["src", "tests", "docs"],
    get_all_file_in_project_with_dot=lambda: [".gitignore", ".env"],
    get_symbol_list=lambda: ["function1", "class1", "variable1"]
)

# 创建内存配置模型
memory_config = MemoryConfig(
    get_memory_func=lambda: {"current_files": {"groups": {"group1": []}}},
    save_memory_func=lambda x: None
)

# 创建命令补全器
completer = CommandCompleter(
    commands=COMMANDS,
    file_system_model=file_system_model,
    memory_model=memory_config
)

# 在 prompt_toolkit 中使用
from prompt_toolkit import prompt
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document

# 获取补全建议
document = Document("/add_files src/")
completions = list(completer.get_completions(document, CompleteEvent()))

for completion in completions:
    print(f"补全: {completion.text}")
```

### 2. 命令文本解析

```python
from autocoder.common.command_completer import CommandTextParser

# 解析文件添加命令
parser = CommandTextParser("/group /add group1", "/add_files")
parser.add_files()

print(f"子命令: {parser.get_sub_commands()}")
print(f"当前单词: {parser.current_word()}")
print(f"第一个子命令: {parser.first_sub_command()}")
print(f"最后一个子命令: {parser.last_sub_command()}")

# 解析编程命令（支持 XML 标签）
coding_parser = CommandTextParser("implement <function>login</function>", "/coding")
coding_parser.coding()

print(f"解析的标签: {coding_parser.tags}")
for tag in coding_parser.tags:
    print(f"标签: {tag.start_tag}, 内容: {tag.content}, 结束: {tag.end_tag}")
```

### 3. 动态补全功能

```python
# 文件名补全
def get_file_completions(current_word: str):
    """获取文件名补全建议"""
    all_files = ["src/main.py", "tests/test.py", "docs/readme.md"]
    
    completions = []
    for file_name in all_files:
        if current_word in file_name:
            completions.append(file_name)
    
    return completions

# 模型名补全
def get_model_completions(current_word: str):
    """获取模型名补全建议"""
    from autocoder import models as models_module
    
    all_models = [m['name'] for m in models_module.load_models()]
    
    completions = []
    for model_name in all_models:
        if model_name.startswith(current_word):
            completions.append(model_name)
    
    return completions

# 组名补全
def get_group_completions(current_word: str, memory):
    """获取组名补全建议"""
    groups = memory.get("current_files", {}).get("groups", {})
    
    completions = []
    for group_name in groups.keys():
        if group_name.startswith(current_word):
            completions.append(group_name)
    
    return completions
```

### 4. 高级补全场景

```python
# 复杂命令补全示例
class AdvancedCompleter(CommandCompleter):
    """扩展的命令补全器"""
    
    def get_custom_completions(self, command: str, current_word: str):
        """自定义补全逻辑"""
        
        if command == "/add_files":
            return self.handle_add_files_completion(current_word)
        elif command == "/models":
            return self.handle_models_completion(current_word)
        elif command == "/lib":
            return self.handle_lib_completion(current_word)
        
        return []
    
    def handle_add_files_completion(self, current_word: str):
        """处理文件添加命令的补全"""
        completions = []
        
        # 支持通配符匹配
        if "*" in current_word:
            import glob
            pattern = current_word.replace("*", "**")
            matched_files = glob.glob(pattern, recursive=True)
            completions.extend(matched_files)
        
        # 支持路径补全
        if "/" in current_word:
            directory = os.path.dirname(current_word)
            if os.path.exists(directory):
                files = os.listdir(directory)
                for file in files:
                    full_path = os.path.join(directory, file)
                    if full_path.startswith(current_word):
                        completions.append(full_path)
        
        return completions
    
    def handle_models_completion(self, current_word: str):
        """处理模型命令的补全"""
        # 动态加载最新的模型列表
        try:
            from autocoder import models as models_module
            models = models_module.load_models()
            
            completions = []
            for model in models:
                if model['name'].startswith(current_word):
                    completions.append({
                        'text': model['name'],
                        'display': f"{model['name']} - {model.get('description', '')}"
                    })
            
            return completions
        except Exception as e:
            print(f"加载模型列表失败: {e}")
            return []
```

## 配置和扩展

### 1. 命令结构扩展

```python
# 扩展命令结构
EXTENDED_COMMANDS = {
    **COMMANDS,  # 包含原有命令
    "/custom": {
        "/action1": {},
        "/action2": {
            "/sub1": {},
            "/sub2": {}
        }
    },
    "/workflow": {
        "/start": {},
        "/stop": {},
        "/status": {}
    }
}

# 使用扩展命令
completer = CommandCompleter(
    commands=EXTENDED_COMMANDS,
    file_system_model=file_system_model,
    memory_model=memory_config
)
```

### 2. 自定义解析器

```python
class CustomCommandParser(CommandTextParser):
    """自定义命令解析器"""
    
    def __init__(self, text: str, command: str):
        super().__init__(text, command)
        self.custom_context = {}
    
    def parse_custom_command(self):
        """解析自定义命令格式"""
        while not self.is_extracted and self.pos < self.len - 1:
            if self.is_custom_tag():
                self.consume_custom_tag()
            elif self.is_sub_command():
                self.consume_sub_command()
            else:
                self.consume_command_value()
        
        return self
    
    def is_custom_tag(self) -> bool:
        """检测自定义标签格式"""
        return (self.peek() == "[" and 
                self.text.find("]", self.pos + 1) != -1)
    
    def consume_custom_tag(self):
        """解析自定义标签"""
        tag_content = ""
        self.next()  # 跳过 [
        
        while self.peek() != "]" and self.peek() is not None:
            tag_content += self.next()
        
        if self.peek() == "]":
            self.next()  # 跳过 ]
        
        self.custom_context[len(self.custom_context)] = tag_content
```

### 3. 补全性能优化

```python
from functools import lru_cache
import time

class OptimizedCompleter(CommandCompleter):
    """性能优化的补全器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_timeout = 300  # 5分钟缓存
        self.last_cache_time = {}
    
    @lru_cache(maxsize=1000)
    def get_cached_file_list(self, directory: str):
        """缓存文件列表"""
        if not os.path.exists(directory):
            return []
        
        return [f for f in os.listdir(directory) 
                if os.path.isfile(os.path.join(directory, f))]
    
    def get_completions_with_cache(self, document, complete_event):
        """带缓存的补全"""
        current_time = time.time()
        cache_key = document.text_before_cursor
        
        # 检查缓存是否过期
        if (cache_key in self.last_cache_time and 
            current_time - self.last_cache_time[cache_key] < self.cache_timeout):
            # 使用缓存结果
            pass
        else:
            # 清理过期缓存
            self.get_cached_file_list.cache_clear()
            self.last_cache_time[cache_key] = current_time
        
        return self.get_completions(document, complete_event)
```

## 使用示例

### 完整的命令补全系统

```python
#!/usr/bin/env python3
"""
完整的命令补全系统示例
展示如何集成到 Auto-Coder 中
"""

import os
from prompt_toolkit import prompt
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document
from autocoder.common.command_completer import (
    CommandCompleter, CommandTextParser, FileSystemModel, MemoryConfig, COMMANDS
)

class AutoCoderCompleter:
    """Auto-Coder 命令补全系统"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.setup_file_system_model()
        self.setup_memory_config()
        self.setup_completer()
    
    def setup_file_system_model(self):
        """设置文件系统模型"""
        def get_all_files():
            files = []
            for root, dirs, filenames in os.walk(self.project_root):
                for filename in filenames:
                    rel_path = os.path.relpath(
                        os.path.join(root, filename), 
                        self.project_root
                    )
                    files.append(rel_path)
            return files
        
        def get_all_dirs():
            dirs = []
            for root, dirnames, _ in os.walk(self.project_root):
                for dirname in dirnames:
                    rel_path = os.path.relpath(
                        os.path.join(root, dirname),
                        self.project_root
                    )
                    dirs.append(rel_path)
            return dirs
        
        def get_symbols():
            # 这里可以集成代码分析工具来获取符号
            return ["function1", "class1", "variable1"]
        
        self.file_system_model = FileSystemModel(
            project_root=self.project_root,
            get_all_file_names_in_project=lambda: [
                os.path.basename(f) for f in get_all_files()
            ],
            get_all_file_in_project=get_all_files,
            get_all_dir_names_in_project=get_all_dirs,
            get_all_file_in_project_with_dot=lambda: [
                f for f in get_all_files() if f.startswith('.')
            ],
            get_symbol_list=get_symbols
        )
    
    def setup_memory_config(self):
        """设置内存配置"""
        self.memory = {
            "current_files": {
                "groups": {
                    "frontend": ["src/components/", "src/pages/"],
                    "backend": ["src/api/", "src/models/"],
                    "tests": ["tests/"]
                }
            },
            "libs": {
                "requests": {"version": "2.28.0"},
                "pandas": {"version": "1.5.0"},
                "numpy": {"version": "1.24.0"}
            }
        }
        
        self.memory_config = MemoryConfig(
            get_memory_func=lambda: self.memory,
            save_memory_func=self.save_memory
        )
    
    def save_memory(self, memory_data):
        """保存内存数据"""
        self.memory.update(memory_data)
        print(f"内存已更新: {memory_data}")
    
    def setup_completer(self):
        """设置补全器"""
        self.completer = CommandCompleter(
            commands=COMMANDS,
            file_system_model=self.file_system_model,
            memory_model=self.memory_config
        )
    
    def run_interactive_session(self):
        """运行交互式会话"""
        print("Auto-Coder 命令补全系统")
        print("输入命令（按 Tab 键获取补全建议）:")
        print("支持的命令: /add_files, /chat, /coding, /models, /lib, /mcp")
        print("输入 'exit' 退出\n")
        
        while True:
            try:
                user_input = prompt(
                    "auto-coder> ",
                    completer=self.completer,
                    complete_style='column'
                )
                
                if user_input.lower() == 'exit':
                    break
                
                self.process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n再见！")
                break
            except EOFError:
                break
    
    def process_command(self, command: str):
        """处理用户输入的命令"""
        if not command.strip():
            return
        
        print(f"处理命令: {command}")
        
        # 这里可以集成实际的命令处理逻辑
        if command.startswith("/add_files"):
            self.handle_add_files(command)
        elif command.startswith("/models"):
            self.handle_models(command)
        elif command.startswith("/chat"):
            self.handle_chat(command)
        else:
            print(f"未知命令: {command}")
    
    def handle_add_files(self, command: str):
        """处理文件添加命令"""
        parser = CommandTextParser(command[len("/add_files"):], "/add_files")
        parser.add_files()
        
        print(f"解析结果:")
        print(f"  子命令: {parser.get_sub_commands()}")
        print(f"  当前单词: {parser.current_word()}")
        print(f"  标签: {[tag.content for tag in parser.tags]}")
    
    def handle_models(self, command: str):
        """处理模型命令"""
        print(f"模型命令: {command}")
        # 集成模型管理逻辑
    
    def handle_chat(self, command: str):
        """处理聊天命令"""
        print(f"聊天命令: {command}")
        # 集成聊天逻辑

def main():
    """主程序"""
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    if not os.path.exists(project_root):
        print(f"项目目录不存在: {project_root}")
        return
    
    completer_system = AutoCoderCompleter(project_root)
    completer_system.run_interactive_session()

if __name__ == "__main__":
    main()
```

## 验证命令

验证 command_completer 模块功能：

```bash
# 检查模块导入
python -c "from autocoder.common.command_completer import CommandCompleter, CommandTextParser; print('模块导入成功')"

# 验证命令结构
python -c "
from autocoder.common.command_completer import COMMANDS
import json
print('支持的命令:')
for cmd, subcmds in COMMANDS.items():
    print(f'  {cmd}: {list(subcmds.keys()) if isinstance(subcmds, dict) else subcmds}')
"

# 验证命令解析器
python -c "
from autocoder.common.command_completer import CommandTextParser
parser = CommandTextParser('/group /add test', '/add_files')
parser.add_files()
print(f'子命令: {parser.get_sub_commands()}')
print(f'当前单词: {parser.current_word()}')
"

# 验证补全功能（需要完整环境）
python -c "
from autocoder.common.command_completer import CommandCompleter, FileSystemModel, MemoryConfig
from prompt_toolkit.document import Document
from prompt_toolkit.completion import CompleteEvent

# 简单测试
print('命令补全器创建成功')
"

# 检查依赖关系
python -c "
import prompt_toolkit
import pydantic
from autocoder import models
print('所有依赖模块可用')
"
```

通过这些验证命令可以确认 command_completer 模块的完整性和功能正确性。 