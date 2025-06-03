import asyncio
import logging

from agentsociety.agent import CitizenAgentBase
from agentsociety.tools.tool import UpdateWithSimulator
import math
import random
import datetime
from agentsociety.cityagent import SocietyAgent
from utils.antennas import ANTENNAS
from utils.websites import WEBSITE_DATABASE

logger = logging.getLogger(__name__)

class InternetAgent(SocietyAgent):
    update_with_sim = UpdateWithSimulator()

    def __init__(self, id: int, name: str, toolbox, memory):
        super().__init__(id=id, name=name, toolbox=toolbox, memory=memory)
        self.last_position = None
        self.connected_antenna = None
        self.name = name

        self.interests = self._assign_interests()
        self.known_websites = self._generate_initial_websites()

        print(f"{self.name} initialized with interests: {self.interests} and {len(self.known_websites)} known websites.")

    async def forward(self):
        previous_position = await self.memory.status.get("position")

        duration = await super().forward()

        current_position = (await self.memory.status.get("position"))["xy_position"]
        if previous_position != current_position:
            await self.connect_to_nearest_antenna(current_position)

        return duration

    async def connect_to_nearest_antenna(self, position: dict):
        nearest_antenna = await self.get_nearest_antenna(position, 10000.0)
        if nearest_antenna:
            self.connected_antenna = nearest_antenna
            print(f"{self.name} connected to antenna {nearest_antenna.id} at position {position}")
            logger.info(f"{self.name} connected to antenna {nearest_antenna.id} - {position}")
        else:
            self.connected_antenna = None
            print(f"{self.name} is out of range of any antenna at position {position}")
            logger.warning(f"{self.name} is out of range of any antenna - {position}")

    async def get_nearest_antenna(self, agent_position: dict, range_meters: float):
        nearest = min(ANTENNAS, key=lambda a: self._distance(agent_position, a.position))
        return nearest if nearest.is_within_range(agent_position) else None

    def _distance(self, pos1: dict, pos2: dict) -> float:
        pos = math.sqrt(
            (pos1["x"] - pos2["x"]) ** 2 + (pos1["y"] - pos2["y"]) ** 2
        )

        return pos

    # -----

    def _assign_interests(self):
        """
        Przypisuje agentowi 3 do 5 głównych zainteresowań z oceną od 0 do 10.
        """
        all_interests = list(WEBSITE_DATABASE.keys())
        # Losujemy liczbę zainteresowań od 3 do 5
        num_interests = random.randint(3, 5)
        # Losujemy unikalne zainteresowania
        selected_interests = random.sample(all_interests, num_interests)
        
        interests_with_scores = {}
        for interest in selected_interests:
            # Przypisujemy losową ocenę od 0 do 10 dla każdego zainteresowania
            interests_with_scores[interest] = random.randint(0, 10)
        return interests_with_scores
    
    def _generate_initial_websites(self):
        """
        Generuje początkowy zestaw "bazowych" stron na podstawie głównych zainteresowań agenta.
        """
        initial_websites = []
        for interest, score in self.interests.items():
            # Im wyższa ocena zainteresowania, tym więcej stron z tej kategorii agent zna
            # Możesz dostosować tę logikę, np. minimum 1 strona, maksimum 3-5 stron na zainteresowanie
            num_sites_to_add = max(1, min(5, int(score / 2) + 1)) # Przykładowa logika: ocena 0-1 -> 1 strona, 9-10 -> 5 stron

            available_sites = WEBSITE_DATABASE.get(interest, [])
            if available_sites:
                # Losujemy unikalne strony z danej kategorii
                selected_sites = random.sample(
                    available_sites, 
                    min(len(available_sites), num_sites_to_add)
                )

                for site in selected_sites:
                    # Tutaj będzie miejsce na odpytanie LLM o ocenę strony.
                    # Na razie przypisujemy losową wartość jako placeholder.
                    # W przyszłości: LLM_evaluation_score = await self.llm.evaluate_website(site, self.interests)
                    website_score = random.randint(0, 10) 
                    initial_websites.append({
                        "website": site,
                        "score": website_score,
                        "count": 1,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
        return initial_websites