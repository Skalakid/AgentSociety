import asyncio
import logging

from agentsociety.agent import CitizenAgentBase
from agentsociety.tools.tool import UpdateWithSimulator
import math
from agentsociety.cityagent import SocietyAgent
from utils.antennas import ANTENNAS

logger = logging.getLogger(__name__)

class InternetAgent(SocietyAgent):
    update_with_sim = UpdateWithSimulator()

    def __init__(self, id: int, name: str, toolbox, memory):
        super().__init__(id=id, name=name, toolbox=toolbox, memory=memory)
        self.last_position = None
        self.connected_antenna = None
        self.name = name

    async def forward(self):
        previous_position = await self.memory.status.get("position")

        duration = await super().forward()

        current_position = (await self.memory.status.get("position"))["xy_position"]
        if previous_position != current_position:
            await self.connect_to_nearest_antenna(current_position)

        return duration

    async def connect_to_nearest_antenna(self, position):
        nearest_antenna = await self.get_nearest_antenna(position, 10000.0)
        if nearest_antenna is not None:
            self.connected_antenna = nearest_antenna
            logger.info(f"{self.name} connected to antenna {nearest_antenna['id']} - {position}")
        else:
            logger.warning(f"{self.name} is out of range of any antenna  - {position}")

    def distance(self, pos1, pos2):
        return math.sqrt(
            (pos1["x"] - pos2["x"]) ** 2 + (pos1["y"] - pos2["y"]) ** 2
        )

    def is_within_range(self, pos1, pos2, range_meters):
        print(f"Checking if {pos1} is within {range_meters} of {pos2}")
        print(f"Distance: {self.distance(pos1, pos2)} = {self.distance(pos1, pos2) <= range_meters}")
        return self.distance(pos1, pos2) <= range_meters

    async def get_nearest_antenna(self, agent_position, range_meters):
        nearest = min(ANTENNAS, key=lambda a: self.distance(agent_position, a["position"]))

        if range_meters is not None and not self.is_within_range(agent_position, nearest["position"], range_meters):
            return None
            
        return nearest
