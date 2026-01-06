#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具调用智能体模块

本模块实现了 ToolCallAgent 类，它是处理工具/函数调用的基础智能体类。
智能体可以调用各种工具来完成复杂任务，支持自动工具选择、工具执行和结果处理。
"""

import asyncio
import json
from typing import Any, List, Optional, Union

from pydantic import Field

from app.agent.react import ReActAgent
from app.exceptions import TokenLimitExceeded
from app.logger import logger
from app.prompt.toolcall import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.schema import TOOL_CHOICE_TYPE, AgentState, Message, ToolCall, ToolChoice
from app.tool import CreateChatCompletion, Terminate, ToolCollection

# 常量定义：当工具调用模式为 REQUIRED 但未提供工具调用时的错误消息
TOOL_CALL_REQUIRED = "Tool calls required but none provided"


class ToolCallAgent(ReActAgent):
    """
    工具调用智能体基类

    继承自 ReActAgent，实现了完整的工具调用功能。智能体可以：
    1. 思考（think）：分析当前状态，决定使用哪些工具
    2. 行动（act）：执行选定的工具，处理返回结果
    3. 清理（cleanup）：释放资源

    工作流程：
    - 接收用户请求
    - 调用 LLM 分析任务并选择工具
    - 执行工具并获取结果
    - 将结果反馈给 LLM 继续思考
    - 重复直到任务完成或达到最大步数
    """

    # 智能体基本信息
    name: str = "toolcall"  # 智能体名称
    description: str = "an agent that can execute tool calls."  # 智能体描述

    # 提示词配置
    system_prompt: str = SYSTEM_PROMPT  # 系统提示词，定义智能体的角色和行为
    next_step_prompt: str = NEXT_STEP_PROMPT  # 下一步提示词，引导智能体继续思考

    # 工具配置
    available_tools: ToolCollection = ToolCollection(
        CreateChatCompletion(), Terminate()
    )  # 可用工具集合，默认包含聊天完成工具和终止工具
    tool_choices: TOOL_CHOICE_TYPE = ToolChoice.AUTO  # type: ignore
    # 工具选择模式：
    # - AUTO: 自动选择是否使用工具（默认）
    # - REQUIRED: 必须使用工具
    # - NONE: 不使用工具
    special_tool_names: List[str] = Field(
        default_factory=lambda: [Terminate().name]
    )  # 特殊工具列表，执行这些工具会触发任务完成

    # 运行时状态
    tool_calls: List[ToolCall] = Field(
        default_factory=list
    )  # 当前步骤中要执行的工具调用列表
    _current_base64_image: Optional[str] = (
        None  # 当前工具返回的 base64 编码图片（用于视觉工具）
    )

    # 执行限制
    max_steps: int = 30  # 最大执行步数，防止无限循环
    max_observe: Optional[Union[int, bool]] = (
        None  # 观察结果的最大长度限制，用于截断过长的工具返回结果
    )

    async def think(self) -> bool:
        """
        思考阶段：分析当前状态并决定下一步行动

        这是 ReAct 模式中的"思考"步骤，智能体会：
        1. 将下一步提示词添加到消息历史
        2. 调用 LLM 分析任务并选择要使用的工具
        3. 处理 LLM 返回的工具调用和文本内容
        4. 根据不同的工具选择模式做出相应处理

        Returns:
            bool:
                - True: 需要继续执行（有工具调用或内容）
                - False: 思考完成，无需继续执行

        Raises:
            ValueError: 当 LLM 返回错误时
            RuntimeError: 当 LLM 未返回响应时
        """
        # 如果有下一步提示词，将其作为用户消息添加到消息历史
        # 这用于引导智能体继续思考下一步该做什么
        if self.next_step_prompt:
            user_msg = Message.user_message(self.next_step_prompt)
            self.messages += [user_msg]

        try:
            # 调用 LLM，请求它分析任务并选择工具
            # ask_tool 方法会返回 LLM 的响应，包括：
            # - content: 文本内容（智能体的思考过程）
            # - tool_calls: 要调用的工具列表
            response = await self.llm.ask_tool(
                messages=self.messages,  # 当前对话历史
                system_msgs=(
                    [Message.system_message(self.system_prompt)]
                    if self.system_prompt
                    else None
                ),  # 系统提示词，定义智能体角色
                tools=self.available_tools.to_params(),  # 可用工具列表
                tool_choice=self.tool_choices,  # 工具选择模式
            )
        except ValueError:
            # ValueError 直接向上抛出，由调用者处理
            raise
        except Exception as e:
            # 检查是否是 TokenLimitExceeded 错误（可能被包装在 RetryError 中）
            # 这种情况通常发生在对话历史过长，超过了模型的 token 限制
            if hasattr(e, "__cause__") and isinstance(e.__cause__, TokenLimitExceeded):
                token_limit_error = e.__cause__
                logger.error(
                    f"🚨 Token limit error (from RetryError): {token_limit_error}"
                )
                # 将错误信息记录到内存中
                self.memory.add_message(
                    Message.assistant_message(
                        f"Maximum token limit reached, cannot continue execution: {str(token_limit_error)}"
                    )
                )
                # 设置智能体状态为已完成
                self.state = AgentState.FINISHED
                return False
            # 其他异常继续向上抛出
            raise

        # 从响应中提取工具调用列表和文本内容
        self.tool_calls = tool_calls = (
            response.tool_calls if response and response.tool_calls else []
        )
        content = response.content if response and response.content else ""

        # 记录日志，方便调试和监控
        logger.info(f"✨ {self.name}'s thoughts: {content}")
        logger.info(
            f"🛠️ {self.name} selected {len(tool_calls) if tool_calls else 0} tools to use"
        )
        if tool_calls:
            logger.info(
                f"🧰 Tools being prepared: {[call.function.name for call in tool_calls]}"
            )
            logger.info(f"🔧 Tool arguments: {tool_calls[0].function.arguments}")

        try:
            # 检查响应是否为空
            if response is None:
                raise RuntimeError("No response received from the LLM")

            # 处理不同的工具选择模式
            if self.tool_choices == ToolChoice.NONE:
                # NONE 模式：不允许使用工具
                if tool_calls:
                    # 如果 LLM 仍然返回了工具调用，记录警告
                    logger.warning(
                        f"🤔 Hmm, {self.name} tried to use tools when they weren't available!"
                    )
                # 如果有文本内容，保存到内存并返回 True
                if content:
                    self.memory.add_message(Message.assistant_message(content))
                    return True
                return False

            # 创建助手消息并保存到内存
            # 如果 LLM 返回了工具调用，使用 from_tool_calls 创建消息
            # 否则创建普通的助手消息
            assistant_msg = (
                Message.from_tool_calls(content=content, tool_calls=self.tool_calls)
                if self.tool_calls
                else Message.assistant_message(content)
            )
            self.memory.add_message(assistant_msg)

            # REQUIRED 模式：必须使用工具
            if self.tool_choices == ToolChoice.REQUIRED and not self.tool_calls:
                # 如果没有工具调用，返回 True 让 act() 方法处理错误
                return True  # Will be handled in act()

            # AUTO 模式：自动选择是否使用工具
            # 如果没有工具调用但有文本内容，继续执行
            if self.tool_choices == ToolChoice.AUTO and not self.tool_calls:
                return bool(content)

            # 如果有工具调用，返回 True 继续执行
            return bool(self.tool_calls)
        except Exception as e:
            # 处理思考过程中的异常
            logger.error(f"🚨 Oops! The {self.name}'s thinking process hit a snag: {e}")
            self.memory.add_message(
                Message.assistant_message(
                    f"Error encountered while processing: {str(e)}"
                )
            )
            return False

    async def act(self) -> str:
        """
        行动阶段：执行工具调用并处理结果

        这是 ReAct 模式中的"行动"步骤，智能体会：
        1. 检查是否有工具需要执行
        2. 依次执行每个工具调用
        3. 将工具执行结果保存到内存
        4. 返回所有工具的执行结果

        Returns:
            str: 所有工具执行结果的组合字符串，用双换行符分隔

        Raises:
            ValueError: 当工具选择模式为 REQUIRED 但没有工具调用时
        """
        # 如果没有工具调用需要执行
        if not self.tool_calls:
            # 如果工具选择模式为 REQUIRED，必须要有工具调用
            if self.tool_choices == ToolChoice.REQUIRED:
                raise ValueError(TOOL_CALL_REQUIRED)

            # 返回最后一条消息的内容，或者默认消息
            return self.messages[-1].content or "No content or commands to execute"

        # 存储所有工具的执行结果
        results = []
        # 依次执行每个工具调用
        for command in self.tool_calls:
            # 每次执行新工具前，重置 base64_image
            # 这样每个工具的结果是独立的
            self._current_base64_image = None

            # 执行工具并获取结果
            result = await self.execute_tool(command)

            # 如果设置了最大观察长度，截断结果
            # 这可以防止过长的工具返回结果占用太多 token
            if self.max_observe:
                result = result[: self.max_observe]

            # 记录工具执行成功的日志
            logger.info(
                f"🎯 Tool '{command.function.name}' completed its mission! Result: {result}"
            )

            # 创建工具消息并添加到内存
            # 工具消息包含：
            # - content: 工具执行结果
            # - tool_call_id: 对应的工具调用 ID（用于关联）
            # - name: 工具名称
            # - base64_image: 如果工具返回了图片，这里会包含图片数据
            tool_msg = Message.tool_message(
                content=result,
                tool_call_id=command.id,
                name=command.function.name,
                base64_image=self._current_base64_image,
            )
            self.memory.add_message(tool_msg)
            results.append(result)

        # 返回所有工具执行结果，用双换行符分隔
        return "\n\n".join(results)

    async def execute_tool(self, command: ToolCall) -> str:
        """
        执行单个工具调用

        这是工具执行的核心方法，负责：
        1. 验证工具调用格式
        2. 检查工具是否存在
        3. 解析工具参数（JSON 格式）
        4. 执行工具
        5. 处理特殊工具（如终止工具）
        6. 处理工具返回的图片数据
        7. 格式化返回结果

        Args:
            command: 工具调用对象，包含工具名称和参数

        Returns:
            str: 工具执行结果的格式化字符串
                格式：Observed output of cmd `工具名` executed:\n结果
        """
        # 验证工具调用格式
        if not command or not command.function or not command.function.name:
            return "Error: Invalid command format"

        name = command.function.name
        # 检查工具是否在可用工具列表中
        if name not in self.available_tools.tool_map:
            return f"Error: Unknown tool '{name}'"

        try:
            # 解析工具参数
            # LLM 返回的参数是 JSON 字符串格式，需要解析为字典
            args = json.loads(command.function.arguments or "{}")

            # 执行工具
            # available_tools.execute 会找到对应的工具实例并调用其 execute 方法
            logger.info(f"🔧 Activating tool: '{name}'...")
            result = await self.available_tools.execute(name=name, tool_input=args)

            # 处理特殊工具
            # 特殊工具（如 Terminate）执行后可能会改变智能体状态
            await self._handle_special_tool(name=name, result=result)

            # 检查工具返回结果是否包含 base64 编码的图片
            # 某些工具（如截图工具）会返回图片数据
            if hasattr(result, "base64_image") and result.base64_image:
                # 保存图片数据，稍后在创建 tool_message 时使用
                self._current_base64_image = result.base64_image

            # 格式化返回结果
            # 标准格式：Observed output of cmd `工具名` executed:\n结果
            observation = (
                f"Observed output of cmd `{name}` executed:\n{str(result)}"
                if result
                else f"Cmd `{name}` completed with no output"
            )

            return observation
        except json.JSONDecodeError:
            # 处理 JSON 解析错误
            # 这通常发生在 LLM 返回的参数格式不正确时
            error_msg = f"Error parsing arguments for {name}: Invalid JSON format"
            logger.error(
                f"📝 Oops! The arguments for '{name}' don't make sense - invalid JSON, arguments:{command.function.arguments}"
            )
            return f"Error: {error_msg}"
        except Exception as e:
            # 处理其他执行错误
            # 工具执行过程中可能出现的任何异常都会被捕获
            error_msg = f"⚠️ Tool '{name}' encountered a problem: {str(e)}"
            logger.exception(error_msg)  # 记录完整的异常堆栈
            return f"Error: {error_msg}"

    async def _handle_special_tool(self, name: str, result: Any, **kwargs):
        """
        处理特殊工具的执行

        特殊工具（如 Terminate）执行后可能需要改变智能体状态。
        例如，当执行终止工具时，应该将智能体状态设置为 FINISHED。

        Args:
            name: 工具名称
            result: 工具执行结果
            **kwargs: 其他可选参数
        """
        # 检查是否是特殊工具
        if not self._is_special_tool(name):
            return

        # 判断是否应该结束执行
        if self._should_finish_execution(name=name, result=result, **kwargs):
            # 设置智能体状态为已完成
            logger.info(f"🏁 Special tool '{name}' has completed the task!")
            self.state = AgentState.FINISHED

    @staticmethod
    def _should_finish_execution(**kwargs) -> bool:
        """
        判断工具执行是否应该结束智能体

        这是一个静态方法，子类可以重写它来实现自定义的结束逻辑。
        例如，可以根据工具返回结果的内容来决定是否结束。

        Args:
            **kwargs: 可能包含 name、result 等参数

        Returns:
            bool: True 表示应该结束执行，False 表示继续执行
        """
        return True

    def _is_special_tool(self, name: str) -> bool:
        """
        检查工具名称是否在特殊工具列表中

        Args:
            name: 工具名称

        Returns:
            bool: True 表示是特殊工具，False 表示普通工具
        """
        # 使用小写比较，避免大小写敏感问题
        return name.lower() in [n.lower() for n in self.special_tool_names]

    async def cleanup(self):
        """
        清理智能体使用的资源

        这个方法会遍历所有可用工具，如果工具实现了 cleanup 方法，
        则调用它来释放资源（如关闭浏览器、断开连接等）。

        这个方法应该在智能体执行完成后调用，确保资源得到正确释放。
        """
        logger.info(f"🧹 Cleaning up resources for agent '{self.name}'...")
        # 遍历所有可用工具
        for tool_name, tool_instance in self.available_tools.tool_map.items():
            # 检查工具是否实现了 cleanup 方法，且是异步方法
            if hasattr(tool_instance, "cleanup") and asyncio.iscoroutinefunction(
                tool_instance.cleanup
            ):
                try:
                    logger.debug(f"🧼 Cleaning up tool: {tool_name}")
                    # 调用工具的清理方法
                    await tool_instance.cleanup()
                except Exception as e:
                    # 清理过程中的错误不应该影响其他工具的清理
                    logger.error(
                        f"🚨 Error cleaning up tool '{tool_name}': {e}", exc_info=True
                    )
        logger.info(f"✨ Cleanup complete for agent '{self.name}'.")

    async def run(self, request: Optional[str] = None) -> str:
        """
        运行智能体，并在完成后自动清理资源

        这是智能体的主要入口方法，它会：
        1. 调用父类的 run 方法执行智能体
        2. 无论成功还是失败，都会在 finally 块中调用 cleanup

        使用 try-finally 确保资源总是被清理，即使执行过程中出现异常。

        Args:
            request: 用户请求的文本内容

        Returns:
            str: 智能体执行完成后的最终结果
        """
        try:
            # 调用父类的 run 方法
            # 父类会处理 ReAct 循环：think -> act -> observe -> think -> ...
            return await super().run(request)
        finally:
            # 无论成功还是失败，都要清理资源
            await self.cleanup()
