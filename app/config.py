#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块

本模块负责加载和管理项目的所有配置，包括：
- LLM 配置（模型、API Key、参数等）
- 浏览器配置
- 搜索配置
- 沙箱配置
- MCP 服务器配置
- 工作空间路径

配置从 config/config.toml 文件加载，支持多 LLM 配置和单例模式。
"""

import json
import threading
import tomllib
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


def get_project_root() -> Path:
    """
    获取项目根目录

    Returns:
        Path: 项目根目录的路径对象
    """
    return Path(__file__).resolve().parent.parent


# 项目根目录和工作空间目录的全局常量
PROJECT_ROOT = get_project_root()
WORKSPACE_ROOT = PROJECT_ROOT / "workspace"


class LLMSettings(BaseModel):
    """
    LLM 配置设置类

    定义单个 LLM 配置的所有参数，包括模型名称、API 地址、密钥等。
    支持多种 API 类型：OpenAI、Azure OpenAI、Ollama 等。
    """

    model: str = Field(..., description="模型名称，如 'gpt-4', 'claude-3-opus' 等")
    base_url: str = Field(..., description="API 基础 URL，如 'https://api.openai.com/v1'")
    api_key: str = Field(..., description="API 密钥，用于身份验证")
    max_tokens: int = Field(4096, description="每次请求的最大 token 数（输出限制）")
    max_input_tokens: Optional[int] = Field(
        None,
        description="所有请求的最大输入 token 总数（None 表示无限制）",
    )
    temperature: float = Field(1.0, description="采样温度，控制回复的随机性（0-2）")
    api_type: str = Field(..., description="API 类型：'openai', 'azure', 'ollama' 等")
    api_version: str = Field(..., description="Azure OpenAI 的 API 版本（仅 Azure 需要）")


class ProxySettings(BaseModel):
    """
    代理服务器配置类

    用于配置浏览器或网络请求的代理设置。
    """

    server: str = Field(None, description="代理服务器地址，如 'http://proxy.example.com:8080'")
    username: Optional[str] = Field(None, description="代理服务器用户名（如果需要认证）")
    password: Optional[str] = Field(None, description="代理服务器密码（如果需要认证）")


class SearchSettings(BaseModel):
    """
    搜索引擎配置类

    配置智能体使用的搜索引擎及其备用选项。
    """

    engine: str = Field(default="Google", description="主要使用的搜索引擎名称")
    fallback_engines: List[str] = Field(
        default_factory=lambda: ["DuckDuckGo", "Baidu", "Bing"],
        description="备用搜索引擎列表，当主要引擎失败时按顺序尝试",
    )
    retry_delay: int = Field(
        default=60,
        description="所有引擎都失败后，等待多少秒再重试（秒）",
    )
    max_retries: int = Field(
        default=3,
        description="所有引擎都失败时的最大重试次数",
    )
    lang: str = Field(
        default="en",
        description="搜索结果的语言代码，如 'en'（英语）、'zh'（中文）、'fr'（法语）",
    )
    country: str = Field(
        default="us",
        description="搜索结果的国家代码，如 'us'（美国）、'cn'（中国）、'uk'（英国）",
    )


class RunflowSettings(BaseModel):
    """
    运行流程配置类

    配置智能体工作流程的相关设置。
    """

    use_data_analysis_agent: bool = Field(
        default=False, description="是否在运行流程中启用数据分析智能体"
    )


class BrowserSettings(BaseModel):
    """
    浏览器配置类

    配置浏览器工具的各种参数，包括运行模式、安全设置、连接方式等。
    """

    headless: bool = Field(False, description="是否以无头模式运行浏览器（不显示窗口）")
    disable_security: bool = Field(
        True, description="是否禁用浏览器安全功能（用于测试和自动化）"
    )
    extra_chromium_args: List[str] = Field(
        default_factory=list, description="传递给浏览器的额外 Chromium 参数列表"
    )
    chrome_instance_path: Optional[str] = Field(
        None, description="要使用的 Chrome 实例路径（如果使用自定义 Chrome）"
    )
    wss_url: Optional[str] = Field(
        None, description="通过 WebSocket 连接到浏览器实例的 URL"
    )
    cdp_url: Optional[str] = Field(
        None, description="通过 CDP（Chrome DevTools Protocol）连接到浏览器实例的 URL"
    )
    proxy: Optional[ProxySettings] = Field(
        None, description="浏览器的代理设置"
    )
    max_content_length: int = Field(
        2000, description="内容检索操作的最大长度（字符数）"
    )


class SandboxSettings(BaseModel):
    """
    沙箱执行环境配置类

    配置用于执行代码的 Docker 容器沙箱环境。
    """

    use_sandbox: bool = Field(False, description="是否使用沙箱环境执行代码")
    image: str = Field("python:3.12-slim", description="Docker 基础镜像名称")
    work_dir: str = Field("/workspace", description="容器内的工作目录路径")
    memory_limit: str = Field("512m", description="内存限制，如 '512m', '1g'")
    cpu_limit: float = Field(1.0, description="CPU 限制（核心数）")
    timeout: int = Field(300, description="默认命令超时时间（秒）")
    network_enabled: bool = Field(
        False, description="是否允许网络访问"
    )


class DaytonaSettings(BaseModel):
    """
    Daytona 平台配置类

    配置 Daytona 云开发平台的连接和沙箱设置。
    """

    daytona_api_key: Optional[str] = Field(None, description="Daytona API 密钥")
    daytona_server_url: Optional[str] = Field(
        "https://app.daytona.io/api", description="Daytona 服务器 API URL"
    )
    daytona_target: Optional[str] = Field("us", description="目标区域，可选值：'eu'（欧洲）或 'us'（美国）")
    sandbox_image_name: Optional[str] = Field("whitezxj/sandbox:0.1.0", description="沙箱 Docker 镜像名称")
    sandbox_entrypoint: Optional[str] = Field(
        "/usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf",
        description="沙箱容器的入口点命令",
    )
    # sandbox_id: Optional[str] = Field(
    #     None, description="要使用的 Daytona 沙箱 ID（如果有）"
    # )
    VNC_password: Optional[str] = Field(
        "123456", description="沙箱中 VNC 服务的密码"
    )


class MCPServerConfig(BaseModel):
    """
    单个 MCP 服务器配置类

    定义如何连接到一个 MCP（Model Context Protocol）服务器。
    支持两种连接方式：SSE（Server-Sent Events）和 stdio（标准输入输出）。
    """

    type: str = Field(..., description="服务器连接类型：'sse'（HTTP 连接）或 'stdio'（本地进程）")
    url: Optional[str] = Field(None, description="SSE 连接的服务器 URL（仅 SSE 类型需要）")
    command: Optional[str] = Field(None, description="stdio 连接的命令（如 'python', 'node'，仅 stdio 类型需要）")
    args: List[str] = Field(
        default_factory=list, description="stdio 命令的参数列表（仅 stdio 类型需要）"
    )


class MCPSettings(BaseModel):
    """
    MCP（Model Context Protocol）配置类

    管理所有 MCP 服务器的配置，支持从 JSON 文件加载服务器配置。
    """

    server_reference: str = Field(
        "app.mcp.server", description="MCP 服务器的模块引用路径"
    )
    servers: Dict[str, MCPServerConfig] = Field(
        default_factory=dict, description="MCP 服务器配置字典，键为服务器 ID，值为服务器配置"
    )

    @classmethod
    def load_server_config(cls) -> Dict[str, MCPServerConfig]:
        """
        从 JSON 文件加载 MCP 服务器配置

        从 config/mcp.json 文件中读取服务器配置，并转换为 MCPServerConfig 对象。

        Returns:
            Dict[str, MCPServerConfig]: 服务器配置字典

        Raises:
            ValueError: 如果配置文件格式错误或加载失败
        """
        config_path = PROJECT_ROOT / "config" / "mcp.json"

        try:
            config_file = config_path if config_path.exists() else None
            if not config_file:
                return {}

            with config_file.open() as f:
                data = json.load(f)
                servers = {}

                for server_id, server_config in data.get("mcpServers", {}).items():
                    servers[server_id] = MCPServerConfig(
                        type=server_config["type"],
                        url=server_config.get("url"),
                        command=server_config.get("command"),
                        args=server_config.get("args", []),
                    )
                return servers
        except Exception as e:
            raise ValueError(f"Failed to load MCP server config: {e}")


class AppConfig(BaseModel):
    """
    应用程序主配置类

    包含所有子系统的配置，是整个应用的配置容器。
    """

    llm: Dict[str, LLMSettings] = Field(..., description="LLM 配置字典，支持多个 LLM 配置（键为配置名称）")
    sandbox: Optional[SandboxSettings] = Field(
        None, description="沙箱环境配置"
    )
    browser_config: Optional[BrowserSettings] = Field(
        None, description="浏览器配置"
    )
    search_config: Optional[SearchSettings] = Field(
        None, description="搜索引擎配置"
    )
    mcp_config: Optional[MCPSettings] = Field(None, description="MCP 服务器配置")
    run_flow_config: Optional[RunflowSettings] = Field(
        None, description="运行流程配置"
    )
    daytona_config: Optional[DaytonaSettings] = Field(
        None, description="Daytona 平台配置"
    )

    class Config:
        """Pydantic 配置：允许使用任意类型"""
        arbitrary_types_allowed = True


class Config:
    """
    配置管理单例类

    使用单例模式确保整个应用只有一个配置实例。
    负责从 TOML 文件加载配置，并提供便捷的访问接口。

    设计模式：
    - 单例模式：确保全局只有一个配置实例
    - 线程安全：使用锁保护初始化过程
    - 延迟加载：只在首次访问时加载配置
    """

    _instance = None  # 单例实例
    _lock = threading.Lock()  # 线程锁，用于线程安全的单例创建
    _initialized = False  # 初始化标志

    def __new__(cls):
        """
        单例模式实现（魔术方法）

        确保整个应用只有一个 Config 实例。
        使用双重检查锁定模式（Double-Checked Locking）保证线程安全。
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        初始化配置实例

        只在首次创建时加载配置，后续访问不会重复加载。
        """
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._config = None
                    self._load_initial_config()
                    self._initialized = True

    @staticmethod
    def _get_config_path() -> Path:
        """
        获取配置文件路径

        优先查找 config.toml，如果不存在则使用 config.example.toml。

        Returns:
            Path: 配置文件路径

        Raises:
            FileNotFoundError: 如果两个配置文件都不存在
        """
        root = PROJECT_ROOT
        config_path = root / "config" / "config.toml"
        if config_path.exists():
            return config_path
        example_path = root / "config" / "config.example.toml"
        if example_path.exists():
            return example_path
        raise FileNotFoundError("在 config 目录中未找到配置文件")

    def _load_config(self) -> dict:
        """
        从 TOML 文件加载配置

        Returns:
            dict: 解析后的配置字典
        """
        config_path = self._get_config_path()
        with config_path.open("rb") as f:
            return tomllib.load(f)

    def _load_initial_config(self):
        raw_config = self._load_config()
        base_llm = raw_config.get("llm", {})
        llm_overrides = {
            k: v for k, v in raw_config.get("llm", {}).items() if isinstance(v, dict)
        }

        default_settings = {
            "model": base_llm.get("model"),
            "base_url": base_llm.get("base_url"),
            "api_key": base_llm.get("api_key"),
            "max_tokens": base_llm.get("max_tokens", 4096),
            "max_input_tokens": base_llm.get("max_input_tokens"),
            "temperature": base_llm.get("temperature", 1.0),
            "api_type": base_llm.get("api_type", ""),
            "api_version": base_llm.get("api_version", ""),
        }

        # handle browser config.
        browser_config = raw_config.get("browser", {})
        browser_settings = None

        if browser_config:
            # handle proxy settings.
            proxy_config = browser_config.get("proxy", {})
            proxy_settings = None

            if proxy_config and proxy_config.get("server"):
                proxy_settings = ProxySettings(
                    **{
                        k: v
                        for k, v in proxy_config.items()
                        if k in ["server", "username", "password"] and v
                    }
                )

            # filter valid browser config parameters.
            valid_browser_params = {
                k: v
                for k, v in browser_config.items()
                if k in BrowserSettings.__annotations__ and v is not None
            }

            # if there is proxy settings, add it to the parameters.
            if proxy_settings:
                valid_browser_params["proxy"] = proxy_settings

            # only create BrowserSettings when there are valid parameters.
            if valid_browser_params:
                browser_settings = BrowserSettings(**valid_browser_params)

        search_config = raw_config.get("search", {})
        search_settings = None
        if search_config:
            search_settings = SearchSettings(**search_config)
        sandbox_config = raw_config.get("sandbox", {})
        if sandbox_config:
            sandbox_settings = SandboxSettings(**sandbox_config)
        else:
            sandbox_settings = SandboxSettings()
        daytona_config = raw_config.get("daytona", {})
        if daytona_config:
            daytona_settings = DaytonaSettings(**daytona_config)
        else:
            daytona_settings = DaytonaSettings()

        mcp_config = raw_config.get("mcp", {})
        mcp_settings = None
        if mcp_config:
            # Load server configurations from JSON
            mcp_config["servers"] = MCPSettings.load_server_config()
            mcp_settings = MCPSettings(**mcp_config)
        else:
            mcp_settings = MCPSettings(servers=MCPSettings.load_server_config())

        run_flow_config = raw_config.get("runflow")
        if run_flow_config:
            run_flow_settings = RunflowSettings(**run_flow_config)
        else:
            run_flow_settings = RunflowSettings()
        config_dict = {
            "llm": {
                "default": default_settings,
                **{
                    name: {**default_settings, **override_config}
                    for name, override_config in llm_overrides.items()
                },
            },
            "sandbox": sandbox_settings,
            "browser_config": browser_settings,
            "search_config": search_settings,
            "mcp_config": mcp_settings,
            "run_flow_config": run_flow_settings,
            "daytona_config": daytona_settings,
        }

        self._config = AppConfig(**config_dict)

    @property
    def llm(self) -> Dict[str, LLMSettings]:
        """
        获取 LLM 配置字典

        Returns:
            Dict[str, LLMSettings]: LLM 配置字典，键为配置名称
        """
        return self._config.llm

    @property
    def sandbox(self) -> SandboxSettings:
        """
        获取沙箱配置

        Returns:
            SandboxSettings: 沙箱配置对象
        """
        return self._config.sandbox

    @property
    def daytona(self) -> DaytonaSettings:
        """
        获取 Daytona 配置

        Returns:
            DaytonaSettings: Daytona 配置对象
        """
        return self._config.daytona_config

    @property
    def browser_config(self) -> Optional[BrowserSettings]:
        """
        获取浏览器配置

        Returns:
            Optional[BrowserSettings]: 浏览器配置对象，如果未配置则返回 None
        """
        return self._config.browser_config

    @property
    def search_config(self) -> Optional[SearchSettings]:
        """
        获取搜索引擎配置

        Returns:
            Optional[SearchSettings]: 搜索引擎配置对象，如果未配置则返回 None
        """
        return self._config.search_config

    @property
    def mcp_config(self) -> MCPSettings:
        """
        获取 MCP 配置

        Returns:
            MCPSettings: MCP 配置对象
        """
        return self._config.mcp_config

    @property
    def run_flow_config(self) -> RunflowSettings:
        """
        获取运行流程配置

        Returns:
            RunflowSettings: 运行流程配置对象
        """
        return self._config.run_flow_config

    @property
    def workspace_root(self) -> Path:
        """
        获取工作空间根目录

        Returns:
            Path: 工作空间根目录路径
        """
        return WORKSPACE_ROOT

    @property
    def root_path(self) -> Path:
        """
        获取应用根目录

        Returns:
            Path: 应用根目录路径
        """
        return PROJECT_ROOT


# 全局配置实例（单例）
config = Config()
