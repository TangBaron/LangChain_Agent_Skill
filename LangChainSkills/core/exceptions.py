"""
自定义异常类
"""

class SkillError(Exception):
    """Skill 系统基础异常"""
    pass


class SkillNotFoundError(SkillError):
    """Skill 未找到异常"""

    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        super().__init__(f"Skill '{skill_name}' not found in registry")


class SkillLoadError(SkillError):
    """Skill 加载失败异常"""

    def __init__(self, skill_name: str, reason: str):
        self.skill_name = skill_name
        self.reason = reason
        super().__init__(f"Failed to load skill '{skill_name}': {reason}")


class SkillPermissionError(SkillError):
    """Skill 权限不足异常"""

    def __init__(self, skill_name: str, required_permission: str):
        self.skill_name = skill_name
        self.required_permission = required_permission
        super().__init__(
            f"Permission denied for skill '{skill_name}': "
            f"requires '{required_permission}'"
        )
