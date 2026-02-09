import os
from typing import List

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware

from core import SkillRegistry, SkillState, SkillMetadata
from core.state import SkillStateAccumulative, SkillStateFIFO
from middleware import SkillMiddleware
from config import SkillSystemConfig, load_config
from pathlib import Path
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from models import DeepSeekReasonerChatModel


import logging


logger = logging.getLogger(__name__)

load_dotenv()

# llm = ChatDeepSeek(
#     model="deepseek-chat",
# )

llm = DeepSeekReasonerChatModel(
    model='deepseek-reasoner',
    api_key=os.getenv('DEEPSEEK_API_KEY')
)

if __name__ == '__main__':
    # 1. 加载配置
    config_path = Path('./config.yaml')
    config = load_config(config_path)
    logger.info(config)
    logger.info(config.skills_dir.exists())

    logger.info(f"初始化Skill Agent的相关配置: {config.to_dict()}")

    # 2. 初始化Skill注册类
    registry = SkillRegistry()

    # 3. 根据配置自动加载skills
    if config.auto_discover and config.skills_dir.exists():
        logger.info(f"从 {config.skills_dir} 目录中加载 skills")
        loaded_count = registry.discover_and_load(
            skills_dir=config.skills_dir,
            module_name=config.skill_module_name
        )
        logger.info(f"共加载 {loaded_count} 个skills")
    else:
        logger.warning(f'Skills 目录未找到，无法自动发现')

    if len(registry) == 0:
        logger.warning('没有skills被加载，智能体不会有skills能力')

    # 4. 获取所有工具，先注册到Agent
    all_tools = registry.get_all_tools()
    logger.info(f"共有{len(all_tools)}个工具被注册")

    # 5. 创建中间件列表(除skill_middleware还可以实现其它中间件)
    middleware_list: List[AgentMiddleware] = []
    if config.middleware_enabled:
        # 【核心】创建 SkillMiddleware 实现动态工具过滤
        skill_middleware = SkillMiddleware(
            skill_registry=registry,
            verbose=config.verbose,
        )
        middleware_list.append(skill_middleware)

        logger.info("Agent Skill 中间件已经添加!")

    # 6. 系统提示词
    system_prompt = ''

    # 7. 创建智能体
    agent = create_agent(
        model=llm,
        tools=all_tools,
        middleware=middleware_list,
        system_prompt=system_prompt
    )

    # 8. 接下来处理相关操作
    for step in agent.stream(
        {
            # 'messages': '帮我数据分析[10,20,30]这组数据，并调用工具求取中位数和平均数'
            'messages': '计算[85,92,78,95,88]的统计数据'
        }, stream_mode='values'):
        step['messages'][-1].pretty_print()

