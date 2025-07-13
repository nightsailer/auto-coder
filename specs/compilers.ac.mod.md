# compilers.ac.mod.md

## 模块信息
- **模块名称**: compilers
- **模块类型**: 包模块 (Package Module)
- **主要功能**: 多语言代码编译和检查系统

## 核心功能

### 编译器系统架构
- **多语言支持**: 支持Python、Java、JavaScript/TypeScript、React、Vue.js等主流编程语言
- **统一接口**: 通过BaseCompiler抽象类提供统一的编译接口
- **工厂模式**: 使用CompilerFactory根据文件类型或语言自动选择合适的编译器
- **配置化编译**: 支持通过YAML配置文件定义自定义编译器

### 编译器类型

#### 1. 内置编译器
- **PythonCompiler**: Python语法检查和导入验证
- **JavaCompiler**: Java代码编译和错误检测
- **ReactJSCompiler**: React/JavaScript/TypeScript编译
- **VueCompiler**: Vue.js组件编译和检查

#### 2. 配置化编译器
- **ProvidedCompiler**: 基于YAML配置的通用编译器
- **NormalCompiler**: 项目级编译器封装
- **ShadowCompiler**: 影子文件编译器，用于路径映射

### 配置管理
- **CompilerConfigManager**: 编译器配置文件管理
- **CompilerConfigAPI**: 高级API接口，提供RESTful风格的配置管理
- **YAML配置**: 支持.auto-coder/projects/compiler.yml配置文件

## 关键组件

### 1. 基础抽象类 (BaseCompiler)
```python
class BaseCompiler(ABC):
    def compile_file(self, file_path: str) -> FileCompilationResult
    def compile_project(self, project_path: str) -> ProjectCompilationResult
    def _check_dependencies(self) -> bool
```

### 2. 编译器工厂 (CompilerFactory)
```python
class CompilerFactory:
    @classmethod
    def create_compiler(cls, language: str = None, file_path: str = None) -> BaseCompiler
    
    @classmethod
    def compile_file(cls, file_path: str) -> Dict[str, Any]
    
    @classmethod
    def compile_project(cls, project_path: str) -> Dict[str, Any]
```

### 3. 编译结果模型
- **FileCompilationResult**: 单文件编译结果
- **ProjectCompilationResult**: 项目编译结果
- **CompilationError**: 编译错误信息
- **CompilationErrorPosition**: 错误位置信息

### 4. 配置管理器 (CompilerConfigManager)
```python
class CompilerConfigManager:
    def read(self) -> Dict[str, Any]
    def write(self, config: Dict[str, Any]) -> bool
    def add_compiler(self, compiler_config: Dict[str, Any]) -> bool
    def get_compiler_by_name(self, name: str) -> Optional[Dict[str, Any]]
    def update_compiler(self, name: str, updates: Dict[str, Any]) -> bool
    def delete_compiler(self, name: str) -> bool
```

## 使用场景

### 1. 语言检测和编译
```python
# 自动检测语言并编译
compiler = CompilerFactory.create_compiler(file_path="main.py")
result = compiler.compile_file("main.py")

# 指定语言编译
compiler = CompilerFactory.create_compiler(language="python")
result = compiler.compile_project("/path/to/project")
```

### 2. 配置化编译
```yaml
# compiler.yml
compilers:
  - name: "Frontend Build"
    type: "frontend"
    working_dir: "src/frontend"
    command: "npm"
    args: ["run", "build"]
    triggers: [".js", ".ts", ".jsx", ".tsx"]
    extract_regex: "(?P<severity>error|warning)\\s+in\\s+(?P<file>[^:]+):(?P<line>\\d+):(?P<column>\\d+)\\s*-\\s*(?P<message>.+)"
```

### 3. 编译器管理
```python
# 添加新编译器配置
config_manager = CompilerConfigManager()
config_manager.add_compiler({
    "name": "TypeScript Compiler",
    "type": "frontend",
    "working_dir": "src",
    "command": "tsc",
    "args": ["--noEmit"],
    "triggers": [".ts", ".tsx"]
})

# 使用API管理
api = CompilerConfigAPI()
response = api.create_compiler(
    name="Custom Compiler",
    compiler_type="backend",
    working_dir="backend",
    command="mvn",
    args=["compile"],
    triggers=[".java"]
)
```

## 技术特性

### 1. 错误处理和报告
- **结构化错误信息**: 包含文件路径、行号、列号、错误级别和消息
- **正则表达式提取**: 支持自定义正则表达式从编译输出中提取错误信息
- **错误级别分类**: 支持error、warning、info等不同级别

### 2. 依赖检查
- **运行时检查**: 自动检查编译器依赖是否安装
- **版本验证**: 验证编译器工具的版本兼容性
- **环境配置**: 支持不同环境下的编译器配置

### 3. 异步和并发
- **非阻塞编译**: 支持异步编译操作
- **批量处理**: 支持批量编译多个文件或项目
- **进度跟踪**: 提供编译进度和状态信息

### 4. 扩展性
- **插件架构**: 支持自定义编译器插件
- **配置驱动**: 通过配置文件扩展新的编译器
- **钩子机制**: 支持编译前后的钩子函数

## 集成点

### 与其他模块的关系
- **linters模块**: 配合代码检查功能
- **common模块**: 使用通用工具和配置
- **utils模块**: 使用项目结构分析工具
- **shadows模块**: 支持影子文件编译

### 外部工具集成
- **npm/yarn**: JavaScript/TypeScript项目编译
- **maven/gradle**: Java项目构建
- **webpack/vite**: 前端项目打包
- **tsc**: TypeScript编译器
- **vue-cli**: Vue.js项目构建

## 配置文件结构

### compiler.yml格式
```yaml
compilers:
  - name: "编译器名称"
    type: "编译器类型"
    working_dir: "工作目录"
    command: "执行命令"
    args: ["参数列表"]
    triggers: ["触发文件扩展名"]
    extract_regex: "错误提取正则表达式"
```

### 配置管理API
- **GET /compilers**: 获取所有编译器配置
- **POST /compilers**: 创建新编译器配置
- **PUT /compilers/{name}**: 更新编译器配置
- **DELETE /compilers/{name}**: 删除编译器配置

## 最佳实践

### 1. 编译器选择
- 优先使用语言特定的编译器
- 对于复杂项目使用配置化编译器
- 根据项目结构自动检测编译器类型

### 2. 错误处理
- 配置合适的错误提取正则表达式
- 设置合理的超时和重试机制
- 提供详细的错误上下文信息

### 3. 性能优化
- 使用增量编译减少编译时间
- 并行编译多个独立模块
- 缓存编译结果避免重复编译

### 4. 配置管理
- 使用版本控制管理编译器配置
- 为不同环境设置不同的编译配置
- 定期更新编译器工具版本

## 模块依赖

### 内部依赖
- `autocoder.common`: 基础工具和配置
- `autocoder.utils.project_structure`: 项目结构分析
- `autocoder.shadows`: 影子文件管理

### 外部依赖
- `pydantic`: 数据模型验证
- `yaml`: YAML配置文件解析
- `subprocess`: 外部命令执行
- `pathlib`: 路径操作

## 扩展指南

### 1. 添加新语言支持
```python
class CustomCompiler(BaseCompiler):
    def get_supported_extensions(self) -> List[str]:
        return ['.custom']
    
    def compile_file(self, file_path: str) -> FileCompilationResult:
        # 实现编译逻辑
        pass
```

### 2. 自定义错误提取
```python
extract_regex = r"(?P<file>[^:]+):(?P<line>\d+):(?P<column>\d+):\s*(?P<severity>\w+):\s*(?P<message>.*)"
```

### 3. 编译器配置模板
```python
def create_custom_compiler_config():
    return {
        "name": "Custom Compiler",
        "type": "custom",
        "working_dir": ".",
        "command": "custom-compiler",
        "args": ["--check"],
        "triggers": [".custom"],
        "extract_regex": "custom_pattern"
    }
```

---

compilers模块提供了完整的多语言编译和检查解决方案，支持从简单的语法检查到复杂的项目构建，通过统一的接口和灵活的配置系统，为自动化代码质量管理提供了强大的基础设施。 