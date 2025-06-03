import asyncio
import json
import logging
from functools import partial
from typing import Literal, Union

import ray

from agentsociety.cityagent import default
from agentsociety.configs import (
    AgentsConfig,
    Config,
    EnvConfig,
    ExpConfig,
    LLMConfig,
    MapConfig,
)
from agentsociety.configs.agent import AgentClassType, AgentConfig
from agentsociety.configs.exp import WorkflowStepConfig, WorkflowType
from agentsociety.environment import EnvironmentConfig
from agentsociety.llm import LLMProviderType
from agentsociety.message import RedisConfig
from agentsociety.metrics import MlflowConfig
from agentsociety.simulation import AgentSociety
from agentsociety.storage import AvroConfig, PostgreSQLConfig
from internetagent import InternetAgent

from agentsociety.cityagent import (
    DEFAULT_DISTRIBUTIONS,
    SocietyAgent,
    default,
    memory_config_societyagent,
)
from hurrican_memory_config import memory_config_societyagent_hurrican

ray.init(logging_level=logging.INFO)


async def update_weather_and_temperature(
    weather: Union[Literal["wind"], Literal["no-wind"]], simulation: AgentSociety
):
    if weather == "wind":
        await simulation.update_environment(
            "weather",
            "Hurricane Dorian has made landfall in other cities, travel is slightly affected, and winds can be felt",
        )
    elif weather == "no-wind":
        await simulation.update_environment(
            "weather", "The weather is normal and does not affect travel"
        )


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
        redis=RedisConfig(
            server="localhost",
            port=6379,
            password="CHANGE_ME",
        ),  # type: ignore
        pgsql=PostgreSQLConfig(
            enabled=True,
            dsn="postgresql://postgres:CHANGE_ME@localhost:5432/postgres",
            num_workers="auto",
        ),
        avro=AvroConfig(
            path="./logs/",
            enabled=True,
        ),
        mlflow=MlflowConfig(
            enabled=True,
            mlflow_uri="http://localhost:59000",
            username="admin",
            password="CHANGE_ME",
        ),
    ),
    map=MapConfig(
        file_path="../../data/beijing_map.pb",
    ),
    agents=AgentsConfig(
        citizens=[
            AgentConfig(
                agent_class=InternetAgent,
                number=1000,
                memory_config_func=memory_config_societyagent_hurrican,
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
    agentsociety = AgentSociety(config)
    await agentsociety.init()
    await agentsociety.run()
    await agentsociety.close()
    ray.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
