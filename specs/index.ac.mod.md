# index.ac.mod.md

## 模块概述

`index` 模块是 Auto-Coder 系统的智能索引和文件过滤核心，提供基于 LLM 的代码索引构建、符号提取、智能文件过滤和相关性分析功能。该模块通过深度分析代码结构和语义，为 AI 编程助手提供精确的上下文文件选择，显著提升代码生成的准确性和相关性。

**模块类型**: 包模块  
**主要功能**: 代码索引构建、智能文件过滤、符号提取、相关性分析  
**依赖关系**: 依赖 `common`、`utils`、`events`、`agent` 等模块

## 核心组件

### 1. 数据模型层 (types.py)
- **IndexItem**: 索引条目，包含模块名、符号信息、修改时间和MD5
- **TargetFile**: 目标文件，包含文件路径和选择原因
- **VerifyFileRelevance**: 文件相关性验证结果
- **FileList**: 文件列表容器
- **FileNumberList**: 文件编号列表

### 2. 索引管理器 (index.py)
- **IndexManager**: 核心索引管理器，负责索引构建和查询
- 支持多线程并发索引构建
- 集成符号提取和语义分析
- 提供查询和相关文件发现功能

### 3. 过滤器系统 (filter/)
- **QuickFilter**: 快速过滤器，适用于小到中等规模项目
- **NormalFilter**: 标准过滤器，提供多级过滤策略
- **AgenticFilter**: 智能代理过滤器，基于 AI 的高级过滤

### 4. 入口函数 (entry.py)
- **build_index_and_filter_files()**: 主要入口函数
- 统一的索引构建和文件过滤流程
- 集成统计和性能监控

### 5. 工具函数
- **symbols_utils.py**: 符号提取和处理工具
- **for_command.py**: 命令行接口支持

## 主要功能

### 1. 索引构建和管理

```python
from autocoder.index.index import IndexManager
from autocoder.common import AutoCoderArgs, SourceCode

# 创建索引管理器
args = AutoCoderArgs(
    source_dir="/path/to/project",
    index_build_workers=4,
    index_filter_workers=2,
    index_filter_level=1,
    anti_quota_limit=0.1
)

sources = [
    SourceCode(module_name="src/main.py", source_code="def main(): pass"),
    SourceCode(module_name="src/utils.py", source_code="def helper(): pass")
]

index_manager = IndexManager(llm=llm, sources=sources, args=args)

# 构建索引
index_data = index_manager.build_index()
print(f"索引构建完成，处理了 {len(index_data)} 个文件")

# 读取索引
index_items = index_manager.read_index()
for item in index_items:
    print(f"文件: {item.module_name}")
    print(f"符号: {item.symbols[:100]}...")
    print(f"MD5: {item.md5}")
    print()
```

### 2. 智能文件过滤

```python
from autocoder.index.entry import build_index_and_filter_files

# 完整的索引和过滤流程
filtered_sources = build_index_and_filter_files(
    llm=llm,
    args=args,
    sources=sources
)

print(f"过滤后的文件数量: {len(filtered_sources.sources)}")
for source in filtered_sources.sources:
    print(f"选中文件: {source.module_name}")
```

### 3. 基于查询的文件搜索

```python
# 根据查询搜索相关文件
query = "用户认证和登录功能"
target_files = index_manager.get_target_files_by_query(query)

print(f"找到 {len(target_files.file_list)} 个相关文件:")
for file in target_files.file_list:
    print(f"- {file.file_path}: {file.reason}")

# 获取相关文件
if target_files.file_list:
    file_paths = [f.file_path for f in target_files.file_list]
    related_files = index_manager.get_related_files(file_paths)
    
    print(f"相关文件 {len(related_files.file_list)} 个:")
    for file in related_files.file_list:
        print(f"- {file.file_path}: {file.reason}")
```

### 4. 快速过滤器使用

```python
from autocoder.index.filter.quick_filter import QuickFilter

# 创建快速过滤器
quick_filter = QuickFilter(index_manager, stats={}, sources=sources)

# 执行过滤
index_items = index_manager.read_index()
filter_result = quick_filter.filter(index_items, query="数据库操作")

print(f"快速过滤结果: {len(filter_result.files)} 个文件")
for file_path, target_file in filter_result.files.items():
    print(f"- {file_path}: {target_file.reason}")

# 获取文件位置信息
if filter_result.file_positions:
    sorted_files = sorted(
        filter_result.file_positions.items(), 
        key=lambda x: x[1]
    )
    print("文件相关性排序:")
    for file_path, position in sorted_files:
        print(f"  {position}. {file_path}")
```

### 5. 标准过滤器多级过滤

```python
from autocoder.index.filter.normal_filter import NormalFilter

# 创建标准过滤器
normal_filter = NormalFilter(index_manager, stats={}, sources=sources)

# 执行多级过滤
filter_result = normal_filter.filter(index_items, query="API接口实现")

print("标准过滤结果:")
for file_path, target_file in filter_result.items():
    print(f"- {file_path}: {target_file.reason}")
```

### 6. 符号提取和分析

```python
from autocoder.index.symbols_utils import extract_symbols, SymbolType, symbols_info_to_str

# 提取代码符号
code = """
class UserService:
    def __init__(self):
        self.db = Database()
    
    def authenticate(self, username, password):
        return self.db.verify_user(username, password)
    
    def create_user(self, user_data):
        return self.db.insert_user(user_data)

def login_handler(request):
    service = UserService()
    return service.authenticate(request.username, request.password)
"""

# 提取所有符号
symbols_info = extract_symbols(code)
print("提取的符号信息:")
print(symbols_info)

# 只提取特定类型的符号
class_symbols = symbols_info_to_str(symbols_info, [SymbolType.CLASS])
print("类符号:")
print(class_symbols)

function_symbols = symbols_info_to_str(symbols_info, [SymbolType.FUNCTION])
print("函数符号:")
print(function_symbols)
```

### 7. 高级索引配置和优化

```python
class AdvancedIndexManager:
    """高级索引管理器，提供更多配置选项"""
    
    def __init__(self, llm, sources, args):
        self.manager = IndexManager(llm, sources, args)
        self.args = args
    
    def build_index_with_progress(self):
        """带进度显示的索引构建"""
        print("开始构建索引...")
        
        # 设置索引构建参数
        self.args.index_build_workers = 6  # 增加并发数
        self.args.index_model_anti_quota_limit = 0.05  # 减少延迟
        
        # 构建索引
        start_time = time.time()
        index_data = self.manager.build_index()
        end_time = time.time()
        
        print(f"索引构建完成:")
        print(f"  处理文件: {len(index_data)}")
        print(f"  耗时: {end_time - start_time:.2f} 秒")
        
        return index_data
    
    def search_with_filters(self, query: str, file_limit: int = 10):
        """带过滤器的搜索"""
        # 设置过滤参数
        self.args.index_filter_level = 2  # 启用二级过滤
        self.args.index_filter_file_num = file_limit
        
        # 执行搜索
        target_files = self.manager.get_target_files_by_query(query)
        
        if not target_files.file_list:
            return []
        
        # 获取相关文件
        related_files = self.manager.get_related_files(
            [f.file_path for f in target_files.file_list]
        )
        
        # 合并结果
        all_files = {}
        for file in target_files.file_list:
            all_files[file.file_path] = file
        
        if related_files:
            for file in related_files.file_list:
                if file.file_path not in all_files:
                    all_files[file.file_path] = file
        
        return list(all_files.values())
    
    def analyze_index_quality(self):
        """分析索引质量"""
        index_items = self.manager.read_index()
        
        stats = {
            "total_files": len(index_items),
            "empty_symbols": 0,
            "large_symbols": 0,
            "avg_symbols_length": 0,
            "file_types": {}
        }
        
        total_length = 0
        for item in index_items:
            # 统计符号信息
            symbols_length = len(item.symbols)
            total_length += symbols_length
            
            if symbols_length == 0:
                stats["empty_symbols"] += 1
            elif symbols_length > 5000:
                stats["large_symbols"] += 1
            
            # 统计文件类型
            ext = os.path.splitext(item.module_name)[1]
            stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
        
        if index_items:
            stats["avg_symbols_length"] = total_length / len(index_items)
        
        return stats
    
    def cleanup_stale_index(self):
        """清理过期索引"""
        index_items = self.manager.read_index()
        stale_files = []
        
        for item in index_items:
            if not os.path.exists(item.module_name):
                stale_files.append(item.module_name)
                continue
            
            # 检查文件是否已修改
            current_mtime = os.path.getmtime(item.module_name)
            if current_mtime != item.last_modified:
                stale_files.append(item.module_name)
        
        if stale_files:
            print(f"发现 {len(stale_files)} 个过期文件，将重新构建索引")
            # 重新构建索引
            self.build_index_with_progress()
        
        return stale_files

# 使用高级索引管理器
advanced_manager = AdvancedIndexManager(llm, sources, args)

# 构建索引并分析质量
index_data = advanced_manager.build_index_with_progress()
quality_stats = advanced_manager.analyze_index_quality()

print("索引质量分析:")
print(f"  总文件数: {quality_stats['total_files']}")
print(f"  空符号文件: {quality_stats['empty_symbols']}")
print(f"  大符号文件: {quality_stats['large_symbols']}")
print(f"  平均符号长度: {quality_stats['avg_symbols_length']:.0f}")
print(f"  文件类型分布: {quality_stats['file_types']}")

# 执行智能搜索
search_results = advanced_manager.search_with_filters(
    query="用户管理和权限控制",
    file_limit=15
)

print(f"\n搜索结果 ({len(search_results)} 个文件):")
for file in search_results:
    print(f"  - {file.file_path}: {file.reason}")

# 清理过期索引
stale_files = advanced_manager.cleanup_stale_index()
if stale_files:
    print(f"\n清理了 {len(stale_files)} 个过期文件")
```

## 过滤策略和算法

### 1. 快速过滤策略

```python
# 快速过滤器支持三种模式
class FilterMode:
    NORMAL = "normal"          # 正常模式：直接过滤
    BIG = "big"               # 大项目模式：分块过滤
    SUPER_BIG = "super_big"   # 超大项目模式：两轮过滤

def determine_filter_mode(tokens_len: int, max_tokens: int) -> str:
    """根据token数量确定过滤模式"""
    if tokens_len <= max_tokens:
        return FilterMode.NORMAL
    elif tokens_len <= 4 * max_tokens:
        return FilterMode.BIG
    else:
        return FilterMode.SUPER_BIG

# 使用示例
tokens_len = count_tokens(prompt_str)
mode = determine_filter_mode(tokens_len, max_tokens=8000)

print(f"当前索引大小: {tokens_len} tokens")
print(f"使用过滤模式: {mode}")
```

### 2. 多级过滤流程

```python
# 标准过滤器的多级流程
def multi_level_filtering(index_manager, query, args):
    """多级过滤流程"""
    final_files = {}
    
    # Level 0: 基础过滤（仅使用文件用途）
    if args.index_filter_level == 0:
        target_files = index_manager.get_target_files_by_query(query)
        for file in target_files.file_list:
            final_files[file.file_path] = file
    
    # Level 1: 符号级过滤（包含符号信息）
    if args.index_filter_level >= 1:
        target_files = index_manager.get_target_files_by_query(query)
        for file in target_files.file_list:
            final_files[file.file_path] = file
    
    # Level 2: 关联文件发现
    if args.index_filter_level >= 2 and target_files.file_list:
        related_files = index_manager.get_related_files(
            [f.file_path for f in target_files.file_list]
        )
        if related_files:
            for file in related_files.file_list:
                final_files[file.file_path] = file
    
    return final_files
```

### 3. 智能查询解析

```python
def parse_advanced_query(query: str):
    """解析高级查询语法"""
    import re
    
    # 解析文件路径标记 @
    file_patterns = re.findall(r'@([^\s@]+)', query)
    
    # 解析符号标记 @@
    symbol_patterns = re.findall(r'@@([^\s@]+)', query)
    
    # 清理查询文本
    clean_query = re.sub(r'@{1,2}[^\s@]+', '', query).strip()
    
    return {
        "clean_query": clean_query,
        "file_patterns": file_patterns,
        "symbol_patterns": symbol_patterns
    }

# 使用示例
query = "实现用户登录功能 @auth/login.py @@authenticate_user"
parsed = parse_advanced_query(query)

print(f"清理后的查询: {parsed['clean_query']}")
print(f"文件模式: {parsed['file_patterns']}")
print(f"符号模式: {parsed['symbol_patterns']}")
```

## 性能优化和监控

### 1. 索引构建性能优化

```python
class IndexPerformanceOptimizer:
    """索引性能优化器"""
    
    def __init__(self, index_manager):
        self.index_manager = index_manager
        self.stats = {}
    
    def optimize_build_params(self, total_files: int):
        """根据项目规模优化构建参数"""
        if total_files < 100:
            return {
                "workers": 2,
                "anti_quota_limit": 0.1,
                "chunk_size": 4096
            }
        elif total_files < 500:
            return {
                "workers": 4,
                "anti_quota_limit": 0.05,
                "chunk_size": 6144
            }
        else:
            return {
                "workers": 8,
                "anti_quota_limit": 0.02,
                "chunk_size": 8192
            }
    
    def monitor_build_progress(self, callback=None):
        """监控构建进度"""
        start_time = time.time()
        
        # 构建索引
        index_data = self.index_manager.build_index()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 收集统计信息
        self.stats = {
            "duration": duration,
            "files_processed": len(index_data),
            "avg_time_per_file": duration / len(index_data) if index_data else 0,
            "timestamp": end_time
        }
        
        if callback:
            callback(self.stats)
        
        return index_data
    
    def analyze_bottlenecks(self):
        """分析性能瓶颈"""
        bottlenecks = []
        
        if self.stats.get("avg_time_per_file", 0) > 2.0:
            bottlenecks.append("文件处理速度慢，考虑增加并发数")
        
        if self.stats.get("duration", 0) > 300:  # 5分钟
            bottlenecks.append("总体构建时间过长，考虑优化模型或分块策略")
        
        return bottlenecks

# 使用性能优化器
optimizer = IndexPerformanceOptimizer(index_manager)

# 优化参数
params = optimizer.optimize_build_params(len(sources))
args.index_build_workers = params["workers"]
args.anti_quota_limit = params["anti_quota_limit"]

# 监控构建
def progress_callback(stats):
    print(f"构建完成: {stats['files_processed']} 文件, "
          f"耗时: {stats['duration']:.2f}s, "
          f"平均: {stats['avg_time_per_file']:.2f}s/文件")

index_data = optimizer.monitor_build_progress(progress_callback)

# 分析瓶颈
bottlenecks = optimizer.analyze_bottlenecks()
if bottlenecks:
    print("性能瓶颈:")
    for bottleneck in bottlenecks:
        print(f"  - {bottleneck}")
```

### 2. 过滤性能监控

```python
class FilterPerformanceMonitor:
    """过滤性能监控器"""
    
    def __init__(self):
        self.metrics = {}
    
    def measure_filter_performance(self, filter_func, *args, **kwargs):
        """测量过滤性能"""
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        # 执行过滤
        result = filter_func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        # 记录指标
        self.metrics = {
            "duration": end_time - start_time,
            "memory_delta": end_memory - start_memory,
            "result_count": len(result.files) if hasattr(result, 'files') else len(result),
            "timestamp": end_time
        }
        
        return result
    
    def get_memory_usage(self):
        """获取内存使用量"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def generate_report(self):
        """生成性能报告"""
        if not self.metrics:
            return "暂无性能数据"
        
        return f"""
过滤性能报告:
  执行时间: {self.metrics['duration']:.2f} 秒
  内存变化: {self.metrics['memory_delta']:.2f} MB
  结果数量: {self.metrics['result_count']} 个文件
  处理效率: {self.metrics['result_count'] / self.metrics['duration']:.1f} 文件/秒
"""

# 使用性能监控
monitor = FilterPerformanceMonitor()

# 监控快速过滤
quick_filter = QuickFilter(index_manager, {}, sources)
result = monitor.measure_filter_performance(
    quick_filter.filter, 
    index_items, 
    "用户认证功能"
)

print(monitor.generate_report())
```

## 使用示例

### 完整的索引和过滤工作流

```python
#!/usr/bin/env python3
"""
完整的索引和过滤工作流示例
展示如何在 Auto-Coder 中使用索引系统
"""

import os
import time
from typing import List
from autocoder.index.entry import build_index_and_filter_files
from autocoder.index.index import IndexManager
from autocoder.common import AutoCoderArgs, SourceCode

class IndexWorkflow:
    """索引工作流管理"""
    
    def __init__(self, project_dir: str, llm):
        self.project_dir = project_dir
        self.llm = llm
        self.setup_args()
    
    def setup_args(self):
        """设置参数"""
        self.args = AutoCoderArgs(
            source_dir=self.project_dir,
            skip_build_index=False,
            skip_filter_index=False,
            index_build_workers=4,
            index_filter_workers=2,
            index_filter_level=2,
            index_filter_file_num=20,
            anti_quota_limit=0.1,
            skip_confirm=True,
            context_prune=True,
            conversation_prune_safe_zone_tokens=8000
        )
    
    def collect_source_files(self) -> List[SourceCode]:
        """收集源代码文件"""
        sources = []
        
        for root, dirs, files in os.walk(self.project_dir):
            # 跳过隐藏目录和常见的排除目录
            dirs[:] = [d for d in dirs if not d.startswith('.') 
                      and d not in ['node_modules', '__pycache__', 'venv']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.h')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        sources.append(SourceCode(
                            module_name=file_path,
                            source_code=content
                        ))
                    except Exception as e:
                        print(f"读取文件失败 {file_path}: {e}")
        
        return sources
    
    def run_full_workflow(self, query: str):
        """运行完整的工作流"""
        print(f"🚀 开始索引和过滤工作流")
        print(f"项目目录: {self.project_dir}")
        print(f"查询: {query}")
        
        # 收集源文件
        print("\n📁 收集源文件...")
        sources = self.collect_source_files()
        print(f"发现 {len(sources)} 个源文件")
        
        # 设置查询
        self.args.query = query
        
        # 执行完整的索引和过滤流程
        print("\n🔍 执行索引和过滤...")
        start_time = time.time()
        
        filtered_sources = build_index_and_filter_files(
            llm=self.llm,
            args=self.args,
            sources=sources
        )
        
        end_time = time.time()
        
        # 显示结果
        print(f"\n✅ 工作流完成 (耗时: {end_time - start_time:.2f}s)")
        print(f"过滤后文件数量: {len(filtered_sources.sources)}")
        
        print("\n📋 选中的文件:")
        for i, source in enumerate(filtered_sources.sources, 1):
            print(f"  {i}. {source.module_name}")
        
        return filtered_sources
    
    def interactive_query(self):
        """交互式查询"""
        print("\n🎯 交互式索引查询系统")
        print("输入查询内容，输入 'exit' 退出")
        
        # 收集源文件（一次性）
        sources = self.collect_source_files()
        
        # 创建索引管理器
        index_manager = IndexManager(self.llm, sources, self.args)
        
        # 构建索引
        print("构建索引中...")
        index_manager.build_index()
        print("索引构建完成")
        
        while True:
            try:
                query = input("\n查询> ").strip()
                
                if query.lower() == 'exit':
                    break
                
                if not query:
                    continue
                
                # 执行查询
                start_time = time.time()
                target_files = index_manager.get_target_files_by_query(query)
                end_time = time.time()
                
                print(f"\n🔍 查询结果 (耗时: {end_time - start_time:.2f}s):")
                
                if target_files.file_list:
                    for i, file in enumerate(target_files.file_list, 1):
                        print(f"  {i}. {file.file_path}")
                        print(f"     原因: {file.reason}")
                    
                    # 获取相关文件
                    if self.args.index_filter_level >= 2:
                        related_files = index_manager.get_related_files(
                            [f.file_path for f in target_files.file_list]
                        )
                        
                        if related_files.file_list:
                            print(f"\n🔗 相关文件:")
                            for i, file in enumerate(related_files.file_list, 1):
                                print(f"  {i}. {file.file_path}")
                                print(f"     原因: {file.reason}")
                else:
                    print("  未找到相关文件")
                    
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 查询错误: {e}")
    
    def analyze_project(self):
        """分析项目结构"""
        sources = self.collect_source_files()
        
        # 统计信息
        file_types = {}
        total_lines = 0
        total_size = 0
        
        for source in sources:
            ext = os.path.splitext(source.module_name)[1]
            file_types[ext] = file_types.get(ext, 0) + 1
            
            lines = len(source.source_code.splitlines())
            total_lines += lines
            total_size += len(source.source_code)
        
        print(f"\n📊 项目分析:")
        print(f"  总文件数: {len(sources)}")
        print(f"  总代码行数: {total_lines:,}")
        print(f"  总大小: {total_size / 1024:.1f} KB")
        
        print(f"\n文件类型分布:")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(sources) * 100
            print(f"  {ext or '无扩展名'}: {count} 个文件 ({percentage:.1f}%)")
        
        return {
            "total_files": len(sources),
            "total_lines": total_lines,
            "total_size": total_size,
            "file_types": file_types
        }

def main():
    """主程序"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python index_workflow.py <项目目录> [查询]")
        return
    
    project_dir = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(project_dir):
        print(f"❌ 项目目录不存在: {project_dir}")
        return
    
    # 这里需要初始化 LLM
    # llm = initialize_llm()  # 根据实际情况初始化
    llm = None  # 占位符
    
    workflow = IndexWorkflow(project_dir, llm)
    
    if query:
        # 运行单次查询
        workflow.run_full_workflow(query)
    else:
        # 分析项目
        workflow.analyze_project()
        
        # 启动交互式查询
        workflow.interactive_query()

if __name__ == "__main__":
    main()
```

## 验证命令

验证 index 模块功能：

```bash
# 检查模块导入
python -c "
from autocoder.index.index import IndexManager
from autocoder.index.types import IndexItem, TargetFile
from autocoder.index.entry import build_index_and_filter_files
print('✅ 模块导入成功')
"

# 验证数据模型
python -c "
from autocoder.index.types import IndexItem, TargetFile, FileList
item = IndexItem(module_name='test.py', symbols='def test(): pass', last_modified=0.0, md5='abc123')
target = TargetFile(file_path='test.py', reason='测试文件')
file_list = FileList(file_list=[target])
print(f'✅ 数据模型正常: {item.module_name}, {target.file_path}')
"

# 验证符号提取
python -c "
from autocoder.index.symbols_utils import extract_symbols, SymbolType
code = 'class Test:\\n    def method(self): pass'
symbols = extract_symbols(code)
print(f'✅ 符号提取正常: 找到符号信息')
"

# 验证过滤器
python -c "
from autocoder.index.filter.quick_filter import QuickFilter
from autocoder.index.filter.normal_filter import NormalFilter
print('✅ 过滤器模块导入成功')
"

# 验证命令行接口
python -c "
from autocoder.index.for_command import index_command, index_query_command
print('✅ 命令行接口可用')
"

# 检查依赖关系
python -c "
import byzerllm
from rich.console import Console
from rich.table import Table
import threading
from concurrent.futures import ThreadPoolExecutor
print('✅ 所有依赖模块可用')
"
```

通过这些验证命令可以确认 index 模块的完整性和功能正确性。 