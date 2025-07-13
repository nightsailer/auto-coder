# common.tokens.ac.mod.md

## 模块信息
- **模块名称**: common.tokens
- **模块类型**: 包模块 (Package Module)
- **主要功能**: 高效统计文件和目录中的token数量，支持正则过滤和智能文件类型识别

## 核心功能

### Token计数系统
- **TokenCounter**: 核心token计数器，支持文件、目录和字符串的token统计
- **智能检测**: 自动识别文件类型和编码格式
- **高效处理**: 支持并行处理和大文件分块处理
- **灵活过滤**: 基于正则表达式和文件类型的灵活过滤机制

### 文件类型检测
- **FileTypeDetector**: 智能文件类型检测器
- **MIME类型识别**: 基于文件内容的MIME类型检测
- **编码检测**: 自动检测文本文件的字符编码
- **二进制文件识别**: 通过文件头部字节识别二进制文件

### 过滤系统
- **FileFilter**: 灵活的文件过滤器
- **正则表达式**: 支持复杂的文件名模式匹配
- **大小过滤**: 按文件大小范围进行过滤
- **类型过滤**: 按文件类型（文本/二进制）过滤

## 关键组件

### 1. TokenCounter 核心计数器
```python
class TokenCounter:
    def __init__(self, timeout: int = 30, parallel: bool = True, max_workers: int = 4)
    
    # 文件统计
    def count_file(self, file_path: str) -> TokenResult
    def count_files(self, file_paths: List[str]) -> List[TokenResult]
    
    # 目录统计
    def count_directory(self, dir_path: str, pattern: str = None) -> DirectoryTokenResult
    
    # 字符串统计
    def count_string_tokens(self, text: str) -> int
    
    # 配置管理
    def set_tokenizer(self, tokenizer_name: str) -> None
```

### 2. FileTypeDetector 文件检测器
```python
class FileTypeDetector:
    def is_text_file(self, file_path: str) -> bool
    def detect_encoding(self, file_path: str) -> str
    def get_mime_type(self, file_path: str) -> str
    def is_binary_file(self, file_path: str) -> bool
```

### 3. FileFilter 文件过滤器
```python
class FileFilter:
    def __init__(self, pattern: str = None)
    
    def matches(self, file_path: str) -> bool
    def add_pattern(self, pattern: str) -> None
    def set_size_range(self, min_size: int, max_size: int) -> None
    def set_type_filter(self, file_types: List[str]) -> None
```

### 4. 数据模型
```python
# 单文件统计结果
class TokenResult:
    file_path: str
    token_count: int
    char_count: int
    line_count: int
    success: bool
    error: Optional[str]
    processing_time: float

# 目录统计结果
class DirectoryTokenResult:
    directory_path: str
    total_tokens: int
    total_chars: int
    total_lines: int
    file_count: int
    skipped_count: int
    file_results: List[TokenResult]
    processing_time: float
```

## 使用指南

### 1. 基本使用
```python
from autocoder.common.tokens import TokenCounter, count_file_tokens, count_directory_tokens, count_string_tokens

# 统计单个文件
result = count_file_tokens("path/to/file.py")
print(f"文件: {result.file_path}")
print(f"Token 数量: {result.token_count}")
print(f"字符数: {result.char_count}")
print(f"行数: {result.line_count}")

# 统计整个目录
dir_result = count_directory_tokens(
    "path/to/directory",
    pattern=r".*\.py$"  # 只统计 Python 文件
)
print(f"总 Token 数: {dir_result.total_tokens}")
print(f"文件数量: {dir_result.file_count}")
print(f"跳过文件数: {dir_result.skipped_count}")

# 统计字符串 Token 数量
text = "Hello, this is a sample text for token counting."
token_count = count_string_tokens(text)
print(f"字符串 Token 数量: {token_count}")
```

### 2. 高级配置
```python
# 创建配置化的计数器
counter = TokenCounter(
    timeout=30,         # 单文件处理超时时间
    parallel=True,      # 启用并行处理
    max_workers=4       # 最大工作线程数
)

# 批量处理文件
files = ["file1.py", "file2.js", "file3.md"]
results = counter.count_files(files)
for result in results:
    if result.success:
        print(f"{result.file_path}: {result.token_count} tokens")
    else:
        print(f"{result.file_path}: 失败 - {result.error}")

# 更换tokenizer
counter.set_tokenizer("cl100k_base")  # GPT-4 tokenizer
```

### 3. 文件过滤
```python
from autocoder.common.tokens.filters import FileFilter

# 创建复杂过滤器
file_filter = FileFilter()

# 添加多个模式
file_filter.add_pattern(r".*\.(py|js|ts)$")  # 代码文件
file_filter.add_pattern(r".*\.md$")          # Markdown文件

# 设置文件大小范围
file_filter.set_size_range(min_size=100, max_size=1000000)  # 100字节到1MB

# 设置文件类型
file_filter.set_type_filter(["text"])  # 只处理文本文件

# 使用过滤器
if file_filter.matches("example.py"):
    result = count_file_tokens("example.py")
```

### 4. 项目代码统计
```python
# 统计整个项目的token使用量
def analyze_project(project_path: str):
    result = count_directory_tokens(
        project_path,
        pattern=r".*\.(py|js|ts|jsx|tsx|vue|go|java|cpp|c|h)$"
    )
    
    print(f"项目路径: {result.directory_path}")
    print(f"总Token数: {result.total_tokens:,}")
    print(f"总文件数: {result.file_count}")
    print(f"平均每文件: {result.total_tokens / result.file_count:,.0f} tokens")
    print(f"处理时间: {result.processing_time:.2f}秒")
    
    # 按文件类型分组统计
    file_types = {}
    for file_result in result.file_results:
        ext = file_result.file_path.split('.')[-1]
        if ext not in file_types:
            file_types[ext] = {'count': 0, 'tokens': 0}
        file_types[ext]['count'] += 1
        file_types[ext]['tokens'] += file_result.token_count
    
    print("\n按文件类型统计:")
    for ext, stats in sorted(file_types.items()):
        print(f"  {ext}: {stats['count']} 文件, {stats['tokens']:,} tokens")

# 使用示例
analyze_project("./src")
```

### 5. API成本估算
```python
def estimate_api_cost(directory: str, cost_per_1k_tokens: float = 0.002):
    """估算GPT API调用成本"""
    result = count_directory_tokens(directory)
    total_cost = (result.total_tokens / 1000) * cost_per_1k_tokens
    
    return {
        "directory": directory,
        "total_tokens": result.total_tokens,
        "estimated_cost": f"${total_cost:.4f}",
        "file_count": result.file_count,
        "cost_per_file": f"${total_cost / result.file_count:.6f}"
    }

# 估算不同模型的成本
models = {
    "gpt-3.5-turbo": 0.002,
    "gpt-4": 0.03,
    "gpt-4-turbo": 0.01
}

for model, cost in models.items():
    estimate = estimate_api_cost("./docs", cost)
    print(f"{model}: {estimate['estimated_cost']} ({estimate['total_tokens']} tokens)")
```

### 6. 字符串Token预估
```python
def estimate_prompt_tokens(prompt_template: str, **kwargs):
    """在发送到LLM前预估Token数量"""
    # 填充模板
    filled_prompt = prompt_template.format(**kwargs)
    
    # 统计Token数量
    token_count = count_string_tokens(filled_prompt)
    
    return {
        "prompt": filled_prompt,
        "token_count": token_count,
        "estimated_cost": f"${(token_count / 1000) * 0.002:.4f}",
        "char_count": len(filled_prompt)
    }

# 使用示例
template = """请分析以下代码：
{code}

分析要求：
{requirements}

请提供详细的分析报告。"""

result = estimate_prompt_tokens(
    template,
    code="def hello(): print('world')",
    requirements="检查代码质量、性能和安全性"
)

print(f"Prompt Token数量: {result['token_count']}")
print(f"预估成本: {result['estimated_cost']}")
```

## 目录结构

```
src/autocoder/common/tokens/
├── __init__.py               # 模块入口，导出主要接口
├── counter.py                # 核心token计数器实现
├── file_detector.py          # 文件类型检测器
├── models.py                 # 数据模型定义
├── filters.py                # 文件过滤器实现
└── .ac.mod.md                # 本文档
```

## 技术特性

### 1. 高性能处理
- **并行计算**: 支持多线程并行处理多个文件
- **内存优化**: 大文件分块读取，避免内存溢出
- **缓存机制**: 智能缓存重复计算结果
- **超时控制**: 防止单个文件处理时间过长

### 2. 智能识别
- **文件类型检测**: 基于内容和扩展名的双重检测
- **编码自动识别**: 支持UTF-8、GBK、ASCII等多种编码
- **二进制文件过滤**: 自动跳过图片、视频等二进制文件
- **MIME类型分析**: 准确识别文件的实际类型

### 3. 灵活过滤
- **正则表达式**: 支持复杂的文件名模式匹配
- **组合条件**: 多个过滤条件的逻辑组合
- **动态配置**: 运行时动态调整过滤规则
- **性能优化**: 高效的过滤算法减少不必要的处理

### 4. 错误处理
- **异常捕获**: 完善的异常处理机制
- **错误报告**: 详细的错误信息和堆栈跟踪
- **容错处理**: 单个文件错误不影响整体处理
- **重试机制**: 对临时错误的自动重试

## 架构图

```mermaid
graph TB
    %% 用户接口层
    API[公共API<br/>count_file_tokens()<br/>count_directory_tokens()<br/>count_string_tokens()]
    
    %% 核心层
    Counter[TokenCounter<br/>核心计数逻辑]
    Detector[FileTypeDetector<br/>文件类型检测]
    Filter[FileFilter<br/>文件过滤器]
    
    %% 数据模型层
    Models[数据模型<br/>TokenResult<br/>DirectoryTokenResult]
    
    %% 外部依赖
    Tiktoken[tiktoken<br/>Token编码器]
    FileSystem[文件系统<br/>pathlib/os]
    
    %% 依赖关系
    API --> Counter
    Counter --> Detector
    Counter --> Filter
    Counter --> Models
    Counter --> Tiktoken
    Detector --> FileSystem
    Filter --> FileSystem
```

## 集成点

### 与其他模块的关系
- **utils.llms模块**: 为LLM相关功能提供token计算服务
- **rag模块**: 为文档检索提供token统计
- **common模块**: 作为通用工具被其他模块使用
- **memory模块**: 为上下文管理提供token统计

### 外部依赖
- **tiktoken**: OpenAI的官方token计数库
- **pathlib**: Python标准库，用于路径操作
- **re**: Python标准库，用于正则表达式
- **mimetypes**: Python标准库，用于MIME类型检测
- **chardet**: 可选依赖，用于更准确的编码检测

## 扩展指南

### 1. 自定义Tokenizer
```python
from autocoder.common.tokens.counter import TokenCounter

class CustomTokenCounter(TokenCounter):
    def __init__(self, custom_tokenizer):
        super().__init__()
        self.custom_tokenizer = custom_tokenizer
    
    def count_string_tokens(self, text: str) -> int:
        # 使用自定义tokenizer
        return len(self.custom_tokenizer.encode(text))
```

### 2. 扩展文件类型检测
```python
from autocoder.common.tokens.file_detector import FileTypeDetector

class EnhancedFileDetector(FileTypeDetector):
    def is_code_file(self, file_path: str) -> bool:
        """检测是否为代码文件"""
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go'}
        return file_path.suffix.lower() in code_extensions
    
    def get_language(self, file_path: str) -> str:
        """获取编程语言类型"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go'
        }
        return extension_map.get(file_path.suffix.lower(), 'unknown')
```

### 3. 自定义过滤器
```python
from autocoder.common.tokens.filters import FileFilter

class AdvancedFileFilter(FileFilter):
    def __init__(self):
        super().__init__()
        self.custom_rules = []
    
    def add_custom_rule(self, rule_func):
        """添加自定义过滤规则"""
        self.custom_rules.append(rule_func)
    
    def matches(self, file_path: str) -> bool:
        # 先检查基础规则
        if not super().matches(file_path):
            return False
        
        # 检查自定义规则
        return all(rule(file_path) for rule in self.custom_rules)

# 使用示例
filter = AdvancedFileFilter()
filter.add_custom_rule(lambda path: 'test' not in path.lower())  # 排除测试文件
filter.add_custom_rule(lambda path: path.stat().st_size < 1000000)  # 排除大文件
```

## 最佳实践

### 1. 性能优化
- 对于大型项目，启用并行处理
- 合理设置文件大小过滤范围
- 使用正确的正则表达式避免过度匹配
- 缓存频繁访问的统计结果

### 2. 内存管理
- 处理大文件时使用分块读取
- 及时释放不需要的文件句柄
- 监控内存使用情况
- 设置合理的超时时间

### 3. 错误处理
- 检查文件权限和可访问性
- 处理编码错误和格式异常
- 记录详细的错误日志
- 提供用户友好的错误提示

### 4. 使用建议
- 根据具体需求选择合适的tokenizer
- 定期更新tiktoken库版本
- 测试不同文件类型的处理效果
- 建立token使用量的监控机制

---

common.tokens模块提供了完整的token统计解决方案，通过智能的文件检测和高效的处理机制，为AI应用的成本控制和性能优化提供了重要的基础工具。 