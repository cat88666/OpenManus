#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM（大语言模型）接口模块

本模块提供了与各种 LLM API 交互的统一接口，支持：
- OpenAI API（包括 Azure OpenAI）
- AWS Bedrock
- Token 计数和管理
- 流式和非流式响应
- 工具调用（Function Calling）
- 多模态输入（图片）

主要类：
- TokenCounter: Token 计数器，用于计算消息的 token 数量
- LLM: LLM 客户端，封装了与各种 LLM API 的交互
"""

import math
from typing import Dict, List, Optional, Union

import tiktoken
from openai import (
    APIError,
    AsyncAzureOpenAI,
    AsyncOpenAI,
    AuthenticationError,
    OpenAIError,
    RateLimitError,
)
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from app.bedrock import BedrockClient
from app.config import LLMSettings, config
from app.exceptions import TokenLimitExceeded
from app.logger import logger
from app.schema import (
    ROLE_VALUES,
    TOOL_CHOICE_TYPE,
    TOOL_CHOICE_VALUES,
    Message,
    ToolChoice,
)


# 推理模型列表：这些模型使用特殊的参数（如 max_completion_tokens）
REASONING_MODELS = ["o1", "o3-mini"]
# 多模态模型列表：这些模型支持图片输入
MULTIMODAL_MODELS = [
    "gpt-4-vision-preview",
    "gpt-4o",
    "gpt-4o-mini",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]


class TokenCounter:
    """
    Token 计数器类

    用于准确计算消息的 token 数量，这对于：
    - 控制 API 调用成本
    - 避免超出模型的最大 token 限制
    - 优化消息长度

    支持：
    - 文本 token 计数
    - 图片 token 计数（根据细节级别）
    - 工具调用 token 计数
    - 完整消息列表的 token 计数
    """

    # ========== Token 常量 ==========
    BASE_MESSAGE_TOKENS = 4  # 每条消息的基础 token 数（格式开销）
    FORMAT_TOKENS = 2  # 消息列表的格式 token 数
    LOW_DETAIL_IMAGE_TOKENS = 85  # 低细节图片的固定 token 数
    HIGH_DETAIL_TILE_TOKENS = 170  # 高细节图片每个 tile 的 token 数

    # ========== 图片处理常量 ==========
    MAX_SIZE = 2048  # 图片最大尺寸（像素）
    HIGH_DETAIL_TARGET_SHORT_SIDE = 768  # 高细节图片短边目标尺寸
    TILE_SIZE = 512  # 图片 tile 尺寸（用于计算高细节图片 token）

    def __init__(self, tokenizer):
        """
        初始化 Token 计数器

        Args:
            tokenizer: tiktoken 编码器，用于将文本编码为 token
        """
        self.tokenizer = tokenizer

    def count_text(self, text: str) -> int:
        """
        计算文本的 token 数量

        Args:
            text: 要计算的文本字符串

        Returns:
            int: token 数量，如果文本为空则返回 0
        """
        return 0 if not text else len(self.tokenizer.encode(text))

    def count_image(self, image_item: dict) -> int:
        """
        根据细节级别和尺寸计算图片的 token 数量

        计算规则：
        - 低细节（low）：固定 85 tokens
        - 中/高细节（medium/high）：
          1. 缩放到 2048x2048 正方形内
          2. 将短边缩放到 768px
          3. 计算 512px tile 的数量（每个 tile 170 tokens）
          4. 加上基础 85 tokens

        Args:
            image_item: 图片信息字典，可能包含：
                - detail: 细节级别（"low", "medium", "high"）
                - dimensions: 图片尺寸 (width, height)

        Returns:
            int: 图片的 token 数量
        """
        detail = image_item.get("detail", "medium")

        # 低细节：固定 token 数
        if detail == "low":
            return self.LOW_DETAIL_IMAGE_TOKENS

        # 中/高细节：根据尺寸计算
        # OpenAI 的 medium 默认使用高细节计算方式
        if detail == "high" or detail == "medium":
            # 如果提供了尺寸信息，使用实际尺寸计算
            if "dimensions" in image_item:
                width, height = image_item["dimensions"]
                return self._calculate_high_detail_tokens(width, height)

        # 如果没有尺寸信息，使用默认值
        return (
            self._calculate_high_detail_tokens(1024, 1024) if detail == "high" else 1024
        )

    def _calculate_high_detail_tokens(self, width: int, height: int) -> int:
        """
        计算高细节图片的 token 数量（基于尺寸）

        这是 OpenAI 的图片 token 计算算法：
        1. 如果图片超过 2048x2048，先缩放到 2048x2048 内
        2. 将短边缩放到 768px（保持宽高比）
        3. 计算需要多少个 512x512 的 tile
        4. 每个 tile 170 tokens，加上基础 85 tokens

        Args:
            width: 图片宽度（像素）
            height: 图片高度（像素）

        Returns:
            int: 计算出的 token 数量
        """
        # 步骤 1: 如果超过最大尺寸，缩放到 MAX_SIZE x MAX_SIZE 正方形内
        if width > self.MAX_SIZE or height > self.MAX_SIZE:
            scale = self.MAX_SIZE / max(width, height)
            width = int(width * scale)
            height = int(height * scale)

        # 步骤 2: 将短边缩放到目标尺寸（保持宽高比）
        scale = self.HIGH_DETAIL_TARGET_SHORT_SIDE / min(width, height)
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)

        # 步骤 3: 计算需要多少个 512px 的 tile
        tiles_x = math.ceil(scaled_width / self.TILE_SIZE)
        tiles_y = math.ceil(scaled_height / self.TILE_SIZE)
        total_tiles = tiles_x * tiles_y

        # 步骤 4: 计算最终 token 数 = tile 数 * 每个 tile 的 token + 基础 token
        return (
            total_tiles * self.HIGH_DETAIL_TILE_TOKENS
        ) + self.LOW_DETAIL_IMAGE_TOKENS

    def count_content(self, content: Union[str, List[Union[str, dict]]]) -> int:
        """
        计算消息内容的 token 数量

        支持多种内容格式：
        - 纯文本字符串
        - 多模态内容列表（文本 + 图片）

        Args:
            content: 消息内容，可以是：
                - 字符串：纯文本
                - 列表：多模态内容，包含 {"type": "text", "text": "..."} 或图片

        Returns:
            int: token 数量
        """
        if not content:
            return 0

        # 如果是字符串，直接计算
        if isinstance(content, str):
            return self.count_text(content)

        # 如果是列表，遍历每个元素
        token_count = 0
        for item in content:
            if isinstance(item, str):
                # 文本元素
                token_count += self.count_text(item)
            elif isinstance(item, dict):
                # 字典元素：可能是文本或图片
                if "text" in item:
                    token_count += self.count_text(item["text"])
                elif "image_url" in item:
                    token_count += self.count_image(item)
        return token_count

    def count_tool_calls(self, tool_calls: List[dict]) -> int:
        """
        计算工具调用的 token 数量

        Args:
            tool_calls: 工具调用列表，每个调用包含 function 字段

        Returns:
            int: token 数量
        """
        token_count = 0
        for tool_call in tool_calls:
            if "function" in tool_call:
                function = tool_call["function"]
                # 计算工具名称的 token
                token_count += self.count_text(function.get("name", ""))
                # 计算工具参数的 token（JSON 字符串）
                token_count += self.count_text(function.get("arguments", ""))
        return token_count

    def count_message_tokens(self, messages: List[dict]) -> int:
        """
        计算消息列表的总 token 数量

        这是最常用的方法，用于计算整个对话历史的 token 数。
        包括：
        - 格式 token（消息列表的基础格式）
        - 每条消息的基础 token
        - 角色、内容、工具调用等所有字段的 token

        Args:
            messages: 消息列表，每个消息是字典格式

        Returns:
            int: 总 token 数量

        使用示例：
            messages = [{"role": "user", "content": "Hello"}]
            tokens = counter.count_message_tokens(messages)
        """
        # 消息列表的基础格式 token
        total_tokens = self.FORMAT_TOKENS

        # 遍历每条消息
        for message in messages:
            # 每条消息的基础 token
            tokens = self.BASE_MESSAGE_TOKENS

            # 添加角色 token
            tokens += self.count_text(message.get("role", ""))

            # 添加内容 token
            if "content" in message:
                tokens += self.count_content(message["content"])

            # 添加工具调用 token
            if "tool_calls" in message:
                tokens += self.count_tool_calls(message["tool_calls"])

            # 添加 name 和 tool_call_id token（用于工具消息）
            tokens += self.count_text(message.get("name", ""))
            tokens += self.count_text(message.get("tool_call_id", ""))

            total_tokens += tokens

        return total_tokens


class LLM:
    """
    LLM（大语言模型）客户端类

    这是与各种 LLM API 交互的统一接口，支持：
    - OpenAI API（包括 Azure OpenAI）
    - AWS Bedrock
    - Token 计数和管理
    - 流式和非流式响应
    - 工具调用（Function Calling）
    - 多模态输入（图片）

    设计模式：
    - 单例模式：每个配置名称只有一个实例，避免重复创建客户端
    - 重试机制：使用 tenacity 库自动重试失败的请求

    主要方法：
    - ask(): 发送文本消息，获取 LLM 回复
    - ask_with_images(): 发送带图片的消息
    - ask_tool(): 发送消息并支持工具调用
    """

    # 单例字典：存储不同配置名称的 LLM 实例
    _instances: Dict[str, "LLM"] = {}

    def __new__(
        cls, config_name: str = "default", llm_config: Optional[LLMSettings] = None
    ):
        """
        单例模式实现（魔术方法）

        确保每个配置名称只有一个 LLM 实例，避免重复创建客户端连接。

        Args:
            config_name: 配置名称，用于区分不同的 LLM 配置
            llm_config: 可选的 LLM 配置对象

        Returns:
            LLM: LLM 实例（单例）
        """
        # 如果该配置名称还没有实例，创建新实例
        if config_name not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(config_name, llm_config)
            cls._instances[config_name] = instance
        # 返回已存在的实例
        return cls._instances[config_name]

    def __init__(
        self, config_name: str = "default", llm_config: Optional[LLMSettings] = None
    ):
        if not hasattr(self, "client"):  # Only initialize if not already initialized
            llm_config = llm_config or config.llm
            llm_config = llm_config.get(config_name, llm_config["default"])
            self.model = llm_config.model
            self.max_tokens = llm_config.max_tokens
            self.temperature = llm_config.temperature
            self.api_type = llm_config.api_type
            self.api_key = llm_config.api_key
            self.api_version = llm_config.api_version
            self.base_url = llm_config.base_url

            # Add token counting related attributes
            self.total_input_tokens = 0
            self.total_completion_tokens = 0
            self.max_input_tokens = (
                llm_config.max_input_tokens
                if hasattr(llm_config, "max_input_tokens")
                else None
            )

            # Initialize tokenizer
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model)
            except KeyError:
                # If the model is not in tiktoken's presets, use cl100k_base as default
                self.tokenizer = tiktoken.get_encoding("cl100k_base")

            if self.api_type == "azure":
                self.client = AsyncAzureOpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    api_version=self.api_version,
                )
            elif self.api_type == "aws":
                self.client = BedrockClient()
            else:
                self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

            self.token_counter = TokenCounter(self.tokenizer)

    def count_tokens(self, text: str) -> int:
        """
        计算文本的 token 数量

        使用 tokenizer 将文本编码为 token，然后返回 token 的数量。
        这是计算文本 token 数的最基本方法。

        Args:
            text: 要计算的文本字符串

        Returns:
            int: token 数量，如果文本为空则返回 0

        使用示例：
            tokens = llm.count_tokens("Hello, world!")
        """
        if not text:
            return 0
        return len(self.tokenizer.encode(text))

    def count_message_tokens(self, messages: List[dict]) -> int:
        """
        计算消息列表的总 token 数量

        这是计算整个对话历史 token 数的便捷方法。
        会调用 TokenCounter 来计算，包括格式 token、消息基础 token、
        内容 token、工具调用 token 等。

        Args:
            messages: 消息列表，每个消息是字典格式

        Returns:
            int: 总 token 数量

        使用示例：
            messages = [{"role": "user", "content": "Hello"}]
            tokens = llm.count_message_tokens(messages)
        """
        return self.token_counter.count_message_tokens(messages)

    def update_token_count(self, input_tokens: int, completion_tokens: int = 0) -> None:
        """
        更新 token 计数

        累加输入和输出的 token 数量，用于跟踪整个会话的 token 使用情况。
        这对于控制 API 调用成本和避免超出限制非常重要。

        Args:
            input_tokens: 本次请求的输入 token 数量
            completion_tokens: 本次请求的输出 token 数量（默认为 0）

        使用示例：
            llm.update_token_count(input_tokens=100, completion_tokens=50)
        """
        # 累加输入 token
        self.total_input_tokens += input_tokens
        # 累加输出 token
        self.total_completion_tokens += completion_tokens
        # 记录日志，显示本次和累计的 token 使用情况
        logger.info(
            f"Token usage: Input={input_tokens}, Completion={completion_tokens}, "
            f"Cumulative Input={self.total_input_tokens}, Cumulative Completion={self.total_completion_tokens}, "
            f"Total={input_tokens + completion_tokens}, Cumulative Total={self.total_input_tokens + self.total_completion_tokens}"
        )

    def check_token_limit(self, input_tokens: int) -> bool:
        """
        检查是否会超出 token 限制

        在发送请求前检查，如果加上本次请求的 token 数后超过最大限制，
        则返回 False，表示不能继续。

        Args:
            input_tokens: 本次请求预计的输入 token 数量

        Returns:
            bool: True 表示未超出限制，可以继续；False 表示会超出限制

        使用示例：
            if not llm.check_token_limit(estimated_tokens):
                raise TokenLimitExceeded("Token limit exceeded")
        """
        if self.max_input_tokens is not None:
            # 检查累计 token + 本次 token 是否超过限制
            return (self.total_input_tokens + input_tokens) <= self.max_input_tokens
        # 如果没有设置最大限制，总是返回 True（不限制）
        return True

    def get_limit_error_message(self, input_tokens: int) -> str:
        """
        生成 token 限制超出的错误消息

        当检测到会超出 token 限制时，生成详细的错误消息，
        包含当前已使用的 token、本次需要的 token 和最大限制。

        Args:
            input_tokens: 本次请求预计的输入 token 数量

        Returns:
            str: 错误消息字符串

        使用示例：
            if not llm.check_token_limit(tokens):
                error_msg = llm.get_limit_error_message(tokens)
                raise TokenLimitExceeded(error_msg)
        """
        if (
            self.max_input_tokens is not None
            and (self.total_input_tokens + input_tokens) > self.max_input_tokens
        ):
            return f"请求可能超出输入 token 限制 (当前: {self.total_input_tokens}, 需要: {input_tokens}, 最大: {self.max_input_tokens})"

        return "Token 限制已超出"

    @staticmethod
    def format_messages(
        messages: List[Union[dict, Message]], supports_images: bool = False
    ) -> List[dict]:
        """
        将消息格式化为 LLM 可接受的格式（OpenAI 消息格式）

        这个方法会将 Message 对象或字典转换为标准的 OpenAI 消息格式。
        如果模型支持图片，还会处理 base64 编码的图片数据。

        Args:
            messages: 消息列表，可以是 Message 对象或字典
            supports_images: 标志，表示目标模型是否支持图片输入

        Returns:
            List[dict]: 格式化后的消息列表，符合 OpenAI 格式

        Raises:
            ValueError: 如果消息无效或缺少必需字段
            TypeError: 如果提供了不支持的消息类型

        使用示例：
            msgs = [
                Message.system_message("你是一个有用的助手"),
                {"role": "user", "content": "你好"},
                Message.user_message("你好吗？")
            ]
            formatted = LLM.format_messages(msgs)
        """
        formatted_messages = []

        for message in messages:
            # Convert Message objects to dictionaries
            if isinstance(message, Message):
                message = message.to_dict()

            if isinstance(message, dict):
                # If message is a dict, ensure it has required fields
                if "role" not in message:
                    raise ValueError("Message dict must contain 'role' field")

                # Process base64 images if present and model supports images
                if supports_images and message.get("base64_image"):
                    # Initialize or convert content to appropriate format
                    if not message.get("content"):
                        message["content"] = []
                    elif isinstance(message["content"], str):
                        message["content"] = [
                            {"type": "text", "text": message["content"]}
                        ]
                    elif isinstance(message["content"], list):
                        # Convert string items to proper text objects
                        message["content"] = [
                            (
                                {"type": "text", "text": item}
                                if isinstance(item, str)
                                else item
                            )
                            for item in message["content"]
                        ]

                    # Add the image to content
                    message["content"].append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{message['base64_image']}"
                            },
                        }
                    )

                    # Remove the base64_image field
                    del message["base64_image"]
                # If model doesn't support images but message has base64_image, handle gracefully
                elif not supports_images and message.get("base64_image"):
                    # Just remove the base64_image field and keep the text content
                    del message["base64_image"]

                if "content" in message or "tool_calls" in message:
                    formatted_messages.append(message)
                # else: do not include the message
            else:
                raise TypeError(f"Unsupported message type: {type(message)}")

        # Validate all messages have required fields
        for msg in formatted_messages:
            if msg["role"] not in ROLE_VALUES:
                raise ValueError(f"Invalid role: {msg['role']}")

        return formatted_messages

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(
            (OpenAIError, Exception, ValueError)
        ),  # Don't retry TokenLimitExceeded
    )
    async def ask(
        self,
        messages: List[Union[dict, Message]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        stream: bool = True,
        temperature: Optional[float] = None,
    ) -> str:
        """
        向 LLM 发送提示并获取回复

        这是最常用的方法，用于与 LLM 进行对话。
        支持流式和非流式响应，自动处理 token 计数和限制检查。

        Args:
            messages: 对话消息列表
            system_msgs: 可选的系统消息，会添加到消息列表的开头
            stream: 是否使用流式响应（默认 True，可以实时看到生成过程）
            temperature: 采样温度，控制回复的随机性（None 表示使用默认值）

        Returns:
            str: LLM 生成的回复文本

        Raises:
            TokenLimitExceeded: 如果超出 token 限制
            ValueError: 如果消息无效或回复为空
            OpenAIError: 如果 API 调用失败（重试后仍失败）
            Exception: 其他意外错误

        使用示例：
            messages = [Message.user_message("你好")]
            response = await llm.ask(messages, stream=True)
        """
        try:
            # Check if the model supports images
            supports_images = self.model in MULTIMODAL_MODELS

            # Format system and user messages with image support check
            if system_msgs:
                system_msgs = self.format_messages(system_msgs, supports_images)
                messages = system_msgs + self.format_messages(messages, supports_images)
            else:
                messages = self.format_messages(messages, supports_images)

            # Calculate input token count
            input_tokens = self.count_message_tokens(messages)

            # Check if token limits are exceeded
            if not self.check_token_limit(input_tokens):
                error_message = self.get_limit_error_message(input_tokens)
                # Raise a special exception that won't be retried
                raise TokenLimitExceeded(error_message)

            params = {
                "model": self.model,
                "messages": messages,
            }

            if self.model in REASONING_MODELS:
                params["max_completion_tokens"] = self.max_tokens
            else:
                params["max_tokens"] = self.max_tokens
                params["temperature"] = (
                    temperature if temperature is not None else self.temperature
                )

            if not stream:
                # Non-streaming request
                response = await self.client.chat.completions.create(
                    **params, stream=False
                )

                if not response.choices or not response.choices[0].message.content:
                    raise ValueError("Empty or invalid response from LLM")

                # Update token counts
                self.update_token_count(
                    response.usage.prompt_tokens, response.usage.completion_tokens
                )

                return response.choices[0].message.content

            # Streaming request, For streaming, update estimated token count before making the request
            self.update_token_count(input_tokens)

            response = await self.client.chat.completions.create(**params, stream=True)

            collected_messages = []
            completion_text = ""
            async for chunk in response:
                chunk_message = chunk.choices[0].delta.content or ""
                collected_messages.append(chunk_message)
                completion_text += chunk_message
                print(chunk_message, end="", flush=True)

            print()  # Newline after streaming
            full_response = "".join(collected_messages).strip()
            if not full_response:
                raise ValueError("Empty response from streaming LLM")

            # estimate completion tokens for streaming response
            completion_tokens = self.count_tokens(completion_text)
            logger.info(
                f"Estimated completion tokens for streaming response: {completion_tokens}"
            )
            self.total_completion_tokens += completion_tokens

            return full_response

        except TokenLimitExceeded:
            # Re-raise token limit errors without logging
            raise
        except ValueError:
            logger.exception(f"Validation error")
            raise
        except OpenAIError as oe:
            logger.exception(f"OpenAI API error")
            if isinstance(oe, AuthenticationError):
                logger.error("Authentication failed. Check API key.")
            elif isinstance(oe, RateLimitError):
                logger.error("Rate limit exceeded. Consider increasing retry attempts.")
            elif isinstance(oe, APIError):
                logger.error(f"API error: {oe}")
            raise
        except Exception:
            logger.exception(f"Unexpected error in ask")
            raise

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(
            (OpenAIError, Exception, ValueError)
        ),  # Don't retry TokenLimitExceeded
    )
    async def ask_with_images(
        self,
        messages: List[Union[dict, Message]],
        images: List[Union[str, dict]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
    ) -> str:
        """
        向 LLM 发送带图片的提示并获取回复

        这个方法专门用于多模态输入，支持同时发送文本和图片。
        只有支持多模态的模型（如 GPT-4 Vision、Claude 3）才能使用。

        Args:
            messages: 对话消息列表
            images: 图片列表，可以是图片 URL 字符串或图片数据字典
            system_msgs: 可选的系统消息，会添加到消息列表的开头
            stream: 是否使用流式响应（默认 False）
            temperature: 采样温度，控制回复的随机性

        Returns:
            str: LLM 生成的回复文本

        Raises:
            TokenLimitExceeded: 如果超出 token 限制
            ValueError: 如果消息无效、回复为空或模型不支持图片
            OpenAIError: 如果 API 调用失败（重试后仍失败）
            Exception: 其他意外错误

        使用示例：
            messages = [Message.user_message("这是什么？")]
            images = ["https://example.com/image.jpg"]
            response = await llm.ask_with_images(messages, images)
        """
        try:
            # For ask_with_images, we always set supports_images to True because
            # this method should only be called with models that support images
            if self.model not in MULTIMODAL_MODELS:
                raise ValueError(
                    f"Model {self.model} does not support images. Use a model from {MULTIMODAL_MODELS}"
                )

            # Format messages with image support
            formatted_messages = self.format_messages(messages, supports_images=True)

            # Ensure the last message is from the user to attach images
            if not formatted_messages or formatted_messages[-1]["role"] != "user":
                raise ValueError(
                    "The last message must be from the user to attach images"
                )

            # Process the last user message to include images
            last_message = formatted_messages[-1]

            # Convert content to multimodal format if needed
            content = last_message["content"]
            multimodal_content = (
                [{"type": "text", "text": content}]
                if isinstance(content, str)
                else content if isinstance(content, list) else []
            )

            # Add images to content
            for image in images:
                if isinstance(image, str):
                    multimodal_content.append(
                        {"type": "image_url", "image_url": {"url": image}}
                    )
                elif isinstance(image, dict) and "url" in image:
                    multimodal_content.append({"type": "image_url", "image_url": image})
                elif isinstance(image, dict) and "image_url" in image:
                    multimodal_content.append(image)
                else:
                    raise ValueError(f"Unsupported image format: {image}")

            # Update the message with multimodal content
            last_message["content"] = multimodal_content

            # Add system messages if provided
            if system_msgs:
                all_messages = (
                    self.format_messages(system_msgs, supports_images=True)
                    + formatted_messages
                )
            else:
                all_messages = formatted_messages

            # Calculate tokens and check limits
            input_tokens = self.count_message_tokens(all_messages)
            if not self.check_token_limit(input_tokens):
                raise TokenLimitExceeded(self.get_limit_error_message(input_tokens))

            # Set up API parameters
            params = {
                "model": self.model,
                "messages": all_messages,
                "stream": stream,
            }

            # Add model-specific parameters
            if self.model in REASONING_MODELS:
                params["max_completion_tokens"] = self.max_tokens
            else:
                params["max_tokens"] = self.max_tokens
                params["temperature"] = (
                    temperature if temperature is not None else self.temperature
                )

            # Handle non-streaming request
            if not stream:
                response = await self.client.chat.completions.create(**params)

                if not response.choices or not response.choices[0].message.content:
                    raise ValueError("Empty or invalid response from LLM")

                self.update_token_count(response.usage.prompt_tokens)
                return response.choices[0].message.content

            # Handle streaming request
            self.update_token_count(input_tokens)
            response = await self.client.chat.completions.create(**params)

            collected_messages = []
            async for chunk in response:
                chunk_message = chunk.choices[0].delta.content or ""
                collected_messages.append(chunk_message)
                print(chunk_message, end="", flush=True)

            print()  # Newline after streaming
            full_response = "".join(collected_messages).strip()

            if not full_response:
                raise ValueError("Empty response from streaming LLM")

            return full_response

        except TokenLimitExceeded:
            raise
        except ValueError as ve:
            logger.error(f"Validation error in ask_with_images: {ve}")
            raise
        except OpenAIError as oe:
            logger.error(f"OpenAI API error: {oe}")
            if isinstance(oe, AuthenticationError):
                logger.error("Authentication failed. Check API key.")
            elif isinstance(oe, RateLimitError):
                logger.error("Rate limit exceeded. Consider increasing retry attempts.")
            elif isinstance(oe, APIError):
                logger.error(f"API error: {oe}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ask_with_images: {e}")
            raise

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(
            (OpenAIError, Exception, ValueError)
        ),  # Don't retry TokenLimitExceeded
    )
    async def ask_tool(
        self,
        messages: List[Union[dict, Message]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        timeout: int = 300,
        tools: Optional[List[dict]] = None,
        tool_choice: TOOL_CHOICE_TYPE = ToolChoice.AUTO,  # type: ignore
        temperature: Optional[float] = None,
        **kwargs,
    ) -> ChatCompletionMessage | None:
        """
        使用工具/函数调用功能向 LLM 发送请求并获取回复

        这个方法支持 Function Calling（函数调用），允许 LLM 选择并调用工具。
        这是实现智能体工具调用的核心方法。

        Args:
            messages: 对话消息列表
            system_msgs: 可选的系统消息，会添加到消息列表的开头
            timeout: 请求超时时间（秒），默认 300 秒
            tools: 可用工具列表，每个工具是字典格式（通过 tool.to_param() 生成）
            tool_choice: 工具选择策略
                - AUTO: 自动选择是否使用工具（默认）
                - REQUIRED: 必须使用工具
                - NONE: 不使用工具
            temperature: 采样温度，控制回复的随机性
            **kwargs: 其他额外的完成参数

        Returns:
            ChatCompletionMessage | None: LLM 的回复消息，包含文本内容和工具调用。
                如果响应无效则返回 None

        Raises:
            TokenLimitExceeded: 如果超出 token 限制
            ValueError: 如果工具、tool_choice 或消息无效
            OpenAIError: 如果 API 调用失败（重试后仍失败）
            Exception: 其他意外错误

        使用示例：
            messages = [Message.user_message("帮我执行某个任务")]
            tools = [tool.to_param() for tool in available_tools]
            response = await llm.ask_tool(messages, tools=tools, tool_choice=ToolChoice.AUTO)
            if response.tool_calls:
                # 处理工具调用
                for tool_call in response.tool_calls:
                    ...
        """
        try:
            # Validate tool_choice
            if tool_choice not in TOOL_CHOICE_VALUES:
                raise ValueError(f"Invalid tool_choice: {tool_choice}")

            # Check if the model supports images
            supports_images = self.model in MULTIMODAL_MODELS

            # Format messages
            if system_msgs:
                system_msgs = self.format_messages(system_msgs, supports_images)
                messages = system_msgs + self.format_messages(messages, supports_images)
            else:
                messages = self.format_messages(messages, supports_images)

            # Calculate input token count
            input_tokens = self.count_message_tokens(messages)

            # If there are tools, calculate token count for tool descriptions
            tools_tokens = 0
            if tools:
                for tool in tools:
                    tools_tokens += self.count_tokens(str(tool))

            input_tokens += tools_tokens

            # Check if token limits are exceeded
            if not self.check_token_limit(input_tokens):
                error_message = self.get_limit_error_message(input_tokens)
                # Raise a special exception that won't be retried
                raise TokenLimitExceeded(error_message)

            # Validate tools if provided
            if tools:
                for tool in tools:
                    if not isinstance(tool, dict) or "type" not in tool:
                        raise ValueError("Each tool must be a dict with 'type' field")

            # Set up the completion request
            params = {
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "tool_choice": tool_choice,
                "timeout": timeout,
                **kwargs,
            }

            if self.model in REASONING_MODELS:
                params["max_completion_tokens"] = self.max_tokens
            else:
                params["max_tokens"] = self.max_tokens
                params["temperature"] = (
                    temperature if temperature is not None else self.temperature
                )

            params["stream"] = False  # Always use non-streaming for tool requests
            response: ChatCompletion = await self.client.chat.completions.create(
                **params
            )

            # Check if response is valid
            if not response.choices or not response.choices[0].message:
                print(response)
                # raise ValueError("Invalid or empty response from LLM")
                return None

            # Update token counts
            self.update_token_count(
                response.usage.prompt_tokens, response.usage.completion_tokens
            )

            return response.choices[0].message

        except TokenLimitExceeded:
            # Re-raise token limit errors without logging
            raise
        except ValueError as ve:
            logger.error(f"Validation error in ask_tool: {ve}")
            raise
        except OpenAIError as oe:
            logger.error(f"OpenAI API error: {oe}")
            if isinstance(oe, AuthenticationError):
                logger.error("Authentication failed. Check API key.")
            elif isinstance(oe, RateLimitError):
                logger.error("Rate limit exceeded. Consider increasing retry attempts.")
            elif isinstance(oe, APIError):
                logger.error(f"API error: {oe}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ask_tool: {e}")
            raise
