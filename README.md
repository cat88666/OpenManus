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

**日志文件位置**: `logs/YYYYMMDD.log`（按日期生成，每天一个文件）

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
1. **开发代码**
在 `app/` 修改或添加代码，参考 `app/tool/` 下的现有代码结构
2. **本地测试**
   ```bash
   python main.py --prompt "测试您的新功能"
   ```
3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加了超级厉害的功能"
   git push
   ```
---
