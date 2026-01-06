#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具基类模块

本模块定义了所有工具的基础类 BaseTool 和工具结果类 ToolResult。
工具是智能体可以调用的功能单元，每个工具都继承自 BaseTool 并实现 execute() 方法。
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field

from app.utils.logger import logger


# class BaseTool(ABC, BaseModel):
#     name: str
#     description: str
#     parameters: Optional[dict] = None

#     class Config:
#         arbitrary_types_allowed = True

#     async def __call__(self, **kwargs) -> Any:
#         """Execute the tool with given parameters."""
#         return await self.execute(**kwargs)

#     @abstractmethod
#     async def execute(self, **kwargs) -> Any:
#         """Execute the tool with given parameters."""

#     def to_param(self) -> Dict:
#         """Convert tool to function call format."""
#         return {
#             "type": "function",
#             "function": {
#                 "name": self.name,
#                 "description": self.description,
#                 "parameters": self.parameters,
#             },
#         }


class ToolResult(BaseModel):
    """
    工具执行结果类

    用于表示工具执行后的返回结果。可以包含：
    - 成功时的输出内容
    - 失败时的错误信息
    - 可选的图片数据（base64 编码）
    - 系统级消息

    这个类支持：
    - 布尔值判断：检查是否有任何有效内容
    - 结果合并：可以将两个结果合并
    - 字符串表示：提供友好的字符串输出
    """

    # 工具执行的成功输出（可以是字符串、字典等任意类型）
    output: Any = Field(default=None, description="工具执行的成功输出")
    # 工具执行失败时的错误信息
    error: Optional[str] = Field(default=None, description="工具执行失败时的错误信息")
    # base64 编码的图片数据（用于视觉类工具）
    base64_image: Optional[str] = Field(
        default=None, description="base64 编码的图片数据"
    )
    # 系统级消息（用于传递系统信息）
    system: Optional[str] = Field(default=None, description="系统级消息")

    class Config:
        """Pydantic 配置：允许使用任意类型"""
        arbitrary_types_allowed = True

    def __bool__(self):
        """
        布尔值判断：检查结果是否有任何有效内容

        如果任何一个字段有值，返回 True；否则返回 False。

        Returns:
            bool: True 表示有有效内容，False 表示结果为空
        """
        return any(getattr(self, field) for field in self.__fields__)

    def __add__(self, other: "ToolResult"):
        """
        合并两个工具结果

        将两个 ToolResult 对象合并成一个新的结果。
        合并规则：
        - output 和 error：如果两者都有值，会连接（concatenate=True）
        - base64_image：如果两者都有值，会报错（不能合并图片）
        - system：如果两者都有值，会连接

        Args:
            other: 要合并的另一个 ToolResult 对象

        Returns:
            ToolResult: 合并后的新结果对象

        Raises:
            ValueError: 当两个结果都有 base64_image 时（无法合并图片）
        """
        def combine_fields(
            field: Optional[str], other_field: Optional[str], concatenate: bool = True
        ):
            """
            合并两个字段的值

            Args:
                field: 当前对象的字段值
                other_field: 另一个对象的字段值
                concatenate: 是否允许连接（True）或必须唯一（False）

            Returns:
                合并后的字段值
            """
            # 如果两个字段都有值
            if field and other_field:
                if concatenate:
                    # 允许连接：将两个值连接起来
                    return field + other_field
                # 不允许连接：抛出错误（如 base64_image）
                raise ValueError("无法合并工具结果")
            # 返回有值的那个，如果都没有则返回 None
            return field or other_field

        # 创建合并后的结果对象
        return ToolResult(
            output=combine_fields(self.output, other.output),
            error=combine_fields(self.error, other.error),
            base64_image=combine_fields(
                self.base64_image, other.base64_image, False
            ),  # 图片不能合并
            system=combine_fields(self.system, other.system),
        )

    def __str__(self):
        """
        字符串表示：提供友好的输出格式

        如果有错误，返回错误信息；否则返回输出内容。

        Returns:
            str: 结果的字符串表示
        """
        return f"错误: {self.error}" if self.error else str(self.output)

    def replace(self, **kwargs):
        """
        创建一个新结果，替换指定字段

        用于创建基于当前结果的新结果，只修改指定的字段。

        Args:
            **kwargs: 要替换的字段和值

        Returns:
            ToolResult: 新的结果对象，包含替换后的值

        使用示例：
            result = ToolResult(output="原始输出")
            new_result = result.replace(output="新输出")
        """
        # 使用当前对象的字典表示，更新指定字段，创建新对象
        return type(self)(**{**self.dict(), **kwargs})


class BaseTool(ABC, BaseModel):
    """
    工具基类

    所有工具都必须继承自这个类。它提供了：
    1. Pydantic 模型验证：自动验证工具的参数
    2. 标准化结果处理：统一的成功/失败响应格式
    3. 抽象执行接口：子类必须实现 execute() 方法
    4. 工具描述转换：将工具转换为 LLM 可理解的函数调用格式

    属性说明：
        name: 工具的唯一名称，用于标识工具
        description: 工具的描述，说明工具的功能和用途
        parameters: 工具参数的 JSON Schema，定义工具接受的参数格式

    使用流程：
        1. 定义工具类，继承 BaseTool
        2. 设置 name、description、parameters
        3. 实现 execute() 方法
        4. 使用 success_response() 或 fail_response() 返回结果
    """

    # 工具的唯一名称（必需）
    name: str = Field(..., description="工具的唯一名称，用于标识和调用工具")
    # 工具的描述信息（必需）
    description: str = Field(
        ..., description="工具的描述，说明工具的功能、用途和使用场景"
    )
    # 工具参数的 JSON Schema（可选）
    # 定义工具接受的参数格式，用于 LLM 理解如何调用工具
    parameters: Optional[dict] = Field(
        default=None, description="工具参数的 JSON Schema，定义参数类型和格式"
    )

    class Config:
        """
        Pydantic 配置类

        arbitrary_types_allowed: 允许使用任意类型
        underscore_attrs_are_private: 下划线开头的属性不是私有的（用于向后兼容）
        """
        arbitrary_types_allowed = True
        underscore_attrs_are_private = False

    # def __init__(self, **data):
    #     """Initialize tool with model validation and schema registration."""
    #     super().__init__(**data)
    #     logger.debug(f"Initializing tool class: {self.__class__.__name__}")
    #     self._register_schemas()

    # def _register_schemas(self):
    #     """Register schemas from all decorated methods."""
    #     for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
    #         if hasattr(method, 'tool_schemas'):
    #             self._schemas[name] = method.tool_schemas
    #             logger.debug(f"Registered schemas for method '{name}' in {self.__class__.__name__}")

    async def __call__(self, **kwargs) -> Any:
        """
        使工具对象可调用（魔术方法）

        允许像函数一样调用工具对象：tool(**kwargs)
        实际上会调用 execute() 方法。

        Args:
            **kwargs: 传递给 execute() 方法的参数

        Returns:
            Any: execute() 方法的返回值（通常是 ToolResult）

        使用示例：
            tool = MyTool()
            result = await tool(param1="value1", param2="value2")
        """
        return await self.execute(**kwargs)

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        执行工具（抽象方法，必须由子类实现）

        这是工具的核心方法，子类必须实现具体的执行逻辑。
        方法应该是异步的，以支持 I/O 操作（如网络请求、文件操作等）。

        Args:
            **kwargs: 工具执行所需的参数，由 parameters 定义

        Returns:
            Any: 通常是 ToolResult 对象，包含执行结果或错误信息

        实现示例：
            async def execute(self, file_path: str, content: str) -> ToolResult:
                try:
                    # 执行具体操作
                    with open(file_path, 'w') as f:
                        f.write(content)
                    return self.success_response("文件写入成功")
                except Exception as e:
                    return self.fail_response(f"写入失败: {str(e)}")
        """

    def to_param(self) -> Dict:
        """
        将工具转换为函数调用格式

        将工具对象转换为 OpenAI 函数调用格式，用于传递给 LLM。
        LLM 可以根据这个格式理解工具的功能和参数，并生成工具调用。

        Returns:
            Dict: 包含工具元数据的字典，格式符合 OpenAI 函数调用规范

        返回格式：
            {
                "type": "function",
                "function": {
                    "name": "工具名称",
                    "description": "工具描述",
                    "parameters": {
                        "type": "object",
                        "properties": {...},
                        "required": [...]
                    }
                }
            }

        使用示例：
            tool = FileWriteTool()
            tool_param = tool.to_param()
            # 传递给 LLM
            response = await llm.ask_tool(messages, tools=[tool_param])
        """
        return {
            "type": "function",  # 固定为 "function"
            "function": {
                "name": self.name,  # 工具名称
                "description": self.description,  # 工具描述
                "parameters": self.parameters,  # 参数 Schema
            },
        }

    # def get_schemas(self) -> Dict[str, List[ToolSchema]]:
    #     """Get all registered tool schemas.

    #     Returns:
    #         Dict mapping method names to their schema definitions
    #     """
    #     return self._schemas

    def success_response(self, data: Union[Dict[str, Any], str]) -> ToolResult:
        """
        创建成功的工具结果

        这是一个便捷方法，用于创建表示成功的 ToolResult 对象。
        如果传入字典，会格式化为 JSON 字符串；如果传入字符串，直接使用。

        Args:
            data: 结果数据，可以是字符串或字典
                - 字符串：直接作为输出
                - 字典：格式化为格式化的 JSON 字符串

        Returns:
            ToolResult: 包含 output 字段的结果对象，error 为 None

        使用示例：
            # 返回字符串结果
            return self.success_response("操作成功完成")

            # 返回字典结果（会自动格式化为 JSON）
            return self.success_response({"status": "ok", "count": 10})
        """
        # 如果是字符串，直接使用
        if isinstance(data, str):
            text = data
        else:
            # 如果是字典，格式化为格式化的 JSON 字符串（带缩进）
            text = json.dumps(data, indent=2, ensure_ascii=False)
        logger.debug(f"工具 {self.__class__.__name__} 创建成功响应")
        return ToolResult(output=text)

    def fail_response(self, msg: str) -> ToolResult:
        """
        创建失败的工具结果

        这是一个便捷方法，用于创建表示失败的 ToolResult 对象。
        用于工具执行出错时返回错误信息。

        Args:
            msg: 错误消息，描述失败的原因

        Returns:
            ToolResult: 包含 error 字段的结果对象，output 为 None

        使用示例：
            try:
                # 执行操作
                result = do_something()
                return self.success_response(result)
            except Exception as e:
                return self.fail_response(f"操作失败: {str(e)}")
        """
        logger.debug(f"工具 {self.__class__.__name__} 返回失败结果: {msg}")
        return ToolResult(error=msg)


class CLIResult(ToolResult):
    """
    CLI 结果类

    继承自 ToolResult，用于表示可以在命令行界面中渲染的结果。
    可以用于需要特殊 CLI 格式显示的工具结果。
    """


class ToolFailure(ToolResult):
    """
    工具失败结果类

    继承自 ToolResult，专门用于表示工具执行失败的结果。
    可以用于需要区分失败类型的场景。
    """
