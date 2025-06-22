# AutoCoder Slim 项目概览

## 📋 文档管理规范

### 统一文档存放规则
**🚨 重要规则：所有项目相关的规范、规划、跟踪文档必须统一放置在 `specs/` 目录下，禁止在其他位置创建。**

**✅ 允许的文档位置：**
```
specs/
├── *.md                    # 项目规范文档
├── phase1/                 # Phase 1 相关文档
├── phase2/                 # Phase 2 相关文档  
├── phase3/                 # Phase 3 相关文档
└── [其他子目录]/            # 按主题分类的文档目录
```

**❌ 禁止的文档位置：**
```
auto-coder/plan.md          # ❌ 根目录
auto-coder/dependencies.md  # ❌ 根目录
auto-coder/docs/            # ❌ 其他目录
auto-coder/任何其他位置/      # ❌ 分散存放
```

### 文档管理原则
1. **集中管理**: 所有规划、分析、跟踪文档统一在specs/目录
2. **分类清晰**: 按阶段(phase1/2/3)或主题创建子目录
3. **避免重复**: 同类型文档不得在多个位置存在
4. **命名规范**: 使用描述性文件名，如`agent.md`, `api-compatibility.md`
5. **版本唯一**: 每个文档只保留一个最新版本

### 当前文档结构
```
specs/
├── PROJECT_OVERVIEW.md      # 本文档 - 项目总览
├── plan.md                  # 总体技术规划
├── dependencies.md          # 依赖分析报告
├── GET_STARTED.md          # 项目启动指南
├── agent.md                # Agent系统分析
├── auto_coder_runner.md    # 运行器分析
├── api-compatibility.md    # API兼容性规范
├── testing-strategy.md     # 测试策略
├── phase1/
│   └── phase1-core-extraction.md    # Phase 1详细方案
├── phase2/
│   └── phase2-sdk-migration.md      # Phase 2 SDK迁移
└── phase3/
    └── phase3-integration.md        # Phase 3集成优化
```

---

## 项目目标

从完整的AutoCoder项目中提取精简版AutoCoder-Slim，保留核心Agent功能，大幅减少代码复杂度。

## 🎯 迁移路径修正

### 正确的迁移目标结构
```
auto-coder/
├── src/
│   ├── autocoder/          # 原始完整版本 (源代码)
│   └── autocoder_slim/     # 精简版本 (目标代码)
├── specs/                  # 项目规划文档
├── dependencies.md         # 依赖分析报告  
└── plan.md                # 执行计划
```

**关键原则：**
- **源路径**: `auto-coder/src/autocoder/` - 原始完整实现
- **目标路径**: `auto-coder/src/autocoder_slim/` - 精简版实现
- **并行结构**: 两个版本在同一项目中，方便对比和复核
- **不创建独立项目**: 避免复杂的项目间依赖管理

## 🔄 迁移策略修正

### 1:1迁移原则
```python
# ❌ 错误：试图优化或简化代码
def simplified_function():
    return "简化实现"

# ✅ 正确：1:1复制原始实现，只修改导入路径
from autocoder_slim.common.v2.agent.agentic_edit import AgenticEdit  # 仅修改导入
# 其余代码完全保持原样
def original_complex_function(self, args, **kwargs):
    # 完整保留原始实现逻辑
    result = original_complex_logic(args, **kwargs)
    return result
```

### 修改范围限制
**允许修改的内容：**
- 导入语句：`from autocoder.xxx` → `from autocoder_slim.xxx`
- 模块名引用：`autocoder.xxx` → `autocoder_slim.xxx`
- 命名空间相关的字符串：配置中的模块路径等

**禁止修改的内容：**
- 函数实现逻辑
- 类定义和方法
- 算法和业务逻辑
- 数据结构和类型定义
- 配置值和常量（除非是路径相关）

## 📊 项目规模对比

| 版本 | 代码量 | 说明 |
|------|--------|------|
| autocoder | ~200,000行 | 完整版本，包含所有功能 |
| autocoder_slim | ~12,000行 | 精简版本，保留核心Agent功能 |

## 🎯 核心价值保留

### 完整保留的核心功能
1. **Agent智能体系统** - 100%保留
2. **14个工具解析器** - 100%保留
3. **Agent运行模式** - 100%保留
4. **MCP协议支持** - 100%保留
5. **SDK API接口** - 100%保留

### 移除的非核心功能
1. **RAG检索系统** - 完全移除
2. **传统命令模式** - 移除，只保留Agent模式
3. **复杂的CLI交互** - 简化为基础功能
4. **多种构建索引方式** - 只保留必要的索引功能

## 📁 目标目录结构

```
auto-coder/src/autocoder_slim/
├── __init__.py
├── auto_coder_runner.py           # 核心运行器(精简版)
├── common/
│   ├── __init__.py                # AutoCoderArgs等基础类
│   ├── types.py                   # 基础类型定义  
│   ├── mcp_server.py              # MCP服务器支持
│   ├── mcp_server_types.py        # MCP类型定义
│   ├── mcp_tools.py               # MCP工具集成
│   └── v2/
│       ├── agent/
│       │   ├── agentic_edit.py    # Agent核心(2432行)
│       │   ├── agentic_edit_types.py # Agent类型定义
│       │   └── agentic_edit_tools/    # 14个工具解析器
│       │       ├── read_file_tool_resolver.py
│       │       ├── write_to_file_tool_resolver.py
│       │       ├── replace_in_file_tool_resolver.py
│       │       ├── execute_command_tool_resolver.py
│       │       ├── attempt_completion_tool_resolver.py
│       │       ├── ask_followup_question_tool_resolver.py
│       │       └── ... (其余8个工具)
├── utils/
│   └── llms.py                    # LLM接口抽象
├── commands/
│   └── auto_command.py            # 命令处理(精简版)
└── sdk/                           # SDK兼容层
    ├── __init__.py                # 对外API
    ├── core/
    │   ├── bridge.py              # 桥接到运行器
    │   └── auto_coder_core.py     # SDK核心封装
    ├── models/
    │   ├── options.py             # 配置选项
    │   ├── messages.py            # 消息模型
    │   └── responses.py           # 响应模型
    └── exceptions.py              # SDK异常类
```

## 🚀 迁移执行原则

### 文件迁移流程
1. **复制原始文件** - 保持完整的原始实现
2. **更新导入路径** - 仅修改`import`和`from`语句
3. **验证语法正确性** - 确保修改后的代码可以正常导入
4. **保持功能一致性** - 确保迁移后的功能与原版本完全一致

### 质量保证标准
- **语法正确**: 所有Python文件都能正确导入
- **功能完整**: 核心Agent功能100%保留
- **接口兼容**: SDK API与原版本完全兼容
- **性能相当**: 执行性能不低于原版本的90%

## 📈 成功指标

### 功能指标
- ✅ Agent智能体运行正常
- ✅ 14个工具解析器全部可用
- ✅ SDK API完全兼容
- ✅ MCP协议支持正常

### 代码指标  
- ✅ 代码量从20万行减少到1.2万行
- ✅ 启动时间减少50%以上
- ✅ 内存占用减少60%以上
- ✅ 核心功能覆盖率100%

### 维护指标
- ✅ 目录结构清晰易懂
- ✅ 依赖关系简洁明确
- ✅ 文档完整准确
- ✅ 测试用例覆盖核心功能

## 项目架构

### 目标结构
```
autocoder_slim/
├── common/
│   ├── v2/agent/              # Agent系统核心
│   │   ├── agentic_edit.py            # 2432行 - 核心Agent类
│   │   ├── agentic_edit_types.py      # 190行 - 类型定义
│   │   └── agentic_edit_tools/        # 2248行 - 14个工具解析器
│   │       ├── __init__.py
│   │       ├── read_file.py
│   │       ├── write_to_file.py
│   │       ├── replace_in_file.py
│   │       ├── execute_command.py
│   │       ├── list_files.py
│   │       ├── attempt_completion.py
│   │       ├── ask_follow_up_question.py
│   │       ├── str_replace_editor.py
│   │       ├── create_directory.py
│   │       ├── search_and_replace.py
│   │       ├── view_range.py
│   │       ├── scroll_to_line.py
│   │       ├── find_in_files.py
│   │       └── open_file.py
│   └── mcp_server.py          # MCP协议支持
├── utils/
│   └── llms.py                # LLM接口抽象
├── commands/
│   └── auto_command.py        # 命令处理逻辑
├── auto_coder_runner.py       # 3486行 - 核心运行器
├── sdk/                       # 4623行 - 完整SDK
│   ├── __init__.py
│   ├── core/
│   ├── models/
│   ├── session/
│   ├── utils/
│   └── cli/
└── compat/
    └── bridge.py              # 兼容层实现
```

### 代码量分布
- **核心运行器**: ~3500行
- **Agent系统**: ~5000行 (包含14个工具解析器)
- **SDK模块**: ~4600行
- **辅助模块**: ~1000行
- **总计**: ~14000行 (保留完整功能)

## 14个Agent工具详解

### 文件操作工具 (8个)
1. **read_file** - 读取文件内容，支持行范围
2. **write_to_file** - 写入文件，支持创建和覆盖
3. **replace_in_file** - 文件内容替换
4. **view_range** - 查看文件指定行范围
5. **scroll_to_line** - 滚动到指定行
6. **open_file** - 打开文件编辑
7. **list_files** - 列出目录文件
8. **create_directory** - 创建目录结构

### 搜索和编辑工具 (3个)
9. **find_in_files** - 跨文件搜索
10. **search_and_replace** - 搜索替换操作
11. **str_replace_editor** - 字符串替换编辑器

### 执行和交互工具 (3个)
12. **execute_command** - 执行系统命令
13. **ask_follow_up_question** - 与用户交互
14. **attempt_completion** - 标记任务完成

## 三阶段实施计划

### Phase 1: 核心模块迁移
**目标**: 迁移Agent系统和核心运行器
- **任务**: 8个具体任务 (T1-T8)
- **代码量**: ~8000-10000行
- **关键成果**: Agent系统在新namespace下完全可用

#### 核心任务依赖图
```
T1: 项目结构创建
  ↓
T2: 基础模块迁移
  ↓  
T3: Agent类型定义迁移
  ↓
T4: 工具解析器迁移 (14个工具)
  ↓
T5: Agent核心迁移
  ↓
T6: 运行器迁移
  ↓
T7: SDK兼容层实现
  ↓
T8: 集成测试和验证
```

### Phase 2: SDK完整迁移
**目标**: 完整迁移SDK模块到autocoder_slim.sdk
- **代码量**: ~4600行
- **关键成果**: SDK API 100%兼容性

#### 主要任务
- SDK核心功能迁移
- 内部依赖关系更新  
- API接口兼容性保证
- 集成测试完善

### Phase 3: 集成优化和发布
**目标**: 性能优化、稳定性增强、发布准备
- **关键成果**: 生产就绪的autocoder_slim

#### 核心工作
- 全面集成测试
- 性能优化
- 稳定性增强
- 文档和示例完善
- 版本发布准备

## 技术实现细节

### Agent系统架构
```python
# 核心工作流
XML解析 → Pydantic模型 → ToolResolver → 执行 → ToolResult
```

### 14个工具的实现模式
每个工具遵循统一的实现模式：
```python
# 工具实现模板
class ToolNameResolver:
    def __init__(self):
        self.model = ToolNameModel
    
    def parse_xml(self, xml_str: str) -> ToolNameModel:
        # XML解析逻辑
        pass
    
    def resolve(self, model: ToolNameModel) -> ToolResult:
        # 工具执行逻辑
        pass
```

### 迁移策略
```python
# 命名空间替换示例
# 原始导入
from autocoder.common.v2.agent.agentic_edit import AgenticEdit

# 迁移后导入  
from autocoder_slim.common.v2.agent.agentic_edit import AgenticEdit

# 函数签名保持完全一致
def create_agent(options: AgentOptions) -> AgenticEdit:
    # 实现保持相同
    pass
```

## 质量保证

### 功能验证
- [ ] 14个工具全部通过单元测试
- [ ] Agent系统端到端测试通过
- [ ] SDK所有API接口兼容性验证
- [ ] 完整的迁移场景测试

### 性能指标
- [ ] 启动时间 < 200ms
- [ ] 内存占用 < 100MB  
- [ ] API响应时间与原版相当
- [ ] 支持并发调用

### 兼容性保证
- [ ] Python 3.8+ 支持
- [ ] 跨平台兼容性 (Windows/macOS/Linux)
- [ ] 向后兼容性保证
- [ ] 第三方集成兼容性

## 项目里程碑

### Phase 1 里程碑 (Week 1-2)
- [ ] Agent系统完全迁移
- [ ] 14个工具全部可用
- [ ] 核心运行器功能正常
- [ ] 基础集成测试通过

### Phase 2 里程碑 (Week 3-4)  
- [ ] SDK完整迁移
- [ ] API 100%兼容性
- [ ] 内部依赖关系清理
- [ ] 集成测试完善

### Phase 3 里程碑 (Week 5-8)
- [ ] 性能优化完成
- [ ] 稳定性增强
- [ ] 文档和示例完善
- [ ] 版本发布就绪

## 成功标准

### 技术标准
- **功能完整性**: 100%功能保留
- **性能标准**: 与原版性能相当或更优
- **代码质量**: 测试覆盖率 > 90%
- **文档完整性**: 100%API文档覆盖

### 用户体验标准
- **迁移成本**: 零代码修改迁移
- **学习成本**: 现有用户无学习成本
- **错误体验**: 清晰的错误信息和修复建议
- **社区反馈**: 用户满意度 > 4.5/5

## 风险评估与缓解

### 技术风险
- **复杂依赖关系**: 通过阶段性迁移和充分测试缓解
- **性能回归**: 通过基准测试和性能监控缓解
- **兼容性问题**: 通过全面的兼容性测试缓解

### 项目风险
- **时间压力**: 通过合理的阶段划分和并行工作缓解
- **质量风险**: 通过自动化测试和代码审查缓解
- **用户接受度**: 通过零破坏性迁移和完整文档缓解

## 长期价值

### 架构优势
- **更清晰的模块结构**: 易于维护和扩展
- **减少依赖复杂性**: 提升系统稳定性
- **更好的测试覆盖**: 提升代码质量
- **优化的性能**: 更快的启动和运行时间

### 开发体验提升
- **更好的IDE支持**: 清晰的类型提示和自动补全
- **更容易的调试**: 简化的调用栈和错误跟踪
- **更快的开发迭代**: 减少构建和测试时间
- **更好的文档**: 完整的API文档和示例

---

**本项目将为AutoCoder生态系统提供一个更加精简、高效、可维护的核心实现，为未来的功能扩展和性能优化奠定坚实基础。** 