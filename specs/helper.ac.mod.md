# helper/ 包模块文档

## 📍 模块位置
- **源码路径**: `src/autocoder/helper/`
- **文档路径**: `specs/helper.ac.mod.md`  
- **模块类型**: 包模块 (Package Module)
- **重要性**: ⭐⭐ 辅助工具集

## 📋 模块概述

`helper` 包是 Auto-Coder 的辅助工具集，提供了用于创建示例项目、生成演示文档和支持开发测试的实用工具。该包主要服务于 Auto-Coder 的演示、测试和快速原型开发场景，帮助用户快速创建结构化的示例项目和生成用于 RAG 系统的示例文档。

### 🎯 核心功能
- **项目创建器**: 自动创建Python和React TypeScript示例项目
- **RAG文档生成**: 创建和管理用于RAG系统的示例代码文档
- **Git集成**: 自动初始化Git仓库和提交
- **Actions配置**: 自动生成Auto-Coder配置文件
- **多项目类型支持**: 支持Python、React TypeScript等项目类型
- **工厂模式设计**: 易于扩展新的项目类型

## 🗂 文件结构

```
helper/
├── __init__.py              # 包初始化文件 (0行)
├── project_creator.py       # 项目创建工具 (752行)
│   ├── FileCreator          # 文件创建抽象基类
│   ├── PythonFileCreator    # Python项目文件创建器
│   ├── ReactJSFileCreator   # React TypeScript项目文件创建器
│   ├── FileCreatorFactory   # 文件创建器工厂
│   └── ProjectCreator       # 项目创建主控制器
└── rag_doc_creator.py       # RAG文档创建工具 (142行)
    ├── create_sample_files  # 创建示例代码文件
    ├── update_sample_file   # 更新示例文件
    ├── add_sample_file      # 新增示例文件
    └── delete_sample_file   # 删除示例文件
```

## 🚀 快速开始

### 项目创建器基本用法

```python
from autocoder.helper.project_creator import ProjectCreator

# 创建Python计算器项目
python_creator = ProjectCreator(
    project_name="my_python_calculator",
    project_type="python",
    git_init=True,
    query="给计算器添加乘法和除法功能"
)

project_path = python_creator.create_project()
print(f"Python项目已创建: {project_path}")
```

### React TypeScript项目创建

```python
# 创建React TypeScript计算器项目
react_creator = ProjectCreator(
    project_name="my_react_calculator",
    project_type="react",
    git_init=True,
    git_user_name="Your Name",
    git_user_email="your.email@example.com",
    query="为React计算器添加历史记录功能"
)

project_path = react_creator.create_project()
print(f"React项目已创建: {project_path}")
```

### RAG文档创建器使用

```python
from autocoder.helper.rag_doc_creator import (
    create_sample_files, 
    add_sample_file, 
    update_sample_file
)

# 创建示例代码文件
base_dir = "sample_code"
create_sample_files(base_dir)

# 添加新的示例文件
new_content = '''
class FileManager:
    def __init__(self):
        self.files = []
    
    def add_file(self, filename: str):
        """添加文件到管理列表"""
        self.files.append(filename)
    
    def list_files(self) -> list:
        """列出所有管理的文件"""
        return self.files.copy()
'''

add_sample_file(base_dir, "file_manager.py", new_content)
```

### 完整项目创建流程

```python
import os
from autocoder.helper.project_creator import ProjectCreator

def create_demo_projects():
    """创建演示项目的完整流程"""
    
    # 配置项目参数
    projects = [
        {
            "name": "python_calculator_demo",
            "type": "python",
            "query": "实现一个支持四则运算和历史记录的计算器",
            "model": "claude3_5_sonnet"
        },
        {
            "name": "react_calculator_demo", 
            "type": "react",
            "query": "创建一个现代化的React计算器界面",
            "model": "claude3_5_sonnet"
        }
    ]
    
    created_projects = []
    
    for project_config in projects:
        creator = ProjectCreator(
            project_name=project_config["name"],
            project_type=project_config["type"],
            git_init=True,
            create_actions=True,
            query=project_config["query"],
            model=project_config["model"]
        )
        
        project_path = creator.create_project()
        created_projects.append(project_path)
        print(f"✅ 创建项目: {project_path}")
    
    return created_projects

# 运行演示
demo_projects = create_demo_projects()
```

## 🔧 核心组件详解

### 1. ProjectCreator 主控制器

```python
class ProjectCreator:
    def __init__(
        self, 
        project_name: str = "test_project",
        project_type: str = "python",
        git_init: bool = True,
        git_user_email: str = "example@example.com",
        git_user_name: str = "Example User",
        create_actions: bool = True,
        query: str = "给计算器添加乘法和除法功能",
        model: str = "v3_chat",
        product_mode: str = "lite"
    ):
        """
        项目创建器主控制器
        
        参数:
            project_name: 项目名称和目录名
            project_type: 项目类型 ('python'/'py' 或 'react'/'js')
            git_init: 是否初始化Git仓库
            git_user_email: Git用户邮箱
            git_user_name: Git用户名
            create_actions: 是否创建actions配置文件
            query: 默认查询内容（用于actions配置）
            model: 使用的模型名称
            product_mode: 模型的产品模式
        """
```

**核心功能流程**:
```python
def create_project(self) -> str:
    """
    创建完整项目的流程
    
    1. 创建项目目录
    2. 使用对应的文件创建器生成项目文件
    3. 创建actions配置文件（可选）
    4. 初始化Git仓库（可选）
    5. 返回项目绝对路径
    """
    # 1. 创建和清理项目目录
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    os.makedirs(project_dir)
    
    # 2. 使用文件创建器创建项目文件
    self.file_creator.create_files(project_dir)
    
    # 3. 创建配置文件
    if self.create_actions:
        self._create_actions_files(project_dir)
    
    # 4. 初始化Git仓库
    if self.git_init:
        self._init_git_repo(project_dir)
    
    return os.path.abspath(project_dir)
```

### 2. 文件创建器架构

#### 抽象基类设计
```python
class FileCreator(ABC):
    """文件创建抽象基类，定义创建项目文件的接口"""
    
    @abstractmethod
    def create_files(self, project_dir: str) -> None:
        """在项目目录中创建必要的文件"""
        pass
    
    @abstractmethod
    def get_file_paths(self, project_dir: str) -> List[str]:
        """获取创建的文件路径列表，用于配置文件中引用"""
        pass
    
    @property
    @abstractmethod
    def project_type(self) -> str:
        """返回项目类型标识"""
        pass
```

#### Python项目文件创建器
```python
class PythonFileCreator(FileCreator):
    """Python计算器项目文件创建器"""
    
    def create_files(self, project_dir: str) -> None:
        """
        创建Python项目文件结构:
        - calculator.py: 计算器类实现
        - main.py: 主程序入口
        """
        self._create_calculator_file(project_dir)
        self._create_main_file(project_dir)
    
    def _create_calculator_file(self, project_dir: str) -> None:
        """创建计算器示例文件"""
        calculator_content = """
class Calculator:
    def __init__(self):
        self.history = []
        
    def add(self, a, b):
        '''加法函数'''
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
        
    def subtract(self, a, b):
        '''减法函数'''
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
        
    def clear_history(self):
        '''清除历史记录'''
        self.history = []
"""
    
    @property
    def project_type(self) -> str:
        return "py"
```

#### React TypeScript项目文件创建器
```python
class ReactJSFileCreator(FileCreator):
    """Vite + React TypeScript计算器项目文件创建器"""
    
    def create_files(self, project_dir: str) -> None:
        """
        创建完整的Vite + React TypeScript项目:
        - package.json: 项目依赖配置
        - vite.config.ts: Vite构建配置  
        - tsconfig.json: TypeScript配置
        - src/App.tsx: 主应用组件
        - src/Calculator.tsx: 计算器组件
        - src/main.tsx: 应用入口
        - 样式文件和配置文件
        """
        self._create_package_json(project_dir)
        self._create_vite_config(project_dir)
        self._create_tsconfig_json(project_dir)
        
        # 创建src目录和组件
        src_dir = os.path.join(project_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        self._create_app_tsx(src_dir)
        self._create_calculator_component(src_dir)
        self._create_main_tsx(src_dir)
    
    def _create_calculator_component(self, src_dir: str) -> None:
        """创建React计算器组件"""
        calculator_content = """
import { useState } from 'react'
import './Calculator.css'

const Calculator: React.FC = () => {
  const [display, setDisplay] = useState<string>('0')
  const [equation, setEquation] = useState<string>('')

  const handleNumber = (num: string) => {
    if (display === '0') {
      setDisplay(num)
    } else {
      setDisplay(display + num)
    }
  }

  const handleOperator = (operator: string) => {
    setEquation(display + ' ' + operator + ' ')
    setDisplay('0')
  }

  const handleEqual = () => {
    try {
      const result = eval(equation + display)
      setDisplay(result.toString())
      setEquation('')
    } catch (error) {
      setDisplay('Error')
      setEquation('')
    }
  }

  // ... 更多计算器逻辑
}
"""
    
    @property  
    def project_type(self) -> str:
        return "tsx"
```

### 3. 工厂模式支持

```python
class FileCreatorFactory:
    """文件创建器工厂类，支持扩展新的项目类型"""
    
    @staticmethod
    def get_creator(project_type: str) -> FileCreator:
        """
        根据项目类型返回对应的文件创建器
        
        支持的项目类型:
        - 'python'/'py': PythonFileCreator
        - 'react'/'reactjs'/'js': ReactJSFileCreator
        
        扩展新类型：
        1. 创建新的FileCreator子类
        2. 在此方法中添加类型映射
        """
        project_type = project_type.lower()
        
        if project_type in ('python', 'py'):
            return PythonFileCreator()
        elif project_type in ('react', 'reactjs', 'js'):
            return ReactJSFileCreator()
        else:
            raise ValueError(f"不支持的项目类型: {project_type}")
```

### 4. Actions配置文件生成

#### 基础配置文件
```python
def _create_base_yml(self, project_dir: str, base_dir: str) -> None:
    """
    创建Auto-Coder基础配置文件
    
    生成路径: actions/base/base.yml
    
    配置内容:
    - source_dir: 项目源码目录
    - target_file: 输出文件路径
    - project_type: 项目类型
    - model: 使用的AI模型
    - 索引和过滤配置
    """
    base_yml_content = f"""source_dir: {abs_project_dir}
target_file: {os.path.join(abs_project_dir, "output.txt")}
project_type: {self.file_creator.project_type}

model: {self.model}
index_model: {self.model}

index_filter_level: 1
index_model_max_input_length: 100000
model_max_input_length: 120000
index_filter_workers: 100
index_build_workers: 100

skip_build_index: false
execute: true
auto_merge: editblock
human_as_model: false
"""
```

#### Chat Action配置
```python
def _create_chat_action_yml(self, project_dir: str, actions_dir: str) -> None:
    """
    创建Chat Action配置文件
    
    生成路径: actions/000000000001_chat_action.yml
    
    配置内容:
    - 继承base.yml配置
    - 指定要处理的文件列表
    - 设置查询内容和模型参数
    """
    file_paths = self.file_creator.get_file_paths(project_dir)
    file_urls = "\n".join([f"- {path}" for path in file_paths])
    
    chat_action_content = f"""add_updated_urls: []
auto_merge: editblock
chat_model: {self.model}
code_model: {self.model}
enable_active_context: true
enable_global_memory: false
enable_task_history: true
generate_times_same_model: 1
human_as_model: false
include_file:
- ./base/base.yml
include_project_structure: true
model: {self.model}
product_mode: {self.product_mode}
query: '{self.query}'
silence: false
skip_build_index: true
skip_confirm: true
skip_filter_index: false
urls:
{file_urls}
"""
```

### 5. Git仓库集成

```python
def _init_git_repo(self, project_dir: str) -> None:
    """
    初始化Git仓库的完整流程
    
    1. 初始化Git仓库
    2. 配置用户信息
    3. 添加所有文件到版本控制
    4. 创建初始提交
    """
    try:
        # 初始化Git仓库
        repo = git.Repo.init(project_dir)
        
        # 设置用户信息
        config_writer = repo.config_writer()
        config_writer.set_value("user", "email", self.git_user_email)
        config_writer.set_value("user", "name", self.git_user_name)
        config_writer.release()
        
        # 添加所有文件并提交
        repo.git.add(A=True)
        repo.index.commit("Initial commit")
        
        print("Git仓库初始化成功")
    except Exception as e:
        print(f"Git初始化失败: {e}")
```

### 6. RAG文档创建工具

#### 示例文件创建
```python
def create_sample_files(base_dir: str):
    """
    创建用于RAG系统的示例代码文件
    
    创建的文件:
    - calculator.py: 完整的计算器类（包含四则运算）
    - string_processor.py: 字符串处理工具类
    - data_processor.py: 数据处理和统计分析类
    
    这些文件用于:
    - RAG系统的演示
    - 测试文档检索功能
    - 提供代码生成的参考示例
    """
    os.makedirs(base_dir, exist_ok=True)
    
    # 创建计算器示例
    calculator_content = """
class Calculator:
    def __init__(self):
        self.history = []
        
    def add(self, a: int, b: int) -> int:
        '''加法函数'''
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
        
    def multiply(self, a: int, b: int) -> int:
        '''乘法函数'''
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
        
    def divide(self, a: int, b: int) -> float:
        '''除法函数'''
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
"""
    
    with open(os.path.join(base_dir, "calculator.py"), "w", encoding="utf-8") as f:
        f.write(calculator_content)
```

#### 文件管理操作
```python
def update_sample_file(base_dir: str, filename: str, content: str):
    """更新指定示例文件内容"""
    file_path = os.path.join(base_dir, filename)
    if not os.path.exists(file_path):
        logger.warning(f"文件 {file_path} 不存在，无法更新")
        return
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"已更新文件: {file_path}")

def add_sample_file(base_dir: str, filename: str, content: str):
    """新增示例文件，若存在则覆盖"""
    file_path = os.path.join(base_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"已新增文件: {file_path}")

def delete_sample_file(base_dir: str, filename: str):
    """删除指定示例文件"""
    file_path = os.path.join(base_dir, filename)
    try:
        os.remove(file_path)
        logger.info(f"已删除文件: {file_path}")
    except FileNotFoundError:
        logger.warning(f"文件 {file_path} 不存在，无法删除")
```

## 📊 支持的项目类型

### Python项目结构

```
my_python_calculator/
├── calculator.py           # 计算器类实现
├── main.py                # 主程序入口
├── actions/               # Auto-Coder配置
│   ├── base/
│   │   └── base.yml      # 基础配置
│   └── 000000000001_chat_action.yml  # Chat动作配置
├── output.txt            # 输出文件
└── .git/                 # Git仓库（可选）
```

**Python项目特点**:
- 简洁的面向对象设计
- 包含历史记录功能
- 支持基本四则运算
- 完整的类型注释和文档

### React TypeScript项目结构

```
my_react_calculator/
├── package.json          # 项目依赖配置
├── vite.config.ts       # Vite构建配置
├── tsconfig.json        # TypeScript配置
├── tsconfig.node.json   # Node环境TypeScript配置
├── index.html           # HTML入口文件
├── .gitignore          # Git忽略文件
├── src/                # 源码目录
│   ├── main.tsx        # 应用入口
│   ├── App.tsx         # 主应用组件
│   ├── App.css         # 应用样式
│   ├── Calculator.tsx  # 计算器组件
│   ├── Calculator.css  # 计算器样式
│   ├── index.css       # 全局样式
├── actions/            # Auto-Coder配置
│   ├── base/
│   │   └── base.yml    # 基础配置
│   └── 000000000001_chat_action.yml  # Chat动作配置
├── output.txt          # 输出文件
└── .git/               # Git仓库（可选）
```

**React项目特点**:
- 现代化的Vite + React + TypeScript技术栈
- 完整的前端构建配置
- 响应式计算器UI组件
- CSS Grid布局的计算器界面
- TypeScript类型安全

## ⚡ 应用场景

### 1. 演示和教学

```python
# 快速创建演示项目用于教学
def create_tutorial_projects():
    """为教学创建多个示例项目"""
    
    tutorials = [
        ("basic_python", "python", "实现基本的加减法计算器"),
        ("advanced_python", "python", "添加科学计算和历史记录功能"),
        ("react_ui", "react", "创建现代化的Web计算器界面"),
        ("react_advanced", "react", "添加主题切换和快捷键支持")
    ]
    
    for name, type, query in tutorials:
        creator = ProjectCreator(
            project_name=f"tutorial_{name}",
            project_type=type,
            query=query,
            git_init=True
        )
        creator.create_project()
        print(f"✅ 教学项目创建: tutorial_{name}")
```

### 2. 测试和验证

```python
# 创建测试项目验证Auto-Coder功能
def create_test_projects():
    """为测试创建标准化项目"""
    
    test_configs = [
        {
            "name": "test_python_simple",
            "type": "python", 
            "model": "claude3_5_sonnet",
            "query": "为计算器添加平方根和平方功能"
        },
        {
            "name": "test_react_complex",
            "type": "react",
            "model": "gpt4",
            "query": "实现计算器的键盘快捷键和内存功能"
        }
    ]
    
    for config in test_configs:
        creator = ProjectCreator(**config)
        project_path = creator.create_project()
        
        # 可以继续调用Auto-Coder进行测试
        # subprocess.run(["auto-coder", "action", "--file", 
        #                os.path.join(project_path, "actions", "chat_action.yml")])
```

### 3. RAG文档准备

```python
from autocoder.helper.rag_doc_creator import create_sample_files, add_sample_file

def prepare_rag_documents():
    """为RAG系统准备丰富的示例文档"""
    
    base_dir = "rag_samples"
    
    # 创建基础示例文件
    create_sample_files(base_dir)
    
    # 添加更多专业领域的示例
    algorithm_content = """
class SortingAlgorithms:
    @staticmethod
    def bubble_sort(arr: List[int]) -> List[int]:
        '''冒泡排序算法'''
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
        return arr
    
    @staticmethod
    def quick_sort(arr: List[int]) -> List[int]:
        '''快速排序算法'''
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left) + middle + quick_sort(right)
"""
    
    add_sample_file(base_dir, "algorithms.py", algorithm_content)
    
    # 添加Web开发示例
    web_utils_content = """
class WebUtils:
    @staticmethod
    def validate_email(email: str) -> bool:
        '''验证邮箱格式'''
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def generate_slug(title: str) -> str:
        '''生成URL友好的slug'''
        import re
        slug = title.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug
"""
    
    add_sample_file(base_dir, "web_utils.py", web_utils_content)
    
    print(f"RAG文档已准备完成，路径: {base_dir}")
```

## 🧪 测试和验证

### 项目创建器测试

```bash
# 测试Python项目创建
python -c "
from autocoder.helper.project_creator import ProjectCreator
import os
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    os.chdir(temp_dir)
    
    # 测试Python项目创建
    creator = ProjectCreator(
        project_name='test_python_project',
        project_type='python',
        git_init=False,  # 测试时跳过Git
        create_actions=True
    )
    
    project_path = creator.create_project()
    
    # 验证文件结构
    assert os.path.exists(os.path.join(project_path, 'calculator.py'))
    assert os.path.exists(os.path.join(project_path, 'main.py'))
    assert os.path.exists(os.path.join(project_path, 'actions', 'base', 'base.yml'))
    
    print('✅ Python项目创建测试通过')
"
```

```bash
# 测试React项目创建
python -c "
from autocoder.helper.project_creator import ProjectCreator
import os
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    os.chdir(temp_dir)
    
    # 测试React项目创建
    creator = ProjectCreator(
        project_name='test_react_project',
        project_type='react',
        git_init=False,
        create_actions=True
    )
    
    project_path = creator.create_project()
    
    # 验证React项目文件结构
    assert os.path.exists(os.path.join(project_path, 'package.json'))
    assert os.path.exists(os.path.join(project_path, 'vite.config.ts'))
    assert os.path.exists(os.path.join(project_path, 'src', 'App.tsx'))
    assert os.path.exists(os.path.join(project_path, 'src', 'Calculator.tsx'))
    
    print('✅ React项目创建测试通过')
"
```

### RAG文档创建器测试

```bash
# 测试RAG文档创建功能
python -c "
from autocoder.helper.rag_doc_creator import *
import os
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    # 测试创建示例文件
    create_sample_files(temp_dir)
    
    # 验证文件创建
    assert os.path.exists(os.path.join(temp_dir, 'calculator.py'))
    assert os.path.exists(os.path.join(temp_dir, 'string_processor.py'))
    assert os.path.exists(os.path.join(temp_dir, 'data_processor.py'))
    
    # 测试添加新文件
    test_content = 'class TestClass: pass'
    add_sample_file(temp_dir, 'test_file.py', test_content)
    assert os.path.exists(os.path.join(temp_dir, 'test_file.py'))
    
    # 测试更新文件
    update_content = 'class UpdatedClass: pass'
    update_sample_file(temp_dir, 'test_file.py', update_content)
    with open(os.path.join(temp_dir, 'test_file.py'), 'r') as f:
        assert 'UpdatedClass' in f.read()
    
    # 测试删除文件
    delete_sample_file(temp_dir, 'test_file.py')
    assert not os.path.exists(os.path.join(temp_dir, 'test_file.py'))
    
    print('✅ RAG文档创建器测试通过')
"
```

### 工厂模式测试

```bash
# 测试工厂模式和扩展性
python -c "
from autocoder.helper.project_creator import FileCreatorFactory
from autocoder.helper.project_creator import PythonFileCreator, ReactJSFileCreator

# 测试工厂方法
python_creator = FileCreatorFactory.get_creator('python')
assert isinstance(python_creator, PythonFileCreator)
assert python_creator.project_type == 'py'

react_creator = FileCreatorFactory.get_creator('react')
assert isinstance(react_creator, ReactJSFileCreator)
assert react_creator.project_type == 'tsx'

# 测试别名支持
py_creator = FileCreatorFactory.get_creator('py')
assert isinstance(py_creator, PythonFileCreator)

js_creator = FileCreatorFactory.get_creator('js')
assert isinstance(js_creator, ReactJSFileCreator)

# 测试不支持的类型
try:
    FileCreatorFactory.get_creator('unsupported')
    assert False, '应该抛出异常'
except ValueError as e:
    assert '不支持的项目类型' in str(e)

print('✅ 工厂模式测试通过')
"
```

## 🔧 扩展新项目类型

### 添加Vue项目支持示例

```python
from autocoder.helper.project_creator import FileCreator

class VueFileCreator(FileCreator):
    """Vue 3 + TypeScript项目文件创建器"""
    
    def create_files(self, project_dir: str) -> None:
        """创建Vue项目文件"""
        self._create_package_json(project_dir)
        self._create_vite_config(project_dir)
        self._create_vue_components(project_dir)
    
    def get_file_paths(self, project_dir: str) -> List[str]:
        """获取Vue项目的主要文件路径"""
        abs_project_dir = os.path.abspath(project_dir)
        return [
            os.path.join(abs_project_dir, "package.json"),
            os.path.join(abs_project_dir, "src", "App.vue"),
            os.path.join(abs_project_dir, "src", "components", "Calculator.vue")
        ]
    
    @property
    def project_type(self) -> str:
        return "vue"
    
    def _create_vue_components(self, project_dir: str) -> None:
        """创建Vue组件"""
        # 实现Vue组件创建逻辑
        pass

# 在工厂类中添加支持
def get_creator(project_type: str) -> FileCreator:
    project_type = project_type.lower()
    
    if project_type in ('python', 'py'):
        return PythonFileCreator()
    elif project_type in ('react', 'reactjs', 'js'):
        return ReactJSFileCreator()
    elif project_type in ('vue', 'vuejs'):  # 新增Vue支持
        return VueFileCreator()
    else:
        raise ValueError(f"不支持的项目类型: {project_type}")
```

## 🔍 故障排除

### 常见问题

1. **Git初始化失败**
   ```
   问题: Git仓库初始化报错
   原因: Git未安装或配置问题
   解决: 
   - 确保系统已安装Git
   - 检查Git用户配置
   - 使用git_init=False跳过Git初始化
   ```

2. **项目目录权限问题**
   ```
   问题: 无法创建项目目录或文件
   原因: 文件系统权限不足
   解决:
   - 检查目录写入权限
   - 选择有权限的目录
   - 以管理员权限运行
   ```

3. **项目类型不支持**
   ```
   问题: ValueError: 不支持的项目类型
   原因: 使用了未实现的项目类型
   解决:
   - 检查支持的项目类型列表
   - 使用正确的类型名称
   - 实现新的FileCreator子类
   ```

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

from autocoder.helper.project_creator import ProjectCreator

# 调试项目创建过程
creator = ProjectCreator(
    project_name="debug_project",
    project_type="python",
    git_init=False  # 调试时禁用Git
)

try:
    project_path = creator.create_project()
    print(f"项目创建成功: {project_path}")
    
    # 检查创建的文件
    import os
    for root, dirs, files in os.walk(project_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"文件: {file_path}")
            
except Exception as e:
    print(f"项目创建失败: {e}")
    import traceback
    traceback.print_exc()
```

---

## 📝 总结

`helper` 包是 Auto-Coder 的实用工具集，为演示、测试和快速原型开发提供了强大的支持。通过项目创建器和RAG文档生成器，用户可以快速搭建标准化的示例项目，为 Auto-Coder 的功能验证和演示提供了便利的基础设施。

### 关键优势
- **快速搭建**: 一键创建完整的示例项目结构
- **多技术栈**: 支持Python和React TypeScript项目
- **配置完整**: 自动生成Auto-Coder配置文件
- **Git集成**: 可选的Git仓库初始化和提交
- **扩展性好**: 工厂模式支持新项目类型扩展
- **RAG支持**: 专门的示例文档生成工具

该模块为 Auto-Coder 生态系统的演示、教学和测试场景提供了完整的工具链支持，是系统易用性和可演示性的重要保障。 