#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manus 智能体模块
Manus 是 OpenManus 项目的核心智能体，它是一个多功能通用智能体，支持：
1. 本地工具：Python 执行、浏览器控制、文本编辑、询问人类等
2. MCP工具：通过 Model Context Protocol 连接远程服务器，使用远程工具
3. 浏览器上下文：智能管理浏览器状态，提供上下文感知的提示词
4. 动态工具管理：可以动态连接/断开 MCP 服务器，实时更新可用工具
"""

from typing import Dict, List, Optional
from pydantic import Field, model_validator
from app.agent.browser import BrowserContextHelper
from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.logger import logger
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.ask_human import AskHuman
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.mcp import MCPClients, MCPClientTool
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor


class Manus(ToolCallAgent):
    """
    Manus 智能体类
    这是 OpenManus 项目的核心智能体，继承自 ToolCallAgent，提供了：

    核心功能：
    - 本地工具执行：Python 代码执行、浏览器控制、文件编辑、人类交互
    - MCP 服务器集成：支持 SSE 和 stdio 两种方式连接远程 MCP 服务器
    - 浏览器上下文管理：自动获取浏览器状态，提供上下文感知的提示词
    - 动态工具管理：运行时连接/断开 MCP 服务器，实时更新工具列表

    工作流程：
    1. 初始化时连接配置的 MCP 服务器
    2. 在思考阶段，如果使用浏览器工具，会获取浏览器状态并更新提示词
    3. 执行工具（本地或远程 MCP 工具）
    4. 清理时断开所有 MCP 连接并关闭浏览器
    """

    # 智能体基本信息
    name: str = "Manus"
    description: str = ("一个多功能的智能体，可以使用多种工具（包括基于 MCP 的工具）解决各种任务")

    # 提示词配置
    # system_prompt 会包含工作空间目录信息，帮助智能体了解文件系统结构
    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT  # 下一步提示词模板
    max_observe: int = 10000  # 工具返回结果的最大观察长度（字符数）
    max_steps: int = 20  # 最大执行步数，防止无限循环

    # MCP 客户端管理
    # MCPClients 负责管理与多个 MCP 服务器的连接
    # 支持两种连接方式：
    # - SSE (Server-Sent Events): 通过 HTTP 连接
    # - stdio: 通过标准输入输出连接（本地进程）
    mcp_clients: MCPClients = Field(default_factory=MCPClients)

    # 可用工具集合
    # 默认包含以下本地工具：
    # - PythonExecute: 执行 Python 代码
    # - BrowserUseTool: 控制浏览器（导航、点击、输入等）
    # - StrReplaceEditor: 文本文件编辑（查找替换）
    # - AskHuman: 询问人类用户输入
    # - Terminate: 终止智能体执行
    # 注意：MCP 工具会在连接服务器后动态添加
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(),
            BrowserUseTool(),
            StrReplaceEditor(),
            AskHuman(),
            Terminate(),
        )
    )

    # 特殊工具列表
    # 执行这些工具会触发智能体状态变为 FINISHED
    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])

    # 浏览器上下文助手
    # 用于获取浏览器状态、格式化浏览器相关的提示词
    browser_context_helper: Optional[BrowserContextHelper] = None

    # MCP 服务器连接跟踪
    # 字典结构：{server_id: url/command}
    # 用于记录已连接的 MCP 服务器，方便管理和清理
    connected_servers: Dict[str, str] = Field(default_factory=dict)

    # 初始化标志
    # 用于标记 MCP 服务器是否已经初始化
    # 避免重复初始化，确保清理时正确断开连接
    _initialized: bool = False

    @model_validator(mode="after")
    def initialize_helper(self) -> "Manus":
        """
        Pydantic 模型验证器：在模型创建后自动初始化浏览器上下文助手

        这个方法会在 Manus 实例创建时自动调用（Pydantic 的 model_validator），
        用于初始化浏览器上下文助手。这是一个同步初始化，因为 BrowserContextHelper
        的创建不需要异步操作。

        Returns:
            Manus: 返回自身，用于链式调用
        """
        self.browser_context_helper = BrowserContextHelper(self)
        return self

    @classmethod
    async def create(cls, **kwargs) -> "Manus":
        """
        工厂方法：创建并完整初始化 Manus 实例

        这是推荐的创建 Manus 实例的方式，因为：
        1. 它会自动连接配置文件中定义的所有 MCP 服务器
        2. 确保所有异步初始化操作完成
        3. 设置初始化标志，确保清理时正确断开连接

        使用示例：
            manus = await Manus.create()
            result = await manus.run("帮我完成某个任务")

        Args:
            **kwargs: 传递给 Manus 构造函数的参数

        Returns:
            Manus: 完全初始化的 Manus 实例
        """
        instance = cls(**kwargs)
        # 初始化 MCP 服务器连接
        await instance.initialize_mcp_servers()
        # 标记为已初始化
        instance._initialized = True
        return instance

    async def initialize_mcp_servers(self) -> None:
        """
        初始化与配置文件中定义的所有 MCP 服务器的连接

        这个方法会：
        1. 读取配置文件中的 MCP 服务器配置
        2. 根据服务器类型（SSE 或 stdio）选择相应的连接方式
        3. 连接成功后，将服务器提供的工具添加到可用工具列表
        4. 记录连接状态，方便后续管理和清理

        支持的连接方式：
        - SSE (Server-Sent Events): 通过 HTTP URL 连接远程服务器
        - stdio: 通过命令行启动本地进程，使用标准输入输出通信

        如果某个服务器连接失败，会记录错误日志但不会中断其他服务器的连接。
        """
        # 遍历配置文件中定义的所有 MCP 服务器
        for server_id, server_config in config.mcp_config.servers.items():
            try:
                # SSE 类型：通过 HTTP URL 连接
                if server_config.type == "sse":
                    if server_config.url:
                        await self.connect_mcp_server(server_config.url, server_id)
                        logger.info(
                            f"已连接到 MCP 服务器 {server_id}，地址: {server_config.url}"
                        )
                # stdio 类型：通过命令行启动本地进程
                elif server_config.type == "stdio":
                    if server_config.command:
                        await self.connect_mcp_server(
                            server_config.command,
                            server_id,
                            use_stdio=True,  # 标记使用 stdio 方式
                            stdio_args=server_config.args,  # 命令行参数
                        )
                        logger.info(
                            f"已连接到 MCP 服务器 {server_id}，使用命令: {server_config.command}"
                        )
            except Exception as e:
                # 连接失败时记录错误，但不中断其他服务器的连接
                logger.error(f"连接 MCP 服务器 {server_id} 失败: {e}")

    async def connect_mcp_server(
        self,
        server_url: str,
        server_id: str = "",
        use_stdio: bool = False,
        stdio_args: List[str] = None,
    ) -> None:
        """
        连接到指定的 MCP 服务器并添加其提供的工具

        这个方法支持两种连接方式：
        1. SSE (Server-Sent Events): 通过 HTTP URL 连接远程服务器
        2. stdio: 通过命令行启动本地进程，使用标准输入输出通信

        连接成功后，会自动：
        1. 获取服务器提供的工具列表
        2. 将工具添加到可用工具集合
        3. 记录连接信息，方便后续管理

        Args:
            server_url:
                - SSE 模式：服务器的 HTTP URL
                - stdio 模式：要执行的命令（如 "python", "node" 等）
            server_id: 服务器标识符，用于区分多个服务器。如果为空，使用 server_url 作为 ID
            use_stdio: 是否使用 stdio 方式连接（False 表示使用 SSE）
            stdio_args: stdio 模式下的命令行参数列表

        示例：
            # SSE 连接
            await manus.connect_mcp_server("http://localhost:8000/mcp", "my_server")

            # stdio 连接
            await manus.connect_mcp_server(
                "python",
                "python_server",
                use_stdio=True,
                stdio_args=["-m", "my_mcp_server"]
            )
        """
        if use_stdio:
            # stdio 模式：启动本地进程
            await self.mcp_clients.connect_stdio(
                server_url, stdio_args or [], server_id
            )
            # 记录连接信息
            self.connected_servers[server_id or server_url] = server_url
        else:
            # SSE 模式：通过 HTTP 连接
            await self.mcp_clients.connect_sse(server_url, server_id)
            # 记录连接信息
            self.connected_servers[server_id or server_url] = server_url

        # 获取此服务器提供的新工具
        # 只添加属于当前服务器的工具（通过 server_id 过滤）
        new_tools = [
            tool for tool in self.mcp_clients.tools if tool.server_id == server_id
        ]
        # 将新工具添加到可用工具集合
        self.available_tools.add_tools(*new_tools)

    async def disconnect_mcp_server(self, server_id: str = "") -> None:
        """
        断开与 MCP 服务器的连接并移除其工具

        这个方法会：
        1. 断开与指定服务器的连接（如果 server_id 为空，断开所有服务器）
        2. 从连接跟踪字典中移除记录
        3. 重建可用工具列表，排除已断开服务器的工具

        注意：断开连接后，该服务器提供的所有工具都会从可用工具列表中移除。

        Args:
            server_id: 要断开的服务器 ID。如果为空字符串，断开所有服务器

        示例：
            # 断开特定服务器
            await manus.disconnect_mcp_server("my_server")

            # 断开所有服务器
            await manus.disconnect_mcp_server()
        """
        # 断开 MCP 客户端连接
        await self.mcp_clients.disconnect(server_id)

        # 从连接跟踪字典中移除
        if server_id:
            self.connected_servers.pop(server_id, None)
        else:
            # 如果 server_id 为空，清空所有连接记录
            self.connected_servers.clear()

        # 重建可用工具列表
        # 1. 先获取所有非 MCP 工具（本地工具）
        base_tools = [
            tool
            for tool in self.available_tools.tools
            if not isinstance(tool, MCPClientTool)
        ]
        # 2. 创建新的工具集合，只包含本地工具
        self.available_tools = ToolCollection(*base_tools)
        # 3. 添加仍然连接的 MCP 服务器的工具
        self.available_tools.add_tools(*self.mcp_clients.tools)

    async def cleanup(self):
        if self.browser_context_helper:
            await self.browser_context_helper.cleanup_browser()

        if self._initialized:
            await self.disconnect_mcp_server()
            self._initialized = False

    async def think(self) -> bool:
        """
        思考阶段：分析当前状态并决定下一步操作（带浏览器上下文感知）

        这是 Manus 智能体的核心思考方法，它在父类 think 方法的基础上增加了：
        1. 延迟初始化：如果 MCP 服务器未初始化，先初始化它们
        2. 浏览器上下文感知：如果最近使用了浏览器工具，会获取浏览器状态并更新提示词

        浏览器上下文感知的工作原理：
        - 检查最近 3 条消息中是否使用了浏览器工具
        - 如果使用了，获取当前浏览器状态（URL、标题、标签页、滚动位置等）
        - 将这些信息格式化后添加到提示词中，帮助 LLM 更好地理解当前浏览器状态
        - 如果浏览器有截图，会将截图添加到消息历史中
        """
        if not self._initialized:
            await self.initialize_mcp_servers()
            self._initialized = True

        original_prompt = self.next_step_prompt
        recent_messages = self.memory.messages[-3:] if self.memory.messages else []
        browser_in_use = any(
            tc.function.name == BrowserUseTool().name
            for msg in recent_messages
            if msg.tool_calls
            for tc in msg.tool_calls
        )
        if browser_in_use:
            self.next_step_prompt = (
                await self.browser_context_helper.format_next_step_prompt()
            )
        result = await super().think()
        self.next_step_prompt = original_prompt
        return result
