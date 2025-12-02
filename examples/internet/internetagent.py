import asyncio
import logging
import random
import datetime
import math

from agentsociety.agent import CitizenAgentBase
from agentsociety.cityagent import SocietyAgent
from utils.antennas import ANTENNAS
from utils.websites import WEBSITE_DATABASE
from utils.prompts import CUSTOM_DETAILED_PLAN_PROMPT

logger = logging.getLogger(__name__)

class InternetAgent(SocietyAgent):
    def __init__(self, id: int, name: str, toolbox, memory, agent_params=None, blocks=None):
        super().__init__(
            id=id, 
            name=name, 
            toolbox=toolbox, 
            memory=memory,
            agent_params=agent_params,
            blocks=blocks
        )
        
        self.last_position = None
        self.connected_antenna = None
        self.name = name
        self.current_website = None
        self.website_start_time = None
        self.browsing_duration = 0

        self.interests = self._assign_interests()
        self.known_websites = self._generate_initial_websites()
        self.last_xy_position = None  # Track last position for comparison

        print(f"$ANTENA$ - {self.name} initialized with interests: {self.interests} and {len(self.known_websites)} known websites.")

    async def forward(self):
        # Get current position before parent forward to check antenna connectivity
        current_position = await self.memory.status.get("position")
        current_xy = current_position.get("xy_position") if current_position else None

        # Check if position changed and update antenna connection BEFORE parent forward
        if current_xy:
            if self.last_xy_position is None:
                # First time setting position
                print(f"$ANTENA$ - {self.name} initial position set to ({current_xy['x']},{current_xy['y']})")
                await self.connect_to_nearest_antenna(current_xy)
                self.last_xy_position = {"x": current_xy["x"], "y": current_xy["y"]}
            elif self.last_xy_position['x'] != current_xy['x'] or self.last_xy_position['y'] != current_xy['y']:
                # Position changed
                print(f"$ANTENA$ - {self.name} position changed from ({self.last_xy_position['x']},{self.last_xy_position['y']}) to ({current_xy['x']},{current_xy['y']})")
                await self.connect_to_nearest_antenna(current_xy)
                self.last_xy_position = {"x": current_xy["x"], "y": current_xy["y"]}

        # Update internet connectivity status in memory so the agent knows during decision making
        has_internet = self.connected_antenna is not None
        await self.memory.status.update("has_internet", has_internet)

        duration = await super().forward()

        # TODO: Handle website browsing
        # await self._handle_website_browsing(duration)
        return duration

    async def _handle_website_browsing(self, duration: int):
        """Handle website browsing logic"""
        if not self.connected_antenna:
            self.current_website = None
            self.website_start_time = None
            return

        # If not currently browsing, decide whether to start
        if not self.current_website:
            if random.random() < 0.3:  # 30% chance to start browsing
                await self._start_browsing()
        else:
            # Update browsing duration
            self.browsing_duration += duration
            
            # Check if we should stop browsing
            if self.browsing_duration >= self.expected_duration:
                await self._stop_browsing()

    async def _start_browsing(self):
        """
        Start browsing a new website using the antenna's surf_internet method
        """
        if not self.connected_antenna:
            return

        website, duration = self.connected_antenna.surf_internet(
            agent_id=self.id,
            agent_name=self.name,
            interests=self.interests,
            known_websites=self.known_websites
        )

        if website:
            self.current_website = website
            self.website_start_time = datetime.datetime.now()
            self.browsing_duration = 0
            self.expected_duration = duration
            print(f"$ANTENA$ - {self.name} started browsing {website}")

    async def _stop_browsing(self):
        """
        Stop browsing current website
        """
        if self.current_website:
            print(f"$ANTENA$ - {self.name} stopped browsing {self.current_website} after {self.browsing_duration} ticks")
            self.current_website = None
            self.website_start_time = None
            self.browsing_duration = 0
            self.expected_duration = 0

    async def connect_to_nearest_antenna(self, position: dict):
        nearest_antenna = await self.get_nearest_antenna(position, 10000.0)
        # Disconnect from previous antenna if exists
        if self.connected_antenna:
            self.connected_antenna.disconnect_agent(self.id)
            self.connected_antenna = None

        if nearest_antenna:
            self.connected_antenna = nearest_antenna
            nearest_antenna.connect_agent(self.id)
            print(f"$ANTENA$ - {self.name} connected to antenna {nearest_antenna.id} at position {position}")
            logger.info(f"{self.name} connected to antenna {nearest_antenna.id} - {position}")
        else:
            print(f"$ANTENA$ - {self.name} is out of range of any antenna at position {position}")
            logger.warning(f"{self.name} is out of range of any antenna - {position}")

    async def get_nearest_antenna(self, agent_position: dict, range_meters: float):
        nearest = min(ANTENNAS, key=lambda a: self._distance(agent_position, a.position))
        return nearest if nearest.is_within_range(agent_position) else None

    def _distance(self, pos1: dict, pos2: dict) -> float:
        pos = math.sqrt(
            (pos1["x"] - pos2["x"]) ** 2 + (pos1["y"] - pos2["y"]) ** 2
        )
        return pos

    def _assign_interests(self):
        """
        Assigns the agent 3 to 5 main interests with a score from 0 to 10.
        """
        all_interests = list(WEBSITE_DATABASE.keys())
        num_interests = random.randint(3, 5)
        selected_interests = random.sample(all_interests, num_interests)
        
        interests_with_scores = {}
        for interest in selected_interests:
            interests_with_scores[interest] = random.randint(0, 10)
        return interests_with_scores
    
    def _generate_initial_websites(self):
        """
        Generates a base set of websites based on the agent's main interests.
        """
        initial_websites = []
        for interest, score in self.interests.items():
            num_sites_to_add = max(1, min(5, int(score / 2) + 1))

            available_sites = WEBSITE_DATABASE.get(interest, [])
            if available_sites:
                selected_sites = random.sample(
                    available_sites, 
                    min(len(available_sites), num_sites_to_add)
                )

                for site in selected_sites:
                    website_score = random.randint(0, 10) 
                    initial_websites.append({
                        "website": site,
                        "score": website_score,
                        "count": 1,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
        return initial_websites