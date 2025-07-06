# Phase 1: 核心模块1:1迁移

## 📋 文档管理规范提醒

**🚨 文档创建规则：**
- 所有Phase 1相关的新文档（如迁移日志、问题记录、验证报告等）必须放在 `specs/phase1/` 目录下
- 禁止在根目录或其他位置创建文档
- 参考完整规范：[PROJECT_OVERVIEW.md#文档管理规范](../PROJECT_OVERVIEW.md#📋-文档管理规范)

---

## 🎯 目标修正

### 正确的迁移路径
```
源代码路径: auto-coder/src/autocoder/
目标路径:   auto-coder/src/autocoder_slim/
```

**重要原则：**
- ✅ 在当前项目内创建parallel结构，方便对比复核
- ✅ 1:1迁移策略，仅修改导入路径
- ❌ 不创建独立项目，避免复杂依赖

## 🔄 1:1迁移策略详解

### 迁移范围限制

**✅ 允许修改：**
1. **导入语句**
   ```python
   # 修改前
   from autocoder.common.v2.agent.agentic_edit import AgenticEdit
   from autocoder.utils.llms import get_single_llm
   import autocoder.auto_coder_runner as runner
   
   # 修改后  
   from autocoder_slim.common.v2.agent.agentic_edit import AgenticEdit
   from autocoder_slim.utils.llms import get_single_llm
   import autocoder_slim.auto_coder_runner as runner
   ```

2. **字符串中的模块路径**
   ```python
   # 修改前
   module_path = "autocoder.common.types"
   
   # 修改后
   module_path = "autocoder_slim.common.types"
   ```

**❌ 禁止修改：**
1. **函数实现逻辑**
2. **类定义结构**
3. **算法实现**
4. **数据结构**
5. **配置值和常量**
6. **函数签名**
7. **异常处理逻辑**

### 验证标准
```bash
# 验证1：文件行数接近（允许±5行差异）
wc -l src/autocoder/target_file.py
wc -l src/autocoder_slim/target_file.py

# 验证2：导入路径修改正确
grep "from autocoder\." src/autocoder_slim/target_file.py  # 应该为空
grep "from autocoder_slim\." src/autocoder_slim/target_file.py  # 应该有结果

# 验证3：可以正确导入
python -c "import autocoder_slim.target_module"
```

## 📋 Phase 1 任务列表

### T1: 项目结构创建
**目标**: 创建正确的目录结构

```bash
# 创建基础目录结构
mkdir -p src/autocoder_slim/{common/v2/agent/agentic_edit_tools,utils,commands,sdk}

# 创建__init__.py文件
find src/autocoder_slim -type d -exec touch {}/__init__.py \;

# 验证结构
tree src/autocoder_slim
```

**验证标准:**
- [ ] src/autocoder_slim目录存在
- [ ] 所有子目录包含__init__.py
- [ ] 目录结构与src/autocoder对应

### T2: 基础依赖模块1:1迁移
**目标**: 迁移核心依赖模块

**优先级1: 基础类型和配置**
```bash
# 迁移AutoCoderArgs等基础类
cp src/autocoder/common/__init__.py src/autocoder_slim/common/__init__.py
sed -i 's/from autocoder\./from autocoder_slim\./g' src/autocoder_slim/common/__init__.py

# 迁移基础类型
cp src/autocoder/common/types.py src/autocoder_slim/common/types.py
sed -i 's/from autocoder\./from autocoder_slim\./g' src/autocoder_slim/common/types.py
```

**验证T2完成:**
```python
# 这些导入应该成功
from autocoder_slim.common import AutoCoderArgs, SourceCode, SourceCodeList
```

### T3: Agent类型系统迁移
**目标**: 迁移Agent相关的类型定义

```bash
# 1:1迁移agentic_edit_types.py
cp src/autocoder/common/v2/agent/agentic_edit_types.py \
   src/autocoder_slim/common/v2/agent/agentic_edit_types.py

# 仅修改导入路径
sed -i 's/from autocoder\./from autocoder_slim\./g' \
   src/autocoder_slim/common/v2/agent/agentic_edit_types.py
```

**验证T3完成:**
```python
from autocoder_slim.common.v2.agent.agentic_edit_types import (
    ToolType, AgenticEditRequest, AgenticEditConversationConfig
)
```

### T4: 核心工具解析器1:1迁移
**目标**: 迁移14个工具解析器

**核心6个工具（优先）:**
1. `read_file_tool_resolver.py`
2. `write_to_file_tool_resolver.py`
3. `replace_in_file_tool_resolver.py`
4. `execute_command_tool_resolver.py`
5. `attempt_completion_tool_resolver.py`
6. `ask_followup_question_tool_resolver.py`

**迁移脚本:**
```bash
#!/bin/bash
TOOLS_DIR="src/autocoder/common/v2/agent/agentic_edit_tools"
TARGET_DIR="src/autocoder_slim/common/v2/agent/agentic_edit_tools"

# 迁移所有工具解析器
for tool_file in $TOOLS_DIR/*_tool_resolver.py; do
    tool_name=$(basename "$tool_file")
    
    # 1:1复制
    cp "$tool_file" "$TARGET_DIR/$tool_name"
    
    # 仅修改导入路径
    sed -i 's/from autocoder\./from autocoder_slim\./g' "$TARGET_DIR/$tool_name"
    sed -i 's/import autocoder\./import autocoder_slim\./g' "$TARGET_DIR/$tool_name"
    
    echo "✅ 迁移完成: $tool_name"
done

# 迁移base_tool_resolver.py和__init__.py
cp $TOOLS_DIR/base_tool_resolver.py $TARGET_DIR/
cp $TOOLS_DIR/__init__.py $TARGET_DIR/

# 修改导入路径
sed -i 's/from autocoder\./from autocoder_slim\./g' $TARGET_DIR/base_tool_resolver.py
sed -i 's/from autocoder\./from autocoder_slim\./g' $TARGET_DIR/__init__.py
```

**验证T4完成:**
```python
from autocoder_slim.common.v2.agent.agentic_edit_tools import (
    ReadFileToolResolver, WriteToFileToolResolver, ReplaceInFileToolResolver,
    ExecuteCommandToolResolver, AttemptCompletionToolResolver,
    AskFollowupQuestionToolResolver
)
```

### T5: Agent核心1:1迁移
**目标**: 迁移agentic_edit.py核心文件

```bash
# 1:1迁移Agent核心文件（2432行）
cp src/autocoder/common/v2/agent/agentic_edit.py \
   src/autocoder_slim/common/v2/agent/agentic_edit.py

# 仅修改导入路径
sed -i 's/from autocoder\./from autocoder_slim\./g' \
   src/autocoder_slim/common/v2/agent/agentic_edit.py
sed -i 's/import autocoder\./import autocoder_slim\./g' \
   src/autocoder_slim/common/v2/agent/agentic_edit.py
```

**验证T5完成:**
```python
from autocoder_slim.common.v2.agent.agentic_edit import AgenticEdit
```

### T6: 运行器核心1:1迁移
**目标**: 迁移auto_coder_runner.py

```bash
# 1:1迁移运行器核心（3486行）
cp src/autocoder/auto_coder_runner.py \
   src/autocoder_slim/auto_coder_runner.py

# 仅修改导入路径
sed -i 's/from autocoder\./from autocoder_slim\./g' \
   src/autocoder_slim/auto_coder_runner.py
sed -i 's/import autocoder\./import autocoder_slim\./g' \
   src/autocoder_slim/auto_coder_runner.py
```

**验证T6完成:**
```python
from autocoder_slim.auto_coder_runner import run_auto_command
```

### T7: 支持模块1:1迁移
**目标**: 迁移必要的支持模块

**关键支持模块:**
1. `utils/llms.py` - LLM接口
2. `commands/auto_command.py` - 命令处理
3. `common/mcp_server.py` - MCP支持
4. `common/mcp_server_types.py` - MCP类型
5. `common/mcp_tools.py` - MCP工具

```bash
# 迁移LLM接口
cp src/autocoder/utils/llms.py src/autocoder_slim/utils/llms.py
sed -i 's/from autocoder\./from autocoder_slim\./g' src/autocoder_slim/utils/llms.py

# 迁移命令处理
cp src/autocoder/commands/auto_command.py src/autocoder_slim/commands/auto_command.py
sed -i 's/from autocoder\./from autocoder_slim\./g' src/autocoder_slim/commands/auto_command.py

# 迁移MCP支持模块
for mcp_file in mcp_server.py mcp_server_types.py mcp_tools.py; do
    cp src/autocoder/common/$mcp_file src/autocoder_slim/common/$mcp_file
    sed -i 's/from autocoder\./from autocoder_slim\./g' src/autocoder_slim/common/$mcp_file
done
```

### T8: 集成验证和测试
**目标**: 确保所有迁移的模块可以正确工作

**基础导入测试:**
```python
#!/usr/bin/env python3
# test_basic_imports.py

def test_basic_imports():
    """测试基础模块导入"""
    try:
        from autocoder_slim.common import AutoCoderArgs
        from autocoder_slim.common.v2.agent.agentic_edit_types import ToolType
        from autocoder_slim.common.v2.agent.agentic_edit import AgenticEdit
        from autocoder_slim.auto_coder_runner import run_auto_command
        print("✅ 基础导入测试通过")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_tool_resolvers():
    """测试工具解析器导入"""
    try:
        from autocoder_slim.common.v2.agent.agentic_edit_tools import (
            ReadFileToolResolver, WriteToFileToolResolver, 
            ReplaceInFileToolResolver, ExecuteCommandToolResolver
        )
        print("✅ 工具解析器导入测试通过") 
        return True
    except ImportError as e:
        print(f"❌ 工具解析器导入失败: {e}")
        return False

if __name__ == "__main__":
    all_passed = True
    all_passed &= test_basic_imports()
    all_passed &= test_tool_resolvers()
    
    if all_passed:
        print("\n🎉 所有基础测试通过！Phase 1迁移成功！")
    else:
        print("\n❌ 部分测试失败，需要检查迁移")
```

## 📊 Phase 1 成功指标

### 功能指标
- [ ] 所有基础模块可以正确导入
- [ ] 14个工具解析器全部可用
- [ ] Agent核心类可以实例化
- [ ] 运行器函数可以调用

### 代码质量指标
- [ ] 迁移文件行数与原文件接近（±5%）
- [ ] 所有导入路径正确更新
- [ ] 核心逻辑代码完全一致
- [ ] Python语法检查通过

### 1:1迁移验证
```bash
# 验证脚本
#!/bin/bash

echo "=== Phase 1 迁移验证 ==="

# 检查文件行数差异
check_file_diff() {
    original="src/autocoder/$1"
    migrated="src/autocoder_slim/$1"
    
    if [[ -f "$original" && -f "$migrated" ]]; then
        orig_lines=$(wc -l < "$original")
        migr_lines=$(wc -l < "$migrated")
        diff=$((migr_lines - orig_lines))
        
        if [[ $diff -ge -5 && $diff -le 5 ]]; then
            echo "✅ $1: $orig_lines → $migr_lines (差异: $diff)"
        else
            echo "❌ $1: 行数差异过大 $orig_lines → $migr_lines (差异: $diff)"
        fi
    fi
}

# 检查关键文件
check_file_diff "auto_coder_runner.py"
check_file_diff "common/v2/agent/agentic_edit.py"
check_file_diff "common/v2/agent/agentic_edit_types.py"

# 检查导入路径
echo -e "\n=== 导入路径检查 ==="
old_imports=$(find src/autocoder_slim -name "*.py" -exec grep -l "from autocoder\." {} \;)
if [[ -z "$old_imports" ]]; then
    echo "✅ 所有旧的导入路径已更新"
else
    echo "❌ 发现未更新的导入路径:"
    echo "$old_imports"
fi

# 基础导入测试
echo -e "\n=== 导入测试 ==="
python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from autocoder_slim.common.v2.agent.agentic_edit import AgenticEdit
    from autocoder_slim.auto_coder_runner import run_auto_command
    print('✅ 关键模块导入成功')
except Exception as e:
    print(f'❌ 导入失败: {e}')
"

echo -e "\n=== Phase 1 验证完成 ==="
```

## 🎯 Phase 1完成标准

**Phase 1任务完成后，应该满足：**

1. **结构完整**: src/autocoder_slim目录结构正确
2. **导入成功**: 所有核心模块可以导入
3. **功能保留**: Agent系统和14个工具完整迁移
4. **代码一致**: 实现逻辑与原版本完全一致
5. **路径正确**: 所有导入路径正确更新

**下一步**: 准备进入Phase 2 SDK迁移阶段 