import asyncio

git
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
                number=10,
                memory_from_file="profiles_hurricane.json",
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
            start_tick=6 * 60 * 60,
            total_tick= 30 * 60,
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
