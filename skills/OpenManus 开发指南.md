# OpenManus 开发指南

## 添加新工具
1. 在 `app/tool/` 目录下创建新文件
2. 继承 `BaseTool` 类
3. 实现 `execute()` 方法（必须是异步）
4. 定义 `name` 和 `description` 属性
5. 使用 Pydantic 模型定义参数
6. 返回 `ToolResult` 对象
7. 参考现有工具实现（如 `str_replace_editor.py`, `python_execute.py`）

## 添加新智能体
1. 在 `app/agent/` 目录下创建新文件
2. 继承 `ToolCallAgent` 或 `BaseAgent`
3. 实现必要的抽象方法
4. 配置 `available_tools` 工具集合
5. 参考 `manus.py` 的实现

## 配置文件
- 配置文件位于 `config/config.toml`
- 使用 `app.config.config` 访问配置
- 配置项使用 TOML 格式
- 支持多模型配置（`[llm]`, `[llm.vision]`）

## 工作空间
- 生成的文件保存在 `workspace/` 目录
- 日志文件保存在 `logs/` 目录
- 不要将生成的文件提交到版本控制

## 测试要求
- 新功能必须通过本地测试
- 使用 `python main.py --prompt "测试您的新功能"` 进行测试
- 确保不破坏现有功能


## Git 提交规范
- 使用有意义的提交信息
- 格式：`feat: 描述` 或 `fix: 描述`
- 提交前确保代码通过测试

## 环境要求
- 必须使用 conda 环境 `open_manus`
- Python 版本 3.11
- 所有依赖在 `requirements.txt` 中定义
- 浏览器驱动通过 `playwright install` 安装
