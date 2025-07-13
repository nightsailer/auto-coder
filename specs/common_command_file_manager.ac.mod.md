# common.command_file_manager.ac.mod.md

## 模块概述

`common.command_file_manager` 模块是 Auto-Coder 系统的命令文件管理核心，提供对 `.autocodercommands` 目录中命令文件的完整管理功能。该模块支持命令文件的发现、读取、分析和 Jinja2 模板渲染，为 Auto-Coder 的命令系统提供灵活的模板化命令管理能力。

**模块类型**: 包模块  
**主要功能**: 命令文件管理、Jinja2 模板处理、变量提取和分析  
**依赖关系**: 依赖 `byzerllm.utils`、`loguru` 等模块

## 核心组件

### 1. 数据模型层 (models.py)
- **CommandFile**: 表示单个命令文件的信息
- **JinjaVariable**: 表示从命令文件中提取的 Jinja2 变量
- **CommandFileAnalysisResult**: 命令文件分析结果
- **ListCommandsResult**: 列出命令文件的结果

### 2. 管理器层 (manager.py)
- **CommandManager**: 主要管理器，提供高层次 API 接口
- 支持递归目录搜索和文件过滤
- 集成 Jinja2 模板渲染功能

### 3. 工具函数层 (utils.py)
- **extract_jinja2_variables()**: 提取 Jinja2 变量名
- **extract_jinja2_variables_with_metadata()**: 提取变量及元数据
- **analyze_command_file()**: 分析命令文件
- **is_command_file()**: 检查是否为命令文件

## 主要功能

### 1. 基础命令文件管理

```python
from autocoder.common.command_file_manager import CommandManager

# 初始化命令管理器
manager = CommandManager()  # 默认使用 .autocodercommands 目录
# 或指定自定义目录
manager = CommandManager("/path/to/custom/commands")

# 列出所有命令文件
result = manager.list_command_files(recursive=True)

if result.success:
    print(f"发现 {len(result.command_files)} 个命令文件:")
    for file_path in result.command_files:
        print(f"  {file_path}")
else:
    print("列出命令文件失败:")
    for path, error in result.errors.items():
        print(f"  {path}: {error}")

# 读取特定命令文件
command_file = manager.read_command_file("example_command.md")

if command_file:
    print(f"文件: {command_file.file_name}")
    print(f"路径: {command_file.file_path}")
    print(f"内容长度: {len(command_file.content)} 字符")
    print(f"内容预览: {command_file.content[:200]}...")
```

### 2. Jinja2 模板渲染

```python
# 创建包含 Jinja2 变量的命令文件
command_content = """
# {{ task_name }} 任务

## 描述
这是一个 {{ task_type }} 任务，由 {{ author }} 创建。

## 参数
- 优先级: {{ priority | default("normal") }}
- 截止日期: {{ deadline | default("未设置") }}

## 执行步骤
{% if steps %}
{% for step in steps %}
{{ loop.index }}. {{ step }}
{% endfor %}
{% else %}
暂无执行步骤
{% endif %}

## 注意事项
{% if notes %}
{{ notes }}
{% endif %}
"""

# 保存为命令文件（假设已保存为 task_template.md）

# 使用变量渲染命令文件
render_variables = {
    "task_name": "用户登录功能开发",
    "task_type": "开发",
    "author": "开发团队",
    "priority": "high",
    "deadline": "2024-12-31",
    "steps": [
        "分析需求",
        "设计数据库",
        "实现后端API",
        "开发前端界面",
        "编写测试用例",
        "部署上线"
    ],
    "notes": "请确保密码加密和安全验证"
}

# 渲染命令文件
rendered_content = manager.read_command_file_with_render(
    "task_template.md",
    render_variables
)

if rendered_content:
    print("渲染后的内容:")
    print(rendered_content)
else:
    print("渲染失败")
```

### 3. 变量提取和分析

```python
from autocoder.common.command_file_manager.utils import (
    extract_jinja2_variables,
    extract_jinja2_variables_with_metadata,
    analyze_command_file
)

# 基础变量提取
template_content = """
Hello {{ name }}!
Your age is {{ age }} and you live in {{ city }}.
{% if premium %}
You have premium access.
{% endif %}
"""

# 提取所有变量名
variables = extract_jinja2_variables(template_content)
print(f"发现变量: {variables}")
# 输出: {'name', 'age', 'city', 'premium'}

# 高级变量提取（包含元数据）
advanced_template = """
{# @var: name, description: 用户姓名 #}
{# @var: age, default: 18, description: 用户年龄 #}
{# @var: city, default: 北京, description: 用户所在城市 #}
{# @var: premium, default: false, description: 是否为高级用户 #}

Hello {{ name }}!
Your age is {{ age }} and you live in {{ city }}.
{% if premium %}
You have premium access.
{% endif %}
"""

# 提取变量及元数据
variables_with_metadata = extract_jinja2_variables_with_metadata(advanced_template)

for var in variables_with_metadata:
    print(f"变量: {var.name}")
    if var.default_value:
        print(f"  默认值: {var.default_value}")
    if var.description:
        print(f"  描述: {var.description}")
    print()

# 分析命令文件
analysis_result = manager.analyze_command_file("task_template.md")

if analysis_result:
    print(f"文件: {analysis_result.file_name}")
    print(f"变量数量: {len(analysis_result.variables)}")
    print(f"原始变量: {analysis_result.raw_variables}")
    
    for var in analysis_result.variables:
        print(f"  {var.name}: {var.description or '无描述'}")
```

### 4. 批量变量分析

```python
# 获取所有命令文件中的变量
all_variables = manager.get_all_variables(recursive=True)

print("所有命令文件的变量分析:")
for file_path, variables in all_variables.items():
    print(f"\n文件: {file_path}")
    print(f"变量: {', '.join(variables) if variables else '无变量'}")

# 统计变量使用频率
variable_frequency = {}
for file_path, variables in all_variables.items():
    for var in variables:
        variable_frequency[var] = variable_frequency.get(var, 0) + 1

print("\n变量使用频率:")
sorted_vars = sorted(variable_frequency.items(), key=lambda x: x[1], reverse=True)
for var_name, count in sorted_vars:
    print(f"  {var_name}: {count} 次")
```

### 5. 高级命令文件操作

```python
import os
from typing import Dict, List, Any

class AdvancedCommandManager(CommandManager):
    """扩展的命令管理器"""
    
    def create_command_file(self, file_name: str, content: str) -> bool:
        """创建新的命令文件"""
        file_path = self.get_command_file_path(file_name)
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 命令文件已创建: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 创建命令文件失败: {e}")
            return False
    
    def update_command_file(self, file_name: str, content: str) -> bool:
        """更新现有命令文件"""
        command_file = self.read_command_file(file_name)
        if not command_file:
            print(f"❌ 命令文件不存在: {file_name}")
            return False
        
        return self.create_command_file(file_name, content)
    
    def delete_command_file(self, file_name: str) -> bool:
        """删除命令文件"""
        file_path = self.get_command_file_path(file_name)
        
        if not os.path.exists(file_path):
            print(f"❌ 命令文件不存在: {file_path}")
            return False
        
        try:
            os.remove(file_path)
            print(f"✅ 命令文件已删除: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 删除命令文件失败: {e}")
            return False
    
    def validate_template(self, file_name: str, variables: Dict[str, Any]) -> bool:
        """验证模板是否可以用给定变量成功渲染"""
        try:
            rendered = self.read_command_file_with_render(file_name, variables)
            return rendered is not None
        except Exception as e:
            print(f"❌ 模板验证失败: {e}")
            return False
    
    def get_missing_variables(self, file_name: str, provided_vars: Dict[str, Any]) -> List[str]:
        """获取缺失的必需变量"""
        analysis = self.analyze_command_file(file_name)
        if not analysis:
            return []
        
        missing = []
        for var in analysis.variables:
            if var.name not in provided_vars and not var.default_value:
                missing.append(var.name)
        
        return missing
    
    def generate_variable_template(self, file_name: str) -> Dict[str, Any]:
        """为命令文件生成变量模板"""
        analysis = self.analyze_command_file(file_name)
        if not analysis:
            return {}
        
        template = {}
        for var in analysis.variables:
            if var.default_value:
                # 尝试转换默认值类型
                try:
                    if var.default_value.lower() in ['true', 'false']:
                        template[var.name] = var.default_value.lower() == 'true'
                    elif var.default_value.isdigit():
                        template[var.name] = int(var.default_value)
                    else:
                        template[var.name] = var.default_value
                except:
                    template[var.name] = var.default_value
            else:
                template[var.name] = f"<请填写{var.description or var.name}>"
        
        return template

# 使用扩展管理器
advanced_manager = AdvancedCommandManager()

# 创建新的命令模板
new_template = """
{# @var: project_name, description: 项目名称 #}
{# @var: language, default: Python, description: 编程语言 #}
{# @var: framework, description: 使用的框架 #}
{# @var: include_tests, default: true, description: 是否包含测试 #}

# {{ project_name }} 项目

## 技术栈
- 语言: {{ language }}
- 框架: {{ framework }}

## 功能
{% if include_tests %}
- 包含单元测试
{% endif %}

## 开发指南
请按照 {{ language }} 的最佳实践进行开发。
"""

# 创建命令文件
advanced_manager.create_command_file("project_template.md", new_template)

# 生成变量模板
var_template = advanced_manager.generate_variable_template("project_template.md")
print("变量模板:")
for key, value in var_template.items():
    print(f"  {key}: {value}")

# 检查缺失变量
provided_vars = {"project_name": "MyApp", "language": "Python"}
missing = advanced_manager.get_missing_variables("project_template.md", provided_vars)
print(f"缺失变量: {missing}")

# 验证模板
complete_vars = {
    "project_name": "MyApp",
    "language": "Python", 
    "framework": "FastAPI",
    "include_tests": True
}
is_valid = advanced_manager.validate_template("project_template.md", complete_vars)
print(f"模板验证: {'通过' if is_valid else '失败'}")
```

## 数据模型详解

### 1. CommandFile 数据模型

```python
from autocoder.common.command_file_manager.models import CommandFile

# 创建命令文件对象
command_file = CommandFile(
    file_path="/path/to/commands/example.md",
    file_name="example.md",
    content="# Example Command\n\nHello {{ name }}!"
)

# 序列化和反序列化
file_dict = command_file.to_dict()
restored_file = CommandFile.from_dict(file_dict)

print(f"文件名: {command_file.file_name}")
print(f"路径: {command_file.file_path}")
print(f"内容: {command_file.content}")
```

### 2. JinjaVariable 数据模型

```python
from autocoder.common.command_file_manager.models import JinjaVariable

# 创建变量对象
variable = JinjaVariable(
    name="user_name",
    default_value="anonymous",
    description="用户名称"
)

# 序列化
var_dict = variable.to_dict()
restored_var = JinjaVariable.from_dict(var_dict)

print(f"变量名: {variable.name}")
print(f"默认值: {variable.default_value}")
print(f"描述: {variable.description}")
```

### 3. 分析结果处理

```python
from autocoder.common.command_file_manager.models import CommandFileAnalysisResult

# 处理分析结果
def process_analysis_result(result: CommandFileAnalysisResult):
    print(f"文件: {result.file_name}")
    print(f"变量数量: {len(result.variables)}")
    
    if result.variables:
        print("变量详情:")
        for var in result.variables:
            print(f"  - {var.name}")
            if var.default_value:
                print(f"    默认值: {var.default_value}")
            if var.description:
                print(f"    描述: {var.description}")
    
    print(f"原始变量集合: {result.raw_variables}")

# 使用示例
analysis = manager.analyze_command_file("example.md")
if analysis:
    process_analysis_result(analysis)
```

## 命令文件模板规范

### 1. 基本模板格式

```markdown
{# @var: variable_name, default: default_value, description: variable description #}

# {{ title }} 命令

## 描述
{{ description }}

## 参数
- 参数1: {{ param1 | default("默认值1") }}
- 参数2: {{ param2 | default("默认值2") }}

## 执行步骤
{% for step in steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

## 条件内容
{% if condition %}
这部分内容只在满足条件时显示
{% endif %}
```

### 2. 高级模板功能

```markdown
{# @var: project_type, default: web, description: 项目类型 #}
{# @var: features, description: 功能列表 #}
{# @var: use_database, default: true, description: 是否使用数据库 #}

# {{ project_type | title }} 项目开发指南

## 项目概述
这是一个 {{ project_type }} 项目。

## 功能列表
{% if features %}
{% for feature in features %}
- {{ feature }}
{% endfor %}
{% else %}
暂无功能定义
{% endif %}

## 技术选型
{% if project_type == "web" %}
- 前端: React/Vue.js
- 后端: Node.js/Python
{% elif project_type == "mobile" %}
- 移动端: React Native/Flutter
{% elif project_type == "desktop" %}
- 桌面应用: Electron/Qt
{% endif %}

{% if use_database %}
## 数据库设计
请根据项目需求设计数据库结构。
{% endif %}

## 开发流程
1. 需求分析
2. 架构设计
{% if use_database %}
3. 数据库设计
{% endif %}
4. 编码实现
5. 测试验证
6. 部署上线
```

### 3. 变量元数据注释规范

```markdown
{# 基本变量定义 #}
{# @var: name #}

{# 带默认值的变量 #}
{# @var: age, default: 18 #}

{# 带描述的变量 #}
{# @var: email, description: 用户邮箱地址 #}

{# 完整的变量定义 #}
{# @var: role, default: user, description: 用户角色 (admin/user/guest) #}

{# 复杂类型变量（通过描述说明） #}
{# @var: config, description: 配置对象，包含数据库连接信息 #}
{# @var: items, description: 项目列表，数组类型 #}
```

## 使用示例

### 完整的命令文件管理系统

```python
#!/usr/bin/env python3
"""
完整的命令文件管理系统示例
展示如何在 Auto-Coder 中集成命令文件管理
"""

import os
import json
from typing import Dict, List, Any
from autocoder.common.command_file_manager import CommandManager
from autocoder.common.command_file_manager.models import CommandFile, JinjaVariable

class CommandFileWorkflow:
    """命令文件工作流管理"""
    
    def __init__(self, commands_dir: str = None):
        self.manager = CommandManager(commands_dir)
        self.setup_default_templates()
    
    def setup_default_templates(self):
        """设置默认模板"""
        default_templates = {
            "task.md": """
{# @var: task_name, description: 任务名称 #}
{# @var: assignee, description: 负责人 #}
{# @var: priority, default: normal, description: 优先级 (low/normal/high) #}
{# @var: due_date, description: 截止日期 #}

# {{ task_name }}

**负责人**: {{ assignee }}  
**优先级**: {{ priority }}  
**截止日期**: {{ due_date }}

## 任务描述
请在此处描述任务的具体要求和目标。

## 验收标准
- [ ] 标准1
- [ ] 标准2
- [ ] 标准3
""",
            
            "api.md": """
{# @var: api_name, description: API名称 #}
{# @var: method, default: GET, description: HTTP方法 #}
{# @var: endpoint, description: API端点 #}
{# @var: auth_required, default: true, description: 是否需要认证 #}

# {{ api_name }} API

## 基本信息
- **方法**: {{ method }}
- **端点**: {{ endpoint }}
{% if auth_required %}
- **认证**: 需要
{% else %}
- **认证**: 不需要
{% endif %}

## 请求参数
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
|        |      |      |      |

## 响应格式
```json
{
  "status": "success",
  "data": {}
}
```

## 错误处理
- 400: 请求参数错误
- 401: 认证失败
- 500: 服务器内部错误
""",
            
            "feature.md": """
{# @var: feature_name, description: 功能名称 #}
{# @var: module, description: 所属模块 #}
{# @var: complexity, default: medium, description: 复杂度 (low/medium/high) #}
{# @var: dependencies, description: 依赖项 #}

# {{ feature_name }} 功能开发

## 功能概述
**所属模块**: {{ module }}  
**复杂度**: {{ complexity }}

## 技术依赖
{% if dependencies %}
{% for dep in dependencies %}
- {{ dep }}
{% endfor %}
{% else %}
无特殊依赖
{% endif %}

## 开发计划
1. 需求分析
2. 技术设计
3. 编码实现
4. 单元测试
5. 集成测试
6. 代码审查

## 测试用例
- [ ] 正常流程测试
- [ ] 异常流程测试
- [ ] 边界条件测试
"""
        }
        
        # 创建默认模板（如果不存在）
        for template_name, content in default_templates.items():
            file_path = self.manager.get_command_file_path(template_name)
            if not os.path.exists(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 创建默认模板: {template_name}")
    
    def list_templates(self):
        """列出所有可用模板"""
        result = self.manager.list_command_files()
        
        if result.success:
            print(f"📋 发现 {len(result.command_files)} 个命令模板:")
            for i, file_path in enumerate(result.command_files, 1):
                print(f"  {i}. {file_path}")
                
                # 显示模板变量
                analysis = self.manager.analyze_command_file(file_path)
                if analysis and analysis.variables:
                    print(f"     变量: {', '.join([v.name for v in analysis.variables])}")
                print()
        else:
            print("❌ 获取模板列表失败")
    
    def render_template(self, template_name: str, variables: Dict[str, Any] = None):
        """渲染模板"""
        if variables is None:
            # 交互式收集变量
            variables = self.collect_variables_interactively(template_name)
        
        if not variables:
            print("❌ 未提供变量，无法渲染模板")
            return None
        
        rendered = self.manager.read_command_file_with_render(template_name, variables)
        
        if rendered:
            print(f"✅ 模板 {template_name} 渲染成功:")
            print("=" * 50)
            print(rendered)
            print("=" * 50)
            return rendered
        else:
            print(f"❌ 模板 {template_name} 渲染失败")
            return None
    
    def collect_variables_interactively(self, template_name: str) -> Dict[str, Any]:
        """交互式收集变量值"""
        analysis = self.manager.analyze_command_file(template_name)
        if not analysis:
            print(f"❌ 无法分析模板 {template_name}")
            return {}
        
        print(f"📝 为模板 {template_name} 收集变量值:")
        variables = {}
        
        for var in analysis.variables:
            prompt = f"  {var.name}"
            if var.description:
                prompt += f" ({var.description})"
            if var.default_value:
                prompt += f" [默认: {var.default_value}]"
            prompt += ": "
            
            user_input = input(prompt).strip()
            
            if user_input:
                # 尝试类型转换
                if user_input.lower() in ['true', 'false']:
                    variables[var.name] = user_input.lower() == 'true'
                elif user_input.isdigit():
                    variables[var.name] = int(user_input)
                elif ',' in user_input:
                    # 假设是列表
                    variables[var.name] = [item.strip() for item in user_input.split(',')]
                else:
                    variables[var.name] = user_input
            elif var.default_value:
                # 使用默认值
                try:
                    if var.default_value.lower() in ['true', 'false']:
                        variables[var.name] = var.default_value.lower() == 'true'
                    elif var.default_value.isdigit():
                        variables[var.name] = int(var.default_value)
                    else:
                        variables[var.name] = var.default_value
                except:
                    variables[var.name] = var.default_value
        
        return variables
    
    def save_rendered_template(self, template_name: str, variables: Dict[str, Any], output_file: str):
        """保存渲染后的模板"""
        rendered = self.manager.read_command_file_with_render(template_name, variables)
        
        if rendered:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(rendered)
                print(f"✅ 渲染结果已保存到: {output_file}")
                return True
            except Exception as e:
                print(f"❌ 保存失败: {e}")
                return False
        else:
            print("❌ 渲染失败，无法保存")
            return False
    
    def interactive_session(self):
        """交互式会话"""
        print("🎯 Auto-Coder 命令文件管理系统")
        print("支持的命令: list, render, save, analyze, exit")
        
        while True:
            try:
                command = input("\ncommand-manager> ").strip().lower()
                
                if command == "exit":
                    break
                elif command == "list":
                    self.list_templates()
                elif command == "render":
                    template_name = input("模板名称: ").strip()
                    if template_name:
                        self.render_template(template_name)
                elif command == "save":
                    template_name = input("模板名称: ").strip()
                    output_file = input("输出文件: ").strip()
                    if template_name and output_file:
                        variables = self.collect_variables_interactively(template_name)
                        self.save_rendered_template(template_name, variables, output_file)
                elif command == "analyze":
                    template_name = input("模板名称: ").strip()
                    if template_name:
                        self.analyze_template(template_name)
                else:
                    print("未知命令，支持: list, render, save, analyze, exit")
                    
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
    
    def analyze_template(self, template_name: str):
        """分析模板"""
        analysis = self.manager.analyze_command_file(template_name)
        
        if analysis:
            print(f"📊 模板分析结果: {template_name}")
            print(f"变量数量: {len(analysis.variables)}")
            
            if analysis.variables:
                print("\n变量详情:")
                for var in analysis.variables:
                    print(f"  📌 {var.name}")
                    if var.default_value:
                        print(f"     默认值: {var.default_value}")
                    if var.description:
                        print(f"     描述: {var.description}")
                    print()
            
            print(f"原始变量集合: {analysis.raw_variables}")
        else:
            print(f"❌ 无法分析模板: {template_name}")

def main():
    """主程序"""
    import sys
    
    commands_dir = sys.argv[1] if len(sys.argv) > 1 else None
    
    workflow = CommandFileWorkflow(commands_dir)
    
    # 显示可用模板
    workflow.list_templates()
    
    # 启动交互式会话
    workflow.interactive_session()

if __name__ == "__main__":
    main()
```

## 验证命令

验证 command_file_manager 模块功能：

```bash
# 检查模块导入
python -c "
from autocoder.common.command_file_manager import CommandManager
from autocoder.common.command_file_manager.models import CommandFile, JinjaVariable
print('✅ 模块导入成功')
"

# 验证数据模型
python -c "
from autocoder.common.command_file_manager.models import CommandFile, JinjaVariable, CommandFileAnalysisResult
file = CommandFile('test.md', 'test.md', 'Hello {{ name }}!')
var = JinjaVariable('name', 'World', '用户名称')
print(f'✅ 数据模型正常: {file.file_name}, {var.name}')
"

# 验证管理器功能
python -c "
from autocoder.common.command_file_manager import CommandManager
import tempfile
import os

with tempfile.TemporaryDirectory() as temp_dir:
    manager = CommandManager(temp_dir)
    print('✅ 命令管理器创建成功')
    
    # 测试基本功能
    result = manager.list_command_files()
    print(f'✅ 列出命令文件正常: {len(result.command_files)} 个文件')
"

# 验证工具函数
python -c "
from autocoder.common.command_file_manager.utils import extract_jinja2_variables, is_command_file

content = 'Hello {{ name }}! Your age is {{ age }}.'
variables = extract_jinja2_variables(content)
print(f'✅ 变量提取正常: {variables}')

is_cmd = is_command_file('test.md')
print(f'✅ 文件检查正常: {is_cmd}')
"

# 验证 Jinja2 渲染
python -c "
from byzerllm.utils import format_str_jinja2

template = 'Hello {{ name }}!'
rendered = format_str_jinja2(template, name='World')
print(f'✅ Jinja2 渲染正常: {rendered}')
"

# 检查依赖关系
python -c "
import loguru
from byzerllm.utils import format_str_jinja2
print('✅ 所有依赖模块可用')
"
```

通过这些验证命令可以确认 command_file_manager 模块的完整性和功能正确性。 