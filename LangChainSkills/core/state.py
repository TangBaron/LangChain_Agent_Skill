"""
状态管理 - 定义三种Skills的模式
"""

from typing import List, Annotated
from langgraph.graph import MessagesState


def skill_list_reducer(current: List[str], new: List[str]) -> List[str]:
    """
    Skill 列表 Reducer

    策略选项：
    1. 替换模式（默认）：用新列表替换旧列表
    2. 累积模式：合并新旧列表（去重）
    3. FIFO 模式：限制最多 K 个 Skill，超出则移除最早的

    当前实现：替换模式
    """
    return new


def skill_list_accumulator(current: List[str], new: List[str]) -> List[str]:
    """
    累积模式：合并已加载的 Skills

    使用方式：
    class SkillState(MessagesState):
        skills_loaded: Annotated[List[str], skill_list_accumulator] = []
    """
    if not current:
        return new
    # 合并并去重，保持顺序
    combined = current + [s for s in new if s not in current]
    return combined


def skill_list_fifo(max_skills: int = 3):
    """
    FIFO 模式工厂：限制同时加载的 Skill 数量

    Args:
        max_skills: 最多同时加载的 Skill 数量

    使用方式：
    class SkillState(MessagesState):
        skills_loaded: Annotated[List[str], skill_list_fifo(3)] = []
    """
    def reducer(current: List[str], new: List[str]) -> List[str]:
        if not current:
            return new[:max_skills]
        # 累积并限制数量
        combined = current + [s for s in new if s not in current]
        return combined[-max_skills:]  # 保留最新的 N 个
    return reducer


class SkillState(MessagesState):
    """
    扩展的 Agent 状态，包含已加载的 Skills

    Attributes:
        skills_loaded: 当前会话中已加载的 Skill 名称列表
        skill_context: 可选的 Skill 上下文数据（用于传递额外信息）
    """
    skills_loaded: Annotated[List[str], skill_list_reducer] = []
    # 可选：添加 Skill 上下文存储
    # skill_context: Dict[str, Any] = {}


# 示例：使用累积模式
class SkillStateAccumulative(MessagesState):
    """累积模式：Skill 一旦加载就保持在整个会话中"""
    skills_loaded: Annotated[List[str], skill_list_accumulator] = []


# 示例：使用 FIFO 模式（最多 3 个 Skill）
class SkillStateFIFO(MessagesState):
    """FIFO 模式：最多同时加载 3 个 Skill"""
    skills_loaded: Annotated[List[str], skill_list_fifo(3)] = []
