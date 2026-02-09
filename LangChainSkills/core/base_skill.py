"""
Skill 基类和元数据定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from pathlib import Path


@dataclass
class SkillMetadata:
    """
    Skill 元数据

    Attributes:
        name: Skill 唯一标识符
        description: Skill 功能描述
        version: 版本号
        tags: 标签列表（用于搜索和分类）
        dependencies: 依赖的其他 Skill 或库
        required_permissions: 需要的权限列表
        author: 作者
        enabled: 是否启用
    """
    name: str
    description: str
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    required_permissions: List[str] = field(default_factory=list)
    author: Optional[str] = None
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "required_permissions": self.required_permissions,
            "author": self.author,
            "enabled": self.enabled,
        }


class BaseSkill(ABC):
    """
    Skill 基类

    每个具体的 Skill 都应继承此类并实现：
    1. metadata 属性：返回 SkillMetadata
    2. get_tools() 方法：返回该 Skill 的工具列表
    3. get_loader_tool() 方法：返回用于加载该 Skill 的 Loader Tool
    4. get_instructions() 方法：返回 Skill 激活后的使用说明
    """

    def __init__(self, skill_dir: Optional[Path] = None):
        """
        Args:
            skill_dir: Skill 所在目录（用于读取配置文件等）
        """
        self.skill_dir = skill_dir
        self._metadata: Optional[SkillMetadata] = None

    @property
    @abstractmethod
    def metadata(self) -> SkillMetadata:
        """返回 Skill 元数据"""
        pass

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """
        返回该 Skill 包含的所有工具

        这些工具只有在 Skill 被激活后才对 Agent 可见
        """
        pass

    @abstractmethod
    def get_loader_tool(self) -> BaseTool:
        """
        返回用于加载该 Skill 的 Loader Tool

        Loader Tool 始终对 Agent 可见，用于激活 Skill
        """
        pass

    def get_instructions(self) -> str:
        """
        返回 Skill 激活后的使用说明

        当 Loader Tool 被调用时，会返回这段说明给 Agent
        默认实现从 instructions.md 文件读取
        """
        if self.skill_dir:
            instructions_file = self.skill_dir / "instructions.md"
            if instructions_file.exists():
                return instructions_file.read_text(encoding="utf-8")

        # 默认生成基础说明
        tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.get_tools()])
        return f"""
            {self.metadata.description}

            Available tools:
            {tools_desc}

            Use these tools to accomplish tasks related to: {', '.join(self.metadata.tags)}
        """

    def validate(self) -> bool:
        """
        验证 Skill 配置是否正确

        可以在子类中重写以添加自定义验证逻辑
        """
        if not self.metadata.name:
            raise ValueError("Skill name cannot be empty")
        if not self.metadata.description:
            raise ValueError("Skill description cannot be empty")
        if not self.get_tools():
            raise ValueError("Skill must provide at least one tool")
        if not self.get_loader_tool():
            raise ValueError("Skill must provide a loader tool")
        return True

    def __repr__(self) -> str:
        return f"<Skill: {self.metadata.name} v{self.metadata.version}>"
