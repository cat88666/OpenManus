# 👋 OpenManus

OpenManus 无需邀请码即可实现任何创意 🛫！这是一个简洁、开源的智能体实现方案。

---

## 📦 快速开始

### 前置要求

- [Conda](https://docs.anaconda.com/miniconda/) 已安装
- Git 已安装

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd OpenManus
```

#### 2. 创建 Conda 环境

```bash
# 创建 Python 3.11 环境
conda create -n open_manus python=3.11 -y

# 激活环境
conda activate open_manus
```

#### 3. 安装依赖

```bash
# 安装 Python 依赖包
pip install -r requirements.txt

# 安装浏览器驱动（用于 Web 浏览功能）
playwright install
```

#### 4. 配置 API

OpenManus 需要配置 LLM 密钥才能运行。

**步骤：**

1. 复制配置模板：
   ```bash
   cp config/config.example.toml config/config.toml
   ```

2. 编辑 `config/config.toml`，填入您的 API Key：
   ```toml
   [llm]
   model = "gpt-4o"
   base_url = "https://api.openai.com/v1"
   api_key = "sk-..."  # 您的 API Key
   ```

#### 5. 验证安装

运行测试命令验证配置是否成功：

```bash
python main.py --prompt "请说 Hello World"
```

如果配置成功，您将看到 AI 的回复。

---

## 🚀 使用方法

### 启动项目

#### 方式一：命令行参数（推荐）

```bash
# 激活环境
conda activate open_manus

# 运行并传入提示
python main.py --prompt "你好"
```

#### 方式二：交互式输入

```bash
# 激活环境
conda activate open_manus

# 运行（不提供 --prompt 参数）
python main.py

# 然后根据提示输入您的需求
```

### 执行流程说明

当您运行 `python main.py --prompt "你的提示"` 时，系统会按以下流程执行：

#### 1. 初始化阶段
- 创建并初始化 Manus 智能体
- 加载配置文件 (`config/config.toml`)
- 初始化工具集合（文件操作、浏览器、Python 执行等）

#### 2. 任务处理阶段
- 智能体接收用户提示
- 分析任务需求并制定执行计划
- 根据任务类型自动选择最合适的工具组合
- 执行多步骤任务（最多 20 步）

#### 3. 工具执行阶段

系统会根据任务需求自动选择以下工具：

| 工具名称 | 功能说明 |
|---------|---------|
| `str_replace_editor` | 文件操作：查看、创建、编辑文件 |
| `browser_use` | 浏览器：网络搜索、网页内容提取、页面导航 |
| `python_execute` | Python 执行：执行 Python 代码 |
| 其他工具 | 根据任务需求动态选择 |

#### 4. 结果输出阶段
- 每个步骤的执行结果会实时显示
- 生成的文件保存在 `workspace/` 目录
- 任务完成后自动清理资源

#### 5. 完成退出
- 智能体调用 `terminate` 工具标记任务完成
- 断开所有 MCP 服务器连接
- 输出 "Request processing completed." 并退出

### 执行示例

```bash
# 完整示例
conda activate open_manus
python main.py --prompt "你好"

# 执行过程会显示：
# ✓ 每个步骤的思考过程
# ✓ 选择的工具和参数
# ✓ 工具执行结果
# ✓ Token 使用统计
# ✓ 最终完成状态
```

### 输出文件位置

所有生成的文件默认保存在 `workspace/` 目录下，例如：
- `workspace/demo_task.py` - 生成的代码文件
- `workspace/python_data_analysis_trends_2024.md` - 生成的报告文件

### 注意事项

- **Token 使用**: 系统会实时显示 Token 使用情况，包括输入、输出和累计统计
- **错误处理**: 如果某个工具执行失败，智能体会自动尝试替代方案
- **中断处理**: 使用 `Ctrl+C` 可以安全中断正在运行的任务
- **日志文件**: 详细的执行日志保存在 `logs/` 目录下

---

## 🏗️ 项目架构

```
OpenManus/
├── app/                    # 核心代码目录
│   ├── agent/              # 智能体核心逻辑 (Manus 等)
│   ├── flow/               # 多智能体流程控制
│   ├── tool/               # 工具集 (Browsing, File, Python 执行等)
│   ├── llm.py              # LLM 接口封装
│   └── config.py           # 配置管理
├── config/                 # 配置文件目录
│   ├── config.toml         # 主配置文件
│   └── config.example.toml # 配置模板
├── workspace/              # 工作空间（生成文件存放目录）
├── logs/                   # 日志文件目录
├── main.py                 # 单智能体启动入口（推荐入门）
├── run_flow.py             # 多智能体流程启动入口
└── run_mcp.py              # MCP 工具服务入口
```

---

## ⚙️ 配置说明

`config/config.toml` 是本项目的控制中心，支持多模型配置。

### 主要配置项

| 配置项 | 说明 |
|-------|------|
| `[llm]` | 主模型配置，用于规划和对话 |
| `[llm.vision]` | 视觉模型配置，用于查看网页截图（通常与主模型一致） |
| `max_tokens` | 允许生成的最大 Token 长度 |

### 配置示例

```toml
[llm]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."

[llm.vision]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."

max_tokens = 4096
```

---

## 🛠️ 开发指南

### 添加新功能

如果您想为 OpenManus 增加新功能，请遵循以下流程：

#### 1. 创建开发分支

```bash
git checkout -b feature/new-amazing-tool
```

#### 2. 开发代码

- 在 `app/` 目录下修改或添加代码
- 如果是添加新工具，请参考 `app/tool/` 下的现有代码结构
- 遵循项目的代码风格和规范

#### 3. 本地测试

确保您的改动没有破坏现有功能：

```bash
python main.py --prompt "测试您的新功能"
```

#### 4. 提交更改

```bash
git add .
git commit -m "feat: 添加了超级厉害的功能"
git push origin feature/new-amazing-tool
```

#### 5. 创建 Pull Request

回到 GitHub 页面点击 "Compare & pull request" 提交代码审查。

---

## 📝 许可证

请查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🤝 贡献

欢迎贡献代码！请查看开发指南部分了解如何参与项目开发。

---
