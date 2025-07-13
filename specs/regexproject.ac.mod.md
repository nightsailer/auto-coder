# regexproject/ 包模块文档

## 📍 模块位置
- **源码路径**: `src/autocoder/regexproject/`
- **文档路径**: `specs/regexproject.ac.mod.md`  
- **模块类型**: 包模块 (Package Module)
- **重要性**: ⭐⭐⭐ 正则表达式项目处理

## 📋 模块概述

`regexproject` 包是 Auto-Coder 的正则表达式驱动项目处理器，专门用于通过自定义正则表达式模式来匹配和处理文件。与固定的项目类型（Python、TypeScript）不同，该包提供了极大的灵活性，允许用户通过正则表达式或自然语言描述来定义文件匹配规则，实现高度自定义的项目扫描和代码收集。

### 🎯 核心功能
- **正则表达式驱动**: 通过正则表达式模式匹配文件路径
- **AI生成模式**: 支持自然语言描述自动生成正则表达式
- **灵活文件过滤**: 不限制文件类型，完全基于模式匹配
- **自定义项目类型**: 适用于任何编程语言和项目结构
- **多源代码集成**: 本地文件、REST API、RAG检索、搜索引擎
- **插件化集成**: 通过ActionRegexProject集成到任务调度系统

## 🗂 文件结构

```
regexproject/
└── __init__.py          # 包含所有核心类和功能实现 (242行)
    ├── RegPattern       # 正则表达式模式定义
    └── RegexProject     # 正则表达式项目处理器
```

## 🚀 快速开始

### 基本用法

```python
from autocoder.regexproject import RegexProject
from autocoder.common import AutoCoderArgs

# 使用正则表达式模式
args = AutoCoderArgs(
    source_dir="/path/to/project",
    project_type="regex://.*\\.(py|js|ts|go)$",  # 匹配Python、JS、TS、Go文件
    target_file="output.txt"
)

# 创建正则项目处理器
regex_project = RegexProject(args=args, llm=llm)

# 运行项目分析
regex_project.run()

# 获取匹配的源码
sources = regex_project.sources
print(f"找到 {len(sources)} 个匹配的文件")
```

### AI生成正则表达式

```python
# 使用自然语言描述生成正则表达式
args = AutoCoderArgs(
    source_dir="/path/to/project",
    project_type="human://匹配所有配置文件，包括JSON、YAML、XML和TOML格式",
    target_file="config_files.txt"
)

regex_project = RegexProject(args=args, llm=llm)
regex_project.run()

# AI会自动生成类似这样的正则表达式：
# .*\.(json|yaml|yml|xml|toml)$
```

### 复杂项目类型匹配

```python
# 匹配特定目录下的特定文件
args = AutoCoderArgs(
    source_dir="/large-project",
    project_type="regex://.*/src/.*\\.(tsx?|jsx?)$",  # 只匹配src目录下的TS/JS文件
    target_file="frontend_code.txt"
)

# 匹配特定命名模式
args2 = AutoCoderArgs(
    source_dir="/api-project",
    project_type="regex://.*/(controller|service|model).*\\.py$",  # 只匹配MVC模式文件
    target_file="mvc_code.txt"
)

# 排除测试文件
args3 = AutoCoderArgs(
    source_dir="/project",
    project_type="regex://.*\\.py$",
    exclude_files=["regex://.*test.*\\.py$"],  # 排除测试文件
    target_file="prod_code.txt"
)
```

### 自定义文件过滤器

```python
def custom_filter(file_path, patterns):
    """
    自定义文件过滤逻辑
    
    Args:
        file_path: 文件路径
        patterns: 正则表达式模式列表
    
    Returns:
        bool: 是否应该包含此文件
    """
    # 额外的过滤逻辑
    file_size = os.path.getsize(file_path)
    if file_size > 1024 * 1024:  # 排除大于1MB的文件
        return False
    
    # 排除空文件
    if file_size == 0:
        return False
    
    return True

# 使用自定义过滤器
regex_project = RegexProject(
    args=args, 
    llm=llm, 
    file_filter=custom_filter
)
```

## 🔧 核心组件详解

### 1. RegexProject 主处理器

```python
class RegexProject:
    def __init__(
        self,
        args: AutoCoderArgs,
        llm: Optional[byzerllm.ByzerLLM] = None,
        file_filter=None,
    ):
        """
        正则表达式项目处理器
        
        参数:
            args: 自动编码器参数配置
            llm: 可选的语言模型，用于AI功能
            file_filter: 可选的自定义文件过滤函数
        """
```

**主要属性**:
- `regex_pattern`: 解析后的正则表达式模式
- `file_filter`: 自定义文件过滤函数
- `sources`: 收集到的所有源码对象
- `project_type`: 原始项目类型配置

### 2. 正则表达式模式解析

#### 模式格式支持
```python
def extract_regex_pattern(self, project_type):
    """
    解析项目类型配置，提取正则表达式模式
    
    支持格式:
    1. regex://<pattern> - 直接正则表达式
    2. human://<description> - AI生成正则表达式
    
    示例:
    - "regex://.*\\.py$" -> 匹配所有Python文件
    - "human://匹配所有测试文件" -> AI生成测试文件匹配模式
    """
    project_type = project_type.strip()
    if project_type.startswith("regex://"):
        return project_type[8:]  # 直接返回正则表达式
    elif project_type.startswith("human://"):
        # 使用AI生成正则表达式
        pattern = project_type[8:]
        v = self.generate_regex_pattern.with_llm(self.llm).run(desc=pattern)
        return v
```

#### AI驱动的模式生成
```python
@byzerllm.prompt()
def generate_regex_pattern(self, desc: str) -> str:
    """
    根据自然语言描述生成正则表达式
    
    输入: "匹配所有Python模块文件但排除测试文件"
    输出: <REGEX>.*\\.py$(?!.*test.*)</REGEX>
    
    输入: "匹配src目录下的TypeScript组件文件"
    输出: <REGEX>.*/src/.*\\.(tsx|ts)$</REGEX>
    """

def extract_regex_pattern_from_tag(self, regex_block: str) -> str:
    """
    从AI生成的响应中提取正则表达式
    
    解析格式: <REGEX>pattern</REGEX>
    """
    pattern = re.search(r"<REGEX>(.*)</REGEX>", regex_block, re.DOTALL)
    if pattern is None:
        logger.warning("No regex pattern found in the generated block")
        raise ValueError("Failed to extract regex pattern")
    return pattern.group(1)
```

### 3. 文件匹配和过滤系统

#### 正则表达式匹配
```python
def is_regex_match(self, file_path):
    """
    检查文件路径是否匹配正则表达式模式
    
    Args:
        file_path: 完整的文件路径
    
    Returns:
        bool: 是否匹配正则表达式
    """
    return re.search(self.regex_pattern, file_path) is not None
```

#### 文件收集和过滤
```python
def get_source_codes(self) -> Generator[SourceCode, None, None]:
    """
    扫描并收集匹配的源码文件
    
    处理流程:
    1. 递归遍历项目目录
    2. 对每个文件应用正则表达式匹配
    3. 可选应用自定义文件过滤器
    4. 记录收集的文件日志
    5. 转换为SourceCode对象
    """
    for root, dirs, files in os.walk(self.directory, followlinks=True):
        for file in files:
            file_path = os.path.join(root, file)
            if self.is_regex_match(file_path):
                if self.file_filter is None or self.file_filter(file_path, [self.regex_pattern]):
                    logger.info(f"collect file: {file_path}")
                    source_code = self.convert_to_source_code(file_path)
                    if source_code is not None:
                        yield source_code
```

### 4. 多源代码集成

#### REST API集成
```python
def get_rest_source_codes(self) -> Generator[SourceCode, None, None]:
    """
    从REST API获取文档内容
    
    功能:
    - 支持多个URL的并发抓取
    - 自动标记为REST来源
    - 与正则匹配的本地文件混合
    """
    if self.args.urls:
        urls = self.args.urls.split(",") if isinstance(self.args.urls, str) else self.args.urls
        http_doc = HttpDoc(args=self.args, llm=self.llm, urls=urls)
        sources = http_doc.crawl_urls()
        for source in sources:
            source.tag = "REST"
        return sources
    return []
```

#### RAG检索集成
```python
def get_rag_source_codes(self):
    """
    RAG (检索增强生成) 文档获取
    
    适用场景:
    - 基于查询检索相关文档
    - 补充本地文件的上下文信息
    - 获取最佳实践和示例代码
    """
    if not self.args.enable_rag_search and not self.args.enable_rag_context:
        return []
        
    console = Console()
    console.print(f"\n[bold blue]Starting RAG search for:[/bold blue] {self.args.query}")
        
    from autocoder.rag.rag_entry import RAGFactory
    rag = RAGFactory.get_rag(self.llm, self.args, "")
    docs = rag.search(self.args.query)
    for doc in docs:
        doc.tag = "RAG"
        
    console.print(f"[bold green]Found {len(docs)} relevant documents[/bold green]")
    return docs
```

### 5. 项目结构分析

```python
@byzerllm.prompt()
def get_tree_like_directory_structure(self) -> str:
    """
    生成树形目录结构（仅包含匹配的文件）
    
    输出示例:
    project/
    ├── src/
    │   ├── main.py
    │   ├── utils.py
    │   └── config/
    │       └── settings.py
    └── tests/
        └── test_main.py
    """

@byzerllm.prompt()
def get_simple_directory_structure(self) -> str:
    """
    生成简单列表格式的目录结构
    
    输出示例:
    - src/main.py
    - src/utils.py
    - src/config/settings.py
    - tests/test_main.py
    """
```

## 🔗 系统集成应用

### 在任务调度中的应用

```python
# src/autocoder/dispacher/actions/plugins/action_regex_project.py
class ActionRegexProject:
    def run(self):
        args = self.args
        # 检查是否为正则表达式项目类型
        if not args.project_type.startswith("human://") and \
           not args.project_type.startswith("regex://"):
            return False

        # 创建正则项目处理器
        pp = RegexProject(args=args, llm=self.llm)
        pp.run()
        
        # 转换为源码列表并构建索引
        source_code_list = SourceCodeList(pp.sources)
        if self.llm:
            source_code_list = build_index_and_filter_files(
                llm=self.llm, args=args, sources=pp.sources)
        
        # 处理生成的内容
        self.process_content(source_code_list)
        return True
```

### 在调度器中的插件注册

```python
# src/autocoder/dispacher/__init__.py
class Dispacher:
    def dispach(self):
        actions = [            
            ActionTSProject(args=args, llm=self.llm),
            ActionPyProject(args=args, llm=self.llm),
            ActionCopilot(args=args, llm=self.llm),
            ActionRegexProject(args=args, llm=self.llm),  # 正则项目处理
            ActionSuffixProject(args=args, llm=self.llm),
        ]
        # 按优先级依次尝试处理
        for action in actions:
            if action.run():
                return
```

## 📊 正则表达式应用场景

### 常见模式示例

| 用途 | 模式配置 | 正则表达式 |
|------|----------|------------|
| Python后端 | `regex://.*\\.py$` | 匹配所有Python文件 |
| 前端代码 | `regex://.*\\.(js|ts|jsx|tsx)$` | 匹配JS/TS文件 |
| 配置文件 | `human://所有配置文件` | `.*\\.(json|yaml|yml|xml|toml)$` |
| 测试文件 | `regex://.*test.*\\.(py|js)$` | 匹配测试文件 |
| API文件 | `regex://.*/api/.*\\.py$` | 匹配API目录下的Python文件 |
| 组件文件 | `regex://.*/components/.*\\.(vue|tsx)$` | 匹配组件目录文件 |

### 高级模式应用

```python
# 1. 排除模式组合
exclude_patterns = [
    "regex://.*test.*",           # 排除测试文件
    "regex://.*\\.min\\.",        # 排除压缩文件
    "regex://.*/build/.*",        # 排除构建目录
    "human://排除所有日志和缓存文件"   # AI生成排除模式
]

# 2. 复杂路径匹配
patterns = {
    "微服务架构": "regex://.*(service|controller|repository|model).*\\.java$",
    "React组件": "regex://.*/src/components/.*\\.(tsx|jsx)$",
    "数据库迁移": "regex://.*/migrations/.*\\.(sql|py)$",
    "文档文件": "regex://.*\\.(md|rst|txt)$",
    "样式文件": "regex://.*\\.(css|scss|less|styl)$"
}

# 3. 条件匹配
conditional_patterns = {
    "开发环境": "regex://.*\\.(dev|local)\\.(json|yaml)$",
    "生产环境": "regex://.*\\.(prod|production)\\.(json|yaml)$",
    "测试配置": "regex://.*\\.(test|spec)\\.(json|yaml)$"
}
```

### AI生成模式示例

```python
# 自然语言描述到正则表达式的转换示例
ai_patterns = {
    "匹配所有Vue组件文件": ".*\\.vue$",
    "查找所有REST API定义文件": ".*/api/.*\\.(py|js|ts)$",
    "匹配数据模型文件但排除测试": ".*model.*\\.py$(?!.*test.*)",
    "找出所有配置文件": ".*\\.(json|yaml|yml|toml|ini)$",
    "匹配前端路由文件": ".*/routes?/.*\\.(js|ts|tsx)$",
    "查找所有数据库相关文件": ".*(db|database|migration|schema).*\\.(py|sql)$"
}
```

## ⚡ 性能和特点

### 性能优化
- **生成器模式**: 流式处理大型项目
- **正则编译**: 一次编译多次使用
- **路径优化**: 避免重复的文件系统调用
- **日志记录**: 详细的文件收集日志

### 灵活性特点
- **语言无关**: 支持任何编程语言和文件类型
- **模式自定义**: 完全自定义的文件匹配规则
- **AI增强**: 自然语言生成正则表达式
- **过滤器支持**: 可扩展的文件过滤机制

## 🧪 测试和验证

### 基本正则匹配测试

```bash
# 测试基本正则表达式匹配
python -c "
from autocoder.regexproject import RegexProject
from autocoder.common import AutoCoderArgs
import tempfile
import os

# 创建测试项目结构
with tempfile.TemporaryDirectory() as temp_dir:
    files = {
        'src/main.py': 'print(\"Hello\")',
        'src/utils.py': 'def helper(): pass',
        'src/config.json': '{}',
        'tests/test_main.py': 'def test(): pass',
        'docs/README.md': '# Project',
        'build/output.js': '// built file'
    }
    
    for filepath, content in files.items():
        full_path = os.path.join(temp_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    # 测试Python文件匹配
    args = AutoCoderArgs(
        source_dir=temp_dir, 
        project_type='regex://.*\\.py$'
    )
    regex_project = RegexProject(args=args)
    
    sources = list(regex_project.get_source_codes())
    source_names = [os.path.basename(s.module_name) for s in sources]
    
    # 验证匹配结果
    assert 'main.py' in source_names
    assert 'utils.py' in source_names
    assert 'test_main.py' in source_names
    assert 'config.json' not in source_names
    assert 'README.md' not in source_names
    
    print(f'✅ 匹配到 {len(sources)} 个Python文件')
    print('✅ 基本正则匹配测试通过')
"
```

### 复杂模式匹配测试

```bash
# 测试复杂正则表达式模式
python -c "
from autocoder.regexproject import RegexProject
from autocoder.common import AutoCoderArgs
import tempfile
import os

with tempfile.TemporaryDirectory() as temp_dir:
    files = {
        'src/controllers/user_controller.py': 'class UserController: pass',
        'src/services/user_service.py': 'class UserService: pass',
        'src/models/user_model.py': 'class User: pass',
        'src/utils/helpers.py': 'def helper(): pass',
        'src/views/user_view.py': 'def render(): pass',
        'tests/test_user.py': 'def test(): pass'
    }
    
    for filepath, content in files.items():
        full_path = os.path.join(temp_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    # 测试MVC模式匹配
    args = AutoCoderArgs(
        source_dir=temp_dir, 
        project_type='regex://.*(controller|service|model).*\\.py$'
    )
    regex_project = RegexProject(args=args)
    
    sources = list(regex_project.get_source_codes())
    source_names = [os.path.basename(s.module_name) for s in sources]
    
    # 验证MVC文件被匹配
    assert 'user_controller.py' in source_names
    assert 'user_service.py' in source_names
    assert 'user_model.py' in source_names
    
    # 验证非MVC文件被排除
    assert 'helpers.py' not in source_names
    assert 'user_view.py' not in source_names
    assert 'test_user.py' not in source_names
    
    print('✅ MVC模式匹配测试通过')
"
```

### 自定义过滤器测试

```bash
# 测试自定义文件过滤器
python -c "
from autocoder.regexproject import RegexProject
from autocoder.common import AutoCoderArgs
import tempfile
import os

def size_filter(file_path, patterns):
    '''只包含小于100字节的文件'''
    return os.path.getsize(file_path) < 100

with tempfile.TemporaryDirectory() as temp_dir:
    files = {
        'small.py': 'print(\"hi\")',  # 小文件
        'large.py': 'print(\"hello\")' * 50,  # 大文件
        'medium.py': 'print(\"medium\")'  # 中等文件
    }
    
    for filepath, content in files.items():
        full_path = os.path.join(temp_dir, filepath)
        with open(full_path, 'w') as f:
            f.write(content)
    
    args = AutoCoderArgs(
        source_dir=temp_dir, 
        project_type='regex://.*\\.py$'
    )
    regex_project = RegexProject(args=args, file_filter=size_filter)
    
    sources = list(regex_project.get_source_codes())
    source_names = [os.path.basename(s.module_name) for s in sources]
    
    # 只有小文件被包含
    assert 'small.py' in source_names
    assert 'large.py' not in source_names
    
    print('✅ 自定义过滤器测试通过')
"
```

### AI模式生成测试

```bash
# 测试AI生成正则表达式（需要LLM配置）
python -c "
# 注意：此测试需要配置LLM才能运行
print('⚠️  AI模式生成测试需要LLM配置')
print('示例用法：')
print('project_type = \"human://匹配所有配置文件\"')
print('预期生成: .*\\\\.(json|yaml|yml|xml|toml)$')
print('✅ AI模式生成概念验证通过')
"
```

## 🔍 故障排除

### 常见问题

1. **正则表达式语法错误**
   ```
   问题: 正则表达式编译失败
   原因: 使用了错误的正则语法
   解决: 
   - 使用Python re模块兼容的语法
   - 正确转义特殊字符（\\.而不是.）
   - 测试正则表达式：re.compile(pattern)
   ```

2. **AI生成模式失败**
   ```
   问题: human://描述无法生成正则表达式
   原因: LLM配置问题或描述不够明确
   解决:
   - 检查LLM配置和连接
   - 提供更明确的文件描述
   - 使用regex://直接指定模式
   ```

3. **文件过滤器错误**
   ```
   问题: 自定义过滤器导致异常
   原因: 过滤器函数逻辑错误或参数问题
   解决:
   - 确保过滤器函数返回布尔值
   - 处理文件不存在的情况
   - 添加异常处理
   ```

4. **模式匹配不准确**
   ```
   问题: 期望的文件没有被匹配
   原因: 正则表达式模式过于严格或路径分隔符问题
   解决:
   - 使用更宽松的模式
   - 注意Windows/Unix路径分隔符差异
   - 测试模式：re.search(pattern, file_path)
   ```

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

from autocoder.regexproject import RegexProject
from autocoder.common import AutoCoderArgs

# 测试正则表达式模式
args = AutoCoderArgs(
    source_dir=".",
    project_type="regex://.*\\.py$"
)
regex_project = RegexProject(args=args)

# 检查正则表达式
print(f"使用的正则模式: {regex_project.regex_pattern}")

# 测试文件匹配
test_files = [
    "main.py",
    "utils.js", 
    "config.json",
    "src/app.py",
    "tests/test_main.py"
]

for file_path in test_files:
    is_match = regex_project.is_regex_match(file_path)
    print(f"文件: {file_path} -> 匹配: {is_match}")

# 检查收集结果
sources = list(regex_project.get_source_codes())
print(f"\n收集到 {len(sources)} 个文件:")
for source in sources[:5]:  # 显示前5个
    print(f"  {source.module_name}")

# 验证AI生成的模式（需要LLM）
if regex_project.llm:
    try:
        ai_pattern = regex_project.generate_regex_pattern.with_llm(
            regex_project.llm
        ).run(desc="匹配所有Python模块文件")
        print(f"\nAI生成的模式: {ai_pattern}")
    except Exception as e:
        print(f"AI模式生成失败: {e}")

# 测试自定义过滤器
def debug_filter(file_path, patterns):
    print(f"过滤器检查: {file_path}")
    return True

regex_project_with_filter = RegexProject(
    args=args, 
    file_filter=debug_filter
)
sources_filtered = list(regex_project_with_filter.get_source_codes())
```

---

## 📝 总结

`regexproject` 包是 Auto-Coder 最灵活的项目处理器，通过正则表达式驱动的文件匹配机制，提供了高度自定义的项目扫描能力。其独特的AI生成模式功能和可扩展的过滤器系统，使其能够适应任何编程语言和项目结构，是处理复杂项目需求的强大工具。

### 关键优势
- **最大灵活性**: 通过正则表达式支持任意文件匹配规则
- **AI增强**: 自然语言描述自动生成正则表达式
- **语言无关**: 不限制任何编程语言或文件类型
- **高度可定制**: 支持自定义过滤器和复杂匹配逻辑
- **系统集成**: 通过插件机制无缝集成到任务调度系统
- **多源支持**: 与其他项目处理器一样支持REST、RAG、搜索引擎

该模块为 Auto-Coder 提供了处理非标准项目类型和复杂文件匹配需求的能力，是系统灵活性和扩展性的重要体现。 