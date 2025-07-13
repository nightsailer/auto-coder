# db.ac.mod.md

## 模块信息
- **模块名称**: db
- **模块类型**: 包模块 (Package Module)
- **主要功能**: 数据库管理和持久化存储系统

## 核心功能

### 数据库抽象层
- **SQLModel集成**: 基于SQLModel提供类型安全的数据库操作
- **SQLite支持**: 使用SQLite作为默认数据库引擎
- **单例模式**: 确保全局唯一的数据库连接和管理
- **自动初始化**: 支持数据库表结构的自动创建和迁移

### Token计数管理
- **TokenCounter模型**: 跟踪项目级别的token使用情况
- **输入输出统计**: 分别记录输入token和生成token的数量
- **项目级别**: 支持多项目的独立token统计
- **累积计算**: 提供token使用量的累积和查询功能

### 存储管理
- **Store类**: 核心存储管理器，实现单例模式
- **连接管理**: 自动管理数据库连接的创建和维护
- **事务支持**: 提供完整的数据库事务操作支持
- **错误处理**: 完善的数据库操作错误处理机制

## 关键组件

### 1. 数据模型 (TokenCounter)
```python
class TokenCounter(SQLModel, table=True):
    project: str = Field(primary_key=True)
    input_tokens_count: int = 0
    generated_tokens_count: int = 0
```

### 2. 单例存储管理器 (Store)
```python
class Store(metaclass=SingletonStore):
    def __init__(self, db_path: str = None)
    def update_token_counter(self, project: str = None, 
                           input_tokens_count: int = 0, 
                           generated_tokens_count: int = 0)
    def get_token_counter(self) -> TokenCounter
```

### 3. 单例元类 (SingletonStore)
```python
class SingletonStore(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
```

## 数据库架构

### 1. 表结构设计
```sql
-- TokenCounter表
CREATE TABLE tokencounter (
    project VARCHAR PRIMARY KEY,
    input_tokens_count INTEGER NOT NULL DEFAULT 0,
    generated_tokens_count INTEGER NOT NULL DEFAULT 0
);
```

### 2. 索引策略
- **主键索引**: project字段作为主键，确保项目唯一性
- **查询优化**: 针对频繁查询的字段建立适当索引
- **性能考虑**: 平衡查询性能和存储空间的使用

### 3. 数据完整性
- **主键约束**: 确保每个项目只有一条记录
- **非空约束**: 确保token计数字段不为空
- **默认值**: 为新记录提供合理的默认值

## 核心操作

### 1. 数据库初始化
```python
def _create_engine(self):
    """创建数据库引擎"""
    if not os.path.exists(self.db_path):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    return create_engine(f"sqlite:///{self.db_path}")

def __init__(self, db_path: str = None):
    """初始化存储管理器"""
    self.db_path = db_path
    self.engine = self._create_engine()
    SQLModel.metadata.create_all(self.engine)
```

### 2. Token计数更新
```python
def update_token_counter(self, project: str = None, 
                        input_tokens_count: int = 0, 
                        generated_tokens_count: int = 0):
    """更新项目的token计数"""
    with Session(self.engine) as session:
        # 查询现有记录
        if project is None:
            statement = select(TokenCounter)
        else:
            statement = select(TokenCounter).where(TokenCounter.project == project)
        
        results = session.exec(statement)
        token_counter = results.first()
        
        # 创建新记录或更新现有记录
        if token_counter is None:
            token_counter = TokenCounter(project=project)
        
        # 累积计数
        token_counter.input_tokens_count += input_tokens_count
        token_counter.generated_tokens_count += generated_tokens_count
        
        # 保存到数据库
        session.add(token_counter)
        session.commit()
```

### 3. 数据查询
```python
def get_token_counter(self) -> TokenCounter:
    """获取token计数记录"""
    with Session(self.engine) as session:
        statement = select(TokenCounter)
        results = session.exec(statement)
        token_counter = results.first()
        return token_counter
```

## 使用模式

### 1. 基本使用
```python
# 获取存储实例
store = Store(db_path="/path/to/database.db")

# 更新token计数
store.update_token_counter(
    project="my_project",
    input_tokens_count=100,
    generated_tokens_count=50
)

# 查询token计数
counter = store.get_token_counter()
print(f"Input tokens: {counter.input_tokens_count}")
print(f"Generated tokens: {counter.generated_tokens_count}")
```

### 2. 项目级别统计
```python
# 为特定项目更新计数
store.update_token_counter(
    project="project_a",
    input_tokens_count=200,
    generated_tokens_count=100
)

store.update_token_counter(
    project="project_b", 
    input_tokens_count=150,
    generated_tokens_count=75
)

# 查询特定项目的统计
project_counter = store.get_token_counter_by_project("project_a")
```

### 3. 批量操作
```python
# 批量更新多个项目的统计
projects_data = [
    {"project": "proj1", "input": 100, "output": 50},
    {"project": "proj2", "input": 200, "output": 100},
    {"project": "proj3", "input": 150, "output": 75}
]

for data in projects_data:
    store.update_token_counter(
        project=data["project"],
        input_tokens_count=data["input"],
        generated_tokens_count=data["output"]
    )
```

## 扩展功能

### 1. 数据模型扩展
```python
# 扩展TokenCounter模型
class ExtendedTokenCounter(SQLModel, table=True):
    project: str = Field(primary_key=True)
    input_tokens_count: int = 0
    generated_tokens_count: int = 0
    
    # 新增字段
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    cost: float = 0.0
    model_name: str = ""
    
    # 计算属性
    @property
    def total_tokens(self) -> int:
        return self.input_tokens_count + self.generated_tokens_count
    
    @property
    def efficiency_ratio(self) -> float:
        if self.input_tokens_count == 0:
            return 0.0
        return self.generated_tokens_count / self.input_tokens_count
```

### 2. 高级查询功能
```python
class AdvancedStore(Store):
    def get_token_counter_by_project(self, project: str) -> TokenCounter:
        """获取指定项目的token计数"""
        with Session(self.engine) as session:
            statement = select(TokenCounter).where(TokenCounter.project == project)
            result = session.exec(statement)
            return result.first()
    
    def get_total_tokens_by_date_range(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """获取指定日期范围内的token统计"""
        with Session(self.engine) as session:
            statement = select(TokenCounter).where(
                TokenCounter.created_at >= start_date,
                TokenCounter.created_at <= end_date
            )
            results = session.exec(statement)
            
            total_input = sum(r.input_tokens_count for r in results)
            total_output = sum(r.generated_tokens_count for r in results)
            
            return {
                "total_input_tokens": total_input,
                "total_generated_tokens": total_output,
                "total_tokens": total_input + total_output
            }
    
    def get_top_projects_by_usage(self, limit: int = 10) -> List[TokenCounter]:
        """获取token使用量最高的项目"""
        with Session(self.engine) as session:
            statement = select(TokenCounter).order_by(
                (TokenCounter.input_tokens_count + TokenCounter.generated_tokens_count).desc()
            ).limit(limit)
            results = session.exec(statement)
            return list(results)
```

### 3. 数据分析功能
```python
class TokenAnalytics:
    def __init__(self, store: Store):
        self.store = store
    
    def generate_usage_report(self) -> Dict[str, Any]:
        """生成token使用报告"""
        with Session(self.store.engine) as session:
            statement = select(TokenCounter)
            results = session.exec(statement)
            counters = list(results)
            
            if not counters:
                return {"error": "No data available"}
            
            total_input = sum(c.input_tokens_count for c in counters)
            total_generated = sum(c.generated_tokens_count for c in counters)
            total_projects = len(counters)
            
            avg_input = total_input / total_projects if total_projects > 0 else 0
            avg_generated = total_generated / total_projects if total_projects > 0 else 0
            
            return {
                "total_projects": total_projects,
                "total_input_tokens": total_input,
                "total_generated_tokens": total_generated,
                "total_tokens": total_input + total_generated,
                "average_input_per_project": avg_input,
                "average_generated_per_project": avg_generated,
                "efficiency_ratio": total_generated / total_input if total_input > 0 else 0
            }
    
    def get_project_rankings(self) -> List[Dict[str, Any]]:
        """获取项目排名"""
        with Session(self.store.engine) as session:
            statement = select(TokenCounter).order_by(
                (TokenCounter.input_tokens_count + TokenCounter.generated_tokens_count).desc()
            )
            results = session.exec(statement)
            
            rankings = []
            for rank, counter in enumerate(results, 1):
                rankings.append({
                    "rank": rank,
                    "project": counter.project,
                    "input_tokens": counter.input_tokens_count,
                    "generated_tokens": counter.generated_tokens_count,
                    "total_tokens": counter.input_tokens_count + counter.generated_tokens_count,
                    "efficiency": counter.generated_tokens_count / counter.input_tokens_count if counter.input_tokens_count > 0 else 0
                })
            
            return rankings
```

## 配置和优化

### 1. 数据库配置
```python
# 数据库配置选项
DATABASE_CONFIG = {
    "default_path": ".auto-coder/db/autocoder.db",
    "backup_interval": 3600,  # 备份间隔（秒）
    "max_connections": 10,    # 最大连接数
    "connection_timeout": 30, # 连接超时（秒）
    "enable_wal_mode": True,  # 启用WAL模式
    "enable_foreign_keys": True,  # 启用外键约束
}

class OptimizedStore(Store):
    def __init__(self, db_path: str = None, config: Dict = None):
        self.config = config or DATABASE_CONFIG
        super().__init__(db_path)
        self._optimize_database()
    
    def _optimize_database(self):
        """优化数据库设置"""
        with self.engine.connect() as conn:
            if self.config.get("enable_wal_mode"):
                conn.execute(text("PRAGMA journal_mode=WAL"))
            
            if self.config.get("enable_foreign_keys"):
                conn.execute(text("PRAGMA foreign_keys=ON"))
            
            # 设置其他优化参数
            conn.execute(text("PRAGMA cache_size=10000"))
            conn.execute(text("PRAGMA temp_store=memory"))
```

### 2. 性能监控
```python
class DatabaseMonitor:
    def __init__(self, store: Store):
        self.store = store
        self.metrics = {
            "query_count": 0,
            "total_query_time": 0.0,
            "slow_queries": []
        }
    
    def monitor_query(self, query_func):
        """监控查询性能的装饰器"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = query_func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                query_time = end_time - start_time
                
                self.metrics["query_count"] += 1
                self.metrics["total_query_time"] += query_time
                
                # 记录慢查询
                if query_time > 1.0:  # 超过1秒的查询
                    self.metrics["slow_queries"].append({
                        "function": query_func.__name__,
                        "duration": query_time,
                        "timestamp": datetime.now()
                    })
        
        return wrapper
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        avg_query_time = (
            self.metrics["total_query_time"] / self.metrics["query_count"]
            if self.metrics["query_count"] > 0 else 0
        )
        
        return {
            "total_queries": self.metrics["query_count"],
            "total_query_time": self.metrics["total_query_time"],
            "average_query_time": avg_query_time,
            "slow_queries_count": len(self.metrics["slow_queries"]),
            "slow_queries": self.metrics["slow_queries"][-10:]  # 最近10个慢查询
        }
```

## 数据备份和恢复

### 1. 备份策略
```python
class DatabaseBackup:
    def __init__(self, store: Store):
        self.store = store
        self.backup_dir = os.path.join(os.path.dirname(store.db_path), "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self) -> str:
        """创建数据库备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}.db")
        
        # 使用SQLite的备份API
        with sqlite3.connect(self.store.db_path) as source:
            with sqlite3.connect(backup_path) as backup:
                source.backup(backup)
        
        return backup_path
    
    def restore_backup(self, backup_path: str) -> bool:
        """从备份恢复数据库"""
        try:
            if os.path.exists(backup_path):
                # 创建当前数据库的备份
                current_backup = self.create_backup()
                
                # 恢复备份
                shutil.copy2(backup_path, self.store.db_path)
                return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def auto_backup(self, interval: int = 3600):
        """自动备份功能"""
        def backup_worker():
            while True:
                try:
                    backup_path = self.create_backup()
                    print(f"Auto backup created: {backup_path}")
                    
                    # 清理旧备份（保留最近7天）
                    self._cleanup_old_backups(days=7)
                    
                except Exception as e:
                    print(f"Auto backup failed: {e}")
                
                time.sleep(interval)
        
        backup_thread = threading.Thread(target=backup_worker, daemon=True)
        backup_thread.start()
```

## 集成点和扩展

### 1. 与其他模块的关系
- **common模块**: 使用基础配置和工具
- **utils模块**: 集成token计算功能
- **memory模块**: 可能存储上下文状态
- **events模块**: 记录数据库操作事件

### 2. 外部依赖
- **SQLModel**: 数据模型和ORM
- **SQLite**: 数据库引擎
- **sqlite3**: Python标准库数据库接口

### 3. 扩展建议
```python
# 支持多种数据库
class MultiDatabaseStore(Store):
    def __init__(self, db_type: str = "sqlite", **kwargs):
        if db_type == "sqlite":
            self.engine = self._create_sqlite_engine(kwargs.get("db_path"))
        elif db_type == "postgresql":
            self.engine = self._create_postgresql_engine(kwargs)
        elif db_type == "mysql":
            self.engine = self._create_mysql_engine(kwargs)
        
        SQLModel.metadata.create_all(self.engine)
```

---

db模块提供了简洁而强大的数据库管理功能，专注于token使用统计和项目数据的持久化存储，通过单例模式确保数据一致性，为整个auto-coder系统提供了可靠的数据基础设施。 