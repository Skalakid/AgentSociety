import asyncio
import inspect
import copy

import agentsociety.vectorstore.vectorstore as _vs
_vs_source = inspect.getsourcefile(_vs.VectorStore)
with open(_vs_source) as _f:
    _vs_code = _f.read()
if "query_points" in _vs_code:
    print("---- THIS IS A PATCHED VERSION ----")
else:
    print("WARNING: unpatched vectorstore detected — simulation may crash (QdrantClient.search removed)")

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
from internetagent import InternetAgent, START_WEEKDAY
from internet_memory_config import memory_config_internetagent

config = Config(
    llm=[
        LLMConfig(
            provider=LLMProviderType.ZhipuAI,
            base_url=None,
            api_key="bc2e3cb9022b4d38b5f144b166d1ac11.oKkJEOu2i4TYw69z",
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
        name="internet 11.12 device test",
        workflow=[
            WorkflowStepConfig(
                type=WorkflowType.RUN,
                days=1,
            ),
        ],
        environment=EnvironmentConfig(
            start_tick=6 * 60 * 60,    # Start at 06:00 AM
            total_tick=18 * 60 * 60,   # Run for 18 hours (until midnight)
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
