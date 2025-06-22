# AutoCoder Slim 项目规范文档

## 📋 目录说明

本目录(`specs/`)是AutoCoder Slim项目的**唯一官方文档存放位置**，包含所有项目规范、规划、分析和跟踪文档。

## 🚨 文档管理规范

### 重要规则
**所有项目相关的规范、规划、跟踪文档必须统一放置在本目录下，禁止在其他位置创建！**

### 目录结构
```
specs/
├── README.md                 # 本文档 - 目录说明
├── PROJECT_OVERVIEW.md       # 项目总览和文档管理规范
├── GET_STARTED.md           # 项目启动指南
├── plan.md                  # 总体技术规划
├── dependencies.md          # 依赖分析报告
├── agent.md                 # Agent系统分析
├── auto_coder_runner.md     # 运行器分析
├── api-compatibility.md     # API兼容性规范
├── testing-strategy.md      # 测试策略
├── phase1/                  # Phase 1 详细文档
│   └── phase1-core-extraction.md
├── phase2/                  # Phase 2 详细文档
│   └── phase2-sdk-migration.md
└── phase3/                  # Phase 3 详细文档
    └── phase3-integration.md
```

## 📖 核心文档指南

### 新手入门
1. **[PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)** - 项目总览，了解项目目标和架构
2. **[GET_STARTED.md](./GET_STARTED.md)** - 启动指南，开始具体实施

### 技术规划
3. **[plan.md](./plan.md)** - 总体技术规划和迁移策略
4. **[dependencies.md](./dependencies.md)** - 完整的依赖分析报告

### 系统分析
5. **[agent.md](./agent.md)** - Agent系统深度分析
6. **[auto_coder_runner.md](./auto_coder_runner.md)** - 运行器功能映射

### 实施阶段
7. **[phase1/](./phase1/)** - Phase 1: 核心模块1:1迁移
8. **[phase2/](./phase2/)** - Phase 2: SDK完整迁移  
9. **[phase3/](./phase3/)** - Phase 3: 集成优化

## 📝 文档创建规则

### 新文档创建
- ✅ **正确位置**: `specs/` 或其子目录下
- ❌ **禁止位置**: 根目录、docs/、其他任何位置

### 文档分类
- **项目级别文档**: 直接放在 `specs/`
- **阶段文档**: 放在对应的 `phase1/`, `phase2/`, `phase3/`
- **主题文档**: 可创建新的主题子目录

### 命名规范
- 使用描述性文件名: `agent.md`, `api-compatibility.md`
- 避免通用名称: `doc.md`, `notes.md`
- 同类型文档只保留最新版本

## 🔗 快速导航

| 任务 | 推荐文档 |
|------|----------|
| 了解项目 | [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) |
| 开始迁移 | [GET_STARTED.md](./GET_STARTED.md) |
| 查看规划 | [plan.md](./plan.md) |
| 分析依赖 | [dependencies.md](./dependencies.md) |
| Phase 1实施 | [phase1/phase1-core-extraction.md](./phase1/phase1-core-extraction.md) |

---

**维护原则**: 保持文档集中、分类清晰、版本唯一、避免重复 