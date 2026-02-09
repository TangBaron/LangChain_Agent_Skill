# -*- coding: utf-8 -*-
"""
自定义 DeepSeek Reasoner ChatModel for LangChain 1.0
通过继承 BaseChatModel 实现对 reasoning_content 的完整支持

集成到 Skill System 中使用
"""

import os
import json
from typing import Any, List, Optional, Dict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.tools import BaseTool
from pydantic import Field

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class DeepSeekReasonerChatModel(BaseChatModel):
    """
    自定义 DeepSeek Reasoner 模型，支持 reasoning_content

    关键特性：
    1. 在工具调用循环中保留 reasoning_content
    2. 将 reasoning_content 存储在 AIMessage.additional_kwargs 中
    3. 发送请求时从 additional_kwargs 恢复 reasoning_content

    使用示例:
    ```python
    from skill_system.models import DeepSeekReasonerChatModel
    from skill_system import create_skill_agent

    model = DeepSeekReasonerChatModel(
        api_key="your-api-key",
        model_name="deepseek-reasoner"
    )

    agent = create_skill_agent(model=model)
    ```
    """

    api_key: str = Field(default=None)
    base_url: str = Field(default="https://api.deepseek.com")
    model_name: str = Field(default="deepseek-reasoner")
    temperature: float = Field(default=0.7)
    timeout: float = Field(default=60.0)
    bound_tools: Optional[List[Dict]] = Field(default=None)

    # OpenAI 客户端（不序列化）
    _client: Optional[Any] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if OpenAI is None:
            raise ImportError(
                "需要安装 openai 库。请运行: pip install openai"
            )

        # 初始化 OpenAI 客户端
        if not self.api_key:
            self.api_key = os.environ.get("DEEPSEEK_API_KEY")

        if not self.api_key:
            raise ValueError(
                "需要提供 api_key 或设置 DEEPSEEK_API_KEY 环境变量"
            )

        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )

    @property
    def _llm_type(self) -> str:
        return "deepseek_reasoner"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "temperature": self.temperature,
        }

    def _convert_messages_to_openai_format(
        self, messages: List[BaseMessage]
    ) -> List[Dict]:
        """
        将 LangChain 消息转换为 OpenAI 格式

        关键：从 additional_kwargs 中恢复 reasoning_content
        """
        openai_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                openai_messages.append({
                    "role": "user",
                    "content": msg.content
                })

            elif isinstance(msg, SystemMessage):
                openai_messages.append({
                    "role": "system",
                    "content": msg.content
                })

            elif isinstance(msg, AIMessage):
                msg_dict = {
                    "role": "assistant",
                    "content": msg.content or "",
                }

                # 处理 tool_calls
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tool_calls = []
                    for tc in msg.tool_calls:
                        # LangChain 1.0 的 tool_call 格式
                        tool_calls.append({
                            "id": tc.get("id") if isinstance(tc, dict) else tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.get("name") if isinstance(tc, dict) else tc.name,
                                "arguments": json.dumps(
                                    tc.get("args") if isinstance(tc, dict) else tc.args
                                )
                            }
                        })
                    msg_dict["tool_calls"] = tool_calls

                # 【关键】恢复 reasoning_content
                if hasattr(msg, 'additional_kwargs') and msg.additional_kwargs:
                    if 'reasoning_content' in msg.additional_kwargs:
                        msg_dict["reasoning_content"] = msg.additional_kwargs['reasoning_content']

                openai_messages.append(msg_dict)

            elif isinstance(msg, ToolMessage):
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "name": msg.name if hasattr(msg, 'name') else "",
                    "content": msg.content
                })

        return openai_messages

    def _create_ai_message_from_response(self, response) -> AIMessage:
        """
        从 OpenAI 响应创建 AIMessage

        关键：将 reasoning_content 保存到 additional_kwargs
        """
        message = response.choices[0].message

        # 处理 tool_calls
        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append({
                    "name": tc.function.name,
                    "args": json.loads(tc.function.arguments),
                    "id": tc.id,
                })

        # 【关键】保存 reasoning_content 到 additional_kwargs
        additional_kwargs = {}
        if hasattr(message, 'reasoning_content') and message.reasoning_content:
            additional_kwargs['reasoning_content'] = message.reasoning_content

        # 构建 AIMessage
        ai_message_kwargs = {
            "content": message.content or "",
            "additional_kwargs": additional_kwargs
        }

        # 只有在有 tool_calls 时才添加
        if tool_calls:
            ai_message_kwargs["tool_calls"] = tool_calls

        return AIMessage(**ai_message_kwargs)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        生成响应的核心方法
        """
        # 转换消息
        openai_messages = self._convert_messages_to_openai_format(messages)

        # 准备请求参数
        request_params = {
            "model": self.model_name,
            "messages": openai_messages,
            "temperature": self.temperature,
        }

        # 添加工具（如果有绑定）
        if self.bound_tools:
            request_params["tools"] = self.bound_tools

        # 添加停止词
        if stop:
            request_params["stop"] = stop

        # 调用 API
        response = self._client.chat.completions.create(**request_params)

        # 创建 AIMessage
        ai_message = self._create_ai_message_from_response(response)

        # 返回 ChatResult
        generation = ChatGeneration(message=ai_message)
        return ChatResult(generations=[generation])

    def bind_tools(
        self,
        tools: List[BaseTool],
        **kwargs: Any
    ) -> "DeepSeekReasonerChatModel":
        """
        绑定工具到模型
        """
        # 转换 LangChain 工具为 OpenAI 格式
        openai_tools = []
        for tool in tools:
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                }
            }

            # 添加参数 schema
            if hasattr(tool, 'args_schema') and tool.args_schema:
                tool_def["function"]["parameters"] = tool.args_schema.model_json_schema()
            else:
                tool_def["function"]["parameters"] = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }

            openai_tools.append(tool_def)

        # 创建新实例，绑定工具
        return self.__class__(
            api_key=self.api_key,
            base_url=self.base_url,
            model_name=self.model_name,
            temperature=self.temperature,
            timeout=self.timeout,
            bound_tools=openai_tools,
            **kwargs
        )


# 方便导入
__all__ = ["DeepSeekReasonerChatModel"]
