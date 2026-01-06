#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型和枚举定义模块

本模块定义了项目中使用的核心数据模型和枚举类型：
- Role: 消息角色枚举
- ToolChoice: 工具选择模式枚举
- AgentState: 智能体状态枚举
- Message: 消息模型
- Memory: 记忆模型
- ToolCall: 工具调用模型
"""

from enum import Enum
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class Role(str, Enum):
    """
    消息角色枚举

    定义消息的发送者类型，用于区分不同来源的消息。
    """

    SYSTEM = "system"  # 系统消息：通常是系统提示词，定义智能体的角色和行为
    USER = "user"  # 用户消息：用户输入的内容
    ASSISTANT = "assistant"  # 助手消息：LLM 生成的回复
    TOOL = "tool"  # 工具消息：工具执行后返回的结果


# 提取所有角色值，用于类型检查
ROLE_VALUES = tuple(role.value for role in Role)
# 类型别名：用于类型提示，限制只能是 Role 枚举中的值
ROLE_TYPE = Literal[ROLE_VALUES]  # type: ignore


class ToolChoice(str, Enum):
    """
    工具选择模式枚举

    定义 LLM 在调用工具时的选择策略。
    """

    NONE = "none"  # 不使用工具：LLM 只能生成文本回复，不能调用工具
    AUTO = "auto"  # 自动选择：LLM 根据情况决定是否使用工具（默认模式）
    REQUIRED = "required"  # 必须使用工具：LLM 必须调用至少一个工具


# 提取所有工具选择值，用于类型检查
TOOL_CHOICE_VALUES = tuple(choice.value for choice in ToolChoice)
# 类型别名：用于类型提示
TOOL_CHOICE_TYPE = Literal[TOOL_CHOICE_VALUES]  # type: ignore


class AgentState(str, Enum):
    """
    智能体执行状态枚举

    定义智能体在整个生命周期中可能处于的状态。
    状态转换流程：IDLE -> RUNNING -> FINISHED/ERROR
    """

    IDLE = "IDLE"  # 空闲状态：智能体已创建但未开始执行
    RUNNING = "RUNNING"  # 运行状态：智能体正在执行任务
    FINISHED = "FINISHED"  # 完成状态：智能体成功完成任务
    ERROR = "ERROR"  # 错误状态：智能体执行过程中出现错误


class Function(BaseModel):
    """
    函数调用模型

    表示 LLM 要调用的函数/工具的信息。
    """

    name: str = Field(..., description="要调用的工具/函数名称")
    arguments: str = Field(
        ..., description="函数参数，JSON 字符串格式，需要解析后使用"
    )


class ToolCall(BaseModel):
    """
    工具调用模型

    表示一条消息中包含的工具调用信息。
    当 LLM 决定调用工具时，会生成 ToolCall 对象。
    """

    id: str = Field(..., description="工具调用的唯一标识符，用于关联工具返回结果")
    type: str = Field(
        default="function", description="调用类型，固定为 'function'"
    )
    function: Function = Field(..., description="要调用的函数信息")


class Message(BaseModel):
    """
    消息模型

    表示对话中的一条消息，可以是用户消息、系统消息、助手消息或工具消息。
    支持文本内容、工具调用、图片等多种形式。
    """

    # 消息角色：user、system、assistant、tool 之一
    role: ROLE_TYPE = Field(..., description="消息角色")  # type: ignore
    # 消息的文本内容（可选，工具消息可能没有）
    content: Optional[str] = Field(default=None, description="消息的文本内容")
    # 工具调用列表（仅 assistant 消息可能有）
    tool_calls: Optional[List[ToolCall]] = Field(
        default=None, description="工具调用列表，当助手决定调用工具时包含"
    )
    # 工具名称（仅 tool 消息需要）
    name: Optional[str] = Field(
        default=None, description="工具名称，用于 tool 消息标识是哪个工具返回的"
    )
    # 工具调用 ID（仅 tool 消息需要，用于关联对应的 tool_calls）
    tool_call_id: Optional[str] = Field(
        default=None, description="工具调用 ID，用于关联 tool_calls 中的调用"
    )
    # base64 编码的图片（用于支持视觉输入）
    base64_image: Optional[str] = Field(
        default=None, description="base64 编码的图片数据，用于视觉输入"
    )

    def __add__(self, other) -> List["Message"]:
        """
        支持 Message + list 或 Message + Message 的操作（魔术方法）

        允许使用 + 运算符将 Message 对象与其他对象组合成列表。
        这提供了便捷的消息列表构建方式。

        Args:
            other: 另一个 Message 对象或消息列表

        Returns:
            List[Message]: 包含当前消息和 other 的消息列表

        Raises:
            TypeError: 如果 other 不是 Message 或 list 类型

        使用示例：
            msg1 = Message.user_message("Hello")
            msg2 = Message.assistant_message("Hi")
            messages = msg1 + msg2  # [msg1, msg2]
            messages = msg1 + [msg2, msg3]  # [msg1, msg2, msg3]
        """
        if isinstance(other, list):
            return [self] + other
        elif isinstance(other, Message):
            return [self, other]
        else:
            raise TypeError(
                f"不支持的操作数类型: '{type(self).__name__}' + '{type(other).__name__}'"
            )

    def __radd__(self, other) -> List["Message"]:
        """
        支持 list + Message 的操作（右加魔术方法）

        当列表在左侧，Message 在右侧时调用（如 [msg1] + msg2）。

        Args:
            other: 消息列表

        Returns:
            List[Message]: 包含 other 和当前消息的消息列表

        Raises:
            TypeError: 如果 other 不是 list 类型

        使用示例：
            msg1 = Message.user_message("Hello")
            msg2 = Message.assistant_message("Hi")
            messages = [msg1] + msg2  # [msg1, msg2]
        """
        if isinstance(other, list):
            return other + [self]
        else:
            raise TypeError(
                f"不支持的操作数类型: '{type(other).__name__}' + '{type(self).__name__}'"
            )

    def to_dict(self) -> dict:
        """
        将消息转换为字典格式

        用于将 Message 对象转换为字典，通常用于：
        - 传递给 LLM API（需要字典格式）
        - 序列化为 JSON
        - 与其他系统交互

        Returns:
            dict: 包含消息所有字段的字典，只包含非 None 的字段

        返回格式示例：
            {
                "role": "user",
                "content": "Hello",
                "base64_image": "iVBORw0KG..."
            }
        """
        # 创建基础字典，包含必需的角色字段
        message = {"role": self.role}
        # 只添加非 None 的字段
        if self.content is not None:
            message["content"] = self.content
        if self.tool_calls is not None:
            # 将 ToolCall 对象列表转换为字典列表
            message["tool_calls"] = [
                tool_call.dict() for tool_call in self.tool_calls
            ]
        if self.name is not None:
            message["name"] = self.name
        if self.tool_call_id is not None:
            message["tool_call_id"] = self.tool_call_id
        if self.base64_image is not None:
            message["base64_image"] = self.base64_image
        return message

    @classmethod
    def user_message(
        cls, content: str, base64_image: Optional[str] = None
    ) -> "Message":
        """
        创建用户消息（类方法）

        便捷方法，用于创建用户角色的消息。

        Args:
            content: 消息的文本内容
            base64_image: 可选的 base64 编码图片

        Returns:
            Message: 用户消息对象

        使用示例：
            msg = Message.user_message("请帮我写代码")
            msg_with_image = Message.user_message("这是什么？", base64_image="...")
        """
        return cls(role=Role.USER, content=content, base64_image=base64_image)

    @classmethod
    def system_message(cls, content: str) -> "Message":
        """
        创建系统消息（类方法）

        便捷方法，用于创建系统角色的消息（通常是系统提示词）。

        Args:
            content: 系统消息的内容

        Returns:
            Message: 系统消息对象

        使用示例：
            msg = Message.system_message("你是一个有用的 AI 助手")
        """
        return cls(role=Role.SYSTEM, content=content)

    @classmethod
    def assistant_message(
        cls, content: Optional[str] = None, base64_image: Optional[str] = None
    ) -> "Message":
        """
        创建助手消息（类方法）

        便捷方法，用于创建助手角色的消息（LLM 的回复）。

        Args:
            content: 消息的文本内容（可选，可能只有 tool_calls）
            base64_image: 可选的 base64 编码图片

        Returns:
            Message: 助手消息对象

        使用示例：
            msg = Message.assistant_message("好的，我来帮你")
        """
        return cls(role=Role.ASSISTANT, content=content, base64_image=base64_image)

    @classmethod
    def tool_message(
        cls, content: str, name, tool_call_id: str, base64_image: Optional[str] = None
    ) -> "Message":
        """
        创建工具消息（类方法）

        便捷方法，用于创建工具角色的消息（工具执行的结果）。

        Args:
            content: 工具执行的结果内容
            name: 工具名称，标识是哪个工具返回的
            tool_call_id: 工具调用 ID，用于关联对应的 tool_calls
            base64_image: 可选的 base64 编码图片（某些工具可能返回图片）

        Returns:
            Message: 工具消息对象

        使用示例：
            msg = Message.tool_message(
                content="执行成功",
                name="python_execute",
                tool_call_id="call_123"
            )
        """
        return cls(
            role=Role.TOOL,
            content=content,
            name=name,
            tool_call_id=tool_call_id,
            base64_image=base64_image,
        )

    @classmethod
    def from_tool_calls(
        cls,
        tool_calls: List[Any],
        content: Union[str, List[str]] = "",
        base64_image: Optional[str] = None,
        **kwargs,
    ):
        """
        从原始工具调用创建助手消息（类方法）

        当 LLM 决定调用工具时，会返回工具调用列表。
        这个方法用于将这些工具调用转换为 Message 对象。

        Args:
            tool_calls: LLM 返回的原始工具调用列表
            content: 可选的文本内容（LLM 可能同时返回文本和工具调用）
            base64_image: 可选的 base64 编码图片
            **kwargs: 其他可选参数

        Returns:
            Message: 包含工具调用的助手消息对象

        使用示例：
            # LLM 返回的工具调用
            raw_calls = [ToolCall(id="call_1", function=Function(...)), ...]
            msg = Message.from_tool_calls(raw_calls, content="我来执行这些工具")
        """
        # 将原始工具调用格式化为标准格式
        formatted_calls = [
            {
                "id": call.id,
                "function": call.function.model_dump(),
                "type": "function",
            }
            for call in tool_calls
        ]
        return cls(
            role=Role.ASSISTANT,
            content=content,
            tool_calls=formatted_calls,
            base64_image=base64_image,
            **kwargs,
        )


class Memory(BaseModel):
    """
    记忆模型

    用于存储和管理智能体的对话历史。
    提供消息的添加、查询、清理等功能，并支持消息数量限制。
    """

    # 消息列表，按时间顺序存储所有对话消息
    messages: List[Message] = Field(
        default_factory=list, description="存储的消息列表"
    )
    # 最大消息数量，超过此数量会自动删除最旧的消息
    max_messages: int = Field(
        default=100, description="最大消息数量，用于限制记忆大小"
    )

    def add_message(self, message: Message) -> None:
        """
        添加一条消息到记忆

        将新消息添加到消息列表末尾，如果超过最大数量限制，
        会删除最旧的消息，只保留最新的 max_messages 条。

        Args:
            message: 要添加的消息对象

        使用示例：
            memory = Memory()
            memory.add_message(Message.user_message("Hello"))
        """
        self.messages.append(message)
        # 如果超过最大消息数量，只保留最新的消息
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def add_messages(self, messages: List[Message]) -> None:
        """
        添加多条消息到记忆

        批量添加消息，比多次调用 add_message 更高效。

        Args:
            messages: 要添加的消息列表

        使用示例：
            memory = Memory()
            memory.add_messages([
                Message.user_message("Hello"),
                Message.assistant_message("Hi")
            ])
        """
        self.messages.extend(messages)
        # 如果超过最大消息数量，只保留最新的消息
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def clear(self) -> None:
        """
        清空所有消息

        删除记忆中的所有消息，用于重置对话历史。

        使用示例：
            memory.clear()  # 清空所有消息
        """
        self.messages.clear()

    def get_recent_messages(self, n: int) -> List[Message]:
        """
        获取最近的 n 条消息

        用于获取最近的对话历史，常用于：
        - 限制发送给 LLM 的消息数量（节省 token）
        - 查看最近的对话内容

        Args:
            n: 要获取的消息数量

        Returns:
            List[Message]: 最近的 n 条消息列表

        使用示例：
            recent = memory.get_recent_messages(10)  # 获取最近 10 条消息
        """
        return self.messages[-n:]

    def to_dict_list(self) -> List[dict]:
        """
        将消息列表转换为字典列表

        用于序列化或传递给需要字典格式的 API。

        Returns:
            List[dict]: 消息字典列表

        使用示例：
            dict_list = memory.to_dict_list()
            # 可以用于 JSON 序列化或传递给 LLM API
        """
        return [msg.to_dict() for msg in self.messages]
