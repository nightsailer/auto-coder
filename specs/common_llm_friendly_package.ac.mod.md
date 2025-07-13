# common.llm_friendly_package.ac.mod.md

## 模块概述

`common.llm_friendly_package` 模块是 Auto-Coder 系统的 LLM 友好包管理核心，提供对第三方库文档的统一管理、获取和集成功能。该模块通过 Git 仓库管理机制，为 LLM 提供结构化的第三方库文档，帮助 AI 更好地理解和使用各种编程库，提升代码生成的准确性和实用性。

**模块类型**: 单文件模块 (`src/autocoder/common/llm_friendly_package.py`)  
**主要功能**: 第三方库管理、文档获取、Git 仓库同步、库浏览  
**依赖关系**: 依赖 `rich`、`git`、`filelock` 等模块

## 核心组件

### 1. 数据模型
- **LibraryInfo**: 库信息数据类，包含域名、用户名、库名等信息
- **PackageDoc**: 包文档数据类，表示文档文件路径和内容

### 2. 主要管理器
- **LLMFriendlyPackageManager**: 核心管理器类，提供完整的包管理功能
- 支持库的添加、删除、列表查看
- 集成 Git 仓库管理和文档提取

### 3. 功能特性
- **库管理**: 添加、删除、列出已添加的库
- **文档获取**: 获取指定包或所有包的文档内容
- **库浏览**: 浏览所有可用的库
- **代理设置**: 设置和管理 Git 代理
- **仓库刷新**: 更新本地仓库到最新版本
- **美观显示**: 使用 Rich 表格美观地显示信息

## 主要功能

### 1. 基础包管理

```python
from autocoder.common.llm_friendly_package import LLMFriendlyPackageManager

# 初始化管理器
manager = LLMFriendlyPackageManager()

# 使用自定义配置
manager = LLMFriendlyPackageManager(
    project_root="/path/to/your/project",
    base_persist_dir="/path/to/your/persistence/directory"
)

# 添加库（会自动克隆仓库）
success = manager.add_library("moonbit")
if success:
    print("库添加成功")

# 删除库
removed = manager.remove_library("moonbit")
if removed:
    print("库删除成功")

# 列出已添加的库
added_libs = manager.list_added_libraries()
print(f"已添加的库: {added_libs}")

# 显示已添加的库（美观的表格）
manager.display_added_libraries()
```

### 2. 文档获取和管理

```python
# 获取所有包的文档内容
docs_content = manager.get_docs()
print(f"获取到 {len(docs_content)} 个文档内容")

# 获取所有包的文档文件路径
docs_paths = manager.get_docs(return_paths=True)
print(f"找到 {len(docs_paths)} 个文档文件")

# 获取特定包的文档
specific_docs = manager.get_docs(package_name="moonbit", return_paths=True)
print(f"moonbit 包的文档文件: {len(specific_docs)} 个")

# 显示特定包的文档路径
manager.display_library_docs("moonbit")

# 获取包的完整路径
package_path = manager.get_package_path("moonbit")
if package_path:
    print(f"moonbit 包路径: {package_path}")

# 获取特定包的文档路径
library_docs = manager.get_library_docs_paths("moonbit")
for doc_path in library_docs:
    print(f"文档: {doc_path}")
```

### 3. 库浏览和发现

```python
# 获取所有可用库的结构化数据
available_libs = manager.list_all_available_libraries()

print(f"总共发现 {len(available_libs)} 个可用库:")
for lib in available_libs[:5]:  # 显示前5个
    print(f"- {lib.full_path} ({lib.domain})")
    print(f"  已添加: {lib.is_added}")
    print(f"  有文档: {lib.has_md_files}")
    print()

# 显示所有可用库（美观的表格）
manager.display_all_libraries()

# 按条件筛选库
github_libs = [lib for lib in available_libs if lib.domain == "github.com"]
added_libs = [lib for lib in available_libs if lib.is_added]
print(f"GitHub 库: {len(github_libs)} 个")
print(f"已添加的库: {len(added_libs)} 个")
```

### 4. 仓库管理和同步

```python
# 获取当前代理设置
current_proxy = manager.set_proxy()
print(f"当前代理: {current_proxy}")

# 设置新的代理
new_proxy = "https://gitee.com/your-mirror/llm_friendly_packages"
manager.set_proxy(new_proxy)
print(f"代理已设置为: {new_proxy}")

# 刷新仓库以获取最新更改
print("刷新仓库中...")
success = manager.refresh_repository()
if success:
    print("仓库刷新成功")
else:
    print("仓库刷新失败")

# 重置代理为默认值
default_proxy = "https://github.com/allwefantasy/llm_friendly_packages"
manager.set_proxy(default_proxy)
```

### 5. 高级功能和集成

```python
import os
from typing import List, Dict, Any

class AdvancedPackageManager:
    """扩展的包管理器，提供高级功能"""
    
    def __init__(self, project_root: str = None):
        self.manager = LLMFriendlyPackageManager(project_root)
    
    def batch_add_libraries(self, lib_names: List[str]) -> Dict[str, bool]:
        """批量添加库"""
        results = {}
        for lib_name in lib_names:
            results[lib_name] = self.manager.add_library(lib_name)
        return results
    
    def get_library_statistics(self) -> Dict[str, Any]:
        """获取库统计信息"""
        available_libs = self.manager.list_all_available_libraries()
        added_libs = self.manager.list_added_libraries()
        
        stats = {
            "total_available": len(available_libs),
            "total_added": len(added_libs),
            "domains": {},
            "users": {},
            "libraries_with_docs": 0
        }
        
        for lib in available_libs:
            # 统计域名
            stats["domains"][lib.domain] = stats["domains"].get(lib.domain, 0) + 1
            
            # 统计用户
            stats["users"][lib.username] = stats["users"].get(lib.username, 0) + 1
            
            # 统计有文档的库
            if lib.has_md_files:
                stats["libraries_with_docs"] += 1
        
        return stats
    
    def search_libraries(self, keyword: str) -> List[str]:
        """搜索包含关键词的库"""
        available_libs = self.manager.list_all_available_libraries()
        matching_libs = []
        
        keyword_lower = keyword.lower()
        for lib in available_libs:
            if (keyword_lower in lib.lib_name.lower() or 
                keyword_lower in lib.username.lower() or
                keyword_lower in lib.full_path.lower()):
                matching_libs.append(lib.full_path)
        
        return matching_libs
    
    def get_documentation_summary(self, package_name: str) -> Dict[str, Any]:
        """获取包的文档摘要"""
        docs_paths = self.manager.get_library_docs_paths(package_name)
        docs_content = self.manager.get_docs(package_name, return_paths=False)
        
        summary = {
            "package_name": package_name,
            "total_files": len(docs_paths),
            "total_content_length": sum(len(content) for content in docs_content),
            "file_types": {},
            "files": []
        }
        
        for doc_path in docs_paths:
            filename = os.path.basename(doc_path)
            file_ext = os.path.splitext(filename)[1]
            
            summary["file_types"][file_ext] = summary["file_types"].get(file_ext, 0) + 1
            summary["files"].append({
                "path": doc_path,
                "name": filename,
                "size": len(docs_content[docs_paths.index(doc_path)]) if docs_paths.index(doc_path) < len(docs_content) else 0
            })
        
        return summary
    
    def export_library_list(self, filename: str) -> bool:
        """导出库列表到文件"""
        try:
            available_libs = self.manager.list_all_available_libraries()
            added_libs = set(self.manager.list_added_libraries())
            
            export_data = {
                "export_time": time.time(),
                "total_libraries": len(available_libs),
                "added_libraries": list(added_libs),
                "libraries": []
            }
            
            for lib in available_libs:
                export_data["libraries"].append({
                    "domain": lib.domain,
                    "username": lib.username,
                    "lib_name": lib.lib_name,
                    "full_path": lib.full_path,
                    "is_added": lib.is_added,
                    "has_md_files": lib.has_md_files
                })
            
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def import_library_list(self, filename: str) -> bool:
        """从文件导入库列表"""
        try:
            import json
            with open(filename, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            added_libs = import_data.get("added_libraries", [])
            results = self.batch_add_libraries(added_libs)
            
            success_count = sum(1 for success in results.values() if success)
            print(f"导入完成: {success_count}/{len(added_libs)} 个库添加成功")
            
            return True
        except Exception as e:
            print(f"导入失败: {e}")
            return False

# 使用高级功能
advanced_manager = AdvancedPackageManager()

# 批量添加库
libraries_to_add = ["moonbit", "python-docs", "react-docs"]
results = advanced_manager.batch_add_libraries(libraries_to_add)
print("批量添加结果:")
for lib, success in results.items():
    print(f"  {lib}: {'成功' if success else '失败'}")

# 获取统计信息
stats = advanced_manager.get_library_statistics()
print(f"\n库统计信息:")
print(f"  总可用库: {stats['total_available']}")
print(f"  已添加库: {stats['total_added']}")
print(f"  有文档的库: {stats['libraries_with_docs']}")
print(f"  域名分布: {stats['domains']}")

# 搜索库
search_results = advanced_manager.search_libraries("python")
print(f"\n搜索 'python' 相关库: {len(search_results)} 个")
for lib in search_results[:3]:
    print(f"  - {lib}")

# 获取文档摘要
if search_results:
    package_name = search_results[0].split('/')[-1]  # 获取库名
    summary = advanced_manager.get_documentation_summary(package_name)
    print(f"\n{package_name} 文档摘要:")
    print(f"  文件数: {summary['total_files']}")
    print(f"  总内容长度: {summary['total_content_length']} 字符")
    print(f"  文件类型: {summary['file_types']}")

# 导出和导入
export_success = advanced_manager.export_library_list("library_export.json")
if export_success:
    print("库列表已导出到 library_export.json")
```

## 数据模型详解

### 1. LibraryInfo 数据类

```python
from autocoder.common.llm_friendly_package import LibraryInfo

# LibraryInfo 包含的字段
library_info = LibraryInfo(
    domain="github.com",           # 域名
    username="allwefantasy",       # 用户名
    lib_name="moonbit",            # 库名
    full_path="allwefantasy/moonbit",  # 完整路径
    is_added=True,                 # 是否已添加
    has_md_files=True              # 是否包含 Markdown 文件
)

print(f"库信息: {library_info.full_path}")
print(f"状态: {'已添加' if library_info.is_added else '未添加'}")
print(f"文档: {'有' if library_info.has_md_files else '无'}")
```

### 2. 内存配置管理

```python
# 管理器内部使用的内存配置结构
memory_structure = {
    "conversation": [],                    # 对话历史
    "current_files": {                     # 当前文件
        "files": [],
        "groups": {}
    },
    "conf": {},                           # 配置信息
    "exclude_dirs": [],                   # 排除目录
    "mode": "auto_detect",                # 模式
    "libs": {                             # 已添加的库
        "moonbit": {},
        "python-docs": {},
        "react-docs": {}
    },
    "lib-proxy": "https://github.com/allwefantasy/llm_friendly_packages"  # Git 代理
}

# 访问已添加的库
added_libraries = list(memory_structure["libs"].keys())
print(f"已添加的库: {added_libraries}")
```

## 与 Auto-Coder 系统集成

### 1. 在 AgenticEdit 中的集成

```python
# 在智能编辑系统中使用 LLM 友好包
from autocoder.common.v2.agent.agentic_edit import AgenticEdit
from autocoder.common.llm_friendly_package import LLMFriendlyPackageManager

class EnhancedAgenticEdit(AgenticEdit):
    """增强的智能编辑，集成 LLM 友好包"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.package_manager = LLMFriendlyPackageManager(
            project_root=self.args.source_dir,
            base_persist_dir=self.base_persist_dir
        )
    
    def prepare_library_context(self) -> str:
        """准备库上下文信息"""
        added_libraries = self.package_manager.list_added_libraries()
        
        if not added_libraries:
            return ""
        
        # 获取库的路径信息
        libraries_with_paths = []
        for lib_name in added_libraries:
            lib_path = self.package_manager.get_package_path(lib_name)
            libraries_with_paths.append({
                'name': lib_name,
                'path': lib_path if lib_path else 'Path not found'
            })
        
        # 获取文档内容
        docs_content = self.package_manager.get_docs(return_paths=False)
        
        if docs_content:
            combined_docs = "\n\n".join(docs_content)
            
            context = f"""
可用的第三方库:
{chr(10).join([f"- {lib['name']}: {lib['path']}" for lib in libraries_with_paths])}

库文档内容:
{combined_docs}
"""
            return context
        
        return ""
    
    def enhanced_analyze(self, request):
        """增强的分析，包含库上下文"""
        # 准备库上下文
        library_context = self.prepare_library_context()
        
        if library_context:
            # 将库上下文添加到对话中
            enhanced_request = request.copy()
            enhanced_request.user_input = f"{request.user_input}\n\n{library_context}"
            return self.analyze(enhanced_request)
        else:
            return self.analyze(request)
```

### 2. 在命令系统中的集成

```python
# 命令行接口集成示例
class LibraryCommandHandler:
    """库管理命令处理器"""
    
    def __init__(self):
        self.manager = LLMFriendlyPackageManager()
    
    def handle_lib_command(self, command: str, args: str) -> str:
        """处理 /lib 命令"""
        if command == "/lib":
            subcommands = args.split()
            if not subcommands:
                return self.show_help()
            
            subcmd = subcommands[0]
            
            if subcmd == "/add" and len(subcommands) > 1:
                lib_name = subcommands[1]
                success = self.manager.add_library(lib_name)
                return f"库 {lib_name} {'添加成功' if success else '添加失败'}"
            
            elif subcmd == "/remove" and len(subcommands) > 1:
                lib_name = subcommands[1]
                success = self.manager.remove_library(lib_name)
                return f"库 {lib_name} {'删除成功' if success else '删除失败'}"
            
            elif subcmd == "/list":
                self.manager.display_added_libraries()
                return "已显示添加的库列表"
            
            elif subcmd == "/list_all":
                self.manager.display_all_libraries()
                return "已显示所有可用库"
            
            elif subcmd == "/get" and len(subcommands) > 1:
                package_name = subcommands[1]
                self.manager.display_library_docs(package_name)
                return f"已显示 {package_name} 的文档"
            
            elif subcmd == "/set-proxy" and len(subcommands) > 1:
                proxy_url = subcommands[1]
                self.manager.set_proxy(proxy_url)
                return f"代理已设置为: {proxy_url}"
            
            elif subcmd == "/refresh":
                success = self.manager.refresh_repository()
                return "仓库刷新成功" if success else "仓库刷新失败"
            
            else:
                return "未知的子命令"
        
        return "不是库管理命令"
    
    def show_help(self) -> str:
        """显示帮助信息"""
        return """
库管理命令:
  /lib /add <库名>      - 添加库
  /lib /remove <库名>   - 删除库
  /lib /list           - 列出已添加的库
  /lib /list_all       - 列出所有可用库
  /lib /get <包名>     - 显示包的文档
  /lib /set-proxy <URL> - 设置 Git 代理
  /lib /refresh        - 刷新仓库
"""

# 使用命令处理器
handler = LibraryCommandHandler()

# 模拟命令处理
commands = [
    ("/lib", "/add moonbit"),
    ("/lib", "/list"),
    ("/lib", "/get moonbit"),
    ("/lib", "/refresh")
]

for cmd, args in commands:
    result = handler.handle_lib_command(cmd, args)
    print(f"命令: {cmd} {args}")
    print(f"结果: {result}\n")
```

## 使用示例

### 完整的 LLM 友好包管理工作流

```python
#!/usr/bin/env python3
"""
完整的 LLM 友好包管理工作流示例
展示如何在 Auto-Coder 项目中集成和使用包管理功能
"""

import os
import json
import time
from typing import List, Dict, Any
from autocoder.common.llm_friendly_package import LLMFriendlyPackageManager

class LLMPackageWorkflow:
    """LLM 包管理工作流"""
    
    def __init__(self, project_root: str = None):
        self.manager = LLMFriendlyPackageManager(project_root)
        self.setup_environment()
    
    def setup_environment(self):
        """设置环境"""
        print("🔧 设置 LLM 包管理环境...")
        
        # 检查是否需要克隆仓库
        current_proxy = self.manager.set_proxy()
        print(f"当前代理: {current_proxy}")
        
        # 尝试添加一个测试库来触发仓库克隆
        test_libs = self.manager.list_added_libraries()
        if not test_libs:
            print("首次使用，将初始化仓库...")
    
    def interactive_library_management(self):
        """交互式库管理"""
        print("\n📚 交互式库管理系统")
        print("支持的命令: add, remove, list, search, docs, stats, export, import, exit")
        
        while True:
            try:
                command = input("\npackage-manager> ").strip().lower()
                
                if command == "exit":
                    break
                elif command == "add":
                    self.interactive_add_library()
                elif command == "remove":
                    self.interactive_remove_library()
                elif command == "list":
                    self.show_library_status()
                elif command == "search":
                    self.interactive_search()
                elif command == "docs":
                    self.interactive_show_docs()
                elif command == "stats":
                    self.show_statistics()
                elif command == "export":
                    self.interactive_export()
                elif command == "import":
                    self.interactive_import()
                else:
                    print("未知命令，支持: add, remove, list, search, docs, stats, export, import, exit")
                    
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
    
    def interactive_add_library(self):
        """交互式添加库"""
        # 显示可用库
        available_libs = self.manager.list_all_available_libraries()
        if not available_libs:
            print("❌ 没有可用的库")
            return
        
        print(f"📋 发现 {len(available_libs)} 个可用库")
        
        # 显示未添加的库
        unadded_libs = [lib for lib in available_libs if not lib.is_added]
        if not unadded_libs:
            print("✅ 所有库都已添加")
            return
        
        print(f"未添加的库 ({len(unadded_libs)} 个):")
        for i, lib in enumerate(unadded_libs[:10], 1):  # 显示前10个
            print(f"  {i}. {lib.full_path}")
        
        if len(unadded_libs) > 10:
            print(f"  ... 还有 {len(unadded_libs) - 10} 个库")
        
        # 用户选择
        lib_name = input("请输入要添加的库名 (完整路径或库名): ").strip()
        if lib_name:
            success = self.manager.add_library(lib_name)
            print(f"{'✅ 添加成功' if success else '❌ 添加失败'}: {lib_name}")
    
    def interactive_remove_library(self):
        """交互式删除库"""
        added_libs = self.manager.list_added_libraries()
        if not added_libs:
            print("❌ 没有已添加的库")
            return
        
        print("已添加的库:")
        for i, lib in enumerate(added_libs, 1):
            print(f"  {i}. {lib}")
        
        lib_name = input("请输入要删除的库名: ").strip()
        if lib_name:
            success = self.manager.remove_library(lib_name)
            print(f"{'✅ 删除成功' if success else '❌ 删除失败'}: {lib_name}")
    
    def interactive_search(self):
        """交互式搜索"""
        keyword = input("请输入搜索关键词: ").strip()
        if not keyword:
            return
        
        available_libs = self.manager.list_all_available_libraries()
        matching_libs = []
        
        keyword_lower = keyword.lower()
        for lib in available_libs:
            if (keyword_lower in lib.lib_name.lower() or 
                keyword_lower in lib.username.lower() or
                keyword_lower in lib.full_path.lower()):
                matching_libs.append(lib)
        
        if matching_libs:
            print(f"🔍 找到 {len(matching_libs)} 个匹配的库:")
            for lib in matching_libs:
                status = "✅ 已添加" if lib.is_added else "⭕ 未添加"
                print(f"  {lib.full_path} - {status}")
        else:
            print("❌ 没有找到匹配的库")
    
    def interactive_show_docs(self):
        """交互式显示文档"""
        added_libs = self.manager.list_added_libraries()
        if not added_libs:
            print("❌ 没有已添加的库")
            return
        
        print("已添加的库:")
        for i, lib in enumerate(added_libs, 1):
            print(f"  {i}. {lib}")
        
        lib_name = input("请输入要查看文档的库名: ").strip()
        if lib_name:
            self.manager.display_library_docs(lib_name)
    
    def show_library_status(self):
        """显示库状态"""
        print("\n📊 库状态概览:")
        
        # 显示已添加的库
        print("\n已添加的库:")
        self.manager.display_added_libraries()
        
        # 显示统计信息
        available_libs = self.manager.list_all_available_libraries()
        added_libs = self.manager.list_added_libraries()
        
        print(f"\n📈 统计信息:")
        print(f"  总可用库: {len(available_libs)}")
        print(f"  已添加库: {len(added_libs)}")
        print(f"  未添加库: {len(available_libs) - len(added_libs)}")
        
        # 域名分布
        domains = {}
        for lib in available_libs:
            domains[lib.domain] = domains.get(lib.domain, 0) + 1
        
        print(f"  域名分布: {domains}")
    
    def show_statistics(self):
        """显示详细统计"""
        available_libs = self.manager.list_all_available_libraries()
        added_libs = set(self.manager.list_added_libraries())
        
        # 基本统计
        total_libs = len(available_libs)
        added_count = len(added_libs)
        with_docs = sum(1 for lib in available_libs if lib.has_md_files)
        
        print(f"\n📊 详细统计:")
        print(f"  总库数: {total_libs}")
        print(f"  已添加: {added_count} ({added_count/total_libs*100:.1f}%)")
        print(f"  有文档: {with_docs} ({with_docs/total_libs*100:.1f}%)")
        
        # 域名统计
        domains = {}
        users = {}
        for lib in available_libs:
            domains[lib.domain] = domains.get(lib.domain, 0) + 1
            users[lib.username] = users.get(lib.username, 0) + 1
        
        print(f"\n域名分布:")
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
            print(f"  {domain}: {count} 个库")
        
        print(f"\n用户分布 (Top 5):")
        top_users = sorted(users.items(), key=lambda x: x[1], reverse=True)[:5]
        for username, count in top_users:
            print(f"  {username}: {count} 个库")
    
    def interactive_export(self):
        """交互式导出"""
        filename = input("请输入导出文件名 (默认: library_export.json): ").strip()
        if not filename:
            filename = "library_export.json"
        
        try:
            available_libs = self.manager.list_all_available_libraries()
            added_libs = set(self.manager.list_added_libraries())
            
            export_data = {
                "export_time": time.time(),
                "total_libraries": len(available_libs),
                "added_libraries": list(added_libs),
                "libraries": []
            }
            
            for lib in available_libs:
                export_data["libraries"].append({
                    "domain": lib.domain,
                    "username": lib.username,
                    "lib_name": lib.lib_name,
                    "full_path": lib.full_path,
                    "is_added": lib.is_added,
                    "has_md_files": lib.has_md_files
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 导出成功: {filename}")
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
    
    def interactive_import(self):
        """交互式导入"""
        filename = input("请输入导入文件名: ").strip()
        if not filename or not os.path.exists(filename):
            print("❌ 文件不存在")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            added_libs = import_data.get("added_libraries", [])
            if not added_libs:
                print("❌ 导入文件中没有库列表")
                return
            
            print(f"📋 将导入 {len(added_libs)} 个库:")
            for lib in added_libs:
                print(f"  - {lib}")
            
            confirm = input("确认导入? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ 导入已取消")
                return
            
            success_count = 0
            for lib_name in added_libs:
                if self.manager.add_library(lib_name):
                    success_count += 1
            
            print(f"✅ 导入完成: {success_count}/{len(added_libs)} 个库添加成功")
            
        except Exception as e:
            print(f"❌ 导入失败: {e}")
    
    def run_workflow(self):
        """运行完整工作流"""
        print("🎯 LLM 友好包管理工作流")
        
        # 显示当前状态
        self.show_library_status()
        
        # 启动交互式管理
        self.interactive_library_management()

def main():
    """主程序"""
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else None
    
    workflow = LLMPackageWorkflow(project_root)
    workflow.run_workflow()

if __name__ == "__main__":
    main()
```

## 验证命令

验证 llm_friendly_package 模块功能：

```bash
# 检查模块导入
python -c "
from autocoder.common.llm_friendly_package import LLMFriendlyPackageManager, LibraryInfo
print('✅ 模块导入成功')
"

# 验证数据模型
python -c "
from autocoder.common.llm_friendly_package import LibraryInfo
lib_info = LibraryInfo('github.com', 'user', 'lib', 'user/lib', True, True)
print(f'✅ 数据模型正常: {lib_info.full_path}')
"

# 验证管理器功能
python -c "
from autocoder.common.llm_friendly_package import LLMFriendlyPackageManager
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    manager = LLMFriendlyPackageManager(temp_dir)
    print('✅ 包管理器创建成功')
    
    # 测试基本功能
    added_libs = manager.list_added_libraries()
    print(f'✅ 列出库功能正常: {len(added_libs)} 个库')
"

# 验证代理设置
python -c "
from autocoder.common.llm_friendly_package import LLMFriendlyPackageManager
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    manager = LLMFriendlyPackageManager(temp_dir)
    proxy = manager.set_proxy()
    print(f'✅ 代理功能正常: {proxy}')
"

# 验证库浏览功能
python -c "
from autocoder.common.llm_friendly_package import LLMFriendlyPackageManager
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    manager = LLMFriendlyPackageManager(temp_dir)
    available_libs = manager.list_all_available_libraries()
    print(f'✅ 库浏览功能正常: {len(available_libs)} 个可用库')
"

# 检查依赖关系
python -c "
import rich
import git
import filelock
print('✅ 所有依赖模块可用')
"

# 运行测试脚本（如果存在）
python src/autocoder/common/llm_friendly_package_test.py || echo "⚠️  测试脚本不存在或测试失败"

# 运行示例脚本（如果存在）
python src/autocoder/common/llm_friendly_package_example.py || echo "⚠️  示例脚本不存在或运行失败"
```

通过这些验证命令可以确认 llm_friendly_package 模块的完整性和功能正确性。 