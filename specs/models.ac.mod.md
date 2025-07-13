# models

Auto-Coder 系统的核心模型配置管理模块，负责 AI 模型的配置存储、加载、更新和管理，支持多种模型类型和 API 密钥管理，为整个系统提供统一的模型访问接口。

## 模块位置

**源码路径**: `src/autocoder/models.py`  
**文档路径**: `specs/models.ac.mod.md`  
**模块类型**: 单文件模块

## 文件结构

```python
# models.py 内容结构
├── 导入部分                    # os, json, typing, urllib.parse 等依赖导入
├── MODELS_JSON                 # 模型配置文件路径常量
├── default_models_list         # 默认模型列表配置
├── process_api_key_path()      # API密钥路径处理函数
├── load_models()               # 模型配置加载函数
├── save_models()               # 模型配置保存函数
├── add_and_activate_models()   # 添加和激活模型函数
├── get_model_by_name()         # 根据名称获取模型函数
├── update_model_input_price()  # 更新模型输入价格函数
├── update_model_output_price() # 更新模型输出价格函数
├── update_model_speed()        # 更新模型速度函数
├── check_model_exists()        # 检查模型是否存在函数
├── update_model_with_api_key() # 更新模型API密钥函数
└── update_model()              # 更新模型信息函数
```

## 快速开始

### 基本使用方式

```python
# 导入模块
from autocoder.models import (
    load_models, save_models, get_model_by_name, 
    add_and_activate_models, check_model_exists,
    update_model_input_price, update_model_output_price
)

# 1. 加载模型列表
models = load_models()
print(f"可用模型数量: {len(models)}")

# 2. 查找特定模型
model = get_model_by_name("deepseek/v3")
if model:
    print(f"模型类型: {model['model_type']}")
    print(f"基础URL: {model['base_url']}")

# 3. 检查模型是否存在
if check_model_exists("gpt-4"):
    print("GPT-4 模型已配置")

# 4. 添加新模型
new_models = [{
    "name": "custom/model",
    "description": "自定义模型",
    "model_name": "custom-model",
    "model_type": "saas/openai",
    "base_url": "https://api.custom.com/v1",
    "api_key": "your-api-key-here"
}]
add_and_activate_models(new_models)

# 5. 更新模型价格
update_model_input_price("deepseek/v3", 0.1)
update_model_output_price("deepseek/v3", 0.2)
```

### 模型配置格式

```python
# 标准模型配置结构
model_config = {
    "name": "deepseek/v3",                    # 模型名称（唯一标识）
    "description": "DeepSeek Chat is for coding", # 模型描述
    "model_name": "deepseek-chat",            # 实际模型名称
    "model_type": "saas/openai",              # 模型类型
    "base_url": "https://api.deepseek.com/v1", # API基础URL
    "api_key_path": "api.deepseek.com",       # API密钥文件路径
    "is_reasoning": False,                    # 是否为推理模型
    "input_price": 0.0,                       # 输入价格（百万tokens）
    "output_price": 0.0,                      # 输出价格（百万tokens）
    "average_speed": 0.0,                     # 平均速度（秒/请求）
    "max_output_tokens": 8096                 # 最大输出tokens
}
```

### 主要功能

该模块提供完整的 AI 模型配置管理功能，包括模型的增删改查、价格配置、API 密钥管理和性能参数设置，支持多种模型类型的统一管理。

## 核心组件详解

### 1. 模块常量

**MODELS_JSON**
- **功能**: 模型配置文件的存储路径
- **值**: `~/.auto-coder/keys/models.json`
- **用途**: 所有模型配置的持久化存储位置

**default_models_list**
- **功能**: 系统预定义的默认模型列表
- **内容**: 包含 DeepSeek、GPT、Claude、Gemini 等主流模型配置
- **特点**: 提供开箱即用的模型配置，支持多种 AI 服务商

### 2. 主要函数

**process_api_key_path(base_url: str) -> str**
- **功能**: 从基础URL中提取并处理API密钥路径
- **参数**: base_url - API基础URL
- **返回值**: 处理后的密钥路径字符串
- **处理规则**: 提取主机名，将冒号替换为下划线
- **使用示例**: 
```python
path = process_api_key_path("https://api.openai.com:443/v1")
# 返回: "api.openai.com_443"
```

**load_models() -> List[Dict]**
- **功能**: 加载模型配置列表，合并默认模型和自定义模型
- **返回值**: 完整的模型配置列表
- **处理逻辑**: 
  - 从默认模型列表开始
  - 读取用户配置文件中的自定义模型
  - 合并并去重（基于模型名称）
  - 自动加载对应的 API 密钥
- **使用示例**:
```python
models = load_models()
for model in models:
    print(f"{model['name']}: {model['description']}")
```

**save_models(models: List[Dict]) -> None**
- **功能**: 将模型配置列表保存到配置文件
- **参数**: models - 要保存的模型列表
- **文件格式**: JSON 格式，UTF-8 编码
- **使用示例**:
```python
models = load_models()
models.append(new_model_config)
save_models(models)
```

**add_and_activate_models(models: List[Dict]) -> None**
- **功能**: 添加新模型并激活（设置API密钥）
- **参数**: models - 要添加的模型列表
- **处理逻辑**: 
  - 检查模型是否已存在，避免重复添加
  - 保存模型配置
  - 如果模型包含API密钥，自动设置密钥文件
- **使用示例**:
```python
new_models = [{
    "name": "custom/gpt-4",
    "model_name": "gpt-4",
    "api_key": "sk-xxx...",
    # 其他配置...
}]
add_and_activate_models(new_models)
```

**get_model_by_name(name: str) -> Dict**
- **功能**: 根据模型名称查找模型配置
- **参数**: name - 模型名称
- **返回值**: 模型配置字典，找不到时返回None
- **错误处理**: 找不到模型时显示错误信息
- **使用示例**:
```python
model = get_model_by_name("deepseek/v3")
if model:
    print(f"模型类型: {model['model_type']}")
```

**update_model_input_price(name: str, price: float) -> bool**
- **功能**: 更新指定模型的输入价格
- **参数**: 
  - name - 模型名称
  - price - 新的输入价格（百万tokens）
- **返回值**: 更新成功返回True，否则返回False
- **使用示例**:
```python
success = update_model_input_price("gpt-4", 0.03)
print(f"价格更新{'成功' if success else '失败'}")
```

**update_model_output_price(name: str, price: float) -> bool**
- **功能**: 更新指定模型的输出价格
- **参数**: 
  - name - 模型名称
  - price - 新的输出价格（百万tokens）
- **返回值**: 更新成功返回True，否则返回False

**update_model_speed(name: str, speed: float) -> bool**
- **功能**: 更新指定模型的平均处理速度
- **参数**: 
  - name - 模型名称
  - speed - 新的平均速度（秒/请求）
- **返回值**: 更新成功返回True，否则返回False

**check_model_exists(name: str) -> bool**
- **功能**: 检查指定名称的模型是否存在
- **参数**: name - 模型名称
- **返回值**: 存在返回True，否则返回False
- **使用示例**:
```python
if check_model_exists("gpt-4"):
    print("GPT-4 模型已配置")
else:
    print("GPT-4 模型未配置")
```

**update_model_with_api_key(name: str, api_key: str) -> Dict**
- **功能**: 更新模型的API密钥
- **参数**: 
  - name - 模型名称
  - api_key - API密钥
- **返回值**: 更新后的模型配置
- **处理逻辑**: 
  - 查找指定模型
  - 生成API密钥文件路径
  - 保存密钥到文件
  - 更新模型配置
- **使用示例**:
```python
updated_model = update_model_with_api_key("gpt-4", "sk-xxx...")
if updated_model:
    print("API密钥更新成功")
```

**update_model(name: str, model_data: Dict) -> Dict**
- **功能**: 更新模型的完整配置信息
- **参数**: 
  - name - 模型名称
  - model_data - 包含更新信息的字典
- **支持更新的字段**: description, model_name, model_type, base_url, api_key, is_reasoning, input_price, output_price, max_output_tokens, average_speed
- **返回值**: 更新后的模型配置
- **使用示例**:
```python
updated_model = update_model("gpt-4", {
    "description": "更新后的描述",
    "input_price": 0.03,
    "output_price": 0.06
})
```

## Mermaid 依赖图

```mermaid
graph TB
    %% 模块组件
    Constants[常量定义<br/>MODELS_JSON<br/>default_models_list]
    LoadSave[加载保存<br/>load_models()<br/>save_models()]
    ModelOps[模型操作<br/>get_model_by_name()<br/>add_and_activate_models()<br/>check_model_exists()]
    Updates[更新功能<br/>update_model_input_price()<br/>update_model_output_price()<br/>update_model_speed()<br/>update_model()]
    APIKey[API密钥管理<br/>process_api_key_path()<br/>update_model_with_api_key()]
    
    %% 外部依赖
    FileSystem[文件系统<br/>~/.auto-coder/keys/]
    JSON[JSON配置<br/>models.json]
    
    %% 内部依赖关系
    LoadSave --> Constants
    ModelOps --> LoadSave
    Updates --> LoadSave
    APIKey --> LoadSave
    LoadSave --> FileSystem
    LoadSave --> JSON
    APIKey --> FileSystem
    
    %% 样式定义
    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef utilClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px
    classDef extClass fill:#fff3e0,stroke:#ef6c00,stroke-width:1px
    
    class Constants,LoadSave coreClass
    class ModelOps,Updates,APIKey utilClass
    class FileSystem,JSON extClass
```

## 依赖关系说明

### 对其他模块的依赖
该模块为纯功能模块，主要依赖 Python 标准库，无需依赖其他 Auto-Coder 模块：

- **标准库依赖**: os, json, typing, urllib.parse

### 被依赖关系
作为模型配置管理的核心模块，被以下模块广泛使用：

- `specs/auto_coder_runner.ac.mod.md` - 模型管理命令处理
- `specs/auto_coder.ac.mod.md` - 主入口的模型加载
- `specs/chat.ac.mod.md` - 聊天模块的模型操作
- `specs/utils_llms.ac.mod.md` - LLM 工具的模型信息获取
- `specs/common_command_completer.ac.mod.md` - 命令补全的模型名称
- `specs/rag.ac.mod.md` - RAG 系统的模型配置

## 可以验证模块可运行的测试命令

```bash
# Python模块测试
python -c "from autocoder.models import load_models; print(f'加载了 {len(load_models())} 个模型')"

# 检查特定模型
python -c "from autocoder.models import get_model_by_name; model = get_model_by_name('deepseek/v3'); print(f'找到模型: {model is not None}')"

# 测试模型存在性检查
python -c "from autocoder.models import check_model_exists; print(f'deepseek/v3 存在: {check_model_exists(\"deepseek/v3\")}')"

# 查看配置文件路径
python -c "from autocoder.models import MODELS_JSON; print(f'配置文件路径: {MODELS_JSON}')"

# 测试API密钥路径处理
python -c "from autocoder.models import process_api_key_path; print(f'处理结果: {process_api_key_path(\"https://api.openai.com:443/v1\")}')"
``` 