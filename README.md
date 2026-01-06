# 👋 OpenManus

OpenManus 无需邀请码即可实现任何创意 🛫！这是一个简洁、开源的智能体实现方案。

## 🚀 快速启动 (Conda 专属)

### 1. 环境准备
确保您的电脑已安装 [Conda](https://docs.anaconda.com/miniconda/)、Git。

```bash
cd OpenManus

# 3. 创建并激活 Conda 环境 (推荐 Python 3.11)
conda create -n open_manus python=3.11 -y
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

## 📋 运行流程

### 启动项目

1. **激活 Conda 环境**：
   ```bash
   conda activate open_manus
   ```

2. **运行主程序**：
   ```bash
   # 方式1: 通过命令行参数传入提示
   python main.py --prompt "你好"

   # 方式2: 交互式输入（不提供 --prompt 参数）
   python main.py
   # 然后输入您的提示
   ```

### 执行流程

当您运行 `python main.py --prompt "你的提示"` 时，系统会按以下流程执行：

1. **初始化阶段**
   - 创建并初始化 Manus 智能体
   - 加载配置文件 (`config/config.toml`)
   - 初始化工具集合（文件操作、浏览器、Python 执行等）

2. **任务处理阶段**
   - 智能体接收用户提示
   - 分析任务需求并制定执行计划
   - 根据任务类型自动选择最合适的工具组合
   - 执行多步骤任务（最多 20 步）

3. **工具执行阶段**
   - **文件操作工具** (`str_replace_editor`): 查看、创建、编辑文件
   - **浏览器工具** (`browser_use`): 网络搜索、网页内容提取、页面导航
   - **Python 执行工具** (`python_execute`): 执行 Python 代码
   - **其他工具**: 根据任务需求动态选择

4. **结果输出阶段**
   - 每个步骤的执行结果会实时显示
   - 生成的文件保存在 `workspace/` 目录
   - 任务完成后自动清理资源

5. **完成退出**
   - 智能体调用 `terminate` 工具标记任务完成
   - 断开所有 MCP 服务器连接
   - 输出 "Request processing completed." 并退出

### 执行示例

```bash
# 示例：测试中文提示
conda activate open_manus
python main.py --prompt "你好"

# 执行过程会显示：
# - 每个步骤的思考过程
# - 选择的工具和参数
# - 工具执行结果
# - Token 使用统计
# - 最终完成状态
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
