# common.pull_requests.ac.mod.md

## 模块信息
- **模块名称**: common.pull_requests
- **模块类型**: 包模块 (Package Module)
- **主要功能**: 统一的Pull Request创建和管理模块，支持GitHub、GitLab、Gitee、GitCode四大代码托管平台的PR操作

## 核心功能

### 多平台支持
- **GitHub**: 支持GitHub.com和GitHub Enterprise
- **GitLab**: 支持GitLab.com和私有部署
- **Gitee**: 支持Gitee.com的API v5
- **GitCode**: 支持GitCode.net的API
- **自动检测**: 根据Git remote URL自动识别平台类型

### PR生命周期管理
- **创建PR**: 统一接口创建Pull Request
- **查询PR**: 获取PR详细信息和状态
- **更新PR**: 修改PR标题、描述和标签
- **关闭PR**: 关闭不需要的PR
- **合并PR**: 自动或手动合并PR

### 配置和认证
- **多种配置方式**: 支持环境变量、配置文件、直接传参
- **安全认证**: 支持各平台的Token认证机制
- **配置管理**: 集中管理多平台的认证信息
- **自动重试**: 网络错误和API限流的自动重试

## 关键组件

### 1. PullRequestManager 主管理器
```python
class PullRequestManager:
    def __init__(self, config: PRConfig)
    
    # PR操作方法
    def create_pull_request(self, repo_path: str, source_branch: str, target_branch: str, 
                           title: str, description: str = "", **kwargs) -> PRResult
    def get_pull_request(self, repo_path: str, pr_number: int) -> PRResult
    def update_pull_request(self, repo_path: str, pr_number: int, **kwargs) -> PRResult
    def close_pull_request(self, repo_path: str, pr_number: int) -> PRResult
    def merge_pull_request(self, repo_path: str, pr_number: int, merge_method: str = "merge") -> PRResult
    
    # 辅助方法
    def detect_platform(self, repo_path: str) -> str
    def validate_branches(self, repo_path: str, source_branch: str, target_branch: str) -> bool
```

### 2. 平台提供者基类
```python
class BasePlatformProvider:
    def __init__(self, config: PRConfig)
    
    # 抽象方法，子类必须实现
    def create_pr(self, repo_info: RepoInfo, pr_data: PRData) -> PRResult
    def get_pr(self, repo_info: RepoInfo, pr_number: int) -> PRResult
    def update_pr(self, repo_info: RepoInfo, pr_number: int, **kwargs) -> PRResult
    def close_pr(self, repo_info: RepoInfo, pr_number: int) -> PRResult
    def merge_pr(self, repo_info: RepoInfo, pr_number: int, merge_method: str) -> PRResult
    
    # 通用方法
    def make_request(self, method: str, url: str, **kwargs) -> dict
    def handle_api_error(self, response: requests.Response) -> None
```

### 3. 具体平台实现
```python
# GitHub提供者
class GitHubProvider(BasePlatformProvider):
    def create_pr(self, repo_info: RepoInfo, pr_data: PRData) -> PRResult
    def _build_github_api_url(self, repo_info: RepoInfo, endpoint: str) -> str

# GitLab提供者
class GitLabProvider(BasePlatformProvider):
    def create_pr(self, repo_info: RepoInfo, pr_data: PRData) -> PRResult
    def _build_gitlab_api_url(self, repo_info: RepoInfo, endpoint: str) -> str

# Gitee提供者
class GiteeProvider(BasePlatformProvider):
    def create_pr(self, repo_info: RepoInfo, pr_data: PRData) -> PRResult
    def _build_gitee_api_url(self, repo_info: RepoInfo, endpoint: str) -> str

# GitCode提供者
class GitCodeProvider(BasePlatformProvider):
    def create_pr(self, repo_info: RepoInfo, pr_data: PRData) -> PRResult
    def _build_gitcode_api_url(self, repo_info: RepoInfo, endpoint: str) -> str
```

### 4. 数据模型
```python
# PR配置模型
class PRConfig(BaseModel):
    platform: str
    token: str
    base_url: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    verify_ssl: bool = True

# 仓库信息模型
class RepoInfo(BaseModel):
    owner: str
    name: str
    platform: str
    base_url: str

# PR数据模型
class PRData(BaseModel):
    title: str
    description: str
    source_branch: str
    target_branch: str
    labels: Optional[List[str]] = None
    assignees: Optional[List[str]] = None
    reviewers: Optional[List[str]] = None

# PR结果模型
class PRResult(BaseModel):
    success: bool
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    error_message: Optional[str] = None
    platform: Optional[str] = None
```

## 使用指南

### 1. 基本使用
```python
from autocoder.common.pull_requests import create_pull_request, PullRequestManager, PRConfig

# 简单方式：直接创建PR
result = create_pull_request(
    repo_path="/path/to/your/repo",
    source_branch="feature/new-feature",
    target_branch="main",
    title="添加新功能",
    description="这是一个新功能的实现",
    platform="github",  # 支持: github, gitlab, gitee, gitcode
    token="your_access_token"
)

if result.success:
    print(f"PR 创建成功: {result.pr_url}")
    print(f"PR 编号: {result.pr_number}")
else:
    print(f"创建失败: {result.error_message}")

# 使用配置管理器
config = PRConfig(
    platform="github",
    token="your_access_token",
    base_url="https://api.github.com",
    timeout=30
)

manager = PullRequestManager(config)
result = manager.create_pull_request(
    repo_path="/path/to/repo",
    source_branch="feature/fix-bug", 
    target_branch="develop",
    title="修复重要Bug",
    description="修复了导致应用崩溃的关键问题"
)

# 自动检测平台
result = create_pull_request(
    repo_path="/path/to/repo",
    source_branch="hotfix/urgent-fix",
    target_branch="main",
    title="紧急修复",
    description="修复生产环境问题",
    # platform 参数可省略，将自动检测
    token="your_access_token"
)
```

### 2. 配置管理
```python
# 配置文件方式
config_data = {
    "github": {
        "token": "ghp_xxxxxxxxxxxx",
        "base_url": "https://api.github.com"
    },
    "gitlab": {
        "token": "glpat-xxxxxxxxxxxx", 
        "base_url": "https://gitlab.com/api/v4"
    },
    "gitee": {
        "token": "xxxxxxxxxxxxxx",
        "base_url": "https://gitee.com/api/v5"
    },
    "gitcode": {
        "token": "xxxxxxxxxxxxxx",
        "base_url": "https://gitcode.net/api/v4"
    }
}

# 从配置字典创建
config = PRConfig.from_dict("github", config_data["github"])

# 从环境变量创建
config = PRConfig.from_env("github")  # 读取 GITHUB_TOKEN 等环境变量

# 从配置文件创建
config = PRConfig.from_file("github", "~/.autocoder/pr_config.json")
```

### 3. 自动化代码审查流程
```python
def create_review_pr(repo_path: str, feature_branch: str):
    """创建代码审查PR"""
    
    # 自动检测平台并创建PR
    result = create_pull_request(
        repo_path=repo_path,
        source_branch=feature_branch,
        target_branch="develop",
        title=f"Code Review: {feature_branch}",
        description="""
## 变更说明
- 新功能实现
- 单元测试覆盖
- 文档更新

## 检查清单
- [ ] 代码风格符合规范
- [ ] 单元测试通过
- [ ] 文档已更新
- [ ] 性能影响评估
        """,
        token=os.getenv("GIT_TOKEN")
    )
    
    if result.success:
        print(f"✅ PR 创建成功: {result.pr_url}")
        return result.pr_number
    else:
        print(f"❌ 创建失败: {result.error_message}")
        return None
```

### 4. 多平台同步发布
```python
def sync_release_to_mirrors(main_repo: str, mirror_repos: List[str], tag: str):
    """将发布同步到多个镜像仓库"""
    
    results = []
    
    for mirror_repo in mirror_repos:
        result = create_pull_request(
            repo_path=mirror_repo,
            source_branch=f"release/{tag}",
            target_branch="main",
            title=f"Release {tag}",
            description=f"同步发布版本 {tag} 到镜像仓库",
            # 自动检测各镜像仓库的平台类型
        )
        results.append(result)
    
    return results
```

### 5. 紧急修复工作流
```python
def create_hotfix_pr(repo_path: str, hotfix_branch: str, issue_number: str):
    """创建紧急修复PR"""
    
    # 获取问题描述
    issue_desc = f"修复关键问题 #{issue_number}"
    
    result = create_pull_request(
        repo_path=repo_path,
        source_branch=hotfix_branch,
        target_branch="main",
        title=f"🚨 Hotfix: {issue_desc}",
        description=f"""
## 紧急修复

**相关问题**: #{issue_number}

### 修复内容
- 识别并修复根本原因
- 添加回归测试
- 验证修复效果

### 影响范围
- 仅影响问题相关功能
- 无破坏性变更

**优先级**: 🔴 高优先级
**需要立即审查和合并**
        """,
        labels=["hotfix", "priority:high"],  # 某些平台支持标签
        assignees=["team-lead"],  # 自动分配审查者
    )
    
    return result
```

### 6. 批量操作支持
```python
def create_multiple_prs(pr_configs: List[dict]) -> List[PRResult]:
    """批量创建PR"""
    
    results = []
    for config in pr_configs:
        result = create_pull_request(**config)
        results.append(result)
    
    return results

# 使用示例
pr_configs = [
    {
        "repo_path": "/path/to/repo1",
        "source_branch": "feature-1",
        "target_branch": "main",
        "title": "功能1实现"
    },
    {
        "repo_path": "/path/to/repo2", 
        "source_branch": "feature-2",
        "target_branch": "develop",
        "title": "功能2实现"
    }
]

results = create_multiple_prs(pr_configs)
```

### 7. PR模板支持
```python
# PR模板配置
template_config = {
    "bug_fix": {
        "title_prefix": "🐛 Bug Fix:",
        "description_template": """
## 问题描述
{problem_description}

## 解决方案
{solution_description}

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试验证

## 影响范围
{impact_scope}
        """
    },
    "feature": {
        "title_prefix": "✨ Feature:",
        "description_template": """
## 新功能说明
{feature_description}

## 实现细节
{implementation_details}

## 使用示例
{usage_examples}
        """
    }
}

# 使用模板创建PR
result = create_pull_request(
    repo_path="/path/to/repo",
    source_branch="fix/login-issue",
    target_branch="main",
    template_type="bug_fix",
    template_vars={
        "problem_description": "用户登录时出现超时错误",
        "solution_description": "优化认证流程，增加重试机制",
        "impact_scope": "仅影响登录功能，无破坏性变更"
    }
)
```

## 目录结构

```
src/autocoder/common/pull_requests/
├── __init__.py                    # 模块入口，导出主要接口
├── models.py                      # 数据模型定义（PRConfig, PRResult等）
├── base_provider.py               # 基础提供者抽象类
├── providers/                     # 各平台具体实现
│   ├── __init__.py               # 提供者模块入口
│   ├── github_provider.py        # GitHub API 实现
│   ├── gitlab_provider.py        # GitLab API 实现  
│   ├── gitee_provider.py         # Gitee API 实现
│   └── gitcode_provider.py       # GitCode API 实现
├── config.py                      # 配置管理和认证处理
├── manager.py                     # 主管理器，统一各平台操作
├── utils.py                       # 工具函数（URL解析、Git操作等）
└── .ac.mod.md                     # 本文档
```

## 技术特性

### 1. 平台自动检测
- **URL解析**: 基于Git remote URL自动识别平台
- **支持格式**: HTTPS和SSH格式的Git URL
- **多域名支持**: 支持企业版和私有部署的域名
- **智能匹配**: 基于域名模式的智能平台匹配

### 2. 统一API接口
- **抽象层设计**: 通过基类定义统一的接口规范
- **平台适配**: 各平台实现适配自己的API特性
- **错误统一**: 统一的错误处理和异常类型
- **结果标准化**: 标准化的返回结果格式

### 3. 配置管理
- **多源配置**: 支持环境变量、配置文件、直接传参
- **安全存储**: Token等敏感信息的安全管理
- **配置验证**: 自动验证配置的完整性和有效性
- **默认值**: 合理的默认配置减少配置复杂度

### 4. 错误处理和重试
- **分类异常**: 详细的异常分类和错误信息
- **自动重试**: 网络错误和API限流的智能重试
- **降级策略**: 失败时的降级处理机制
- **日志记录**: 详细的操作日志和错误追踪

## 架构图

```mermaid
graph TB
    %% 核心接口层
    API[公共API<br/>create_pull_request()<br/>PullRequestManager]
    
    %% 管理层
    Manager[PullRequestManager<br/>统一管理器]
    Config[PRConfig<br/>配置管理]
    Utils[Utils<br/>工具函数]
    
    %% 提供者层
    BaseProvider[BasePlatformProvider<br/>基础提供者抽象类]
    GitHubProvider[GitHubProvider<br/>GitHub实现]
    GitLabProvider[GitLabProvider<br/>GitLab实现]
    GiteeProvider[GiteeProvider<br/>Gitee实现]
    GitCodeProvider[GitCodeProvider<br/>GitCode实现]
    
    %% 数据模型层
    Models[数据模型<br/>PRConfig, PRResult<br/>RepoInfo, PRData]
    
    %% 外部依赖
    GitUtils[git_utils.py<br/>Git操作]
    Requests[requests<br/>HTTP客户端]
    Pydantic[pydantic<br/>数据验证]
    
    %% 依赖关系
    API --> Manager
    Manager --> Config
    Manager --> BaseProvider
    Manager --> Utils
    Manager --> Models
    
    BaseProvider --> GitHubProvider
    BaseProvider --> GitLabProvider
    BaseProvider --> GiteeProvider
    BaseProvider --> GitCodeProvider
    
    GitHubProvider --> Requests
    GitLabProvider --> Requests
    GiteeProvider --> Requests
    GitCodeProvider --> Requests
    
    Manager --> GitUtils
    Utils --> GitUtils
    Models --> Pydantic
```

## 集成点

### 与其他模块的关系
- **common.git_utils模块**: 复用Git操作功能
- **agent模块**: 为智能代理提供PR创建能力
- **events模块**: 可集成到事件系统中发送PR事件
- **memory模块**: 可记录PR创建历史和状态

### 外部依赖
- **requests**: HTTP客户端，用于API调用
- **pydantic**: 数据模型验证和序列化
- **gitpython**: Git仓库操作（可选）
- **urllib3**: URL解析和处理

## 扩展指南

### 1. 添加新平台支持
```python
from autocoder.common.pull_requests.base_provider import BasePlatformProvider

class CustomPlatformProvider(BasePlatformProvider):
    def create_pr(self, repo_info: RepoInfo, pr_data: PRData) -> PRResult:
        """实现自定义平台的PR创建逻辑"""
        api_url = self._build_api_url(repo_info, "pulls")
        
        payload = {
            "title": pr_data.title,
            "body": pr_data.description,
            "head": pr_data.source_branch,
            "base": pr_data.target_branch
        }
        
        response = self.make_request("POST", api_url, json=payload)
        
        return PRResult(
            success=True,
            pr_number=response["number"],
            pr_url=response["html_url"],
            platform="custom"
        )
    
    def _build_api_url(self, repo_info: RepoInfo, endpoint: str) -> str:
        """构建自定义平台的API URL"""
        return f"{repo_info.base_url}/repos/{repo_info.owner}/{repo_info.name}/{endpoint}"

# 注册新平台
from autocoder.common.pull_requests.manager import PullRequestManager
PullRequestManager.register_provider("custom", CustomPlatformProvider)
```

### 2. 自定义PR模板
```python
class PRTemplateManager:
    def __init__(self):
        self.templates = {}
    
    def register_template(self, name: str, template: dict):
        """注册新的PR模板"""
        self.templates[name] = template
    
    def apply_template(self, template_name: str, variables: dict) -> dict:
        """应用模板生成PR内容"""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        title = template["title_prefix"] + variables.get("title", "")
        description = template["description_template"].format(**variables)
        
        return {"title": title, "description": description}

# 使用自定义模板
template_manager = PRTemplateManager()
template_manager.register_template("security_fix", {
    "title_prefix": "🔒 Security Fix: ",
    "description_template": """
## 安全修复

**漏洞类型**: {vulnerability_type}
**严重级别**: {severity_level}

### 修复内容
{fix_description}

### 安全测试
- [ ] 漏洞扫描通过
- [ ] 安全测试验证
- [ ] 代码审查完成
    """
})
```

### 3. 自定义错误处理
```python
from autocoder.common.pull_requests.exceptions import PRError

class CustomPRError(PRError):
    """自定义PR错误"""
    pass

class EnhancedPullRequestManager(PullRequestManager):
    def create_pull_request(self, *args, **kwargs):
        """增强的PR创建，包含自定义错误处理"""
        try:
            return super().create_pull_request(*args, **kwargs)
        except requests.exceptions.Timeout:
            raise CustomPRError("请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise CustomPRError("连接失败，请检查平台可用性")
```

## 最佳实践

### 1. 配置管理
- 使用环境变量存储敏感的Token信息
- 为不同环境配置不同的API端点
- 定期轮换和更新访问Token
- 验证配置的有效性和权限

### 2. 错误处理
- 实现重试机制处理临时网络问题
- 记录详细的错误日志用于问题排查
- 提供用户友好的错误信息
- 建立错误监控和告警机制

### 3. 性能优化
- 使用连接池复用HTTP连接
- 实现请求缓存减少API调用
- 并行处理批量操作
- 合理设置超时时间

### 4. 安全考虑
- 验证SSL证书确保通信安全
- 限制API调用频率避免被限流
- 使用最小权限原则配置Token
- 定期审计和更新依赖库

---

common.pull_requests模块提供了完整的多平台PR管理解决方案，通过统一的接口和灵活的配置，简化了跨平台的代码协作流程，是现代软件开发工作流的重要组成部分。 