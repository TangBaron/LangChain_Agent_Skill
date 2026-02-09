# LangChainSkills

基于 LangChain 的可扩展智能体系统，支持动态加载和管理多种 Skill（技能）。

## 功能特性

- **动态 Skill 加载**：自动发现和加载 Skills 目录下的技能模块
- **工具激活机制**：通过 Loader Tool 按需激活特定技能
- **中间件支持**：实现动态工具过滤和状态管理
- **灵活配置**：支持 YAML 配置文件自定义系统行为

## 项目结构

```
LangChainSkills/
├── core/           # 核心模块（基类、注册表、状态管理）
├── middleware/     # 中间件（工具过滤）
├── models/         # 模型封装（DeepSeek）
├── skills/         # 技能实现（数据分析、PDF处理等）
├── config/         # 配置管理
└── agent.py        # 主程序入口
```

## 快速开始

### 环境配置

1. 安装依赖：
```bash
pip install langchain langchain-deepseek
```

2. 配置环境变量（`.env` 文件）：
```
DEEPSEEK_API_KEY=your_api_key_here
```

3. 修改 `config.yaml` 配置文件（可选）

### 运行

```bash
python agent.py
```

## 内置技能

- **数据分析**：统计计算、图表生成、数据摘要
- **PDF 处理**：PDF 文档解析和处理

## 自定义 Skill

在 `skills/` 目录下创建新技能文件夹，包含：
- `skill.py`：技能实现（继承 `BaseSkill`）
- `instructions.md`：使用说明

系统会自动发现并加载新技能。

## 配置说明

主要配置项（`config.yaml`）：
- `skills_dir`：Skills 目录路径
- `auto_discover`：是否自动发现 Skills
- `middleware_enabled`：是否启用中间件
- `verbose`：详细日志开关

## 技术栈

- LangChain
- LangGraph
- DeepSeek API
