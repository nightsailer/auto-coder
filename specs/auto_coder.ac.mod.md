# auto_coder

AutoCoder系统的主入口模块，提供统一的命令行接口和配置管理，支持多种操作模式包括项目初始化、代码生成、文档处理、代理系统、索引管理等核心功能。

## 模块位置

**源码路径**: `src/autocoder/auto_coder.py`  
**文档路径**: `specs/auto_coder.ac.mod.md`  
**模块类型**: 单文件模块

## 文件结构

```python
# auto_coder.py 内容结构
├── 导入部分                    # 系统依赖和AutoCoder模块导入
├── resolve_include_path()      # 解析包含文件路径
├── load_include_files()        # 加载包含的配置文件
└── main()                      # 主入口函数，处理所有命令和操作模式
```

## 快速开始

### 基本使用方式

```python
# 直接调用main函数
from autocoder.auto_coder import main

# 1. 项目初始化
main(["init", "--project_type", ".py", "--source_dir", "/path/to/project"])

# 2. 代码生成
main(["--model", "gpt-4", "--query", "创建一个HTTP服务器", "--source_dir", "/path/to/project"])

# 3. 代理模式
main(["agent", "chat", "--model", "gpt-4", "--query", "分析代码结构"])

# 4. 文档处理
main(["doc", "build", "--source_dir", "/path/to/project"])

# 5. 索引管理
main(["index", "--source_dir", "/path/to/project"])
```

### 命令行使用

```bash
# 项目初始化
auto-coder init --project_type .py --source_dir .

# 基本代码生成
auto-coder --model gpt-4 --query "实现用户认证模块" --source_dir .

# 代理系统
auto-coder agent chat --model gpt-4 --query "帮我分析这个项目"

# 文档构建
auto-coder doc build --source_dir .

# 索引构建
auto-coder index --source_dir .
```

### 配置文件支持

```yaml
# config.yml
model: "gpt-4"
source_dir: "/path/to/project"
project_type: ".py,.ts"
query: "实现RESTful API"
include_file:
  - "base_config.yml"  # 支持配置文件包含
```

## 核心组件详解

### 1. main() 主函数

**功能**: AutoCoder系统的统一入口点，处理所有命令和操作模式
- **参数解析**: 解析命令行参数和配置文件
- **模式分发**: 根据命令类型分发到不同的处理模块
- **LLM初始化**: 根据产品模式(pro/lite)初始化大语言模型
- **环境配置**: 设置工作目录、存储、日志等运行环境

### 2. 配置管理系统

**load_include_files()**: 递归加载配置文件
- **功能**: 支持配置文件的嵌套包含，避免循环依赖
- **模板支持**: 支持环境变量模板(ENV {{VARIABLE_NAME}})
- **深度控制**: 防止无限递归包含

**resolve_include_path()**: 解析包含文件路径
- **功能**: 处理相对路径和绝对路径的解析
- **安全性**: 确保路径解析的安全性

### 3. 命令处理系统

**支持的主要命令**:
- **init**: 项目初始化，创建目录结构和配置文件
- **agent**: 代理系统，支持chat、planner、designer等子命令
- **doc**: 文档处理，支持build、query、serve、chat等操作
- **index**: 索引管理，支持构建和查询
- **screenshot**: 网页截图功能
- **store**: 存储状态查询
- **revert**: 文件恢复功能

### 4. LLM模型管理

**Pro模式**: 企业级部署模式
- 使用ByzerLLM连接Ray集群
- 支持分布式模型服务
- 自动模型发现和负载均衡

**Lite模式**: 轻量级部署模式
- 使用SimpleByzerLLM直接连接SaaS服务
- 支持多种模型提供商(OpenAI、Claude等)
- 本地配置管理

## Mermaid 依赖图

```mermaid
graph TB
    %% 核心模块定义
    auto_coder[auto_coder.py<br/>主入口模块]
    
    %% 主要函数
    main_func[main()<br/>主入口函数]
    load_include[load_include_files()<br/>配置文件加载]
    resolve_path[resolve_include_path()<br/>路径解析]
    
    %% 命令处理模块
    dispacher[Dispacher<br/>命令分发器]
    agent_system[agent<br/>代理系统]
    doc_system[doc<br/>文档系统]
    index_system[index<br/>索引系统]
    
    %% 核心依赖模块
    common[common<br/>通用工具模块]
    rag[rag<br/>RAG系统]
    events[events<br/>事件系统]
    db[db<br/>数据库模块]
    utils[utils<br/>工具模块]
    
    %% 内部关系
    auto_coder --> main_func
    auto_coder --> load_include
    auto_coder --> resolve_path
    
    main_func --> dispacher
    main_func --> agent_system
    main_func --> doc_system
    main_func --> index_system
    
    %% 外部依赖关系
    auto_coder --> common
    auto_coder --> rag
    auto_coder --> events
    auto_coder --> db
    auto_coder --> utils
    
    %% 样式定义
    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:3px
    classDef funcClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef cmdClass fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef depClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class auto_coder coreClass
    class main_func,load_include,resolve_path funcClass
    class dispacher,agent_system,doc_system,index_system cmdClass
    class common,rag,events,db,utils depClass
```

## 依赖关系说明

### 对其他模块的依赖
列出该模块依赖的其他具有 `.ac.mod.md` 文档的模块（使用specs目录下的文档路径）：

- `specs/common.ac.mod.md` - 使用AutoCoderArgs、git_utils、代码执行等核心功能
- `specs/rag.ac.mod.md` - 文档处理和RAG服务功能
- `specs/agent.ac.mod.md` - 代理系统的各种代理实现
- `specs/events.ac.mod.md` - 事件管理和流式处理
- `specs/db.ac.mod.md` - 数据存储和Token计数
- `specs/utils_llms.ac.mod.md` - LLM工具函数和模型管理
- `specs/index.ac.mod.md` - 索引构建和查询功能

### 被依赖关系
列出依赖于该模块的其他模块：

- `specs/auto_coder_runner.ac.mod.md` - 导入main函数和AutoCoderArgs、load_include_files等
- `specs/auto_coder_server.ac.mod.md` - 导入main函数作为服务器入口
- `specs/commands.ac.mod.md` - 导入AutoCoderArgs类型定义
- `specs/utils_other.ac.mod.md` - operate_config_api模块导入配置相关函数
- `specs/agent.ac.mod.md` - agentic_filter模块导入AutoCoderArgs类型
- **命令行入口点**: 通过setup.py配置为auto-coder、auto-coder.core等命令行工具
- **测试模块**: 多个测试文件导入load_tokenizer等函数

## 可以验证模块可运行的测试命令

提供可执行的验证命令，例如：

```bash
# 单文件模块测试
python -c "from autocoder.auto_coder import main; print('Auto-coder main module imported successfully')"

# 验证主要功能
python -c "from autocoder.auto_coder import load_include_files, resolve_include_path; print('Config functions available')"

# 测试命令行接口
auto-coder --help
auto-coder init --help
auto-coder agent --help
auto-coder doc --help

# 验证配置文件加载
echo "model: gpt-4" > test_config.yml
python -c "
import yaml
from autocoder.auto_coder import load_include_files
config = yaml.safe_load(open('test_config.yml'))
result = load_include_files(config, 'test_config.yml')
print('Config loading works:', 'model' in result)
"
rm test_config.yml

# 检查依赖关系
python -c "from autocoder.common import AutoCoderArgs; from autocoder.dispacher import Dispacher; print('Dependencies available')"
``` 