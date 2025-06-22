# API兼容性设计规范

## 目标
确保AutoCoder-Slim与原SDK API的100%兼容性，用户无需修改代码即可从原版本迁移到精简版本。

## 🎯 兼容性要求

### 核心API兼容
- **公共接口**: 所有原SDK的公共接口必须保持一致
- **函数签名**: 所有函数的参数和返回值类型不变
- **行为一致**: 相同输入产生相同输出
- **错误处理**: 错误类型和消息格式保持一致

## 📋 SDK API清单

### 主要接口 (autocoder.sdk)
```python
# 异步查询接口
async def query(prompt: str, options: Optional[AutoCodeOptions] = None, 
                show_terminal: bool = True) -> AsyncIterator[Message]

# 同步查询接口  
def query_sync(prompt: str, options: Optional[AutoCodeOptions] = None,
               show_terminal: bool = True) -> str

# 代码修改接口
def modify_code(prompt: str, pre_commit: bool = False,
                extra_args: Optional[Dict[str, Any]] = None,
                options: Optional[AutoCodeOptions] = None,
                show_terminal: bool = True) -> CodeModificationResult

# 异步流式代码修改接口
async def modify_code_stream(prompt: str, pre_commit: bool = False,
                           extra_args: Optional[Dict[str, Any]] = None,
                           options: Optional[AutoCodeOptions] = None,
                           show_terminal: bool = True) -> AsyncIterator[StreamEvent]
```

### 配置类 (AutoCodeOptions)
```python
@dataclass
class AutoCodeOptions:
    max_turns: int = DEFAULT_MAX_TURNS
    system_prompt: Optional[str] = None
    cwd: Optional[Union[str, Path]] = None
    allowed_tools: List[str] = field(default_factory=list)
    permission_mode: str = DEFAULT_PERMISSION_MODE
    output_format: str = DEFAULT_OUTPUT_FORMAT
    stream: bool = False
    session_id: Optional[str] = None
    continue_session: bool = False
    model: Optional[str] = None
    temperature: float = 0.7
    timeout: int = 30
    verbose: bool = False
    include_project_structure: bool = True
```

### 数据模型
```python
# 消息模型
class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

# 流式事件模型
class StreamEvent(BaseModel):
    event_type: str
    data: Any
    timestamp: Optional[datetime] = None

# 代码修改结果模型
class CodeModificationResult(BaseModel):
    success: bool
    message: str
    modified_files: List[str] = field(default_factory=list)
    created_files: List[str] = field(default_factory=list)
    deleted_files: List[str] = field(default_factory=list)
    error_details: Optional[str] = None
```

## 🔧 兼容性实现策略

### 1. 接口适配层
```python
# autocoder_slim/compat/bridge.py
class SDKCompatibilityBridge:
    def __init__(self):
        self.core_agent = SlimAgenticEdit()
    
    async def query(self, prompt, options=None, show_terminal=True):
        # 将SDK调用转换为内部Agent调用
        return self._adapt_query(prompt, options, show_terminal)
    
    def query_sync(self, prompt, options=None, show_terminal=True):
        # 同步版本的适配
        return asyncio.run(self.query(prompt, options, show_terminal))
```

### 2. 数据模型适配
```python
# 确保所有数据模型的字段和行为完全一致
class SlimMessage(Message):
    # 继承原Message，确保所有字段一致
    pass

class SlimStreamEvent(StreamEvent):
    # 继承原StreamEvent，确保兼容性
    pass
```

### 3. 配置选项映射
```python
class OptionsMapper:
    @staticmethod
    def map_to_slim_config(options: AutoCodeOptions) -> SlimConfig:
        # 将原配置映射到精简版配置
        return SlimConfig(
            model=options.model,
            max_turns=options.max_turns,
            cwd=options.cwd,
            # ... 其他映射
        )
```

## 📋 兼容性测试策略

### 1. 接口契约测试
```python
class TestAPICompatibility:
    def test_query_signature(self):
        # 测试函数签名一致性
        pass
    
    def test_query_behavior(self):
        # 测试行为一致性
        pass
    
    def test_error_handling(self):
        # 测试错误处理一致性
        pass
```

### 2. 回归测试套件
- [ ] 创建原SDK的完整测试用例
- [ ] 在精简版上运行相同测试
- [ ] 确保所有测试结果一致
- [ ] 特别关注边界情况和错误情况

### 3. 集成测试
- [ ] 使用真实的用户代码进行测试
- [ ] 测试不同配置组合的兼容性
- [ ] 验证流式和非流式接口的一致性
- [ ] 测试异步和同步接口的一致性

## ⚠️ 兼容性风险点

### 高风险区域
1. **事件系统**: 原版本事件类型众多，需要确保类型兼容
2. **错误处理**: 错误类型和消息格式必须完全一致
3. **配置选项**: 所有配置项的行为必须保持一致
4. **文件路径处理**: 路径解析和相对路径处理逻辑

### 缓解策略
- 建立详细的API测试矩阵
- 自动化兼容性测试
- 版本对比测试
- 用户反馈收集机制

## 📊 兼容性验证标准

### 功能兼容性
- [ ] 所有公共API接口100%兼容
- [ ] 数据模型字段和类型完全一致
- [ ] 错误处理行为保持一致
- [ ] 配置选项功能等效

### 性能兼容性
- [ ] 相同场景下性能不下降
- [ ] 内存使用模式类似
- [ ] 并发处理能力保持
- [ ] 错误恢复时间相当

### 用户体验兼容性
- [ ] 现有用户代码无需修改
- [ ] 迁移过程透明
- [ ] 学习成本为零
- [ ] 调试体验一致

## 🚀 兼容性实施计划

### Phase 1: 设计阶段
- [ ] 完成API契约定义
- [ ] 设计适配层架构
- [ ] 制定测试策略
- [ ] 识别风险点

### Phase 2: 实现阶段
- [ ] 实现兼容性适配层
- [ ] 创建测试用例
- [ ] 进行初步验证
- [ ] 修复发现的问题

### Phase 3: 验证阶段
- [ ] 全面的回归测试
- [ ] 性能对比测试
- [ ] 用户场景测试
- [ ] 文档和示例验证

## 📈 成功指标

### 技术指标
- API兼容性测试通过率: 100%
- 回归测试通过率: 100%
- 性能测试达标率: 95%+
- 错误处理一致性: 100%

### 用户指标
- 零修改迁移成功率: 95%+
- 用户满意度: 4.5/5+
- 问题报告数量: < 5个/月
- 支持请求减少: 80%+

---
*API兼容性是项目成功的关键指标，将在整个开发过程中持续验证和维护* 