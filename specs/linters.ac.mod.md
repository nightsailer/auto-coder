# linters.ac.mod.md

## 模块概述

`linters` 模块是 Auto-Coder 系统的代码质量检查核心，提供对多种编程语言的静态代码分析、错误检测、风格检查和自动修复功能。该模块支持 Python、JavaScript/TypeScript、React、Vue 等主流技术栈，通过统一的接口为 AI 编程助手提供代码质量保障和最佳实践建议。

**模块类型**: 包模块  
**主要功能**: 多语言代码检查、静态分析、自动修复、质量报告  
**依赖关系**: 依赖外部工具如 pylint、eslint、flake8 等

## 核心组件

### 1. 数据模型层 (models.py)
- **LintIssue**: 单个代码问题的表示，包含位置、严重性、消息等
- **FileLintResult**: 单个文件的检查结果
- **ProjectLintResult**: 整个项目的检查结果汇总
- **IssuePosition**: 问题在文件中的位置信息
- **IssueSeverity**: 问题严重性枚举（ERROR、WARNING、INFO、HINT）

### 2. 基础框架 (base_linter.py)
- **BaseLinter**: 所有语言特定 linter 的抽象基类
- 定义统一的接口和通用功能
- 支持文件类型检测和扩展名匹配

### 3. 语言特定实现
- **PythonLinter**: Python 代码检查器，基于 pylint 和 flake8
- **ReactJSLinter**: React/JavaScript/TypeScript 检查器，基于 ESLint
- **VueLinter**: Vue.js 代码检查器，基于 ESLint 和 Vue 特定规则

### 4. 工厂和管理器
- **LinterFactory**: 根据语言或文件类型创建合适的 linter
- **NormalLinter**: 项目级别的代码检查管理器
- **ShadowLinter**: 影子系统集成的代码检查器

## 主要功能

### 1. 基础代码检查

```python
from autocoder.linters.linter_factory import LinterFactory
from autocoder.linters.models import FileLintResult

# 自动检测并检查单个文件
result = LinterFactory.lint_file(
    file_path="src/main.py",
    fix=False,  # 是否自动修复
    verbose=True
)

if result and result['success']:
    print(f"检查完成: {result['language']}")
    print(f"发现 {result['error_count']} 个错误")
    print(f"发现 {result['warning_count']} 个警告")
    
    for issue in result['issues']:
        print(f"  {issue['file']}:{issue['line']} - {issue['message']}")
else:
    print(f"检查失败: {result.get('error', '未知错误')}")
```

### 2. 项目级别检查

```python
from autocoder.linters.normal_linter import NormalLinter

# 创建项目检查器
linter = NormalLinter(
    project_dir="/path/to/project",
    verbose=True
)

# 检查单个文件
file_result = linter.lint_file("src/utils.py", fix=False)
print(file_result.to_str())

# 检查整个项目
project_result = linter.lint_all_files(fix=False)
print(f"项目检查结果:")
print(f"  总文件数: {project_result.total_files}")
print(f"  有问题的文件: {project_result.files_with_issues}")
print(f"  总问题数: {project_result.total_issues}")

# 生成详细报告
report = project_result.to_str(
    include_all_files=False,  # 只显示有问题的文件
    include_issues=True       # 包含问题详情
)
print(report)
```

### 3. Python 代码检查

```python
from autocoder.linters.python_linter import PythonLinter

# 创建 Python 检查器
python_linter = PythonLinter(verbose=True)

# 检查 Python 文件
result = python_linter.lint_file("script.py", fix=False)

print("Python 代码检查结果:")
print(f"  语言: {result['language']}")
print(f"  成功: {result['success']}")

if result['success']:
    print(f"  错误数: {result['error_count']}")
    print(f"  警告数: {result['warning_count']}")
    
    # 显示具体问题
    for issue in result['issues']:
        severity = issue['severity'].upper()
        print(f"  [{severity}] {issue['file']}:{issue['line']} - {issue['message']}")
        if issue.get('rule'):
            print(f"    规则: {issue['rule']}")

# 检查整个 Python 项目
project_result = python_linter.lint_project("/path/to/python/project", fix=False)
print(f"\n项目检查: 分析了 {project_result['files_analyzed']} 个文件")
```

### 4. React/JavaScript 代码检查

```python
from autocoder.linters.reactjs_linter import ReactJSLinter

# 创建 React 检查器
react_linter = ReactJSLinter(verbose=True)

# 检查 React 组件
result = react_linter.lint_file("src/components/Button.jsx", fix=False)

print("React 代码检查结果:")
if result['success']:
    print(f"  框架: {result['framework']}")
    print(f"  分析文件数: {result['files_analyzed']}")
    
    for issue in result['issues']:
        print(f"  {issue['file']}:{issue['line']}:{issue['column']}")
        print(f"    {issue['severity']}: {issue['message']}")
        if issue.get('ruleId'):
            print(f"    规则: {issue['ruleId']}")

# 检查整个 React 项目
project_result = react_linter.lint_project("/path/to/react/project", fix=True)
print(f"项目检查完成，自动修复了一些问题")
```

### 5. Vue.js 代码检查

```python
from autocoder.linters.vue_linter import VueLinter

# 创建 Vue 检查器
vue_linter = VueLinter(verbose=True)

# 检查 Vue 单文件组件
result = vue_linter.lint_file("src/components/HelloWorld.vue", fix=False)

print("Vue 代码检查结果:")
if result['success']:
    print(f"  框架: {result['framework']}")
    
    for issue in result['issues']:
        print(f"  {issue['file']}:{issue['line']} - {issue['message']}")
        print(f"    严重性: {issue['severity']}")

# 检查 Vue 项目
project_result = vue_linter.lint_project("/path/to/vue/project", fix=False)
print(f"Vue 项目检查: {project_result['files_analyzed']} 个文件")
```

### 6. 自动修复功能

```python
# 启用自动修复的代码检查
def lint_and_fix_project(project_path: str, language: str = None):
    """检查项目并自动修复可修复的问题"""
    
    # 使用工厂创建合适的 linter
    linter = LinterFactory.create_linter(language=language, verbose=True)
    
    if not linter:
        print(f"不支持的语言: {language}")
        return
    
    print(f"开始检查和修复项目: {project_path}")
    
    # 执行检查和修复
    result = linter.lint_project(project_path, fix=True)
    
    if result['success']:
        print("检查和修复完成:")
        print(f"  分析文件数: {result['files_analyzed']}")
        print(f"  错误数: {result['error_count']}")
        print(f"  警告数: {result['warning_count']}")
        
        if result.get('fixed_issues_count', 0) > 0:
            print(f"  自动修复: {result['fixed_issues_count']} 个问题")
        
        # 显示剩余问题
        remaining_issues = [issue for issue in result['issues'] 
                          if not issue.get('fixable', False)]
        
        if remaining_issues:
            print(f"\n剩余 {len(remaining_issues)} 个需要手动修复的问题:")
            for issue in remaining_issues[:10]:  # 只显示前10个
                print(f"  {issue['file']}:{issue['line']} - {issue['message']}")
    else:
        print(f"检查失败: {result.get('error', '未知错误')}")

# 使用示例
lint_and_fix_project("/path/to/python/project", "python")
lint_and_fix_project("/path/to/react/project", "react")
```

### 7. 高级检查配置和过滤

```python
class AdvancedLintManager:
    """高级代码检查管理器"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.linter = NormalLinter(project_dir, verbose=True)
        self.config = {
            "severity_filter": ["error", "warning"],  # 只关注错误和警告
            "exclude_patterns": [
                "*/node_modules/*",
                "*/venv/*", 
                "*/__pycache__/*",
                "*.min.js"
            ],
            "max_issues_per_file": 50,
            "auto_fix_safe_rules": [
                "missing-final-newline",
                "trailing-whitespace", 
                "indent"
            ]
        }
    
    def lint_with_filters(self, fix: bool = False) -> dict:
        """带过滤器的代码检查"""
        print("开始高级代码检查...")
        
        # 执行项目检查
        result = self.linter.lint_all_files(fix=fix)
        
        # 应用过滤器
        filtered_result = self._apply_filters(result)
        
        # 生成报告
        report = self._generate_advanced_report(filtered_result)
        
        return {
            "original_result": result,
            "filtered_result": filtered_result,
            "report": report
        }
    
    def _apply_filters(self, result):
        """应用过滤器"""
        filtered_files = {}
        
        for file_path, file_result in result.file_results.items():
            # 检查排除模式
            if self._should_exclude_file(file_path):
                continue
            
            # 过滤问题严重性
            filtered_issues = [
                issue for issue in file_result.issues
                if issue.severity.value in self.config["severity_filter"]
            ]
            
            # 限制每个文件的问题数量
            if len(filtered_issues) > self.config["max_issues_per_file"]:
                filtered_issues = filtered_issues[:self.config["max_issues_per_file"]]
            
            if filtered_issues:  # 只保留有问题的文件
                # 创建新的文件结果
                filtered_file_result = FileLintResult(
                    file_path=file_result.file_path,
                    success=file_result.success,
                    language=file_result.language,
                    issues=filtered_issues,
                    error_count=sum(1 for i in filtered_issues if i.severity.value == "error"),
                    warning_count=sum(1 for i in filtered_issues if i.severity.value == "warning"),
                    info_count=sum(1 for i in filtered_issues if i.severity.value == "info")
                )
                filtered_files[file_path] = filtered_file_result
        
        # 创建过滤后的项目结果
        total_issues = sum(len(fr.issues) for fr in filtered_files.values())
        total_errors = sum(fr.error_count for fr in filtered_files.values())
        total_warnings = sum(fr.warning_count for fr in filtered_files.values())
        
        filtered_project_result = ProjectLintResult(
            project_path=result.project_path,
            file_results=filtered_files,
            total_files=len(filtered_files),
            files_with_issues=len(filtered_files),
            total_issues=total_issues,
            total_errors=total_errors,
            total_warnings=total_warnings,
            success=True
        )
        
        return filtered_project_result
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """检查文件是否应该被排除"""
        import fnmatch
        
        for pattern in self.config["exclude_patterns"]:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False
    
    def _generate_advanced_report(self, result) -> str:
        """生成高级报告"""
        report_lines = [
            "# 代码质量检查报告",
            f"**项目路径**: {result.project_path}",
            f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 摘要",
            f"- 检查文件数: {result.total_files}",
            f"- 有问题的文件: {result.files_with_issues}",
            f"- 总问题数: {result.total_issues}",
            f"- 错误: {result.total_errors}",
            f"- 警告: {result.total_warnings}",
            ""
        ]
        
        # 按严重性分组问题
        if result.total_issues > 0:
            report_lines.extend([
                "## 问题分布",
                f"- 错误占比: {result.total_errors/result.total_issues*100:.1f}%",
                f"- 警告占比: {result.total_warnings/result.total_issues*100:.1f}%",
                ""
            ])
            
            # 最严重的文件
            files_by_issues = sorted(
                result.file_results.items(),
                key=lambda x: len(x[1].issues),
                reverse=True
            )
            
            report_lines.extend([
                "## 问题最多的文件 (Top 10)",
                ""
            ])
            
            for file_path, file_result in files_by_issues[:10]:
                issue_count = len(file_result.issues)
                report_lines.append(
                    f"- `{file_path}`: {issue_count} 个问题 "
                    f"({file_result.error_count} 错误, {file_result.warning_count} 警告)"
                )
            
            report_lines.append("")
            
            # 常见问题规则
            rule_counts = {}
            for file_result in result.file_results.values():
                for issue in file_result.issues:
                    rule = issue.rule_name or "unknown"
                    rule_counts[rule] = rule_counts.get(rule, 0) + 1
            
            if rule_counts:
                top_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                
                report_lines.extend([
                    "## 最常见的问题规则 (Top 10)",
                    ""
                ])
                
                for rule, count in top_rules:
                    report_lines.append(f"- `{rule}`: {count} 次")
                
                report_lines.append("")
        
        # 建议
        report_lines.extend([
            "## 改进建议",
            ""
        ])
        
        if result.total_errors > 0:
            report_lines.append("- 🔴 优先修复所有错误级别的问题")
        
        if result.total_warnings > result.total_errors * 2:
            report_lines.append("- 🟡 警告数量较多，建议逐步清理")
        
        if result.files_with_issues / result.total_files > 0.5:
            report_lines.append("- 📋 超过一半的文件存在问题，建议制定代码规范")
        
        return "\n".join(report_lines)
    
    def generate_fix_script(self, result) -> str:
        """生成自动修复脚本"""
        script_lines = [
            "#!/bin/bash",
            "# 自动生成的代码修复脚本",
            f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "echo '开始自动修复代码问题...'",
            ""
        ]
        
        # 按语言分组文件
        files_by_language = {}
        for file_path, file_result in result.file_results.items():
            lang = file_result.language
            if lang not in files_by_language:
                files_by_language[lang] = []
            files_by_language[lang].append(file_path)
        
        # 为每种语言生成修复命令
        for language, files in files_by_language.items():
            script_lines.append(f"# 修复 {language} 文件")
            
            if language == "python":
                script_lines.extend([
                    "echo '修复 Python 文件...'",
                    f"python -m black {' '.join(files)}",
                    f"python -m isort {' '.join(files)}",
                    ""
                ])
            elif language in ["javascript", "typescript", "react"]:
                script_lines.extend([
                    f"echo '修复 {language} 文件...'",
                    f"npx eslint --fix {' '.join(files)}",
                    f"npx prettier --write {' '.join(files)}",
                    ""
                ])
            elif language == "vue":
                script_lines.extend([
                    "echo '修复 Vue 文件...'",
                    f"npx eslint --fix {' '.join(files)}",
                    ""
                ])
        
        script_lines.extend([
            "echo '自动修复完成!'",
            "echo '请检查修复结果并重新运行代码检查。'"
        ])
        
        return "\n".join(script_lines)

# 使用高级检查管理器
manager = AdvancedLintManager("/path/to/project")

# 执行高级检查
result = manager.lint_with_filters(fix=False)

# 显示报告
print(result["report"])

# 生成修复脚本
fix_script = manager.generate_fix_script(result["filtered_result"])
with open("fix_issues.sh", "w") as f:
    f.write(fix_script)

print("修复脚本已生成: fix_issues.sh")
```

## 数据模型详解

### 1. 问题严重性级别

```python
from autocoder.linters.models import IssueSeverity

# 严重性级别
severity_levels = {
    IssueSeverity.ERROR: "错误 - 必须修复",
    IssueSeverity.WARNING: "警告 - 建议修复", 
    IssueSeverity.INFO: "信息 - 可选修复",
    IssueSeverity.HINT: "提示 - 改进建议"
}

for level, description in severity_levels.items():
    print(f"{level.value}: {description}")
```

### 2. 问题位置信息

```python
from autocoder.linters.models import IssuePosition

# 创建位置信息
position = IssuePosition(
    line=42,
    column=15,
    end_line=42,
    end_column=25
)

print(f"问题位置: {position.to_str()}")
# 输出: 问题位置: 第 42 行，第 15 列 到第 42 行，第 25 列
```

### 3. 完整的问题对象

```python
from autocoder.linters.models import LintIssue, IssuePosition, IssueSeverity

# 创建完整的问题对象
issue = LintIssue(
    code="E302",
    message="expected 2 blank lines, found 1",
    severity=IssueSeverity.ERROR,
    position=IssuePosition(line=10, column=1),
    file_path="src/main.py",
    rule_name="blank-lines",
    source="def function():",
    fix_available=True,
    fix_description="添加一个空行"
)

# 格式化输出
print(issue.to_str())
```

### 4. 文件和项目结果

```python
from autocoder.linters.models import FileLintResult, ProjectLintResult

# 创建文件结果
file_result = FileLintResult(
    file_path="src/utils.py",
    success=True,
    language="python",
    issues=[issue],  # 使用上面创建的问题
    error_count=1,
    warning_count=0,
    info_count=0,
    execution_time_ms=150
)

# 创建项目结果
project_result = ProjectLintResult(
    project_path="/path/to/project",
    file_results={"src/utils.py": file_result},
    total_files=1,
    files_with_issues=1,
    total_issues=1,
    total_errors=1,
    total_warnings=0,
    success=True
)

# 生成报告
print(project_result.to_str(include_all_files=True, include_issues=True))
```

## 与 Auto-Coder 系统集成

### 1. 在代码生成后自动检查

```python
from autocoder.linters.shadow_linter import ShadowLinter
from autocoder.shadows.shadow_manager import ShadowManager

# 创建影子系统 linter
shadow_manager = ShadowManager("/path/to/project", "events.json")
shadow_linter = ShadowLinter(shadow_manager, verbose=True)

# 在代码生成后自动检查
def lint_generated_code(generated_files: list) -> dict:
    """对生成的代码进行自动检查"""
    
    lint_results = {}
    
    for file_path in generated_files:
        print(f"检查生成的文件: {file_path}")
        
        # 使用影子系统检查
        result = shadow_linter.lint_file(file_path, fix=False)
        
        if result and result.success:
            lint_results[file_path] = result
            
            if result.total_issues > 0:
                print(f"  发现 {result.total_issues} 个问题")
                
                # 显示严重问题
                for issue in result.issues:
                    if issue.severity == IssueSeverity.ERROR:
                        print(f"    错误: {issue.message} (第{issue.position.line}行)")
            else:
                print("  ✅ 无问题")
        else:
            print(f"  ❌ 检查失败: {result.error if result else '未知错误'}")
    
    return lint_results

# 使用示例
generated_files = ["src/new_feature.py", "src/utils/helper.py"]
results = lint_generated_code(generated_files)
```

### 2. 代码质量门禁

```python
class CodeQualityGate:
    """代码质量门禁"""
    
    def __init__(self, project_dir: str):
        self.linter = NormalLinter(project_dir, verbose=False)
        self.thresholds = {
            "max_errors": 0,           # 最大错误数
            "max_warnings": 10,        # 最大警告数
            "max_issues_per_file": 20, # 每个文件最大问题数
            "min_pass_rate": 0.8       # 最小通过率
        }
    
    def check_quality_gate(self, file_paths: list = None) -> dict:
        """检查代码质量门禁"""
        
        if file_paths:
            # 检查指定文件
            results = {}
            for file_path in file_paths:
                results[file_path] = self.linter.lint_file(file_path)
            
            # 创建项目结果
            total_issues = sum(len(r.issues) for r in results.values())
            total_errors = sum(r.error_count for r in results.values())
            total_warnings = sum(r.warning_count for r in results.values())
            
            project_result = ProjectLintResult(
                file_results=results,
                total_files=len(results),
                files_with_issues=sum(1 for r in results.values() if len(r.issues) > 0),
                total_issues=total_issues,
                total_errors=total_errors,
                total_warnings=total_warnings,
                success=True
            )
        else:
            # 检查整个项目
            project_result = self.linter.lint_all_files()
        
        # 评估质量门禁
        gate_result = self._evaluate_gate(project_result)
        
        return {
            "passed": gate_result["passed"],
            "score": gate_result["score"],
            "violations": gate_result["violations"],
            "project_result": project_result,
            "recommendations": gate_result["recommendations"]
        }
    
    def _evaluate_gate(self, result: ProjectLintResult) -> dict:
        """评估质量门禁"""
        violations = []
        score = 100
        
        # 检查错误数
        if result.total_errors > self.thresholds["max_errors"]:
            violations.append(f"错误数超限: {result.total_errors} > {self.thresholds['max_errors']}")
            score -= result.total_errors * 10
        
        # 检查警告数
        if result.total_warnings > self.thresholds["max_warnings"]:
            violations.append(f"警告数超限: {result.total_warnings} > {self.thresholds['max_warnings']}")
            score -= (result.total_warnings - self.thresholds["max_warnings"]) * 2
        
        # 检查每个文件的问题数
        files_over_limit = [
            file_path for file_path, file_result in result.file_results.items()
            if len(file_result.issues) > self.thresholds["max_issues_per_file"]
        ]
        
        if files_over_limit:
            violations.append(f"{len(files_over_limit)} 个文件问题数超限")
            score -= len(files_over_limit) * 5
        
        # 检查通过率
        if result.total_files > 0:
            pass_rate = (result.total_files - result.files_with_issues) / result.total_files
            if pass_rate < self.thresholds["min_pass_rate"]:
                violations.append(f"通过率过低: {pass_rate:.1%} < {self.thresholds['min_pass_rate']:.1%}")
                score -= (self.thresholds["min_pass_rate"] - pass_rate) * 50
        
        # 确保分数不为负
        score = max(0, score)
        
        # 生成建议
        recommendations = self._generate_recommendations(result, violations)
        
        return {
            "passed": len(violations) == 0,
            "score": score,
            "violations": violations,
            "recommendations": recommendations
        }
    
    def _generate_recommendations(self, result: ProjectLintResult, violations: list) -> list:
        """生成改进建议"""
        recommendations = []
        
        if result.total_errors > 0:
            recommendations.append("优先修复所有错误级别的问题")
        
        if result.total_warnings > result.total_errors * 3:
            recommendations.append("警告数量过多，建议逐步清理")
        
        if result.files_with_issues / result.total_files > 0.6:
            recommendations.append("建议建立代码规范和自动化检查流程")
        
        # 基于常见问题生成建议
        rule_counts = {}
        for file_result in result.file_results.values():
            for issue in file_result.issues:
                rule = issue.rule_name or "unknown"
                rule_counts[rule] = rule_counts.get(rule, 0) + 1
        
        if rule_counts:
            top_rule = max(rule_counts.items(), key=lambda x: x[1])
            if top_rule[1] > 5:
                recommendations.append(f"重点关注 '{top_rule[0]}' 规则，出现了 {top_rule[1]} 次")
        
        return recommendations

# 使用质量门禁
gate = CodeQualityGate("/path/to/project")

# 检查特定文件
result = gate.check_quality_gate(["src/main.py", "src/utils.py"])

print(f"质量门禁: {'✅ 通过' if result['passed'] else '❌ 未通过'}")
print(f"质量分数: {result['score']}/100")

if result['violations']:
    print("违规项目:")
    for violation in result['violations']:
        print(f"  - {violation}")

if result['recommendations']:
    print("改进建议:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
```

## 使用示例

### 完整的代码质量检查工作流

```python
#!/usr/bin/env python3
"""
完整的代码质量检查工作流示例
展示如何在 Auto-Coder 中集成代码检查功能
"""

import os
import json
from datetime import datetime
from autocoder.linters.normal_linter import NormalLinter
from autocoder.linters.linter_factory import LinterFactory
from autocoder.linters.models import IssueSeverity

class CodeQualityWorkflow:
    """代码质量检查工作流"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.linter = NormalLinter(project_dir, verbose=True)
        self.report_dir = os.path.join(project_dir, ".auto-coder", "lint-reports")
        
        # 确保报告目录存在
        os.makedirs(self.report_dir, exist_ok=True)
    
    def run_full_check(self, fix: bool = False) -> dict:
        """运行完整的代码质量检查"""
        print("🔍 开始代码质量检查...")
        
        start_time = datetime.now()
        
        # 执行检查
        result = self.linter.lint_all_files(fix=fix)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 生成报告
        report_data = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "project_path": self.project_dir,
            "summary": {
                "total_files": result.total_files,
                "files_with_issues": result.files_with_issues,
                "total_issues": result.total_issues,
                "total_errors": result.total_errors,
                "total_warnings": result.total_warnings,
                "success": result.success
            },
            "files": {}
        }
        
        # 处理文件结果
        for file_path, file_result in result.file_results.items():
            report_data["files"][file_path] = {
                "language": file_result.language,
                "issue_count": len(file_result.issues),
                "error_count": file_result.error_count,
                "warning_count": file_result.warning_count,
                "execution_time_ms": file_result.execution_time_ms,
                "issues": [
                    {
                        "code": issue.code,
                        "message": issue.message,
                        "severity": issue.severity.value,
                        "line": issue.position.line,
                        "column": issue.position.column,
                        "rule_name": issue.rule_name
                    }
                    for issue in file_result.issues
                ]
            }
        
        # 保存报告
        report_file = os.path.join(
            self.report_dir, 
            f"lint-report-{start_time.strftime('%Y%m%d-%H%M%S')}.json"
        )
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 检查完成 (耗时: {duration:.2f}s)")
        print(f"📊 报告已保存: {report_file}")
        
        return {
            "result": result,
            "report_data": report_data,
            "report_file": report_file
        }
    
    def check_specific_files(self, file_patterns: list, fix: bool = False) -> dict:
        """检查特定文件模式"""
        import glob
        
        files_to_check = []
        for pattern in file_patterns:
            matching_files = glob.glob(os.path.join(self.project_dir, pattern), recursive=True)
            files_to_check.extend(matching_files)
        
        # 去重并过滤
        files_to_check = list(set(files_to_check))
        files_to_check = [f for f in files_to_check if os.path.isfile(f)]
        
        print(f"🎯 检查 {len(files_to_check)} 个匹配的文件...")
        
        results = {}
        for file_path in files_to_check:
            rel_path = os.path.relpath(file_path, self.project_dir)
            result = self.linter.lint_file(file_path, fix=fix)
            results[rel_path] = result
            
            if result.success:
                issue_count = len(result.issues)
                if issue_count > 0:
                    print(f"  📄 {rel_path}: {issue_count} 个问题")
                else:
                    print(f"  ✅ {rel_path}: 无问题")
            else:
                print(f"  ❌ {rel_path}: 检查失败")
        
        return results
    
    def generate_html_report(self, report_data: dict) -> str:
        """生成 HTML 格式的报告"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>代码质量检查报告</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .metric { background: white; padding: 15px; border: 1px solid #ddd; border-radius: 5px; flex: 1; }
        .metric h3 { margin: 0 0 10px 0; color: #333; }
        .metric .value { font-size: 24px; font-weight: bold; }
        .error { color: #d32f2f; }
        .warning { color: #f57c00; }
        .info { color: #1976d2; }
        .file-list { margin: 20px 0; }
        .file-item { margin: 10px 0; padding: 10px; border: 1px solid #eee; border-radius: 3px; }
        .file-header { font-weight: bold; margin-bottom: 5px; }
        .issue-list { margin-left: 20px; }
        .issue { margin: 5px 0; padding: 5px; background: #f9f9f9; border-radius: 3px; }
        .no-issues { color: #4caf50; font-style: italic; }
    </style>
</head>
<body>
    <div class="header">
        <h1>代码质量检查报告</h1>
        <p><strong>项目:</strong> {project_path}</p>
        <p><strong>检查时间:</strong> {timestamp}</p>
        <p><strong>耗时:</strong> {duration:.2f} 秒</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>文件统计</h3>
            <div class="value">{total_files}</div>
            <div>总文件数</div>
        </div>
        <div class="metric">
            <h3>问题文件</h3>
            <div class="value">{files_with_issues}</div>
            <div>有问题的文件</div>
        </div>
        <div class="metric">
            <h3>总问题数</h3>
            <div class="value">{total_issues}</div>
            <div>所有问题</div>
        </div>
        <div class="metric error">
            <h3>错误</h3>
            <div class="value">{total_errors}</div>
            <div>必须修复</div>
        </div>
        <div class="metric warning">
            <h3>警告</h3>
            <div class="value">{total_warnings}</div>
            <div>建议修复</div>
        </div>
    </div>
    
    <div class="file-list">
        <h2>文件详情</h2>
        {file_details}
    </div>
</body>
</html>
"""
        
        # 生成文件详情
        file_details = []
        for file_path, file_info in report_data["files"].items():
            if file_info["issue_count"] > 0:
                issues_html = []
                for issue in file_info["issues"]:
                    severity_class = issue["severity"]
                    issues_html.append(f"""
                    <div class="issue {severity_class}">
                        <strong>第{issue["line"]}行:</strong> {issue["message"]}
                        {f'<em>({issue["rule_name"]})</em>' if issue["rule_name"] else ''}
                    </div>
                    """)
                
                file_details.append(f"""
                <div class="file-item">
                    <div class="file-header">
                        📄 {file_path} 
                        <span class="error">({file_info["error_count"]} 错误)</span>
                        <span class="warning">({file_info["warning_count"]} 警告)</span>
                    </div>
                    <div class="issue-list">
                        {''.join(issues_html)}
                    </div>
                </div>
                """)
            else:
                file_details.append(f"""
                <div class="file-item">
                    <div class="file-header">✅ {file_path}</div>
                    <div class="no-issues">无问题发现</div>
                </div>
                """)
        
        # 格式化 HTML
        html_content = html_template.format(
            project_path=report_data["project_path"],
            timestamp=report_data["timestamp"],
            duration=report_data["duration_seconds"],
            total_files=report_data["summary"]["total_files"],
            files_with_issues=report_data["summary"]["files_with_issues"],
            total_issues=report_data["summary"]["total_issues"],
            total_errors=report_data["summary"]["total_errors"],
            total_warnings=report_data["summary"]["total_warnings"],
            file_details=''.join(file_details)
        )
        
        # 保存 HTML 报告
        html_file = os.path.join(
            self.report_dir,
            f"lint-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
        )
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file
    
    def interactive_fix_session(self):
        """交互式修复会话"""
        print("🛠️  交互式代码修复会话")
        print("支持的命令: check, fix, status, exit")
        
        while True:
            try:
                command = input("\nlint> ").strip().lower()
                
                if command == "exit":
                    break
                elif command == "check":
                    result = self.run_full_check(fix=False)
                    summary = result["report_data"]["summary"]
                    print(f"检查结果: {summary['total_issues']} 个问题 "
                          f"({summary['total_errors']} 错误, {summary['total_warnings']} 警告)")
                
                elif command == "fix":
                    confirm = input("确认自动修复可修复的问题? (y/N): ").strip().lower()
                    if confirm == 'y':
                        result = self.run_full_check(fix=True)
                        print("自动修复完成，请重新检查代码")
                
                elif command == "status":
                    # 显示最新报告摘要
                    report_files = glob.glob(os.path.join(self.report_dir, "lint-report-*.json"))
                    if report_files:
                        latest_report = max(report_files, key=os.path.getctime)
                        with open(latest_report, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        summary = data["summary"]
                        print(f"最新检查状态:")
                        print(f"  文件数: {summary['total_files']}")
                        print(f"  问题数: {summary['total_issues']}")
                        print(f"  错误: {summary['total_errors']}")
                        print(f"  警告: {summary['total_warnings']}")
                    else:
                        print("暂无检查报告")
                
                else:
                    print("未知命令，支持: check, fix, status, exit")
                    
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

def main():
    """主程序"""
    import sys
    import glob
    
    if len(sys.argv) < 2:
        print("用法: python lint_workflow.py <项目目录> [命令]")
        return
    
    project_dir = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "check"
    
    if not os.path.exists(project_dir):
        print(f"❌ 项目目录不存在: {project_dir}")
        return
    
    workflow = CodeQualityWorkflow(project_dir)
    
    if command == "check":
        # 执行检查
        result = workflow.run_full_check(fix=False)
        
        # 生成 HTML 报告
        html_file = workflow.generate_html_report(result["report_data"])
        print(f"📊 HTML 报告: {html_file}")
        
    elif command == "fix":
        # 执行修复
        result = workflow.run_full_check(fix=True)
        print("自动修复完成")
        
    elif command == "interactive":
        # 交互式会话
        workflow.interactive_fix_session()
        
    elif command.startswith("files:"):
        # 检查特定文件
        patterns = command[6:].split(",")
        results = workflow.check_specific_files(patterns, fix=False)
        print(f"检查了 {len(results)} 个文件")
        
    else:
        print(f"未知命令: {command}")
        print("支持的命令: check, fix, interactive, files:<pattern1>,<pattern2>")

if __name__ == "__main__":
    main()
```

## 验证命令

验证 linters 模块功能：

```bash
# 检查模块导入
python -c "
from autocoder.linters.linter_factory import LinterFactory
from autocoder.linters.models import LintIssue, FileLintResult, ProjectLintResult
from autocoder.linters.normal_linter import NormalLinter
print('✅ 模块导入成功')
"

# 验证数据模型
python -c "
from autocoder.linters.models import LintIssue, IssuePosition, IssueSeverity
position = IssuePosition(line=10, column=5)
issue = LintIssue(
    code='E302', 
    message='测试问题', 
    severity=IssueSeverity.ERROR,
    position=position,
    file_path='test.py'
)
print(f'✅ 数据模型正常: {issue.code} - {issue.message}')
"

# 验证 linter 工厂
python -c "
from autocoder.linters.linter_factory import LinterFactory
languages = LinterFactory.get_supported_languages()
print(f'✅ 支持的语言: {languages}')

# 测试创建 linter
python_linter = LinterFactory.create_linter(language='python')
if python_linter:
    print('✅ Python linter 创建成功')
"

# 验证特定语言 linter
python -c "
from autocoder.linters.python_linter import PythonLinter
from autocoder.linters.reactjs_linter import ReactJSLinter
from autocoder.linters.vue_linter import VueLinter

py_linter = PythonLinter()
js_linter = ReactJSLinter()
vue_linter = VueLinter()

print(f'✅ Python 支持扩展名: {py_linter.get_supported_extensions()}')
print(f'✅ React 支持扩展名: {js_linter.get_supported_extensions()}')
print(f'✅ Vue 支持扩展名: {vue_linter.get_supported_extensions()}')
"

# 验证项目 linter
python -c "
from autocoder.linters.normal_linter import NormalLinter
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    linter = NormalLinter(temp_dir, verbose=False)
    print('✅ 项目 linter 创建成功')
"

# 检查依赖工具（可选）
python -c "
import subprocess
import sys

tools = ['python', 'node', 'npm']
for tool in tools:
    try:
        subprocess.run([tool, '--version'], check=True, capture_output=True)
        print(f'✅ {tool} 可用')
    except:
        print(f'⚠️  {tool} 不可用（某些功能可能受限）')
"
```

通过这些验证命令可以确认 linters 模块的完整性和功能正确性。 