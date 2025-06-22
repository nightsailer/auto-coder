# Auto-Coder SDK 重构技术规划（更新版 v2）

## 核心目标
通过namespace迁移创建`autocoder_slim`包，保留所有Agent需要的工具，移除RAG集成，保留MCP支持。包括核心模块和SDK模块的完整迁移。

## 更新的策略方针

### 1. 功能保留策略
- ✅ **保留所有Agent工具**：当前14个工具全部保留，即便SDK暂未使用
- ✅ **保留MCP支持**：MCP协议对Agent扩展重要
- ❌ **移除RAG集成**：RAG功能可以移除
- ✅ **完整SDK迁移**：包括autocoder.sdk → autocoder_slim.sdk
- ✅ **保持SDK原样**：SDK代码无需调整，已经很精简

### 2. 移植规则
```
原版本                           →  精简版本
autocoder.xxx                    →  autocoder_slim.xxx
autocoder.common.v2.agent        →  autocoder_slim.common.v2.agent  
autocoder.utils.llms             →  autocoder_slim.utils.llms
autocoder.commands.auto_command   →  autocoder_slim.commands.auto_command
autocoder.sdk.xxx                →  autocoder_slim.sdk.xxx
```
**关键原则**：
- 顶级namespace: `autocoder` → `autocoder_slim`
- 模块相对路径、函数名、签名保持完全一致
- 最大化保持原有结构

### 3. 目标架构
```
autocoder_slim/
├── common/
│   ├── v2/agent/               # Agent系统（完整保留）
│   │   ├── agentic_edit.py
│   │   ├── agentic_edit_types.py
│   │   └── agentic_edit_tools/ # 14个工具全部保留
│   ├── mcp_server.py           # MCP支持保留
│   ├── AutoCoderArgs.py        # 基础数据结构
│   └── [其他common模块]
├── utils/
│   ├── llms.py                 # LLM接口
│   └── [其他utils模块]
├── commands/
│   └── auto_command.py         # 命令处理
├── auto_coder_runner.py        # 核心运行器
├── sdk/                        # ⭐ 新增：SDK模块迁移
│   ├── __init__.py
│   ├── core/
│   ├── models/
│   ├── session/
│   └── [所有SDK模块]
└── compat/
    └── bridge.py               # SDK兼容层
```

## 分阶段实施计划（更新版）

### Phase 1: AutoCoder核心模块迁移
**目标**: 迁移Agent系统和核心运行器
**状态**: 📋 规划完成，待执行

#### 核心任务
1. 创建`autocoder_slim`包结构
2. 迁移Agent核心模块（保持完整功能）
3. 迁移14个工具解析器
4. 迁移auto_coder_runner
5. 实现基础的namespace替换

#### 预期结果
- ✅ 完整的Agent系统迁移
- ✅ 14个工具全部可用
- ✅ 核心运行器功能完整
- ✅ MCP支持保留

### Phase 2: SDK模块迁移
**目标**: 迁移完整的SDK模块到autocoder_slim.sdk
**状态**: 📝 待规划

#### 核心任务
1. 分析SDK模块结构和依赖
2. 迁移所有SDK子模块
3. 更新SDK内部的import语句
4. 确保SDK与新的核心模块的集成
5. 验证SDK API完全兼容

#### 具体模块迁移
```python
# SDK模块迁移清单
autocoder/sdk/__init__.py        → autocoder_slim/sdk/__init__.py
autocoder/sdk/core/              → autocoder_slim/sdk/core/
autocoder/sdk/models/            → autocoder_slim/sdk/models/
autocoder/sdk/session/           → autocoder_slim/sdk/session/
autocoder/sdk/utils/             → autocoder_slim/sdk/utils/
autocoder/sdk/cli/               → autocoder_slim/sdk/cli/
```

#### 特殊处理
- SDK内部对autocoder核心模块的依赖需要更新为autocoder_slim
- 保持SDK的所有公共API接口不变
- 确保用户代码零修改迁移

### Phase 3: 集成优化和验证
**目标**: 整体优化、测试和文档完善
**状态**: 📝 待规划

#### 核心任务
1. 完整的集成测试
2. 性能优化和调试
3. 文档更新和示例代码
4. 发布准备和版本管理

## 依赖分析更新

### Phase 1: Agent需要的14个工具（全部保留）
1. **read_file** - 文件读取
2. **write_to_file** - 文件写入  
3. **replace_in_file** - 文件内容替换
4. **execute_command** - 命令执行
5. **list_files** - 文件列表
6. **attempt_completion** - 任务完成
7. **ask_follow_up_question** - 追问用户
8. **str_replace_editor** - 字符串替换编辑器
9. **create_directory** - 创建目录
10. **search_and_replace** - 搜索替换
11. **view_range** - 查看文件范围
12. **scroll_to_line** - 滚动到行
13. **find_in_files** - 文件内搜索
14. **open_file** - 打开文件

### Phase 2: SDK模块（需要完整迁移）
基于当前SDK目录结构：
- **core/** - 核心功能模块
- **models/** - 数据模型
- **session/** - 会话管理
- **utils/** - 工具函数
- **cli/** - 命令行接口（如果存在）

### 保留的模块清单
#### 🔴 核心Agent模块（Phase 1）
- `autocoder.common.v2.agent.agentic_edit` (2432行)
- `autocoder.common.v2.agent.agentic_edit_types` (190行)  
- `autocoder.common.v2.agent.agentic_edit_tools/` (~2248行，14个工具)
- `autocoder.auto_coder_runner` (3486行)

#### 🔴 SDK模块（Phase 2）
- `autocoder.sdk.*` (4623行) - 完整SDK实现

#### 🟡 重要支持模块（Phase 1）
- `autocoder.common` - AutoCoderArgs, SourceCode等基础结构
- `autocoder.utils.llms` - LLM接口
- `autocoder.commands.auto_command` - 命令处理
- `autocoder.common.mcp_server` - MCP支持保留
- `autocoder.events` - 事件管理
- `autocoder.memory.active_context_manager` - 上下文管理

#### 🟢 可移除模块
- `autocoder.common.rag_manager` - RAG功能移除
- `autocoder.rag.*` - 所有RAG相关模块

## 技术实现细节

### 1. Namespace替换策略
```python
# 在每个迁移的文件中，替换import语句
# 原代码
from autocoder.utils.llms import get_single_llm
from autocoder.common import AutoCoderArgs

# 新代码  
from autocoder_slim.utils.llms import get_single_llm
from autocoder_slim.common import AutoCoderArgs
```

### 2. SDK集成更新
```python
# SDK内部对核心模块的依赖更新
# 原SDK代码
from autocoder.auto_coder_runner import run_auto_command

# 新SDK代码
from autocoder_slim.auto_coder_runner import run_auto_command
```

### 3. 完整兼容层
```python
# autocoder_slim/compat/bridge.py
from autocoder_slim.auto_coder_runner import run_auto_command as _run_auto_command
from autocoder_slim.auto_coder_runner import configure as _configure

# 同时支持SDK和核心模块的兼容性
def run_auto_command(args):
    """兼容原版run_auto_command接口"""
    return _run_auto_command(args)

def configure(config):
    """兼容原版configure接口"""
    return _configure(config)
```

## 预期结果

### 代码量估算
- **Phase 1**: ~8000-10000行（核心模块）
- **Phase 2**: ~4623行（SDK模块）
- **总计**: ~12000-14000行（完整迁移）

### 功能完整性
- ✅ 100%保留Agent功能
- ✅ 14个工具全部可用
- ✅ MCP协议支持
- ✅ 100% SDK API兼容
- ✅ 完整的SDK功能迁移
- ❌ 移除RAG功能

### 性能指标
- 启动时间: 与原版相当（功能完整）
- 内存占用: 略有减少（移除RAG）
- 包大小: 与原版相当（完整功能保留）

## 实施方式

### 任务驱动开发
每个Phase开始前先创建`phase{N}-tasks.md`，包含：
- 具体的迁移任务清单
- 任务间的依赖关系
- 验证标准
- 按依赖顺序执行

### 目录结构管理
```
specs/
├── phase1/
│   ├── phase1-core-extraction.md
│   ├── phase1-tasks.md
│   └── [其他Phase 1文档]
├── phase2/
│   ├── phase2-sdk-migration.md
│   ├── phase2-tasks.md
│   └── [其他Phase 2文档]
└── phase3/
    ├── phase3-integration.md
    └── [其他Phase 3文档]
```

### 迁移验证
每个模块迁移后都要验证：
- import语句正确性
- 功能完整性测试
- 与原版行为一致性
- API兼容性确认 