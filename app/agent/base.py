#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体基类模块

本模块定义了 BaseAgent 抽象基类，它是所有智能体的基础。
提供了状态管理、记忆管理、执行循环等核心功能。
所有具体的智能体类都应该继承自 BaseAgent 并实现 step() 方法。
"""

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from app.llm import LLM
from app.logger import logger
from app.sandbox.client import SANDBOX_CLIENT
from app.schema import ROLE_TYPE, AgentState, Memory, Message


class BaseAgent(BaseModel, ABC):
    """
    智能体抽象基类

    这是所有智能体的基础类，提供了以下核心功能：
    1. 状态管理：管理智能体的运行状态（空闲、运行中、已完成、错误）
    2. 记忆管理：存储和管理对话历史消息
    3. 执行循环：提供基于步骤的执行框架
    4. 卡住检测：自动检测智能体是否陷入循环

    子类必须实现 step() 方法来定义具体的执行逻辑。

    设计模式：
    - 模板方法模式：run() 方法定义了执行流程，step() 由子类实现
    - 状态机模式：通过 state_context 管理状态转换
    """

    # ========== 核心属性 ==========
    name: str = Field(..., description="智能体的唯一名称，用于标识不同的智能体实例")
    description: Optional[str] = Field(
        None, description="智能体的描述信息，说明智能体的功能和用途"
    )

    # ========== 提示词配置 ==========
    system_prompt: Optional[str] = Field(
        None, description="系统级提示词，定义智能体的角色、行为准则和任务目标"
    )
    next_step_prompt: Optional[str] = Field(
        None, description="下一步提示词，用于引导智能体在每步执行后思考下一步行动"
    )

    # ========== 依赖组件 ==========
    llm: LLM = Field(
        default_factory=LLM,
        description="语言模型实例，用于与 LLM API 交互，生成文本和工具调用",
    )
    memory: Memory = Field(
        default_factory=Memory, description="智能体的记忆存储，保存所有对话消息历史"
    )
    state: AgentState = Field(
        default=AgentState.IDLE,
        description="智能体的当前状态：IDLE(空闲)、RUNNING(运行中)、FINISHED(已完成)、ERROR(错误)",
    )

    # ========== 执行控制 ==========
    max_steps: int = Field(
        default=10, description="最大执行步数，防止智能体陷入无限循环"
    )
    current_step: int = Field(default=0, description="当前执行的步数，从 0 开始计数")

    # 卡住检测阈值：当智能体连续返回相同内容达到此次数时，认为智能体卡住了
    duplicate_threshold: int = 2

    class Config:
        """
        Pydantic 配置类

        arbitrary_types_allowed: 允许使用任意类型（如 LLM、Memory 等自定义类）
        extra: 允许子类添加额外的字段，提供灵活性
        """

        arbitrary_types_allowed = True
        extra = "allow"  # 允许子类添加额外字段，提供灵活性

    @model_validator(mode="after")
    def initialize_agent(self) -> "BaseAgent":
        """
        初始化智能体

        这是一个 Pydantic 模型验证器，在模型创建后自动调用。
        用于确保 llm 和 memory 被正确初始化。

        Returns:
            BaseAgent: 初始化后的智能体实例

        说明：
        - 如果 llm 未提供或类型不正确，会根据智能体名称创建默认的 LLM 实例
        - 如果 memory 未提供，会创建默认的 Memory 实例
        """
        # 如果 LLM 未提供或类型不正确，创建默认实例
        # 使用智能体名称（小写）作为配置名称，这样可以支持多个 LLM 配置
        if self.llm is None or not isinstance(self.llm, LLM):
            self.llm = LLM(config_name=self.name.lower())
        # 如果记忆未提供，创建默认实例
        if not isinstance(self.memory, Memory):
            self.memory = Memory()
        return self

    @asynccontextmanager
    async def state_context(self, new_state: AgentState):
        """
        状态上下文管理器：安全的状态转换

        这是一个异步上下文管理器，用于安全地管理智能体状态的转换。
        使用 with 语句可以确保状态在代码块执行后自动恢复。

        工作原理：
        1. 保存当前状态
        2. 切换到新状态
        3. 执行代码块
        4. 如果出现异常，切换到 ERROR 状态
        5. 无论成功还是失败，都会恢复原来的状态

        Args:
            new_state: 要转换到的新状态

        Yields:
            None: 在上下文内执行代码

        Raises:
            ValueError: 如果 new_state 不是有效的 AgentState 枚举值

        使用示例：
            async with agent.state_context(AgentState.RUNNING):
                # 在这里执行需要 RUNNING 状态的代码
                await agent.step()
            # 执行完成后，状态自动恢复为之前的状态
        """
        # 验证状态是否有效
        if not isinstance(new_state, AgentState):
            raise ValueError(f"无效的状态: {new_state}")

        # 保存当前状态，以便后续恢复
        previous_state = self.state
        # 切换到新状态
        self.state = new_state
        try:
            # 在上下文中执行代码
            yield
        except Exception as e:
            # 如果出现异常，将状态设置为 ERROR
            self.state = AgentState.ERROR
            # 重新抛出异常，让调用者处理
            raise e
        finally:
            # 无论成功还是失败，都恢复原来的状态
            self.state = previous_state

    def update_memory(
        self,
        role: ROLE_TYPE,  # type: ignore
        content: str,
        base64_image: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        更新智能体的记忆：添加一条消息到对话历史

        这个方法用于将各种类型的消息添加到智能体的记忆中。
        支持的消息类型包括：用户消息、系统消息、助手消息、工具消息。

        Args:
            role: 消息发送者的角色
                - "user": 用户消息
                - "system": 系统消息（通常是系统提示词）
                - "assistant": 助手消息（LLM 的回复）
                - "tool": 工具消息（工具执行的结果）
            content: 消息的文本内容
            base64_image: 可选的 base64 编码图片，用于支持视觉输入
            **kwargs: 其他可选参数
                - 对于 tool 消息，可以包含 tool_call_id、name 等参数

        Raises:
            ValueError: 如果 role 不是支持的角色类型

        使用示例：
            # 添加用户消息
            agent.update_memory("user", "请帮我写一个 Python 函数")

            # 添加带图片的用户消息
            agent.update_memory("user", "这是什么？", base64_image="iVBORw0KG...")

            # 添加工具消息
            agent.update_memory("tool", "执行成功", tool_call_id="call_123", name="python_execute")
        """
        # 消息类型到创建函数的映射
        message_map = {
            "user": Message.user_message,  # 创建用户消息
            "system": Message.system_message,  # 创建系统消息
            "assistant": Message.assistant_message,  # 创建助手消息
            "tool": lambda content, **kw: Message.tool_message(
                content, **kw
            ),  # 创建工具消息（需要额外参数）
        }

        # 检查角色是否支持
        if role not in message_map:
            raise ValueError(f"不支持的消息角色: {role}")

        # 根据角色准备参数
        # 对于 tool 消息，需要传递所有 kwargs（如 tool_call_id、name）
        # 对于其他消息，只需要 base64_image
        kwargs = {"base64_image": base64_image, **(kwargs if role == "tool" else {})}
        # 使用对应的创建函数创建消息并添加到记忆
        self.memory.add_message(message_map[role](content, **kwargs))

    async def run(self, request: Optional[str] = None) -> str:
        """
        执行智能体的主循环（异步方法）

        这是智能体的主要入口方法，负责：
        1. 检查智能体状态（必须是 IDLE 才能开始）
        2. 记录用户请求到记忆
        3. 进入运行状态并开始执行循环
        4. 在循环中反复调用 step() 方法
        5. 检测是否卡住并处理
        6. 达到最大步数或完成时退出
        7. 清理资源

        执行流程：
        - 状态检查：确保智能体处于 IDLE 状态
        - 记录请求：如果有用户请求，添加到记忆
        - 执行循环：在 RUNNING 状态下反复执行 step()
        - 卡住检测：每步后检查是否陷入循环
        - 退出条件：达到最大步数或状态变为 FINISHED
        - 资源清理：清理沙箱客户端资源

        Args:
            request: 可选的初始用户请求文本

        Returns:
            str: 执行结果的摘要字符串，包含每步的执行结果

        Raises:
            RuntimeError: 如果智能体不是从 IDLE 状态开始运行

        使用示例：
            agent = MyAgent(name="my_agent")
            result = await agent.run("请帮我完成这个任务")
            print(result)
        """
        # 状态检查：只能从 IDLE 状态开始运行
        if self.state != AgentState.IDLE:
            raise RuntimeError(
                f"无法从 {self.state} 状态运行智能体，必须从 IDLE 状态开始"
            )

        # 如果有用户请求，记录到记忆
        if request:
            self.update_memory("user", request)

        # 存储每步的执行结果
        results: List[str] = []
        # 使用状态上下文管理器，确保状态正确转换和恢复
        async with self.state_context(AgentState.RUNNING):
            # 执行循环：直到达到最大步数或状态变为 FINISHED
            while (
                self.current_step < self.max_steps and self.state != AgentState.FINISHED
            ):
                # 增加步数计数
                self.current_step += 1
                logger.info(f"执行步骤 {self.current_step}/{self.max_steps}")

                # 执行一步（由子类实现具体逻辑）
                step_result = await self.step()

                # 检查是否卡住（重复相同内容）
                if self.is_stuck():
                    # 处理卡住状态：添加提示词引导智能体改变策略
                    self.handle_stuck_state()

                # 记录这一步的结果
                results.append(f"步骤 {self.current_step}: {step_result}")

            # 如果达到最大步数，重置并记录终止原因
            if self.current_step >= self.max_steps:
                self.current_step = 0
                self.state = AgentState.IDLE
                results.append(f"已终止：达到最大步数 ({self.max_steps})")

        # 清理沙箱客户端资源（如浏览器、终端等）
        await SANDBOX_CLIENT.cleanup()

        # 返回所有步骤的结果摘要
        return "\n".join(results) if results else "未执行任何步骤"

    @abstractmethod
    async def step(self) -> str:
        """
        执行智能体的单步操作（抽象方法，必须由子类实现）

        这是智能体执行的核心方法，每个子类必须实现自己的 step() 逻辑。
        这个方法会在 run() 方法的循环中被反复调用，直到任务完成或达到最大步数。

        Returns:
            str: 这一步的执行结果描述

        注意：
        - 这是抽象方法，子类必须实现
        - 方法应该是异步的（async def）
        - 应该返回描述执行结果的字符串

        实现示例：
            async def step(self) -> str:
                # 1. 分析当前状态
                # 2. 选择要执行的操作
                # 3. 执行操作
                # 4. 返回结果
                return "执行完成"
        """

    def handle_stuck_state(self):
        """
        处理卡住状态：添加提示词引导智能体改变策略

        当检测到智能体陷入循环时（重复返回相同内容），
        这个方法会添加一个提示词，引导智能体尝试新的策略。

        工作原理：
        - 在 next_step_prompt 前面添加卡住提示
        - 提示智能体避免重复已经尝试过的无效路径
        - 记录警告日志
        """
        # 卡住提示词：引导智能体改变策略
        stuck_prompt = "检测到重复响应。请考虑新的策略，避免重复已经尝试过的无效路径。"
        # 将卡住提示添加到下一步提示词前面
        self.next_step_prompt = f"{stuck_prompt}\n{self.next_step_prompt}"
        logger.warning(f"智能体检测到卡住状态。已添加提示: {stuck_prompt}")

    def is_stuck(self) -> bool:
        """
        检查智能体是否卡住（陷入循环）

        通过检测智能体是否连续返回相同的内容来判断是否卡住。
        如果最后一条助手消息的内容与之前的助手消息内容相同，
        且重复次数达到阈值，则认为智能体卡住了。

        检测逻辑：
        1. 检查消息数量是否足够（至少 2 条）
        2. 检查最后一条消息是否有内容
        3. 从后往前遍历消息，统计相同内容的助手消息数量
        4. 如果重复次数 >= duplicate_threshold，返回 True

        Returns:
            bool: True 表示智能体卡住了，False 表示正常

        示例：
            如果智能体连续 3 次返回 "我需要更多信息"，
            且 duplicate_threshold=2，则返回 True
        """
        # 消息数量不足，无法判断
        if len(self.memory.messages) < 2:
            return False

        # 获取最后一条消息
        last_message = self.memory.messages[-1]
        # 如果最后一条消息没有内容，无法判断
        if not last_message.content:
            return False

        # 从后往前遍历消息（排除最后一条），统计相同内容的助手消息数量
        duplicate_count = sum(
            1
            for msg in reversed(self.memory.messages[:-1])
            if msg.role == "assistant" and msg.content == last_message.content
        )

        # 如果重复次数达到阈值，认为卡住了
        return duplicate_count >= self.duplicate_threshold

    @property
    def messages(self) -> List[Message]:
        """
        获取智能体记忆中的所有消息（属性访问器）

        这是一个属性（property），提供便捷的方式访问智能体的消息历史。
        相当于 self.memory.messages 的快捷方式。

        Returns:
            List[Message]: 消息列表，按时间顺序排列

        使用示例：
            # 获取所有消息
            all_messages = agent.messages

            # 获取最后一条消息
            last_message = agent.messages[-1]
        """
        return self.memory.messages

    @messages.setter
    def messages(self, value: List[Message]):
        """
        设置智能体的消息列表（属性设置器）

        允许直接设置智能体的消息历史，用于重置或恢复对话状态。

        Args:
            value: 新的消息列表

        使用示例：
            # 重置消息历史
            agent.messages = []

            # 恢复之前的消息
            agent.messages = saved_messages
        """
        self.memory.messages = value
