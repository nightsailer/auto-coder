# pyproject/ 包模块文档

## 📍 模块位置
- **源码路径**: `src/autocoder/pyproject/`
- **文档路径**: `specs/pyproject.ac.mod.md`  
- **模块类型**: 包模块 (Package Module)
- **重要性**: ⭐⭐⭐ Python项目处理

## 📋 模块概述

`pyproject` 包是 Auto-Coder 的 Python 项目处理核心模块，负责扫描、分析和处理 Python 项目文件。该包实现了智能的文件过滤机制、多源代码集成、项目结构分析，以及与外部资源（REST API、RAG、搜索引擎）的集成。

### 🎯 核心功能
- **Python项目扫描**: 递归扫描目录中的Python文件
- **智能文件过滤**: 支持正则表达式和AI生成的过滤规则
- **多源代码集成**: 本地文件、包导入、REST API、RAG检索
- **项目结构分析**: 生成树形和列表形式的项目结构
- **依赖分析**: 分析脚本的导入依赖关系
- **Git仓库支持**: 支持从远程仓库克隆和处理代码

## 🗂 文件结构

```
pyproject/
└── __init__.py          # 包含所有核心类和功能实现 (375行)
    ├── RegPattern       # 正则表达式模式定义
    ├── Level1PyProject  # 简单项目依赖分析
    └── PyProject        # 完整项目处理器
```

## 🚀 快速开始

### 基本用法

```python
from autocoder.pyproject import PyProject
from autocoder.common import AutoCoderArgs

# 创建项目参数
args = AutoCoderArgs(
    source_dir="/path/to/python/project",
    project_type="py",
    exclude_files=["regex://test_.*\\.py", "human://忽略临时文件"],
    target_file="output.txt"
)

# 创建Python项目处理器
py_project = PyProject(args=args, llm=llm)

# 运行项目分析
py_project.run(packages=["mypackage", "utils"])

# 获取所有源码
sources = py_project.sources
print(f"找到 {len(sources)} 个源文件")

# 生成项目结构
structure = py_project.get_tree_like_directory_structure()
print("项目结构:")
print(structure)
```

### 依赖分析模式

```python
from autocoder.pyproject import Level1PyProject

# 简单的依赖分析
analyzer = Level1PyProject(
    script_path="main.py",
    package_name="mypackage"
)

# 分析脚本依赖并自动实现
result = analyzer.run()
print("依赖分析结果:", result)
```

### 多源集成使用

```python
# 配置多种数据源
args = AutoCoderArgs(
    source_dir="/project",
    urls=["https://api.example.com/docs"],  # REST API文档
    enable_rag_search=True,                 # 启用RAG检索
    search_engine="bing",                   # 搜索引擎
    search_engine_token="your_token",
    query="Python数据处理最佳实践"
)

py_project = PyProject(args=args, llm=llm)
py_project.run()

# 查看不同来源的代码
for source in py_project.sources:
    print(f"文件: {source.module_name}")
    print(f"来源: {source.tag}")  # LOCAL, PACKAGE, REST, RAG, SEARCH
```

## 🔧 核心组件详解

### 1. PyProject 主处理器

```python
class PyProject:
    def __init__(self, args: AutoCoderArgs, llm: Optional[byzerllm.ByzerLLM] = None):
        """
        Python项目处理器
        
        参数:
            args: 自动编码器参数配置
            llm: 可选的语言模型，用于AI功能
        """
```

**主要属性**:
- `directory`: 项目根目录
- `sources`: 收集到的所有源码对象
- `exclude_patterns`: 编译后的排除模式
- `default_exclude_dirs`: 默认排除的目录

### 2. 智能文件过滤系统

```python
def parse_exclude_files(self, exclude_files):
    """
    解析排除文件模式
    
    支持格式:
    - "regex://pattern": 直接正则表达式
    - "human://description": AI生成正则表达式
    """

@byzerllm.prompt()
def generate_regex_pattern(self, desc: str) -> str:
    """
    根据自然语言描述生成正则表达式
    
    示例输入: "忽略所有测试文件和临时文件"
    示例输出: <REGEX>(test_.*|.*_temp.*|.*\\.tmp)\.py$</REGEX>
    """
```

**过滤模式示例**:
```python
exclude_files = [
    "regex://test_.*\\.py$",              # 直接正则表达式
    "human://忽略所有备份和临时文件",        # AI生成正则表达式
    "regex://__pycache__/.*",             # 缓存目录
    "human://排除示例和演示代码"            # 自然语言描述
]
```

### 3. 多源代码获取系统

#### 本地文件扫描
```python
def get_source_codes(self) -> Generator[SourceCode, None, None]:
    """
    扫描本地Python文件
    
    扫描策略:
    1. 递归遍历项目目录
    2. 过滤掉默认排除目录
    3. 应用用户定义的排除规则
    4. 只处理.py文件
    5. 支持符号链接跟随
    """
    for root, dirs, files in os.walk(self.directory, followlinks=True):
        dirs[:] = [d for d in dirs if d not in self.default_exclude_dirs]
        for file in files:
            if self.is_python_file(file_path) and not self.should_exclude(file_path):
                yield self.convert_to_source_code(file_path)
```

#### 包模块导入
```python
def get_package_source_codes(self, package_name: str) -> Generator[SourceCode, None, None]:
    """
    获取指定Python包的源码
    
    工作流程:
    1. 导入包模块
    2. 获取包路径
    3. 遍历包中的所有模块
    4. 读取模块源码
    5. 标记为PACKAGE来源
    """
    package = importlib.import_module(package_name)
    package_path = os.path.dirname(package.__file__)
    
    for _, name, _ in pkgutil.iter_modules([package_path]):
        module_name = f"{package_name}.{name}"
        # 获取并转换模块源码
```

#### REST API文档获取
```python
def get_rest_source_codes(self) -> Generator[SourceCode, None, None]:
    """
    从REST API获取文档
    
    支持功能:
    - 多URL并发抓取
    - 自动内容解析
    - 标记为REST来源
    """
    if self.args.urls:
        http_doc = HttpDoc(args=self.args, llm=self.llm, urls=urls)
        sources = http_doc.crawl_urls()
        for source in sources:
            source.tag = "REST"
        return sources
```

#### RAG检索集成
```python
def get_rag_source_codes(self):
    """
    RAG (检索增强生成) 文档获取
    
    功能:
    - 基于查询检索相关文档
    - 支持多种RAG配置
    - 智能相关性排序
    - 标记为RAG来源
    """
    from autocoder.rag.rag_entry import RAGFactory
    rag = RAGFactory.get_rag(self.llm, self.args, "")
    docs = rag.search(self.args.query)
    for doc in docs:
        doc.tag = "RAG"
    return docs
```

#### 搜索引擎集成
```python
def get_search_source_codes(self):
    """
    搜索引擎内容获取
    
    支持引擎:
    - Bing Search API
    - Google Search API
    
    功能:
    - 基于查询搜索相关内容
    - 自动上下文提取
    - 标记为SEARCH来源
    """
    if self.args.search_engine and self.args.search_engine_token:
        searcher = Search(args=self.args, llm=self.llm, 
                         search_engine=search_engine)
        search_context = searcher.answer_with_the_most_related_context(search_query)
        return [SourceCode(module_name="SEARCH_ENGINE", 
                          source_code=search_context, tag="SEARCH")]
```

### 4. 项目结构分析

```python
@byzerllm.prompt()
def get_tree_like_directory_structure(self) -> str:
    """
    生成树形目录结构
    
    输出格式:
    project_root/
        ├── main.py
        ├── utils/
        │   ├── __init__.py
        │   └── helpers.py
        └── tests/
            └── test_main.py
    """
    
@byzerllm.prompt()
def get_simple_directory_structure(self) -> str:
    """
    生成简单列表格式的目录结构
    
    输出格式:
    - main.py
    - utils/__init__.py
    - utils/helpers.py
    - tests/test_main.py
    """
```

### 5. Level1PyProject 依赖分析器

```python
class Level1PyProject:
    def __init__(self, script_path, package_name):
        """
        简单的Python脚本依赖分析器
        
        用于分析单个脚本的包依赖关系
        """
    
    def get_imports_from_script(self, file_path):
        """
        从脚本中提取导入语句
        
        使用AST解析:
        1. 解析Python文件为AST
        2. 遍历所有导入节点
        3. 提取import和from import语句
        """
        tree = ast.parse(script, filename=file_path)
        imports = [node for node in ast.walk(tree) 
                  if isinstance(node, (ast.Import, ast.ImportFrom))]
    
    def filter_imports(self, imports, package_name):
        """
        过滤指定包的导入
        
        只保留以package_name开头的导入
        """
    
    @byzerllm.prompt(render="jinja")
    def auto_implement(self, instruction: str, sources: List[Dict[str, Any]]) -> str:
        """
        基于依赖源码自动实现功能
        
        使用Jinja2模板渲染源码上下文
        """
```

## 🔗 系统集成应用

### 在任务调度中的应用

```python
# src/autocoder/dispacher/actions/action.py
class ActionPyProject(BaseAction):
    def run(self):
        if args.project_type != "py":
            return False
        
        # 创建Python项目处理器
        pp = PyProject(args=self.args, llm=self.llm)
        
        # 运行项目分析，包含指定包
        pp.run(packages=args.py_packages.split(",") if args.py_packages else [])
        
        # 转换为源码列表
        source_code_list = SourceCodeList(pp.sources)
        
        # 构建索引并过滤文件
        if self.llm:
            source_code_list = build_index_and_filter_files(
                llm=self.llm, args=args, sources=pp.sources)
        
        # 处理生成的内容
        self.process_content(source_code_list)
```

### 在自动工具中的应用

```python
# src/autocoder/agent/auto_tool.py
class AutoTool:
    def __init__(self, args: AutoCoderArgs, llm: byzerllm.ByzerLLM):
        if self.args.project_type == "py":
            self.pp = PyProject(args=self.args, llm=llm)
    
    def get_tree_like_directory_structure(self) -> str:
        self.pp.run()
        return self.pp.get_tree_like_directory_structure.prompt()
```

### 在索引构建中的应用

```python
# src/autocoder/index/for_command.py
def index_command(args, llm):
    if args.project_type == "py":
        pp = PyProject(args=args, llm=llm)
    pp.run()
    sources = pp.sources
    index_manager = IndexManager(llm=llm, sources=sources, args=args)
    index_manager.build_index()
```

### 在聊天代理中的应用

```python
# src/autocoder/agent/entry_command_agent/chat.py
class ChatAgent:
    def _build_conversations(self, commands_info, chat_history):
        if self.args.project_type == "py":
            pp = PyProject(args=self.args, llm=self.llm)
        pp.run()
        sources = pp.sources
        
        # 应用模型过滤器
        filtered_sources = []
        for source in sources:
            if model_filter.is_accessible(source.module_name):
                filtered_sources.append(source)
        
        # 构建对话上下文
        source_code_list = build_index_and_filter_files(
            llm=self.llm, args=self.args, sources=filtered_sources)
```

## 📊 文件处理特性

### 支持的文件格式
```python
def is_python_file(self, file_path):
    """只处理.py文件"""
    return file_path.endswith(".py")
```

### 特殊读取模式
```python
def read_file_content(self, file_path):
    """
    支持多种读取模式
    
    strict_diff模式: 为每行添加行号
    普通模式: 直接读取文件内容
    """
    if self.args.auto_merge == "strict_diff":
        result = []
        for line_number, line in FileUtils.read_file_with_line_numbers(file_path, line_number_start=1):
            result.append(f"{line_number}:{line}")
        return "\n".join(result)
    return FileUtils.read_file(file_path)
```

### 默认排除目录
```python
default_exclude_dirs = [
    ".git", ".svn", ".hg",          # 版本控制
    "build", "dist",                # 构建产物
    "__pycache__",                  # Python缓存
    "node_modules",                 # Node.js依赖
    ".auto-coder",                  # 工具目录
    "actions",                      # 动作目录
    ".vscode", ".idea",             # IDE配置
    "venv",                         # 虚拟环境
]
```

## ⚡ 性能和扩展特点

### 性能优化
- **生成器模式**: 使用Generator避免内存占用过大
- **延迟加载**: 只在需要时读取文件内容
- **符号链接支持**: followlinks=True支持符号链接
- **并发抓取**: REST API支持并发请求

### 扩展能力
- **多源集成**: 支持本地、远程、API、RAG多种数据源
- **智能过滤**: AI生成正则表达式，支持自然语言描述
- **格式适配**: 支持不同的代码生成格式需求
- **标签分类**: 为不同来源的代码添加标签便于识别

## 🧪 测试和验证

### 基本功能测试

```bash
# 测试Python项目扫描
python -c "
from autocoder.pyproject import PyProject
from autocoder.common import AutoCoderArgs
import tempfile
import os

# 创建测试项目结构
with tempfile.TemporaryDirectory() as temp_dir:
    # 创建Python文件
    main_py = os.path.join(temp_dir, 'main.py')
    with open(main_py, 'w') as f:
        f.write('import os\nprint(\"Hello World\")')
    
    utils_dir = os.path.join(temp_dir, 'utils')
    os.makedirs(utils_dir)
    utils_py = os.path.join(utils_dir, '__init__.py')
    with open(utils_py, 'w') as f:
        f.write('def helper(): pass')
    
    # 测试项目扫描
    args = AutoCoderArgs(source_dir=temp_dir, project_type='py')
    py_project = PyProject(args=args)
    
    sources = list(py_project.get_source_codes())
    print(f'✅ 扫描到 {len(sources)} 个Python文件')
    assert len(sources) == 2
    print('✅ Python项目扫描测试通过')
"
```

### 文件过滤测试

```bash
# 测试智能过滤功能
python -c "
from autocoder.pyproject import PyProject
from autocoder.common import AutoCoderArgs
import tempfile
import os
import re

with tempfile.TemporaryDirectory() as temp_dir:
    # 创建测试文件
    files = ['main.py', 'test_main.py', 'backup_old.py', 'utils.py']
    for filename in files:
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f'# {filename}')
    
    # 测试正则表达式过滤
    args = AutoCoderArgs(
        source_dir=temp_dir,
        project_type='py',
        exclude_files=['regex://(test_|backup_).*\\.py$']
    )
    py_project = PyProject(args=args)
    
    sources = list(py_project.get_source_codes())
    source_names = [os.path.basename(s.module_name) for s in sources]
    
    assert 'main.py' in source_names
    assert 'utils.py' in source_names
    assert 'test_main.py' not in source_names
    assert 'backup_old.py' not in source_names
    
    print('✅ 文件过滤测试通过')
"
```

### 项目结构测试

```bash
# 测试项目结构生成
python -c "
from autocoder.pyproject import PyProject
from autocoder.common import AutoCoderArgs
import tempfile
import os

with tempfile.TemporaryDirectory() as temp_dir:
    # 创建复杂项目结构
    structure = {
        'main.py': 'main content',
        'utils/__init__.py': 'utils init',
        'utils/helpers.py': 'helper functions',
        'tests/test_main.py': 'test content'
    }
    
    for filepath, content in structure.items():
        full_path = os.path.join(temp_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    args = AutoCoderArgs(source_dir=temp_dir, project_type='py')
    py_project = PyProject(args=args)
    
    # 测试树形结构
    tree_structure = py_project.get_tree_like_directory_structure()
    print('树形结构:', tree_structure)
    
    # 测试简单结构
    simple_structure = py_project.get_simple_directory_structure()
    print('简单结构:', simple_structure)
    
    print('✅ 项目结构生成测试通过')
"
```

### 依赖分析测试

```bash
# 测试Level1PyProject依赖分析
python -c "
from autocoder.pyproject import Level1PyProject
import tempfile
import os

with tempfile.TemporaryDirectory() as temp_dir:
    # 创建测试脚本
    script_path = os.path.join(temp_dir, 'test_script.py')
    with open(script_path, 'w') as f:
        f.write('''
import os
import sys
from mypackage import module1
from mypackage.submodule import function1
import other_package
''')
    
    # 测试依赖分析
    analyzer = Level1PyProject(script_path, 'mypackage')
    imports, script = analyzer.get_imports_from_script(script_path)
    filtered = analyzer.filter_imports(imports, 'mypackage')
    
    print(f'总导入数: {len(imports)}')
    print(f'过滤后导入: {filtered}')
    
    assert 'mypackage' in filtered or 'mypackage.submodule' in filtered
    print('✅ 依赖分析测试通过')
"
```

## 🔍 故障排除

### 常见问题

1. **文件扫描失败**
   ```
   问题: Failed to read file: permission denied
   原因: 文件权限不足或文件被占用
   解决: 检查文件权限，确保可读访问
   ```

2. **正则表达式生成失败**
   ```
   问题: Fail to generate regex pattern, try again
   原因: AI模型无法理解自然语言描述
   解决: 
   - 使用更清晰的描述
   - 直接使用regex://模式
   - 检查LLM配置是否正确
   ```

3. **包导入失败**
   ```
   问题: Package not found
   原因: 指定的包不在Python路径中
   解决: 
   - 确保包已安装
   - 检查PYTHONPATH设置
   - 使用绝对包名
   ```

4. **Git克隆失败**
   ```
   问题: Repository clone failed
   原因: 网络问题或权限不足
   解决:
   - 检查网络连接
   - 验证Git凭据
   - 确保目标目录可写
   ```

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

from autocoder.pyproject import PyProject
from autocoder.common import AutoCoderArgs

args = AutoCoderArgs(source_dir=".", project_type="py")
py_project = PyProject(args=args)

# 检查排除模式
print("排除模式:", py_project.exclude_patterns)

# 逐步检查文件扫描
for source in py_project.get_source_codes():
    print(f"文件: {source.module_name}")
    print(f"大小: {len(source.source_code)} 字符")
    print(f"标签: {getattr(source, 'tag', 'LOCAL')}")

# 检查项目结构
structure = py_project.get_tree_like_directory_structure()
print("项目结构:", structure)

# 检查多源集成
print("REST源码数:", len(list(py_project.get_rest_source_codes())))
print("RAG源码数:", len(list(py_project.get_rag_source_codes())))
```

---

## 📝 总结

`pyproject` 包是 Auto-Coder 处理 Python 项目的专业工具，通过智能文件过滤、多源代码集成和项目结构分析，为 Python 开发者提供了强大的项目处理能力。其独特的AI驱动过滤机制和丰富的数据源集成使其在处理复杂Python项目时表现出色。

### 关键优势
- **智能过滤**: AI生成正则表达式，支持自然语言描述
- **多源集成**: 本地文件、包导入、REST API、RAG、搜索引擎
- **结构分析**: 详细的项目结构和依赖关系分析
- **灵活配置**: 丰富的配置选项和排除规则
- **系统集成**: 深度集成到Auto-Coder的各个核心功能中

该模块为 Python 项目的自动化代码生成和分析提供了坚实的基础设施支持。 