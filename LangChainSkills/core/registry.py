"""
Skill Registry - 管理所有 Skills 的注册、查找和过滤
"""

from typing import Dict, List, Optional, Callable
from pathlib import Path
import importlib.util
import logging

from langchain_core.tools import BaseTool

from .base_skill import BaseSkill, SkillMetadata
from .exceptions import SkillNotFoundError, SkillLoadError

logger = logging.getLogger(__name__)


class SkillRegistry:
    """
    Skill 注册中心

    负责：
    1. 发现和加载 Skills（从目录或手动注册）
    2. 管理 Skill 的生命周期
    3. 根据条件过滤 Skills（权限、可见性等）
    4. 提供工具查询接口
    """

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._metadata_cache: Dict[str, SkillMetadata] = {}

    def register(self, skill: BaseSkill) -> None:
        """
        注册一个 Skill

        Args:
            skill: BaseSkill 实例

        Raises:
            ValueError: 如果 Skill 验证失败或名称冲突
        """
        skill.validate()
        name = skill.metadata.name

        if name in self._skills:
            logger.warning(f"Skill '{name}' already registered, overwriting")

        self._skills[name] = skill
        self._metadata_cache[name] = skill.metadata
        logger.info(f"Registered skill: {name} v{skill.metadata.version}")

    def unregister(self, skill_name: str) -> None:
        """取消注册一个 Skill"""
        if skill_name in self._skills:
            del self._skills[skill_name]
            del self._metadata_cache[skill_name]
            logger.info(f"Unregistered skill: {skill_name}")

    def get(self, skill_name: str) -> BaseSkill:
        """
        获取指定名称的 Skill

        Args:
            skill_name: Skill 名称

        Returns:
            BaseSkill 实例

        Raises:
            SkillNotFoundError: 如果 Skill 不存在
        """
        if skill_name not in self._skills:
            raise SkillNotFoundError(skill_name)
        return self._skills[skill_name]

    def get_metadata(self, skill_name: str) -> SkillMetadata:
        """获取 Skill 元数据"""
        if skill_name not in self._metadata_cache:
            raise SkillNotFoundError(skill_name)
        return self._metadata_cache[skill_name]

    def list_skills(
        self,
        filter_fn: Optional[Callable[[SkillMetadata], bool]] = None
    ) -> List[str]:
        """
        列出所有 Skill 名称

        Args:
            filter_fn: 可选的过滤函数，接收 SkillMetadata 返回 bool

        Returns:
            Skill 名称列表
        """
        if filter_fn is None:
            return list(self._skills.keys())

        return [
            name for name, meta in self._metadata_cache.items()
            if filter_fn(meta)
        ]

    def get_all_loader_tools(
        self,
        filter_fn: Optional[Callable[[SkillMetadata], bool]] = None
    ) -> List[BaseTool]:
        """
        获取所有 Skill 的 Loader Tools

        这些工具应该始终对 Agent 可见，用于激活 Skills

        Args:
            filter_fn: 可选的过滤函数（基于权限、可见性等）

        Returns:
            Loader Tools 列表
        """
        skill_names = self.list_skills(filter_fn)
        loaders = []

        for name in skill_names:
            skill = self._skills[name]
            if skill.metadata.enabled:
                loaders.append(skill.get_loader_tool())

        return loaders

    def get_all_tools(
        self,
        filter_fn: Optional[Callable[[SkillMetadata], bool]] = None
    ) -> List[BaseTool]:
        """
        获取所有工具（包括 Loaders 和实际工具）

        用于注册到 Agent（满足 LangChain 的预注册要求）

        Args:
            filter_fn: 可选的过滤函数

        Returns:
            所有工具的列表
        """
        skill_names = self.list_skills(filter_fn)
        all_tools = []

        for name in skill_names:
            skill = self._skills[name]
            if skill.metadata.enabled:
                # 添加 Loader
                all_tools.append(skill.get_loader_tool())
                # 添加实际工具
                all_tools.extend(skill.get_tools())

        return all_tools

    def get_tools_for_skills(self, skill_names: List[str]) -> List[BaseTool]:
        """
        根据已加载的 Skill 名称获取对应的工具

        用于中间件动态过滤

        Args:
            skill_names: 已加载的 Skill 名称列表

        Returns:
            所有 Loader Tools + 已加载 Skills 的工具
        """
        # 始终包含所有 Loader Tools
        tools = self.get_all_loader_tools()

        # 添加已加载 Skills 的工具
        for name in skill_names:
            if name in self._skills:
                skill = self._skills[name]
                if skill.metadata.enabled:
                    tools.extend(skill.get_tools())

        return tools

    def discover_and_load(
        self,
        skills_dir: Path,
        module_name: str = "skill"
    ) -> int:
        """
        从目录自动发现并加载 Skills

        目录结构示例：
        skills_dir/
            pdf_processing/
                skill.py       <- 必须定义 create_skill() 函数
                instructions.md
            data_analysis/
                skill.py
                instructions.md

        Args:
            skills_dir: Skills 根目录
            module_name: Skill 模块文件名（默认 "skill.py"）

        Returns:
            成功加载的 Skill 数量
        """
        if not skills_dir.exists():
            logger.warning(f"Skills directory not found: {skills_dir}")
            return 0

        loaded_count = 0

        for skill_path in skills_dir.iterdir():
            if not skill_path.is_dir():
                continue

            skill_file = skill_path / f"{module_name}.py"
            if not skill_file.exists():
                continue

            try:
                skill = self._load_skill_from_file(skill_file, skill_path)
                self.register(skill)
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load skill from {skill_path}: {e}")
                continue

        logger.info(f"Loaded {loaded_count} skills from {skills_dir}")
        return loaded_count

    def _load_skill_from_file(
        self,
        skill_file: Path,
        skill_dir: Path
    ) -> BaseSkill:
        """
        从文件加载 Skill

        期望文件中定义 create_skill() 函数返回 BaseSkill 实例
        """
        spec = importlib.util.spec_from_file_location(
            f"skill_{skill_dir.name}",
            skill_file
        )
        if spec is None or spec.loader is None:
            raise SkillLoadError(skill_dir.name, "Failed to load module spec")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "create_skill"):
            raise SkillLoadError(
                skill_dir.name,
                "Module must define create_skill() function"
            )

        skill = module.create_skill(skill_dir)

        if not isinstance(skill, BaseSkill):
            raise SkillLoadError(
                skill_dir.name,
                "create_skill() must return BaseSkill instance"
            )

        return skill

    def search(
        self,
        query: str = "",
        tags: Optional[List[str]] = None,
    ) -> List[SkillMetadata]:
        """
        搜索 Skills

        Args:
            query: 搜索关键词（匹配名称或描述）
            tags: 标签过滤

        Returns:
            匹配的 SkillMetadata 列表
        """
        results = []

        for meta in self._metadata_cache.values():
            # 查询过滤
            if query:
                if query.lower() not in meta.name.lower() and \
                   query.lower() not in meta.description.lower():
                    continue

            # 标签过滤
            if tags:
                if not any(tag in meta.tags for tag in tags):
                    continue

            results.append(meta)

        return results

    def __len__(self) -> int:
        """返回已注册的 Skill 数量"""
        return len(self._skills.keys())

    def __contains__(self, skill_name: str) -> bool:
        """检查 Skill 是否已注册"""
        return skill_name in self._skills

    def __repr__(self) -> str:
        return f"<SkillRegistry: {len(self)} skills>"
