# OpenManus 项目架构

## 目录结构
```
app/
├── agent/          # 智能体核心逻辑
│   ├── base.py     # 基础智能体类
│   ├── manus.py    # Manus 主智能体
│   ├── toolcall.py # 工具调用智能体
│   └── react.py    # ReAct 模式实现
├── tool/           # 工具集
│   ├── base.py     # 工具基类
│   ├── tool_collection.py # 工具集合管理
│   └── [各种工具实现]
├── flow/           # 多智能体流程控制
├── prompt/         # 提示词模板
├── config.py       # 配置管理
└── logger.py       # 日志配置
```

## 核心组件
- **智能体（Agent）**: 继承自 `ToolCallAgent`，实现任务处理逻辑
- **工具（Tool）**: 继承自 `BaseTool`，实现具体功能
- **工具集合（ToolCollection）**: 管理可用工具
- **MCP 客户端**: 支持远程工具访问
