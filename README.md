#OpenManus

OpenManus 一个简洁、开源的智能体实现方案。

## 快速开始
### 安装步骤
**1. 创建 Conda 环境**
```bash
conda create -n open_manus python=3.11 -y
conda activate open_manus
```

**2. 安装依赖**
```bash
pip install -r requirements.txt
playwright install
```

**3. 配置 API**
```bash
config/config.toml
```

**4. 验证安装**
```bash
python main.py --prompt "请说 Hello World"
```

## 使用方法
### 启动项目
**方式一：命令行参数（推荐）**
```bash
conda activate open_manus
python main.py --prompt "你好"
```

**方式二：交互式输入**
```bash
conda activate open_manus
python main.py  # 然后根据提示输入您的需求
```

### 执行流程
运行 `python main.py --prompt "你的提示"` 时，系统按以下流程执行：
1. **初始化阶段** - 创建 Manus 智能体，加载配置，初始化工具集合
2. **任务处理阶段** - 接收提示，分析需求，制定计划，自动选择工具组合（最多 20 步）
3. **工具执行阶段** - 根据任务自动选择工具：
   - `str_replace_editor` - 文件操作（查看、创建、编辑）
   - `browser_use` - 浏览器（搜索、内容提取、导航）
   - `python_execute` - Python 代码执行
   - 其他工具 - 动态选择
4. **结果输出阶段** - 实时显示执行结果，文件保存在 `workspace/` 目录
5. **完成退出** - 调用 `terminate` 工具，断开 MCP 连接，输出完成信息

### 注意事项
- **Token 使用**: 实时显示输入、输出和累计统计
- **错误处理**: 工具失败时自动尝试替代方案
- **中断处理**: 使用 `Ctrl+C` 安全中断任务
- **日志文件**: 详细日志保存在 `logs/` 目录

## 🏗️ 项目架构
```
OpenManus/
├── app/                    # 核心代码
│   ├── agent/              # 智能体逻辑 (Manus 等)
│   ├── flow/               # 多智能体流程控制
│   ├── tool/               # 工具集
│   ├── llm.py              # LLM 接口封装
│   └── config.py           # 配置管理
├── config/                 # 配置文件
├── workspace/              # 生成文件存放目录
├── logs/                   # 日志文件目录
├── main.py                 # 单智能体启动入口
├── run_flow.py             # 多智能体流程启动入口
└── run_mcp.py              # MCP 工具服务入口
```

## 🛠️ 开发指南
### 添加新功能
1. **开发代码** - 在 `app/` 目录下修改或添加代码，参考 `app/tool/` 下的现有代码结构
2. **本地测试**
   ```bash
   python main.py --prompt "测试您的新功能"
   ```
3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加了超级厉害的功能"
   git push origin feature/new-amazing-tool
   ```
---
