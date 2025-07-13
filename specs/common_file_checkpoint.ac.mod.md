# common.file_checkpoint.ac.mod.md

## 模块概述

`common.file_checkpoint` 模块是 Auto-Coder 系统的文件变更管理核心，提供可靠的文件版本控制、变更跟踪、备份恢复和对话状态管理功能。该模块实现了完整的文件变更生命周期管理，支持原子性操作、批量变更、历史版本回溯等功能，确保代码修改的安全性和可追溯性。

**模块类型**: 包模块  
**主要功能**: 文件变更管理、版本控制、备份恢复、对话检查点  
**依赖关系**: 独立模块，为其他模块提供文件管理服务

## 核心组件

### 1. 数据模型层 (models.py)
- **FileChange**: 表示单个文件的变更信息
- **ChangeRecord**: 变更记录，包含元数据和详细信息
- **DiffResult**: 文件差异比较结果
- **ApplyResult**: 变更应用结果
- **UndoResult**: 变更撤销结果

### 2. 管理器层 (manager.py)
- **FileChangeManager**: 主要管理器，提供高层次API接口
- 支持原子性操作和批量变更
- 集成备份、存储和对话管理功能

### 3. 存储层 (store.py)
- **FileChangeStore**: 变更记录持久化存储
- 支持历史版本查询和管理
- 提供变更分组和时间序列功能

### 4. 备份层 (backup.py)
- **FileBackupManager**: 文件备份和恢复管理
- 支持增量备份和完整恢复
- 提供备份验证和清理功能

### 5. 对话检查点 (conversation_checkpoint.py)
- **ConversationCheckpointStore**: 对话状态持久化
- **ConversationCheckpoint**: 对话检查点数据模型
- 支持变更与对话状态的关联管理

## 主要功能

### 1. 基础文件变更管理

```python
from autocoder.common.file_checkpoint import FileChangeManager, FileChange

# 初始化管理器
manager = FileChangeManager(
    project_dir="/path/to/project",
    backup_dir="/path/to/backups",
    store_dir="/path/to/changes",
    max_history=50
)

# 创建文件变更
changes = {
    "src/main.py": FileChange(
        file_path="src/main.py",
        content="def main():\n    print('Hello, World!')\n",
        is_new=False,
        is_deletion=False
    ),
    "src/utils.py": FileChange(
        file_path="src/utils.py", 
        content="def helper():\n    return 'utility function'\n",
        is_new=True,
        is_deletion=False
    )
}

# 应用变更
result = manager.apply_changes(changes)

if result.success:
    print(f"成功应用 {len(result.change_ids)} 个变更")
    for change_id in result.change_ids:
        print(f"  变更ID: {change_id}")
else:
    print("应用变更失败:")
    for file_path, error in result.errors.items():
        print(f"  {file_path}: {error}")
```

### 2. 变更预览和差异比较

```python
# 预览变更差异
diff_results = manager.preview_changes(changes)

for file_path, diff_result in diff_results.items():
    print(f"\n文件: {file_path}")
    print(f"摘要: {diff_result.get_diff_summary()}")
    
    if diff_result.is_new:
        print("这是一个新文件")
        print(f"内容:\n{diff_result.new_content}")
    elif diff_result.is_deletion:
        print("这个文件将被删除")
    else:
        print("文件修改:")
        # 生成详细的差异文本
        diff_text = manager.get_diff_text(
            diff_result.old_content or "",
            diff_result.new_content
        )
        print(diff_text)
```

### 3. 变更撤销和版本回溯

```python
# 撤销最近的变更
undo_result = manager.undo_last_change()

if undo_result.success:
    print(f"成功撤销变更，恢复了 {len(undo_result.restored_files)} 个文件:")
    for file_path in undo_result.restored_files:
        print(f"  {file_path}")
else:
    print("撤销变更失败:")
    for file_path, error in undo_result.errors.items():
        print(f"  {file_path}: {error}")

# 撤销指定的变更
specific_undo = manager.undo_change("change_id_here")

# 撤销变更组
group_undo = manager.undo_change_group("group_id_here")

# 回滚到指定版本
version_undo = manager.undo_to_version("version_id_here")
```

### 4. 变更历史和查询

```python
# 获取变更历史
history = manager.get_change_history(limit=20)

print("最近的变更记录:")
for record in history:
    timestamp = datetime.fromtimestamp(record.timestamp)
    print(f"  {record.change_id}: {record.file_path} ({timestamp})")
    if record.is_new:
        print("    [新建文件]")
    elif record.is_deletion:
        print("    [删除文件]")
    else:
        print("    [修改文件]")

# 获取特定文件的历史
file_history = manager.get_file_history("src/main.py", limit=10)

# 获取变更组信息
change_groups = manager.get_change_groups(limit=10)
for group_id, timestamp, count in change_groups:
    group_time = datetime.fromtimestamp(timestamp)
    print(f"组 {group_id}: {count} 个变更 ({group_time})")
```

### 5. 批量变更和分组管理

```python
import uuid

# 生成变更组ID
group_id = str(uuid.uuid4())

# 批量创建多个相关变更
batch_changes = {
    "frontend/components/Header.tsx": FileChange(
        file_path="frontend/components/Header.tsx",
        content="// Updated header component\nexport default Header;",
        is_new=False
    ),
    "frontend/components/Footer.tsx": FileChange(
        file_path="frontend/components/Footer.tsx", 
        content="// Updated footer component\nexport default Footer;",
        is_new=False
    ),
    "frontend/styles/main.css": FileChange(
        file_path="frontend/styles/main.css",
        content="/* Updated styles */\nbody { margin: 0; }",
        is_new=True
    )
}

# 应用批量变更（使用相同的组ID）
batch_result = manager.apply_changes(batch_changes, change_group_id=group_id)

if batch_result.success:
    print(f"批量应用成功，组ID: {group_id}")
    
    # 稍后可以按组撤销所有相关变更
    group_undo_result = manager.undo_change_group(group_id)
    if group_undo_result.success:
        print("成功撤销整个变更组")
```

### 6. 对话状态集成管理

```python
# 应用变更并保存对话状态
conversations = [
    {"role": "user", "content": "请更新前端组件"},
    {"role": "assistant", "content": "我将为您更新Header和Footer组件"},
    {"role": "user", "content": "请添加响应式设计"}
]

metadata = {
    "task_type": "frontend_update",
    "user_id": "user123",
    "session_id": "session456"
}

# 应用变更并保存对话检查点
result = manager.apply_changes_with_conversation(
    changes=batch_changes,
    conversations=conversations,
    change_group_id=group_id,
    metadata=metadata
)

if result.success:
    print("变更和对话状态已保存")
    
    # 撤销变更并恢复对话状态
    undo_result, checkpoint = manager.undo_last_change_with_conversation()
    
    if undo_result.success and checkpoint:
        print("变更已撤销，对话状态已恢复:")
        print(f"  检查点ID: {checkpoint.checkpoint_id}")
        print(f"  对话数量: {len(checkpoint.conversations)}")
        print(f"  元数据: {checkpoint.metadata}")
        
        # 恢复对话历史
        restored_conversations = checkpoint.conversations
        for conv in restored_conversations:
            print(f"  {conv['role']}: {conv['content']}")
```

### 7. 高级文件操作

```python
# 处理文件删除
deletion_changes = {
    "old_file.py": FileChange(
        file_path="old_file.py",
        content="",  # 删除操作时内容可以为空
        is_deletion=True
    )
}

deletion_result = manager.apply_changes(deletion_changes)

# 处理新文件创建
new_file_changes = {
    "new_feature.py": FileChange(
        file_path="new_feature.py",
        content="class NewFeature:\n    def __init__(self):\n        pass\n",
        is_new=True
    )
}

new_file_result = manager.apply_changes(new_file_changes)

# 复杂的混合操作
mixed_changes = {
    "config.json": FileChange(
        file_path="config.json",
        content='{\n  "version": "2.0",\n  "features": ["new_feature"]\n}',
        is_new=False
    ),
    "deprecated.py": FileChange(
        file_path="deprecated.py",
        content="",
        is_deletion=True
    ),
    "migration.py": FileChange(
        file_path="migration.py", 
        content="# Migration script\nprint('Migrating to v2.0')\n",
        is_new=True
    )
}

mixed_result = manager.apply_changes(mixed_changes)
```

## 数据模型详解

### 1. FileChange 数据模型

```python
from autocoder.common.file_checkpoint.models import FileChange

# 创建文件变更对象
change = FileChange(
    file_path="src/example.py",
    content="print('Hello, World!')",
    is_new=False,        # 是否为新文件
    is_deletion=False    # 是否为删除操作
)

# 序列化和反序列化
change_dict = change.to_dict()
restored_change = FileChange.from_dict(change_dict)

print(f"文件路径: {change.file_path}")
print(f"是否新文件: {change.is_new}")
print(f"是否删除: {change.is_deletion}")
```

### 2. ChangeRecord 数据模型

```python
from autocoder.common.file_checkpoint.models import ChangeRecord

# 创建变更记录
record = ChangeRecord.create(
    file_path="src/example.py",
    backup_id="backup_123",
    is_new=False,
    is_deletion=False,
    group_id="group_456"
)

print(f"变更ID: {record.change_id}")
print(f"时间戳: {record.timestamp}")
print(f"文件路径: {record.file_path}")
print(f"备份ID: {record.backup_id}")
print(f"组ID: {record.group_id}")

# 序列化
record_dict = record.to_dict()
restored_record = ChangeRecord.from_dict(record_dict)
```

### 3. 结果对象处理

```python
from autocoder.common.file_checkpoint.models import ApplyResult, UndoResult

# 处理应用结果
def handle_apply_result(result: ApplyResult):
    if result.success:
        print("✅ 变更应用成功")
        print(f"成功的变更ID: {result.change_ids}")
    else:
        print("❌ 变更应用失败")
        for file_path, error in result.errors.items():
            print(f"  {file_path}: {error}")
    
    if result.has_errors:
        print("⚠️  存在部分错误")

# 处理撤销结果
def handle_undo_result(result: UndoResult):
    if result.success:
        print("✅ 变更撤销成功")
        print(f"恢复的文件: {result.restored_files}")
    else:
        print("❌ 变更撤销失败")
        for file_path, error in result.errors.items():
            print(f"  {file_path}: {error}")
```

## 存储和备份管理

### 1. 自定义存储配置

```python
# 自定义存储目录
custom_manager = FileChangeManager(
    project_dir="/path/to/project",
    backup_dir="/custom/backup/path",
    store_dir="/custom/store/path",
    max_history=100,  # 保留更多历史记录
    conversation_store_dir="/custom/conversation/path"
)

# 获取存储统计信息
history_count = len(custom_manager.get_change_history(limit=1000))
print(f"历史记录数量: {history_count}")

# 清理旧的备份（通过备份管理器）
backup_manager = custom_manager.backup_manager
# backup_manager.cleanup_old_backups(days=30)  # 清理30天前的备份
```

### 2. 备份验证和恢复

```python
# 验证备份完整性
def verify_backups(manager: FileChangeManager):
    """验证备份文件的完整性"""
    history = manager.get_change_history(limit=50)
    
    for record in history:
        if record.backup_id:
            # 检查备份文件是否存在
            backup_exists = manager.backup_manager.backup_exists(record.backup_id)
            if not backup_exists:
                print(f"⚠️  备份文件缺失: {record.backup_id} (文件: {record.file_path})")
            else:
                print(f"✅ 备份文件正常: {record.backup_id}")

# 手动恢复特定备份
def manual_restore(manager: FileChangeManager, file_path: str, backup_id: str):
    """手动从备份恢复文件"""
    abs_path = manager._get_absolute_path(file_path)
    success = manager.backup_manager.restore_file(abs_path, backup_id)
    
    if success:
        print(f"✅ 文件 {file_path} 已从备份 {backup_id} 恢复")
    else:
        print(f"❌ 文件 {file_path} 恢复失败")
    
    return success
```

### 3. 高级查询和过滤

```python
# 按时间范围查询变更
from datetime import datetime, timedelta

def get_changes_in_range(manager: FileChangeManager, hours: int = 24):
    """获取指定时间范围内的变更"""
    now = datetime.now()
    start_time = now - timedelta(hours=hours)
    start_timestamp = start_time.timestamp()
    
    all_changes = manager.get_change_history(limit=1000)
    recent_changes = [
        change for change in all_changes 
        if change.timestamp >= start_timestamp
    ]
    
    return recent_changes

# 按文件类型分组变更
def group_changes_by_type(changes):
    """按文件类型分组变更"""
    groups = {}
    
    for change in changes:
        ext = os.path.splitext(change.file_path)[1] or "no_extension"
        if ext not in groups:
            groups[ext] = []
        groups[ext].append(change)
    
    return groups

# 使用示例
recent_changes = get_changes_in_range(manager, hours=12)
grouped = group_changes_by_type(recent_changes)

for file_type, type_changes in grouped.items():
    print(f"{file_type}: {len(type_changes)} 个变更")
```

## 使用示例

### 完整的文件变更管理流程

```python
#!/usr/bin/env python3
"""
完整的文件变更管理流程示例
展示如何在 Auto-Coder 中集成文件变更管理
"""

import os
import uuid
from datetime import datetime
from autocoder.common.file_checkpoint import (
    FileChangeManager, FileChange, ChangeRecord, ApplyResult, UndoResult
)

class CodeChangeWorkflow:
    """代码变更工作流管理"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.setup_manager()
    
    def setup_manager(self):
        """设置文件变更管理器"""
        # 在项目目录下创建 .autocoder 目录用于存储变更信息
        autocoder_dir = os.path.join(self.project_dir, ".autocoder")
        
        self.manager = FileChangeManager(
            project_dir=self.project_dir,
            backup_dir=os.path.join(autocoder_dir, "backups"),
            store_dir=os.path.join(autocoder_dir, "changes"),
            conversation_store_dir=os.path.join(autocoder_dir, "conversations"),
            max_history=100
        )
    
    def implement_feature(self, feature_name: str, file_changes: dict, 
                         conversations: list = None):
        """实现新功能的完整流程"""
        print(f"🚀 开始实现功能: {feature_name}")
        
        # 1. 预览变更
        print("\n📋 预览变更:")
        diff_results = self.manager.preview_changes(file_changes)
        
        for file_path, diff in diff_results.items():
            print(f"  📁 {file_path}: {diff.get_diff_summary()}")
        
        # 2. 确认后应用变更
        confirm = input("\n是否应用这些变更? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 变更已取消")
            return None
        
        # 3. 生成变更组ID
        group_id = str(uuid.uuid4())
        
        # 4. 应用变更
        if conversations:
            result = self.manager.apply_changes_with_conversation(
                changes=file_changes,
                conversations=conversations,
                change_group_id=group_id,
                metadata={
                    "feature_name": feature_name,
                    "timestamp": datetime.now().isoformat(),
                    "change_type": "feature_implementation"
                }
            )
        else:
            result = self.manager.apply_changes(file_changes, group_id)
        
        # 5. 处理结果
        if result.success:
            print(f"✅ 功能 '{feature_name}' 实现成功")
            print(f"   变更组ID: {group_id}")
            print(f"   变更数量: {len(result.change_ids)}")
            return group_id
        else:
            print(f"❌ 功能 '{feature_name}' 实现失败:")
            for file_path, error in result.errors.items():
                print(f"   {file_path}: {error}")
            return None
    
    def rollback_feature(self, group_id: str):
        """回滚功能实现"""
        print(f"🔄 回滚变更组: {group_id}")
        
        # 获取变更组信息
        changes = self.manager.get_changes_by_group(group_id)
        if not changes:
            print("❌ 未找到指定的变更组")
            return False
        
        print(f"📋 将回滚 {len(changes)} 个变更:")
        for change in changes:
            change_time = datetime.fromtimestamp(change.timestamp)
            print(f"  📁 {change.file_path} ({change_time})")
        
        # 确认回滚
        confirm = input("\n是否确认回滚? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 回滚已取消")
            return False
        
        # 执行回滚
        undo_result, checkpoint = self.manager.undo_change_group_with_conversation(group_id)
        
        if undo_result.success:
            print("✅ 回滚成功")
            print(f"   恢复文件: {len(undo_result.restored_files)}")
            
            if checkpoint:
                print(f"   恢复对话检查点: {checkpoint.checkpoint_id}")
                print(f"   对话数量: {len(checkpoint.conversations)}")
            
            return True
        else:
            print("❌ 回滚失败:")
            for file_path, error in undo_result.errors.items():
                print(f"   {file_path}: {error}")
            return False
    
    def show_history(self, limit: int = 10):
        """显示变更历史"""
        print(f"📚 最近 {limit} 个变更:")
        
        history = self.manager.get_change_history(limit)
        
        if not history:
            print("   暂无变更记录")
            return
        
        for i, record in enumerate(history, 1):
            timestamp = datetime.fromtimestamp(record.timestamp)
            status = "🆕" if record.is_new else "🗑️" if record.is_deletion else "✏️"
            
            print(f"   {i}. {status} {record.file_path}")
            print(f"      ID: {record.change_id}")
            print(f"      时间: {timestamp}")
            if record.group_id:
                print(f"      组: {record.group_id}")
            print()
    
    def interactive_session(self):
        """交互式会话"""
        print("🎯 Auto-Coder 文件变更管理系统")
        print("支持的命令: history, rollback, status, exit")
        
        while True:
            try:
                command = input("\nauto-coder-changes> ").strip().lower()
                
                if command == "exit":
                    break
                elif command == "history":
                    limit = input("显示多少条记录? (默认10): ").strip()
                    limit = int(limit) if limit.isdigit() else 10
                    self.show_history(limit)
                elif command == "status":
                    self.show_status()
                elif command.startswith("rollback"):
                    parts = command.split()
                    if len(parts) > 1:
                        group_id = parts[1]
                        self.rollback_feature(group_id)
                    else:
                        print("用法: rollback <group_id>")
                else:
                    print("未知命令，支持: history, rollback, status, exit")
                    
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
    
    def show_status(self):
        """显示当前状态"""
        print("📊 变更管理状态:")
        
        # 总变更数
        all_changes = self.manager.get_change_history(limit=1000)
        print(f"   总变更数: {len(all_changes)}")
        
        # 变更组数
        groups = self.manager.get_change_groups(limit=100)
        print(f"   变更组数: {len(groups)}")
        
        # 最近的变更
        if all_changes:
            latest = all_changes[0]
            latest_time = datetime.fromtimestamp(latest.timestamp)
            print(f"   最近变更: {latest.file_path} ({latest_time})")
        
        # 对话检查点
        checkpoints = self.manager.get_available_checkpoints(limit=10)
        print(f"   对话检查点: {len(checkpoints)}")

def main():
    """主程序"""
    import sys
    
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    if not os.path.exists(project_dir):
        print(f"❌ 项目目录不存在: {project_dir}")
        return
    
    workflow = CodeChangeWorkflow(project_dir)
    
    # 示例：实现一个简单功能
    sample_changes = {
        "src/hello.py": FileChange(
            file_path="src/hello.py",
            content="def hello(name):\n    return f'Hello, {name}!'\n",
            is_new=True
        )
    }
    
    sample_conversations = [
        {"role": "user", "content": "请创建一个hello函数"},
        {"role": "assistant", "content": "我将为您创建hello函数"}
    ]
    
    # 实现功能
    group_id = workflow.implement_feature(
        "hello_function",
        sample_changes,
        sample_conversations
    )
    
    # 显示历史
    workflow.show_history()
    
    # 启动交互式会话
    workflow.interactive_session()

if __name__ == "__main__":
    main()
```

## 验证命令

验证 file_checkpoint 模块功能：

```bash
# 检查模块导入
python -c "
from autocoder.common.file_checkpoint import FileChangeManager, FileChange, ChangeRecord
print('✅ 模块导入成功')
"

# 验证数据模型
python -c "
from autocoder.common.file_checkpoint.models import FileChange, ChangeRecord, ApplyResult, UndoResult
change = FileChange('test.py', 'print(\"test\")', is_new=True)
record = ChangeRecord.create('test.py', 'backup_123')
print(f'✅ 数据模型正常: {change.file_path}, {record.change_id}')
"

# 验证管理器功能
python -c "
from autocoder.common.file_checkpoint import FileChangeManager
import tempfile
import os

with tempfile.TemporaryDirectory() as temp_dir:
    manager = FileChangeManager(temp_dir)
    print('✅ 文件变更管理器创建成功')
    
    # 测试基本功能
    history = manager.get_change_history()
    print(f'✅ 历史记录查询正常: {len(history)} 条记录')
"

# 验证备份功能
python -c "
from autocoder.common.file_checkpoint.backup import FileBackupManager
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    backup_manager = FileBackupManager(temp_dir)
    print('✅ 备份管理器创建成功')
"

# 验证存储功能
python -c "
from autocoder.common.file_checkpoint.store import FileChangeStore
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    store = FileChangeStore(temp_dir)
    print('✅ 变更存储器创建成功')
"

# 运行单元测试（如果存在）
python -m pytest src/autocoder/common/file_checkpoint/test_*.py -v || echo "⚠️  单元测试文件不存在或测试失败"
```

通过这些验证命令可以确认 file_checkpoint 模块的完整性和功能正确性。 