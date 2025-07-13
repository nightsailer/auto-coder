# version

Auto-Coder 系统的版本管理模块，提供统一的版本号定义和管理，确保整个系统的版本一致性，支持版本号的集中维护和自动化版本更新。

## 模块位置

**源码路径**: `src/autocoder/version.py`  
**文档路径**: `specs/version.ac.mod.md`  
**模块类型**: 单文件模块

## 文件结构

```python
# version.py 内容结构
└── __version__                 # 版本号常量定义
```

## 快速开始

### 基本使用方式

```python
# 1. 导入版本号
from autocoder.version import __version__

# 2. 显示当前版本
print(f"Auto-Coder version: {__version__}")

# 3. 在应用启动时显示版本信息
def show_banner():
    print(f"""
    Auto-Coder v{__version__}
    Code with AI
    """)

# 4. 版本比较和验证
def check_version_compatibility(required_version: str):
    from packaging import version
    current = version.parse(__version__)
    required = version.parse(required_version)
    return current >= required

# 5. 在API响应中包含版本信息
def get_system_info():
    return {
        "name": "Auto-Coder",
        "version": __version__,
        "status": "running"
    }
```

### 在系统启动banner中的使用

```python
# 在 auto_coder_rag.py 中的使用示例
from autocoder.version import __version__

def main():
    print(f"""
    \033[1;32m
      _     _     __  __       _   _    _  _____ _____     _______   ____      _    ____ 
     | |   | |   |  \/  |     | \ | |  / \|_   _|_ _\ \   / / ____| |  _ \    / \  / ___|
     | |   | |   | |\/| |_____|  \| | / _ \ | |  | | \ \ / /|  _|   | |_) |  / _ \| |  _ 
     | |___| |___| |  | |_____| |\  |/ ___ \| |  | |  \ V / | |___  |  _ <  / ___ \ |_| |
     |_____|_____|_|  |_|     |_| \_/_/   \_\_| |___|  \_/  |_____| |_| \_\/_/   \_\____|
                                                                            v{__version__}
    \033[0m""")
```

### 主要功能

该模块提供系统唯一的版本号定义，确保所有组件使用一致的版本标识，支持版本信息的统一管理和显示。

## 核心组件详解

### 1. __version__ 常量

**定义**: `__version__ = "1.0.0"`

**功能**: 定义Auto-Coder系统的当前版本号

**格式**: 采用语义化版本控制（Semantic Versioning）规范
- **主版本号**: 表示不兼容的API变更
- **次版本号**: 表示向后兼容的新功能  
- **修订版本号**: 表示向后兼容的错误修复

**用途**:
- 系统启动banner显示
- API响应中的版本标识
- 包管理和分发
- 兼容性检查
- 日志记录和错误报告

### 2. 版本管理策略

**语义化版本控制**:
```
版本格式: MAJOR.MINOR.PATCH
例如: 1.0.0
```

- **1.x.x**: 主要版本更新，可能包含破坏性变更
- **x.1.x**: 次要版本更新，新功能向后兼容
- **x.x.1**: 补丁版本更新，错误修复向后兼容

**版本生命周期**:
1. **开发版本**: 0.x.x - 开发阶段，API可能变化
2. **稳定版本**: 1.x.x - 正式发布，API稳定
3. **维护版本**: x.x.x - 错误修复和安全更新

### 3. 在系统中的使用

该版本号被以下模块引用：

**启动和显示模块**:
- `auto_coder_rag.py`: RAG服务器启动banner
- `chat_auto_coder.py`: 聊天界面启动信息
- `auto_coder_runner.py`: 主运行器版本显示

**使用示例**:
```python
# 在启动banner中显示版本
print(f"Auto-Coder v{__version__}")

# 在日志中记录版本
logger.info(f"Starting Auto-Coder {__version__}")

# 在API响应中包含版本
{"version": __version__, "status": "ready"}
```

### 4. 版本更新流程

**手动更新**:
1. 修改 `src/autocoder/version.py` 中的版本号
2. 更新相关文档和说明
3. 提交版本变更

**自动化版本管理**:
```bash
# 使用工具自动更新版本
bump2version patch  # 增加补丁版本号
bump2version minor  # 增加次版本号  
bump2version major  # 增加主版本号
```

### 5. 版本兼容性检查

```python
from packaging import version
from autocoder.version import __version__

def check_compatibility(min_version: str) -> bool:
    """检查当前版本是否满足最小版本要求"""
    current = version.parse(__version__)
    minimum = version.parse(min_version)
    return current >= minimum

def get_version_info() -> dict:
    """获取详细的版本信息"""
    parts = __version__.split('.')
    return {
        "full": __version__,
        "major": int(parts[0]),
        "minor": int(parts[1]) if len(parts) > 1 else 0,
        "patch": int(parts[2]) if len(parts) > 2 else 0
    }
```

## Mermaid 依赖图

```mermaid
graph TB
    %% 核心版本模块
    Version[version.py<br/>__version__ = "1.0.0"]
    
    %% 使用版本的模块
    RAGServer[auto_coder_rag.py<br/>RAG服务器启动]
    ChatCoder[chat_auto_coder.py<br/>聊天界面启动]
    Runner[auto_coder_runner.py<br/>主运行器]
    
    %% 版本显示场景
    Banner[启动Banner<br/>版本信息显示]
    API[API响应<br/>版本标识]
    Logs[日志记录<br/>版本追踪]
    
    %% 版本管理
    SemVer[语义化版本<br/>MAJOR.MINOR.PATCH]
    Compatibility[兼容性检查<br/>版本比较]
    Release[发布管理<br/>版本控制]
    
    %% 依赖关系
    Version --> RAGServer
    Version --> ChatCoder
    Version --> Runner
    
    RAGServer --> Banner
    ChatCoder --> Banner
    Runner --> Banner
    
    Version --> API
    Version --> Logs
    
    Version --> SemVer
    Version --> Compatibility
    Version --> Release
    
    %% 样式定义
    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:3px
    classDef moduleClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef usageClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:1px
    classDef mgmtClass fill:#fff3e0,stroke:#ef6c00,stroke-width:1px
    
    class Version coreClass
    class RAGServer,ChatCoder,Runner moduleClass
    class Banner,API,Logs usageClass
    class SemVer,Compatibility,Release mgmtClass
```

## 依赖关系说明

### 对其他模块的依赖
该模块是纯常量定义模块，不依赖任何其他Auto-Coder模块或外部库。

### 被依赖关系
作为版本标识的核心模块，被以下模块广泛使用：

- `src/autocoder/auto_coder_rag.py` - RAG服务器启动banner中显示版本
- `src/autocoder/chat_auto_coder.py` - 聊天界面启动时显示版本
- `src/autocoder/auto_coder_runner.py` - 主运行器中的版本标识
- **setup.py**: 包管理和分发时的版本定义
- **__init__.py**: 包级别的版本导出

## 可以验证模块可运行的测试命令

```bash
# Python模块测试
python -c "from autocoder.version import __version__; print(f'当前版本: {__version__}')"

# 验证版本格式
python -c "from autocoder.version import __version__; import re; pattern = r'^\d+\.\d+\.\d+$'; print(f'版本格式正确: {bool(re.match(pattern, __version__))}')"

# 测试版本比较
python -c "from autocoder.version import __version__; from packaging import version; print(f'版本对象: {version.parse(__version__)}')"

# 验证版本在其他模块中的导入
python -c "from autocoder.auto_coder_rag import __version__ as rag_version; print(f'RAG模块版本: {rag_version}')" 2>/dev/null || echo "RAG模块未导入版本"

# 检查版本一致性
python -c "
from autocoder.version import __version__ as main_version
try:
    from autocoder.chat_auto_coder import __version__ as chat_version
    print(f'版本一致性: {main_version == chat_version}')
except:
    print('聊天模块未导入版本，这是正常的')
"

# 测试语义化版本解析
python -c "
from autocoder.version import __version__
parts = __version__.split('.')
print(f'主版本: {parts[0]}, 次版本: {parts[1]}, 修订版本: {parts[2]}')
"
``` 