# Autocoder Input YAML Schema 使用指南

这个 JSON Schema 为 `autocoder_input.yaml` 文件提供了智能补全功能，特别是支持 `@` 和 `@@` 符号的补全。

## 文件结构

```
├── autocoder-schema.json         # 主Schema文件
├── autocoder-improved-schema.json # 增强版Schema文件
├── symbols/
│   ├── single-at-symbols.json    # 单@符号定义
│   └── double-at-symbols.json    # 双@@符号定义
└── .vscode/
    └── settings.json             # VS Code配置
```

## 设置说明

1. 在VS Code中已配置此Schema以匹配所有`*autocoder_input.yaml`文件
2. 当编辑这些文件时，会提供命令和符号的智能补全

## 支持的功能

1. `cmd` 字段限制为有效命令列表：
   - `/ask`
   - `/chat`
   - `/coding`
   - `/coding/apply`

2. `content` 字段支持以下符号补全：
   - 单`@`符号：如`@user`, `@file`, `@var`等
   - 双`@@`符号：如`@@include`, `@@import`, `@@env`等

## 如何使用符号补全

当在`content`字段中输入文本时，如果需要插入符号：

1. 输入`@`，然后按`Ctrl+Space`触发补全菜单
2. 输入`@@`，然后按`Ctrl+Space`触发补全菜单

### 示例

```yaml
cmd: /ask
content: |
  请帮我检查 @file 代码中的问题
  
  并包含 @@include 文件的内容
```

## 扩展符号列表

如需添加更多符号，只需编辑以下文件：

- 单@符号：编辑 `symbols/single-at-symbols.json`
- 双@@符号：编辑 `symbols/double-at-symbols.json`

## 注意事项

- JSON Schema 的补全功能在多行字符串中可能需要手动触发
- 两个Schema文件提供了不同的实现方式，可根据效果选择使用
- 在VS Code设置中可以切换使用哪个Schema文件 