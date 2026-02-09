"""
系统配置类
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
import os
import yaml


@dataclass
class SkillSystemConfig:
    """
    Skill System 配置

    Attributes:
        skills_dir: Skills 目录路径
        state_mode: 状态管理模式 (replace/accumulate/fifo)
        verbose: 是否启用详细日志
        default_model: 默认 LLM 模型
        middleware_enabled: 是否启用中间件
        auto_discover: 是否自动发现 Skills
    """
    # 基础路径配置
    skills_dir: Path = Path("./skills")

    # 状态管理配置
    state_mode: str = "replace"  # replace, accumulate, fifo

    # 日志配置
    verbose: bool = False
    log_level: str = "INFO"

    # Agent 配置
    default_model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    # 中间件配置
    middleware_enabled: bool = True

    # Skill 发现配置
    auto_discover: bool = True
    skill_module_name: str = "skill"  # 默认是skills目录下的skill.py

    # 自定义配置
    custom_config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理"""
        # 确保路径是 Path 对象
        if not isinstance(self.skills_dir, Path):
            self.skills_dir = Path(self.skills_dir)

        # 验证状态模式
        valid_modes = ["replace", "accumulate", "fifo"]
        if self.state_mode not in valid_modes:
            raise ValueError(
                f"Invalid state_mode: {self.state_mode}. "
                f"Must be one of {valid_modes}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """将相关配置转换为字典"""
        return {
            "skills_dir": str(self.skills_dir),
            "state_mode": self.state_mode,
            "verbose": self.verbose,
            "log_level": self.log_level,
            "default_model": self.default_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "middleware_enabled": self.middleware_enabled,
            "auto_discover": self.auto_discover,
            "skill_module_name": self.skill_module_name,
            "custom_config": self.custom_config,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "SkillSystemConfig":
        """从字典创建配置"""
        return cls(**config_dict)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "SkillSystemConfig":
        """从 YAML 文件加载配置"""
        with open(yaml_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    def save_to_yaml(self, yaml_path: Path) -> None:
        """保存配置到 YAML 文件"""
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)


def load_config(
    config_path: Optional[Path] = None,
    env_prefix: str = "SKILL_SYSTEM_"
) -> SkillSystemConfig:
    """
    加载配置（优先级：文件 > 环境变量 > 默认值）

    Args:
        config_path: 配置文件路径（YAML）
        env_prefix: 环境变量前缀

    Returns:
        SkillSystemConfig 实例
    """
    config_dict = {}

    # 1. 从文件加载
    if config_path and config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f) or {}

    # 2. 从环境变量覆盖
    env_mappings = {
        f"{env_prefix}SKILLS_DIR": "skills_dir",
        f"{env_prefix}STATE_MODE": "state_mode",
        f"{env_prefix}VERBOSE": "verbose",
        f"{env_prefix}LOG_LEVEL": "log_level",
        f"{env_prefix}DEFAULT_MODEL": "default_model",
        f"{env_prefix}TEMPERATURE": "temperature",
        f"{env_prefix}MIDDLEWARE_ENABLED": "middleware_enabled",
        f"{env_prefix}AUTO_DISCOVER": "auto_discover",
    }

    for env_key, config_key in env_mappings.items():
        if env_key in os.environ:
            value = os.environ[env_key]
            # 类型转换
            if config_key in ["temperature"]:
                value = float(value)
            elif config_key in ["verbose", "middleware_enabled", "auto_discover"]:
                value = value.lower() in ["true", "1", "yes"]
            config_dict[config_key] = value

    # 3. 创建配置对象
    return SkillSystemConfig.from_dict(config_dict)


# 默认配置实例
DEFAULT_CONFIG = SkillSystemConfig()
