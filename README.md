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

运行 `python main.py --prompt "你的提示"` 时，系统按以下详细流程执行：

#### 1. 程序启动阶段
```
__main__:main → 解析命令行参数 → 创建 Manus 智能体实例
```

#### 2. 智能体初始化阶段
- 加载配置文件 (`config/config.toml`)
- 初始化工具集合（文件操作、浏览器、Python 执行等）
- 连接 MCP 服务器（如果配置了）
- 设置系统提示词和工作空间路径

#### 3. 任务执行循环（ReAct 模式，最多 20 步）
每个步骤包含以下子流程：

**3.1 思考阶段 (Think)**
```
app.agent.toolcall:think → LLM 分析当前状态 → 生成思考内容
```
- 分析用户需求和当前上下文
- 决定下一步行动
- 选择需要使用的工具

**3.2 工具选择阶段**
```
app.agent.toolcall:think → 选择工具 → 准备工具参数
```
- 根据任务需求选择合适工具
- 准备工具执行所需的参数
- 记录 Token 使用情况（输入/输出/累计）

**3.3 工具执行阶段 (Act)**
```
app.agent.toolcall:execute_tool → 工具执行 → 获取结果
```
- 激活选定的工具
- 执行具体操作（如网络搜索、文件操作、代码执行等）
- 捕获工具执行结果

**3.4 观察阶段 (Observe)**
```
app.agent.toolcall:act → 处理工具结果 → 更新上下文
```
- 处理工具返回的结果
- 将结果添加到对话历史
- 为下一步决策提供上下文

**3.5 循环判断**
- 如果任务完成 → 调用 `terminate` 工具退出
- 如果未完成且未达到最大步数 → 继续下一步
- 如果达到最大步数（20步）→ 自动退出

#### 4. 工具类型示例
根据日志分析，常用工具执行流程：
**浏览器工具 (browser_use)**
```
web_search → 尝试 Google → 尝试 Baidu → 返回搜索结果
go_to_url → 导航到指定网页
click_element → 点击页面元素
extract_content → 提取页面内容
scroll_down → 滚动页面
```

**文件操作工具 (str_replace_editor)**
```
view → 查看文件/目录
create → 创建新文件
edit → 编辑文件内容
```

**Python 执行工具 (python_execute)**
```
接收代码 → 在子进程中执行 → 返回输出结果
```

#### 5. 错误处理机制
- 工具执行失败时，记录错误日志
- 智能体会自动尝试替代方案
- 继续执行下一步，不会因单个工具失败而中断

#### 6. 资源清理阶段
```
app.tool.mcp:disconnect → 断开 MCP 连接
app.agent.cleanup → 清理浏览器上下文
__main__:main → 请求处理完成
```

#### 7. 日志记录
每个步骤的详细信息都会记录到日志文件：
- 时间戳
- 日志级别（INFO/WARNING/ERROR）
- 模块和函数位置
- 执行内容
- Token 使用统计

## 🏗️ 项目架构

```
OpenManus/
├── app/                              # 核心应用代码
│   ├── agent/                        # 智能体模块
│   │   ├── base.py                  # 智能体基类，提供状态管理、记忆管理、执行循环
│   │   ├── react.py                 # ReAct 模式实现（思考-行动-观察循环）
│   │   ├── toolcall.py              # 工具调用智能体基类，处理工具选择和执行
│   │   ├── manus.py                 # Manus 主智能体，支持本地工具和 MCP 工具
│   │   ├── browser.py               # 浏览器上下文助手，管理浏览器状态
│   │   ├── data_analysis.py         # 数据分析智能体
│   │   ├── swe.py                   # 软件工程智能体（代码生成、调试等）
│   │   ├── sandbox_agent.py         # 沙箱智能体，使用 Daytona 云沙箱
│   │   └── mcp.py                   # MCP 协议智能体
│   │
│   ├── flow/                        # 多智能体流程控制
│   │   ├── base.py                  # 流程基类，定义流程执行框架
│   │   ├── planning.py              # 规划流程，协调多个智能体完成任务
│   │   └── flow_factory.py          # 流程工厂，创建不同类型的流程实例
│   │
│   ├── tool/                        # 工具集模块
│   │   ├── base.py                  # 工具基类，定义工具接口和结果格式
│   │   ├── tool_collection.py       # 工具集合管理，工具注册和查找
│   │   ├── python_execute.py        # Python 代码执行工具
│   │   ├── browser_use_tool.py      # 浏览器自动化工具（导航、点击、输入等）
│   │   ├── str_replace_editor.py    # 文本文件编辑工具（查看、创建、编辑）
│   │   ├── web_search.py            # 网络搜索工具（统一搜索接口）
│   │   ├── search/                  # 搜索引擎实现
│   │   │   ├── google_search.py     # Google 搜索
│   │   │   ├── baidu_search.py      # 百度搜索
│   │   │   ├── bing_search.py       # Bing 搜索
│   │   │   └── duckduckgo_search.py # DuckDuckGo 搜索
│   │   ├── sandbox/                 # 沙箱工具（基于 Daytona）
│   │   │   ├── sb_browser_tool.py   # 沙箱浏览器工具（VNC 可视化）
│   │   │   ├── sb_shell_tool.py     # 沙箱终端工具
│   │   │   ├── sb_files_tool.py     # 沙箱文件操作工具
│   │   │   └── sb_vision_tool.py    # 沙箱视觉工具（截图等）
│   │   ├── chart_visualization/     # 数据可视化工具
│   │   │   └── data_visualization.py # 图表生成和可视化
│   │   ├── mcp.py                   # MCP 客户端工具，连接远程 MCP 服务器
│   │   ├── ask_human.py             # 询问人类工具，支持人机交互
│   │   ├── terminate.py             # 终止工具，结束智能体执行
│   │   └── file_operators.py        # 文件操作工具（本地和沙箱）
│   │
│   ├── prompt/                      # 提示词模板模块
│   │   ├── manus.py                 # Manus 智能体的系统提示词
│   │   ├── toolcall.py              # 工具调用提示词
│   │   ├── browser.py               # 浏览器操作提示词
│   │   ├── planning.py              # 规划流程提示词
│   │   ├── swe.py                   # 软件工程提示词
│   │   ├── mcp.py                   # MCP 协议提示词
│   │   └── visualization.py         # 数据可视化提示词
│   │
│   ├── daytona/                     # Daytona 云沙箱集成
│   │   ├── sandbox.py               # 沙箱管理（创建、启动、删除）
│   │   └── tool_base.py             # 沙箱工具基类
│   │
│   ├── sandbox/                     # 本地沙箱模块
│   │   ├── client.py                # 沙箱客户端
│   │   └── core/                    # 沙箱核心功能
│   │       ├── manager.py           # 沙箱管理器
│   │       ├── sandbox.py           # 沙箱实现
│   │       └── terminal.py          # 终端执行
│   │
│   ├── mcp/                         # MCP（Model Context Protocol）模块
│   │   └── server.py                # MCP 服务器实现
│   │
│   ├── utils/                       # 工具函数模块
│   │   ├── files_utils.py           # 文件操作工具函数
│   │   └── logger.py                # 日志工具
│   │
│   ├── llm.py                       # LLM 接口封装
│   │                                # - 支持 OpenAI、Azure、Ollama、Bedrock 等
│   │                                # - Token 计数和管理
│   │                                # - 流式和非流式响应
│   │                                # - 工具调用（Function Calling）
│   │                                # - 多模态输入（图片）
│   │
│   ├── config.py                    # 配置管理模块
│   │                                # - 加载 TOML 配置文件
│   │                                # - LLM、浏览器、搜索、MCP 等配置
│   │                                # - 单例模式，全局配置访问
│   │
│   ├── schema.py                    # 数据模型定义
│   │                                # - Message、Memory、ToolCall 等
│   │                                # - AgentState、Role、ToolChoice 枚举
│   │
│   ├── logger.py                    # 日志配置
│   ├── bedrock.py                   # AWS Bedrock 客户端
│   └── exceptions.py                # 自定义异常类
│
├── protocol/                        # 协议集成模块
│   └── a2a/                         # A2A（Agent-to-Agent）协议集成
│       └── app/                     # A2A 服务器实现
│           ├── main.py              # A2A 服务器启动入口
│           ├── agent.py              # A2AManus 类，A2A 协议适配
│           └── agent_executor.py    # A2A 请求执行器
│
├── config/                          # 配置文件目录
│   ├── config.toml                  # 主配置文件（需自行创建）
│   ├── config.example.toml          # 配置示例文件
│   ├── config.example-daytona.toml  # Daytona 配置示例
│   └── mcp.json                     # MCP 服务器配置（可选）
│
├── workspace/                       # 工作空间目录
│   └── [生成的文件和项目]              # 智能体生成的文件存放于此
│
├── logs/                           # 日志文件目录
│   └── [日期].log                   # 按日期记录的日志文件
│
├── main.py                        # 单智能体启动入口
│                                  # - 创建 Manus 智能体
│                                  # - 执行用户任务
│                                  # - 支持命令行参数和交互式输入
│
├── run_flow.py                    # 多智能体流程启动入口
│                                  # - 启动规划流程
│                                  # - 协调多个智能体协作
│
├── run_mcp.py                     # MCP 工具服务启动入口
│                                  # - 启动 MCP 服务器
│                                  # - 提供工具服务
│
└── sandbox_main.py               # 沙箱智能体启动入口
                                  # - 使用 Daytona 云沙箱
                                  # - 支持可视化调试
```

### 模块功能说明

#### 核心模块

- **agent/**：智能体实现
  - `base.py`：所有智能体的基类，提供状态管理、记忆管理、执行循环等核心功能
  - `react.py`：ReAct（Reasoning + Acting）模式，实现思考-行动-观察循环
  - `toolcall.py`：工具调用智能体，处理工具选择、参数准备、执行和结果处理
  - `manus.py`：主智能体，集成本地工具和 MCP 工具，支持浏览器上下文感知

- **tool/**：工具集
  - 本地工具：Python 执行、浏览器控制、文件编辑、网络搜索等
  - 沙箱工具：基于 Daytona 的云沙箱工具，支持 VNC 可视化
  - MCP 工具：通过 MCP 协议连接远程工具服务器

- **flow/**：多智能体流程
  - 规划流程：将复杂任务分解，协调多个智能体协作完成

- **llm.py**：LLM 接口统一封装
  - 支持多种 LLM 提供商（OpenAI、Azure、Ollama、Bedrock 等）
  - Token 计数和限制管理
  - 工具调用（Function Calling）支持

- **config.py**：配置管理
  - 单例模式，全局配置访问
  - 支持多 LLM 配置
  - 自动加载 TOML 配置文件

#### 扩展模块

- **daytona/**：Daytona 云沙箱集成
  - 创建和管理云沙箱环境
  - 支持 VNC 远程访问和可视化调试

- **mcp/**：MCP 协议支持
  - 实现 MCP 服务器，提供工具服务
  - 支持 SSE 和 stdio 两种连接方式

- **protocol/a2a/**：A2A 协议集成
  - 将 OpenManus 智能体暴露为 A2A 标准服务
  - 支持其他 A2A 客户端调用

#### 辅助模块

- **prompt/**：提示词模板
  - 各智能体的系统提示词和下一步提示词
  - 支持动态格式化（工作空间路径等）

- **utils/**：工具函数
  - 文件操作、路径处理
  - 日志记录工具

- **schema.py**：数据模型
  - 定义消息、记忆、工具调用等核心数据结构

## 🛠️ 开发指南
### 添加新功能
1. **开发代码**
在 `app/` 修改或添加代码，参考 `app/tool/` 下的现有代码结构
2. **本地测试**
   ```bash
   python main.py --prompt "测试您的新功能"
   ```
3. **提交更改**
   ```bash
   git add . && git commit -m "feat: 添加了超级厉害的功能" && git push
   ```
---
