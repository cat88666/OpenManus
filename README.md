# 👋 OpenManus

OpenManus 无需邀请码即可实现任何创意 🛫！这是一个简洁、开源的智能体实现方案。

## 🚀 快速启动 (Conda 专属)

### 1. 环境准备
确保您的电脑已安装 [Conda](https://docs.anaconda.com/miniconda/)、Git。

```bash
# 1. 并在 GitHub 点击 Fork 将项目复制到您自己的仓库
# 2. 克隆您的 Fork 仓库 (请将 `username` 替换为您自己的 GitHub 用户名)
git clone https://github.com/username/OpenManus.git
cd OpenManus

# 3. 创建并激活 Conda 环境 (推荐 Python 3.12)
conda create -n open_manus python=3.12 -y
conda activate open_manus

# 4. 安装依赖
pip install -r requirements.txt

# 5. 安装浏览器驱动 (用于 Web 浏览功能)
playwright install
```

### 2. 配置 API
OpenManus 需要配置 LLM 密钥才能运行。

1.  复制配置模板：
    ```bash
    cp config/config.example.toml config/config.toml
    ```
2.  编辑 `config/config.toml` (使用记事本或 VS Code) 并填入您的 API Key：
    ```toml
    [llm]
    model = "gpt-4o"
    base_url = "https://api.openai.com/v1"
    api_key = "sk-..."  # 您的 API Key
    ```

### 3. 本地验证
在正式使用前，运行一个简单的命令测试配置是否成功：

```bash
# 测试简单的问答
python main.py --prompt "请说 Hello World"

# 如果配置成功，您将看到 AI 的回复。
```

---

## 🏗️ 项目架构

```text
OpenManus/
├── app/                # 核心代码目录
│   ├── agent/          # 智能体核心逻辑 (Manus 等)
│   ├── basic/          # 基础组件 (Memory, Planning)
│   ├── flow/           # 多智能体流程控制
│   └── tool/           # 工具集 (Browsing, File, Python 执行等)
├── config/             # 配置文件目录
├── main.py             # 单智能体启动入口 (推荐入门)
├── run_flow.py         # 多智能体流程启动入口
└── run_mcp.py          # MCP 工具服务入口
```

## ⚙️ 关键配置说明

`config.toml` 是本项目的控制中心，支持多模型配置。

*   **`[llm]`**: 主模型，用于规划和对话。
*   **`[llm.vision]`**: 视觉模型，用于查看网页截图（通常与主模型一致）。
*   **`max_tokens`**: 允许生成的最大长度。

## 🛠️ 二次开发流程 (贡献代码)

如果您想为 OpenManus 增加新功能：

1.  **创建开发分支**：
    ```bash
    git checkout -b feature/new-amazing-tool
    ```
2.  **开发**：在 `app/` 目录下修改或添加代码。如果是添加新工具，请参考 `app/tool/` 下的现有代码。
3.  **本地测试**：确保您的改动没有破坏现有功能。
    ```bash
    python main.py --prompt "测试您的新功能"
    ```
4.  **提交更改**：
    ```bash
    git add .
    git commit -m "feat: 添加了超级厉害的功能"
    git push origin feature/new-amazing-tool
    ```
5.  **Pull Request**: 回到 GitHub 页面点击 "Compare & pull request"。

---
