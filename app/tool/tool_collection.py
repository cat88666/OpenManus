#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具集合管理模块

本模块提供了 ToolCollection 类，用于管理和组织多个工具。
工具集合可以添加、查找、执行工具，并将工具转换为 LLM 可理解的格式。
"""

from typing import Any, Dict, List

from app.exceptions import ToolError
from app.logger import logger
from app.tool.base import BaseTool, ToolFailure, ToolResult


class ToolCollection:
    """
    工具集合类

    用于管理多个工具，提供工具的添加、查找、执行等功能。
    支持将工具转换为 LLM 函数调用格式，方便智能体使用。

    主要功能：
    - 工具管理：添加、查找工具
    - 工具执行：执行单个或所有工具
    - 格式转换：将工具转换为 LLM 可理解的参数格式
    """

    class Config:
        """Pydantic 配置：允许使用任意类型"""
        arbitrary_types_allowed = True

    def __init__(self, *tools: BaseTool):
        """
        初始化工具集合

        Args:
            *tools: 可变参数，可以传入多个工具实例

        使用示例：
            collection = ToolCollection(
                PythonExecute(),
                BrowserUseTool(),
                StrReplaceEditor()
            )
        """
        # 工具元组：存储所有工具实例
        self.tools = tools
        # 工具映射：以工具名称为键，工具实例为值的字典，用于快速查找
        self.tool_map = {tool.name: tool for tool in tools}

    def __iter__(self):
        """
        使工具集合可迭代（魔术方法）

        允许使用 for 循环遍历所有工具。

        Returns:
            iterator: 工具迭代器

        使用示例：
            for tool in tool_collection:
                print(tool.name)
        """
        return iter(self.tools)

    def to_params(self) -> List[Dict[str, Any]]:
        """
        将工具集合转换为 LLM 函数调用参数格式

        将集合中的所有工具转换为 OpenAI 函数调用格式的列表。
        这个列表可以直接传递给 LLM 的 ask_tool 方法。

        Returns:
            List[Dict[str, Any]]: 工具参数列表，每个元素是一个工具的 to_param() 结果

        使用示例：
            tool_params = collection.to_params()
            response = await llm.ask_tool(messages, tools=tool_params)
        """
        return [tool.to_param() for tool in self.tools]

    async def execute(
        self, *, name: str, tool_input: Dict[str, Any] = None
    ) -> ToolResult:
        """
        执行指定名称的工具

        根据工具名称查找工具实例，然后执行它。
        如果工具不存在或执行失败，会返回相应的错误结果。

        Args:
            name: 要执行的工具名称
            tool_input: 工具输入参数字典（默认为 None，表示无参数）

        Returns:
            ToolResult: 工具执行结果，包含输出或错误信息

        使用示例：
            result = await collection.execute(name="python_execute", tool_input={"code": "print('hello')"})
            if result.error:
                print(f"执行失败: {result.error}")
            else:
                print(f"执行成功: {result.output}")
        """
        # 根据名称查找工具
        tool = self.tool_map.get(name)
        if not tool:
            # 工具不存在，返回失败结果
            return ToolFailure(error=f"工具 '{name}' 不存在")
        try:
            # 执行工具（工具对象是可调用的，会调用 execute 方法）
            result = await tool(**(tool_input or {}))
            return result
        except ToolError as e:
            # 捕获工具错误，返回失败结果
            return ToolFailure(error=e.message)

    async def execute_all(self) -> List[ToolResult]:
        """
        顺序执行集合中的所有工具

        遍历所有工具并依次执行，返回所有工具的执行结果列表。
        如果某个工具执行失败，会在结果列表中包含失败信息。

        Returns:
            List[ToolResult]: 所有工具的执行结果列表

        使用示例：
            results = await collection.execute_all()
            for i, result in enumerate(results):
                print(f"工具 {i+1} 执行结果: {result}")
        """
        results = []
        for tool in self.tools:
            try:
                # 执行工具（无参数）
                result = await tool()
                results.append(result)
            except ToolError as e:
                # 执行失败，添加失败结果
                results.append(ToolFailure(error=e.message))
        return results

    def get_tool(self, name: str) -> BaseTool:
        """
        根据名称获取工具实例

        Args:
            name: 工具名称

        Returns:
            BaseTool: 工具实例，如果不存在则返回 None

        使用示例：
            tool = collection.get_tool("python_execute")
            if tool:
                result = await tool(code="print('hello')")
        """
        return self.tool_map.get(name)

    def add_tool(self, tool: BaseTool):
        """
        向集合中添加单个工具

        如果工具名称已存在，会跳过添加并记录警告日志。
        支持链式调用。

        Args:
            tool: 要添加的工具实例

        Returns:
            ToolCollection: 返回自身，支持链式调用

        使用示例：
            collection.add_tool(MyTool()).add_tool(AnotherTool())
        """
        if tool.name in self.tool_map:
            # 工具名称冲突，记录警告并跳过
            logger.warning(f"工具 '{tool.name}' 已存在于集合中，跳过添加")
            return self

        # 添加工具到元组和映射
        self.tools += (tool,)
        self.tool_map[tool.name] = tool
        return self

    def add_tools(self, *tools: BaseTool):
        """
        向集合中添加多个工具

        可以一次添加多个工具。如果某个工具名称冲突，会跳过该工具并记录警告。
        支持链式调用。

        Args:
            *tools: 可变参数，可以传入多个工具实例

        Returns:
            ToolCollection: 返回自身，支持链式调用

        使用示例：
            collection.add_tools(
                PythonExecute(),
                BrowserUseTool(),
                StrReplaceEditor()
            )
        """
        for tool in tools:
            self.add_tool(tool)
        return self
