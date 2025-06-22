# AutoCoder Slim 项目启动指南

## 📋 文档管理规范

**🚨 重要提醒：所有项目规划、分析、跟踪文档都必须统一放在 `specs/` 目录下！**
- 详细规范请参考：[PROJECT_OVERVIEW.md#文档管理规范](./PROJECT_OVERVIEW.md#📋-文档管理规范)
- 禁止在根目录或其他位置创建规划文档
- 按阶段(phase1/2/3)或主题创建子目录组织文档

---

## 项目状态

✅ **规划完成** - 所有技术分析和实施计划已就绪  
🚀 **准备启动** - 可以开始Phase 1具体实施

## 🎯 迁移路径修正

### 正确的目标结构
```
auto-coder/
├── src/
│   ├── autocoder/          # 原始完整版本 (源代码)
│   └── autocoder_slim/     # 精简版本 (目标代码) 
├── specs/                  # 项目规划文档
├── dependencies.md         # 依赖分析报告  
└── plan.md                # 执行计划
```

**重要修正：**
- ❌ **错误路径**: 创建独立的`autocoder-slim`项目
- ✅ **正确路径**: 在当前项目中创建`src/autocoder_slim`目录
- 🎯 **目标**: 方便对比和复核，避免复杂的项目间依赖

## 🔄 1:1迁移策略

### 迁移原则
**✅ 允许修改：**
```python
# 导入路径修改
from autocoder.common.v2.agent.agentic_edit import AgenticEdit
↓
from autocoder_slim.common.v2.agent.agentic_edit import AgenticEdit

# 模块引用修改  
autocoder.auto_coder_runner.run_auto_command()
↓
autocoder_slim.auto_coder_runner.run_auto_command()
```

**❌ 禁止修改：**
```python
# 禁止简化或优化实现逻辑
def complex_original_function(self, args, **kwargs):
    # 保持所有原始实现细节
    step1 = complex_preprocessing(args)
    step2 = detailed_validation(step1) 
    step3 = multi_stage_processing(step2, **kwargs)
    return complex_postprocessing(step3)
```

### 迁移检查清单
- [ ] 文件结构1:1复制
- [ ] 仅修改导入路径，不修改实现逻辑
- [ ] 保持所有函数签名完全一致
- [ ] 保持所有类定义完全一致
- [ ] 保持所有常量和配置值一致
- [ ] 验证修改后的文件可以正确导入

## 核心技术发现

### 当前AutoCoder分析结果
- **总代码量**: ~200,000行
- **SDK代码**: 4623行 (相对精简)
- **Agent系统**: ~5000行 (核心功能)
- **核心运行器**: 3486行 (40+函数)
- **14个工具解析器**: 完整保留

### 重要决策确认
1. **保留所有Agent工具** ✅ - 14个工具全部保留
2. **完整功能迁移** ✅ - 1:1迁移，不优化
3. **移除RAG保留MCP** ✅ - 简化依赖
4. **namespace迁移** ✅ - autocoder → autocoder_slim

## 立即开始：Phase 1 实施

### 当前优先任务：T1 - 项目结构创建

#### 第一步：创建正确的目录结构
```bash
mkdir -p src/autocoder_slim/{common/v2/agent/agentic_edit_tools,utils,commands,sdk}
```

#### 第二步：创建基础__init__.py文件
所有目录都需要__init__.py文件以形成Python包结构。

#### 第三步：开始T2 - 基础模块1:1迁移
重点迁移（保持原始实现）：
- `common/__init__.py` - AutoCoderArgs等基础类
- `utils/llms.py` - LLM接口抽象
- `commands/auto_command.py` - 命令处理

### 具体执行命令

```bash
# 1. 创建正确的目录结构
mkdir -p src/autocoder_slim

# 2. 开始Phase 1任务
# 使用cp + sed的方式确保1:1迁移
```

## Phase 1 任务依赖图

```
T1: 项目结构创建 (立即执行)
  ↓
T2: 基础模块1:1迁移 (common/, utils/, commands/)
  ↓  
T3: Agent类型定义迁移 (agentic_edit_types.py)
  ↓
T4: 工具解析器1:1迁移 (14个工具)
  ↓
T5: Agent核心1:1迁移 (agentic_edit.py)
  ↓
T6: 运行器1:1迁移 (auto_coder_runner.py)
  ↓
T7: SDK兼容层实现 (sdk/)
  ↓
T8: 集成测试和验证
```

## 详细技术路线图

### Phase 1: 核心模块1:1迁移 (Week 1-2)
- **目标**: Agent系统和核心运行器迁移
- **预期代码量**: 8000-10000行
- **关键成果**: 14个工具在新namespace下可用
- **迁移策略**: 完全1:1复制，仅修改导入路径

### Phase 2: SDK完整迁移 (Week 3-4)
- **目标**: SDK模块100%兼容迁移
- **预期代码量**: 4600行
- **关键成果**: autocoder_slim.sdk完全可用
- **迁移策略**: 保持API完全兼容

### Phase 3: 集成优化 (Week 5-8)
- **目标**: 性能优化和发布准备
- **关键成果**: 生产就绪版本

## 关键代码模块定位

### Agent核心文件路径
```
原始路径 → 目标路径

src/autocoder/common/v2/agent/agentic_edit.py
→ src/autocoder_slim/common/v2/agent/agentic_edit.py

src/autocoder/common/v2/agent/agentic_edit_types.py  
→ src/autocoder_slim/common/v2/agent/agentic_edit_types.py

src/autocoder/common/v2/agent/agentic_edit_tools/
→ src/autocoder_slim/common/v2/agent/agentic_edit_tools/
```

### 14个工具文件路径
```
agentic_edit_tools/
├── read_file_tool_resolver.py
├── write_to_file_tool_resolver.py
├── replace_in_file_tool_resolver.py
├── execute_command_tool_resolver.py
├── list_files_tool_resolver.py
├── attempt_completion_tool_resolver.py
├── ask_followup_question_tool_resolver.py
├── search_files_tool_resolver.py
├── list_code_definition_names_tool_resolver.py
├── list_package_info_tool_resolver.py
├── use_mcp_tool_resolver.py
├── plan_mode_respond_tool_resolver.py
├── base_tool_resolver.py
└── __init__.py
```

### SDK模块路径
```
src/autocoder/sdk/ → src/autocoder_slim/sdk/
├── __init__.py
├── core/
├── models/
├── session/
├── utils/
└── cli/
```

## 验证检查点

### T1完成验证
- [ ] src/autocoder_slim/目录结构创建
- [ ] 所有必要的__init__.py文件存在
- [ ] 基础包导入无错误

### T2完成验证  
- [ ] common/__init__.py 1:1迁移成功
- [ ] utils/llms.py 1:1迁移成功
- [ ] import autocoder_slim.utils.llms 成功

### 每个任务的具体验证标准
```bash
# 验证文件迁移成功
wc -l src/autocoder_slim/target_file.py
python -c "import autocoder_slim.target_module"

# 验证导入路径修改正确
grep -n "from autocoder\." src/autocoder_slim/target_file.py  # 应该为空
grep -n "from autocoder_slim\." src/autocoder_slim/target_file.py  # 应该有结果
```

## 预期成果

### Phase 1结束时
```python
# 这些导入应该全部工作 (1:1迁移后)
from autocoder_slim.common.v2.agent.agentic_edit import AgenticEdit
from autocoder_slim.common.v2.agent.agentic_edit_types import ToolType
from autocoder_slim.auto_coder_runner import run_auto_command

# 14个工具解析器全部可用 (1:1迁移后)
from autocoder_slim.common.v2.agent.agentic_edit_tools import (
    ReadFileResolver, WriteToFileResolver, ReplaceInFileResolver,
    # ... 其他11个
)
```

### Phase 2结束时
```python
# SDK完全可用 (API保持完全兼容)
from autocoder_slim.sdk import query, modify_code_stream
from autocoder_slim.sdk import AutoCodeOptions

# 100%兼容的API
result = query("创建一个Python函数")
```

### Phase 3结束时
- 性能优化完成
- 稳定性验证通过
- 文档和示例完整
- 发布版本准备就绪

## 质量保证检查点

### 代码质量
- [ ] 所有迁移的代码通过静态分析
- [ ] 类型提示完整准确
- [ ] 导入路径正确更新
- [ ] 函数签名保持完全一致

### 功能完整性
- [ ] 14个Agent工具全部功能正常
- [ ] SDK所有API接口兼容
- [ ] 核心运行器功能完整
- [ ] MCP协议支持正常

### 1:1迁移验证
- [ ] 原始文件与迁移文件行数接近（允许导入行数差异）
- [ ] 核心逻辑代码完全一致
- [ ] 类和函数定义完全一致
- [ ] 算法实现完全一致

## 迁移执行工具

### 推荐的迁移脚本
```bash
#!/bin/bash
# 1:1迁移脚本示例

# 复制文件
cp src/autocoder/target_file.py src/autocoder_slim/target_file.py

# 修改导入路径（仅此修改）
sed -i 's/from autocoder\./from autocoder_slim\./g' src/autocoder_slim/target_file.py
sed -i 's/import autocoder\./import autocoder_slim\./g' src/autocoder_slim/target_file.py

# 验证修改结果
echo "修改后的导入语句："
grep "from autocoder_slim\|import autocoder_slim" src/autocoder_slim/target_file.py

# 验证可以导入
python -c "import autocoder_slim.target_module" && echo "✅ 导入成功"
```

## 下一步行动

### 立即执行
1. **开始T1**: 创建src/autocoder_slim项目结构
2. **准备T2**: 识别需要1:1迁移的基础模块
3. **开始迁移**: 按照1:1原则执行具体任务

### 推荐工作方式
- 每完成一个文件迁移，立即进行验证测试
- 使用cp + sed确保1:1迁移
- 优先保证功能正确性，避免任何优化
- 定期备份进度，避免大幅回退

### 需要的工具和资源
- Python 3.8+ 开发环境
- 原始autocoder代码访问权限
- 测试环境用于验证迁移结果
- 版本控制系统记录迁移进度

---

**现在可以开始执行Phase 1的T1任务：在src/目录下创建autocoder_slim结构**

**所有技术分析已完成，1:1迁移策略已明确，可以立即开始具体的代码迁移工作。** 