# -*- coding: utf-8 -*-
"""
Skill Middleware - 使用 LangChain 1.0 正确的 API 实现运行时动态工具过滤

核心功能：在每次模型调用前，根据 skills_loaded 状态动态过滤工具列表
这是 Claude Skills 的核心 - 让模型只看到相关的 5 个工具，而不是全部 50 个
"""

import logging
from typing import Optional, List, Callable, Any

from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
)
from langchain_core.tools import BaseTool

from core.registry import SkillRegistry

logger = logging.getLogger(__name__)


class SkillMiddleware(AgentMiddleware):
    """
    Skill 中间件 - 实现动态工具过滤

    工作流程：
    1. 拦截每次模型调用请求 (wrap_model_call)
    2. 从 request.state 中读取 skills_loaded 列表
    3. 调用 Registry 获取对应的工具（Loaders + 已加载 Skills 的工具）
    4. 使用 request.override(tools=relevant_tools) 替换工具列表
    5. 传递给下一个 handler

    这样模型只会看到相关的工具，大大减少 token 使用和错误率
    """

    def __init__(
        self,
        skill_registry: SkillRegistry,
        verbose: bool = False,
        filter_fn: Optional[Callable[[Any], bool]] = None
    ):
        """
        Args:
            skill_registry: Skill 注册中心
            verbose: 是否打印详细日志
            filter_fn: 可选的额外过滤函数（用于权限控制等）
        """
        super().__init__()
        self.registry = skill_registry
        self.verbose = verbose
        self.filter_fn = filter_fn

    def _get_filtered_tools(self, skills_loaded: List[str]) -> List[BaseTool]:
        """
        获取过滤后的工具列表

        Args:
            skills_loaded: 已加载的 Skill 名称列表

        Returns:
            过滤后的工具列表（Loaders + 已加载 Skills 的工具）
        """
        # 从 Registry 获取工具
        tools = self.registry.get_tools_for_skills(skills_loaded)

        return tools

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
    ) -> ModelResponse:
        """
        【核心方法】拦截模型调用，动态过滤工具

        Args:
            request: 模型调用请求（包含 state, tools 等）
            handler: 下一个处理器

        Returns:
            模型响应
        """
        # 从状态中获取已加载的 Skills
        # AgentState 是 TypedDict (基于 dict)，使用字典方式访问
        skills_loaded = []
        if hasattr(request, 'state') and request.state is not None:
            # 优先使用字典访问方式
            if isinstance(request.state, dict):
                skills_loaded = request.state.get("skills_loaded", [])
            else:
                skills_loaded = getattr(request.state, "skills_loaded", [])

        # 获取过滤后的工具
        relevant_tools = self._get_filtered_tools(skills_loaded)

        # 记录日志
        if self.verbose:
            logger.info(f"[SkillMiddleware] Skills loaded: {skills_loaded}")
            logger.info(
                f"[SkillMiddleware] Filtered tools ({len(relevant_tools)}): "
                f"{[t.name for t in relevant_tools]}"
            )

        # 【关键】使用 request.override() 替换工具列表
        filtered_request = request.override(tools=relevant_tools)

        # 调用下一个 handler
        return handler(filtered_request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
    ) -> ModelResponse:
        """
        异步版本 - 拦截模型调用

        LangChain 可能使用异步调用，所以需要同时实现
        """
        # 从状态中获取已加载的 Skills (字典方式访问)
        skills_loaded = []
        if hasattr(request, 'state') and request.state is not None:
            if isinstance(request.state, dict):
                skills_loaded = request.state.get("skills_loaded", [])
            else:
                skills_loaded = getattr(request.state, "skills_loaded", [])

        # 获取过滤后的工具
        relevant_tools = self._get_filtered_tools(skills_loaded)

        # 记录日志
        if self.verbose:
            logger.info(f"[SkillMiddleware] (async) Skills loaded: {skills_loaded}")
            logger.info(
                f"[SkillMiddleware] (async) Filtered tools ({len(relevant_tools)}): "
                f"{[t.name for t in relevant_tools]}"
            )

        # 【关键】使用 request.override() 替换工具列表
        filtered_request = request.override(tools=relevant_tools)

        # 调用下一个 handler
        return await handler(filtered_request)
