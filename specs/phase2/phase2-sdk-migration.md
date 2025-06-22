# Phase 2: SDK模块迁移技术实现

## 实现目标
完整迁移SDK模块到`autocoder_slim.sdk`命名空间，保持所有SDK API接口和功能完全一致，确保用户代码零修改迁移。

## SDK模块结构分析

### 当前SDK目录结构
```
src/autocoder/sdk/
├── __init__.py (189行)           # 主要API导出
├── README.md                     # 文档
├── constants.py (103行)          # 常量定义
├── exceptions.py (73行)          # 异常类定义
├── example.py                    # 示例代码
├── core/                         # 核心功能模块
├── models/                       # 数据模型
├── session/                      # 会话管理
├── utils/                        # 工具函数
└── cli/                          # 命令行接口
```

### SDK模块规模
- **总代码量**: 4623行
- **模块数量**: 5个主要子模块 + 核心文件
- **API复杂度**: 中等（主要为封装和调用）

## 迁移策略

### 1. 完整结构迁移
```
原模块                               目标模块
src/autocoder/sdk/                   → autocoder_slim/sdk/
├── __init__.py                      → __init__.py
├── constants.py                     → constants.py  
├── exceptions.py                    → exceptions.py
├── core/                            → core/
├── models/                          → models/
├── session/                         → session/
├── utils/                           → utils/
└── cli/                             → cli/
```

### 2. 依赖关系更新
SDK模块内部对autocoder核心模块的依赖需要全部更新：

```python
# SDK内部import更新示例
# 原代码
from autocoder.auto_coder_runner import run_auto_command, configure
from autocoder.common import AutoCoderArgs

# 新代码
from autocoder_slim.auto_coder_runner import run_auto_command, configure
from autocoder_slim.common import AutoCoderArgs
```

### 3. API兼容性保证
确保所有SDK公共API保持完全一致：

```python
# autocoder_slim/sdk/__init__.py
# 保持与原版完全相同的API导出
from .core.auto_coder_core import AutoCoderCore
from .models.message import Message
# ... 所有其他导出保持一致
```

## 详细迁移计划

### 2.1 SDK核心文件迁移

#### 迁移__init__.py
```python
# autocoder_slim/sdk/__init__.py
# 这是SDK的主要入口文件，需要仔细处理所有import

# 原有的所有import都需要更新namespace
# 同时保持所有导出的API接口不变
```

#### 迁移constants.py
```python
# autocoder_slim/sdk/constants.py  
# 常量定义文件，相对简单
# 主要是替换任何对autocoder的引用
```

#### 迁移exceptions.py
```python
# autocoder_slim/sdk/exceptions.py
# 异常类定义，需要保持异常类名和继承关系完全一致
```

### 2.2 SDK子模块迁移

#### 2.2.1 core/模块迁移
```bash
# 查看core模块结构
src/autocoder/sdk/core/ → autocoder_slim/sdk/core/
# 需要分析core模块的具体内容和依赖
```

#### 2.2.2 models/模块迁移  
```bash
# 迁移数据模型
src/autocoder/sdk/models/ → autocoder_slim/sdk/models/
# 数据模型通常依赖较少，迁移相对简单
```

#### 2.2.3 session/模块迁移
```bash
# 迁移会话管理
src/autocoder/sdk/session/ → autocoder_slim/sdk/session/
# 可能有对核心模块的依赖需要更新
```

#### 2.2.4 utils/模块迁移
```bash  
# 迁移工具函数
src/autocoder/sdk/utils/ → autocoder_slim/sdk/utils/
# 工具函数可能有复杂的依赖关系
```

#### 2.2.5 cli/模块迁移
```bash
# 迁移命令行接口
src/autocoder/sdk/cli/ → autocoder_slim/sdk/cli/
# CLI可能对多个模块有依赖
```

## SDK依赖分析

### 对autocoder核心模块的依赖
SDK模块可能依赖的核心模块：

```python
# 常见的依赖模式
from autocoder.auto_coder_runner import run_auto_command, configure
from autocoder.common import AutoCoderArgs, SourceCode, SourceCodeList  
from autocoder.common.v2.agent.agentic_edit import AgenticEdit
from autocoder.utils.llms import get_single_llm
# ... 其他可能的依赖
```

### 内部依赖关系
```python
# SDK内部模块间的依赖
from autocoder.sdk.core import AutoCoderCore
from autocoder.sdk.models import Message, AutoCodeOptions
from autocoder.sdk.utils import some_utility_function
# 这些内部依赖保持不变，只需要确保路径正确
```

## 迁移实施步骤

### Step 1: 创建SDK目录结构
```bash
# 在autocoder_slim下创建SDK目录结构
autocoder_slim/
└── sdk/
    ├── __init__.py
    ├── constants.py
    ├── exceptions.py
    ├── core/
    │   └── __init__.py
    ├── models/
    │   └── __init__.py
    ├── session/
    │   └── __init__.py
    ├── utils/
    │   └── __init__.py
    └── cli/
        └── __init__.py
```

### Step 2: 批量文件复制和namespace替换
```python
# 自动化迁移脚本
def migrate_sdk_module(source_path, target_path):
    # 复制文件
    shutil.copy2(source_path, target_path)
    
    # 替换namespace
    with open(target_path, 'r') as f:
        content = f.read()
    
    # 替换autocoder引用为autocoder_slim
    content = re.sub(r'from autocoder\.', 'from autocoder_slim.', content)
    content = re.sub(r'import autocoder\.', 'import autocoder_slim.', content)
    
    with open(target_path, 'w') as f:
        f.write(content)
```

### Step 3: SDK内部依赖验证
```python
# 验证SDK内部所有模块可以正常导入
from autocoder_slim.sdk import AutoCoderCore
from autocoder_slim.sdk.models import Message
from autocoder_slim.sdk.session import SessionManager
# ... 验证所有主要组件
```

### Step 4: SDK API兼容性测试
```python
# 测试所有公共API接口
def test_sdk_api_compatibility():
    # 测试查询接口
    from autocoder_slim.sdk import query, query_sync
    
    # 测试代码修改接口  
    from autocoder_slim.sdk import modify_code, modify_code_stream
    
    # 测试配置接口
    from autocoder_slim.sdk import AutoCodeOptions
    
    # 验证所有接口签名和行为一致
```

## 特殊处理事项

### 1. 文档和示例更新
```python
# SDK的README.md和example.py需要更新
# 将所有示例代码中的import语句更新

# 原示例
from autocoder.sdk import query

# 新示例  
from autocoder_slim.sdk import query
```

### 2. 版本和元数据
```python
# 更新SDK的版本信息和包元数据
__version__ = "1.0.0-slim"
__package_name__ = "autocoder_slim"
```

### 3. 向后兼容处理
```python
# 在必要时提供向后兼容的别名
# 但主要目标是完全迁移，减少兼容性负担
```

## 验证标准

### 功能验证
- [ ] 所有SDK模块可以正常导入
- [ ] 所有公共API接口功能正常
- [ ] SDK与新的核心模块集成正常
- [ ] 异步和同步接口都正常工作

### 兼容性验证
- [ ] 原有的SDK使用代码无需修改即可迁移
- [ ] API签名和返回值格式完全一致
- [ ] 错误处理和异常类型保持一致
- [ ] 性能特征与原版相当

### 集成验证
- [ ] SDK与autocoder_slim核心模块的集成正常
- [ ] Agent系统通过SDK调用正常
- [ ] 所有工具通过SDK接口可用
- [ ] 配置和会话管理正常

## 风险和挑战

### 技术风险
- **依赖复杂性**: SDK可能有深层的依赖关系
- **API一致性**: 确保迁移后API行为完全一致
- **集成问题**: SDK与新核心模块的集成可能有问题

### 缓解策略
- 建立完整的API测试套件
- 逐模块验证和测试
- 保持原有的单元测试和集成测试
- 建立新旧版本的对比测试

## 成功指标

### 迁移完整性
- [ ] 所有SDK模块100%迁移
- [ ] 所有API接口保持一致
- [ ] 所有依赖关系正确更新

### 用户体验
- [ ] 用户代码零修改迁移
- [ ] 学习成本为零
- [ ] 性能无明显下降
- [ ] 错误信息清晰有用

---
*Phase 2将在Phase 1完成后开始实施，确保核心模块迁移稳定后再进行SDK迁移* 