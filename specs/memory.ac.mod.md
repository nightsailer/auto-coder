# memory.ac.mod.md

## 模块信息
- **模块名称**: memory
- **模块类型**: 包模块 (Package Module)
- **主要功能**: 活动上下文管理和智能内存系统

## 核心功能

### 活动上下文跟踪
- **ActiveContextManager**: 核心上下文管理器，单例模式实现
- **实时监控**: 跟踪项目文件变更和代码修改
- **智能文档生成**: 基于变更自动生成活动上下文文档
- **异步处理**: 非阻塞的后台任务处理机制

### 目录映射系统
- **DirectoryMapper**: 将文件URL映射到目录结构
- **上下文聚合**: 按目录组织相关文件和变更信息
- **智能分组**: 自动识别相关文件并进行逻辑分组
- **层次化管理**: 支持多层级目录结构的上下文管理

### 文档生成引擎
- **ActivePackage**: 活动包文档生成器
- **模块化设计**: 分别处理标题、变更、文档、图表四个部分
- **增量更新**: 基于现有内容的智能更新机制
- **多格式支持**: 支持Markdown、Mermaid图表等多种格式

## 关键组件

### 1. 活动上下文管理器 (ActiveContextManager)
```python
class ActiveContextManager:
    def __init__(self, llm: ByzerLLM, source_dir: str)
    
    def process_changes(self, args: AutoCoderArgs) -> str
    def get_task_status(self, task_id: str) -> Dict[str, Any]
    def list_active_tasks(self) -> List[Dict[str, Any]]
    def cancel_task(self, task_id: str) -> bool
```

### 2. 目录映射器 (DirectoryMapper)
```python
class DirectoryMapper:
    def map_directories(self, project_path: str, 
                       changed_urls: List[str], 
                       current_urls: List[str] = None) -> List[Dict[str, Any]]
    
    def _extract_directory_files(self, directory: str, 
                                all_files: List[str]) -> List[str]
```

### 3. 活动包生成器 (ActivePackage)
```python
class ActivePackage:
    def generate_active_file(self, context: Dict[str, Any], 
                           query: str, 
                           existing_file_path: str = None) -> Tuple[str, Dict[str, Any]]
    
    def generate_new_active_file(self, context: Dict[str, Any], 
                               query: str) -> Tuple[str, Dict[str, Any]]
    
    def generate_updated_active_file(self, context: Dict[str, Any], 
                                   query: str, 
                                   existing_content: str) -> Tuple[str, Dict[str, Any]]
```

### 4. 专业化处理器
```python
class ActiveHeader:
    def generate_header(self, context: Dict[str, Any]) -> str
    def update_header(self, context: Dict[str, Any], header: str) -> str

class ActiveChanges:
    def generate_changes(self, context: Dict[str, Any], query: str) -> Tuple[str, Dict]
    def update_changes(self, context: Dict[str, Any], query: str, existing: str) -> Tuple[str, Dict]

class ActiveDocuments:
    def generate_documents(self, context: Dict[str, Any], query: str) -> Tuple[str, Dict]
    def update_documents(self, context: Dict[str, Any], query: str, existing: str) -> Tuple[str, Dict]

class ActiveDiagrams:
    def generate_diagrams(self, context: Dict[str, Any], query: str) -> Tuple[str, Dict]
    def update_diagrams(self, context: Dict[str, Any], query: str, existing: str) -> Tuple[str, Dict]
```

## 工作流程

### 1. 变更检测和处理
```python
def process_changes(self, args: AutoCoderArgs) -> str:
    # 1. 从YAML文件加载任务数据
    yaml_content = self.yml_manager.load_yaml_content(file_name)
    
    # 2. 提取变更信息
    changed_urls = yaml_content.get('add_updated_urls', [])
    current_urls = yaml_content.get('urls', []) + yaml_content.get('dynamic_urls', [])
    
    # 3. 创建后台任务
    task_id = f"active_context_{int(time.time())}_{file_name}"
    
    # 4. 异步处理
    thread = threading.Thread(target=self._execute_task_in_background, args=(...))
    thread.start()
    
    return task_id
```

### 2. 目录上下文映射
```python
def map_directories(self, project_path: str, changed_urls: List[str], current_urls: List[str]):
    # 1. 提取所有相关目录
    directories = set()
    for url in changed_urls:
        directories.add(os.path.dirname(url))
    
    # 2. 创建目录上下文
    directory_contexts = []
    for directory in directories:
        context = {
            'directory_path': directory,
            'changed_files': self._extract_directory_files(directory, changed_urls),
            'current_files': self._extract_directory_files(directory, current_urls)
        }
        directory_contexts.append(context)
    
    return directory_contexts
```

### 3. 活动文档生成
```python
def generate_active_file(self, context: Dict[str, Any], query: str):
    # 1. 检查现有文件
    if existing_file_path and os.path.exists(existing_file_path):
        return self.generate_updated_active_file(context, query, existing_content)
    else:
        return self.generate_new_active_file(context, query)

def generate_new_active_file(self, context: Dict[str, Any], query: str):
    # 1. 生成标题部分
    header = self.header_processor.generate_header(context)
    
    # 2. 生成当前变更部分
    current_change, changes_stats = self.changes_processor.generate_changes(context, query)
    
    # 3. 生成文档部分
    document, document_stats = self.documents_processor.generate_documents(context, query)
    
    # 4. 生成关系图表部分
    diagrams, diagrams_stats = self.diagrams_processor.generate_diagrams(context, query)
    
    # 5. 组合最终内容
    file_content = f"{header}\n{current_change}\n{document}\n{diagrams}"
    
    return file_content, total_stats
```

## 任务管理系统

### 1. 任务状态跟踪
```python
class TaskStatus:
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# 任务信息结构
task_info = {
    'status': 'running',
    'start_time': datetime.now(),
    'file_name': file_name,
    'query': query,
    'changed_urls': changed_urls,
    'current_urls': current_urls,
    'queue_position': 0,
    'total_tokens': 0,
    'input_tokens': 0,
    'output_tokens': 0,
    'cost': 0.0
}
```

### 2. 任务持久化
```python
def _save_tasks_to_disk(self):
    """将任务信息保存到磁盘"""
    with self.tasks_lock:
        tasks_copy = {}
        for task_id, task in self.tasks.items():
            # 序列化处理
            task_copy = {}
            for k, v in task.items():
                if k in ['start_time', 'completion_time'] and isinstance(v, datetime):
                    task_copy[k] = v.isoformat()
                else:
                    task_copy[k] = v
            tasks_copy[task_id] = task_copy
        
        # 写入JSON文件
        with open(self.tasks_file_path, 'w', encoding='utf-8') as f:
            json.dump(tasks_copy, f, ensure_ascii=False, indent=2)
```

### 3. 异步处理机制
```python
def _execute_task_in_background(self, task_id: str, query: str, 
                               changed_urls: List[str], current_urls: List[str]):
    """在后台线程中执行任务"""
    try:
        # 更新任务状态为运行中
        self._update_task(task_id, status='running')
        
        # 执行实际处理
        self._process_changes_async(task_id, query, changed_urls, current_urls)
        
        # 更新任务状态为已完成
        self._update_task(task_id, status='completed', completion_time=datetime.now())
        
    except Exception as e:
        # 记录错误
        error_msg = f"Background task {task_id} failed: {str(e)}"
        self._update_task(task_id, status='failed', error=error_msg)
```

## 文档结构和内容

### 1. Active.md文件结构
```markdown
# 活动上下文 - {目录名}

## 当前变更
{基于用户查询和文件变更生成的变更说明}

## 文档
{目录中文件的详细文档和说明}

## 关系图表
{Mermaid格式的关系图和流程图}
```

### 2. 内容增强机制
```python
def _enhance_context_with_changes(self, context: Dict[str, Any], 
                                 file_changes: Dict[str, Tuple[str, str]]):
    """增强上下文信息，添加文件变更信息"""
    enhanced_context = context.copy()
    
    if file_changes:
        enhanced_context['file_changes'] = []
        for file_path, (before_content, after_content) in file_changes.items():
            enhanced_context['file_changes'].append({
                'file_path': file_path,
                'before_content': before_content,
                'after_content': after_content,
                'change_type': self._detect_change_type(before_content, after_content)
            })
    
    return enhanced_context
```

### 3. 智能更新策略
```python
def generate_updated_active_file(self, context: Dict[str, Any], query: str, existing_content: str):
    """基于现有内容生成更新后的活动文件内容"""
    # 1. 从现有内容中提取各部分
    header, existing_current_change, existing_document, existing_diagrams = self.extract_sections(existing_content)
    
    # 2. 更新各个部分
    updated_header = self.header_processor.update_header(context, header)
    updated_current_change, changes_stats = self.changes_processor.update_changes(context, query, existing_current_change)
    updated_document, document_stats = self.documents_processor.update_documents(context, query, existing_document)
    updated_diagrams, diagrams_stats = self.diagrams_processor.update_diagrams(context, query, existing_diagrams)
    
    # 3. 组合更新后的内容
    updated_content = f"{updated_header}\n{updated_current_change}\n{updated_document}\n{updated_diagrams}"
    
    return updated_content, total_stats
```

## 性能优化和监控

### 1. Token使用统计
```python
class TokenUsageStats:
    total_tokens: int
    input_tokens: int
    output_tokens: int
    total_cost: float

# 使用TokenCostCalculator跟踪
token_calculator = TokenCostCalculator(logger_name="ActivePackage")
stats = token_calculator.track_token_usage(
    llm=self.llm,
    meta_holder=meta_holder,
    operation_name="Document Generation",
    start_time=start_time,
    end_time=end_time,
    product_mode=self.product_mode
)
```

### 2. 并发控制
```python
# 单例模式确保唯一实例
class ActiveContextManager(metaclass=SingletonMeta):
    _instance = None
    _is_initialized = False

# 线程安全的任务管理
self.tasks_lock = threading.Lock()
with self.tasks_lock:
    self.tasks[task_id] = task_info
```

### 3. 资源管理
```python
# 后台线程管理
self.__class__._queue_thread = threading.Thread(
    target=self._process_queue, daemon=True)
self.__class__._queue_thread.start()

# 任务队列控制
self.__class__._task_queue = queue.Queue()
```

## 集成点和扩展

### 1. 与其他模块的关系
- **common模块**: 使用ActionYmlFileManager和基础工具
- **utils模块**: 集成项目分析和token计算
- **events模块**: 发送处理进度和状态事件
- **rag模块**: 可能集成检索增强功能

### 2. 外部依赖
- **ByzerLLM**: 用于智能文档生成
- **pydantic**: 数据模型验证
- **threading**: 异步任务处理
- **json**: 任务状态持久化

### 3. 配置选项
```python
# 活动上下文配置
active_context_config = {
    'max_workers': 3,  # 最大工作线程数
    'task_timeout': 300,  # 任务超时时间（秒）
    'auto_cleanup': True,  # 自动清理完成的任务
    'enable_diagrams': True,  # 启用图表生成
    'max_file_size': 1000000,  # 最大文件大小（字节）
}
```

## 使用场景

### 1. 代码变更跟踪
```python
# 自动处理代码变更
manager = ActiveContextManager(llm, source_dir)
task_id = manager.process_changes(args)

# 查询处理状态
status = manager.get_task_status(task_id)
print(f"Task status: {status['status']}")
```

### 2. 项目文档维护
```python
# 生成项目活动文档
context = {
    'directory_path': '/project/src/components',
    'changed_files': ['Button.tsx', 'Modal.tsx'],
    'current_files': ['Button.tsx', 'Modal.tsx', 'Input.tsx']
}

package = ActivePackage(llm)
content, stats = package.generate_active_file(context, "重构UI组件")
```

### 3. 团队协作支持
```python
# 为团队成员生成上下文文档
for directory in project_directories:
    context = mapper.map_directories(project_path, changed_files, all_files)
    for ctx in context:
        active_content = package.generate_active_file(ctx, team_query)
        save_team_context(ctx['directory_path'], active_content)
```

## 最佳实践

### 1. 任务管理
- 定期清理已完成的任务
- 监控任务执行时间和资源使用
- 设置合理的并发限制

### 2. 文档质量
- 提供清晰的变更描述
- 保持文档结构的一致性
- 定期更新和优化生成模板

### 3. 性能优化
- 使用增量更新减少重复计算
- 缓存频繁访问的上下文信息
- 优化大文件的处理策略

---

memory模块提供了完整的活动上下文管理解决方案，通过智能的文档生成和异步任务处理，为开发团队提供了实时的项目状态跟踪和上下文感知能力，大大提升了代码理解和协作效率。 