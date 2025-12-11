import asyncio

import copy
from agentsociety.cityagent import default, DEFAULT_DISTRIBUTIONS
from agentsociety.cityagent.blocks.economy_block import EconomyBlock, EconomyBlockParams
from agentsociety.cityagent.blocks.mobility_block import MobilityBlock, MobilityBlockParams
from agentsociety.cityagent.blocks.other_block import OtherBlock, OtherBlockParams
from agentsociety.cityagent.blocks.social_block import SocialBlock, SocialBlockParams
from agentsociety.configs import (
    AgentsConfig,
    Config,
    EnvConfig,
    ExpConfig,
    LLMConfig,
    MapConfig,
)
from agentsociety.configs.agent import AgentConfig
from agentsociety.configs.exp import WorkflowStepConfig, WorkflowType
from agentsociety.environment import EnvironmentConfig
from agentsociety.llm import LLMProviderType
from agentsociety.simulation import AgentSociety
from agentsociety.storage import DatabaseConfig
from internetagent import InternetAgent
from internet_memory_config import memory_config_internetagent

config = Config(
    llm=[
        LLMConfig(
            provider=LLMProviderType.ZhipuAI,
            base_url=None,
            api_key="",
            model="GLM-4-Flash",
            semaphore=200,
        )
    ],
    env=EnvConfig(
        db=DatabaseConfig(
            enabled=True,
            db_type="sqlite",
            pg_dsn=None,
        ),
    ),
    map=MapConfig(
        file_path="../../agentsociety_data/beijing.pb",
    ),
    agents=AgentsConfig(
        citizens=[
            AgentConfig(
                agent_class=InternetAgent,
                number=100,
                memory_config_func=memory_config_internetagent,  # Use custom memory config with ICT device fields
                memory_distributions=copy.deepcopy(DEFAULT_DISTRIBUTIONS),
                blocks={
                    MobilityBlock: MobilityBlockParams(),
                    EconomyBlock: EconomyBlockParams(),
                    SocialBlock: SocialBlockParams(),
                    OtherBlock: OtherBlockParams(),
                },
            )
        ]
    ),  # type: ignore
    exp=ExpConfig(
        name="internet",
        workflow=[
            WorkflowStepConfig(
                type=WorkflowType.RUN,
                days=1,
            ),
        ],
        environment=EnvironmentConfig(
            start_tick=12 * 60 * 60,  # Start at 12:00 PM
            total_tick= 8 * 60 * 60,  # Run for 8 hours (until 8:00 PM) to see more movement
        ),
    ),
)
config = default(config)


async def main():
    agentsociety = AgentSociety.create(config)
    try:
        await agentsociety.init()
        await agentsociety.run()
    finally:
        await agentsociety.close()


if __name__ == "__main__":
    asyncio.run(main())
