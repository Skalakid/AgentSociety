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
from utils.ict_devices import assign_devices_to_agent, get_device_awareness_text, ICTDevice
from utils.device_logger import log_device_usage, log_internet_browsing

logger = logging.getLogger(__name__)

class InternetAgent(SocietyAgent):
    def __init__(self, id: int, name: str, toolbox, memory, agent_params=None, blocks=None):
        # Override the plan generation prompt with our custom one that includes device_usage
        if agent_params:
            agent_params.plan_generation_prompt = CUSTOM_DETAILED_PLAN_PROMPT

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
        self.ict_devices: list[ICTDevice] = []  # Will be populated after memory is initialized

        print(f"$ANTENA$ - {self.name} initialized with interests: {self.interests} and {len(self.known_websites)} known websites.")

    async def forward(self):
        # Initialize ICT devices on first run (after memory is available)
        if not self.ict_devices:
            await self._initialize_ict_devices()

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

        # Update internet connectivity and device awareness in memory
        has_internet = self.connected_antenna is not None
        await self.memory.status.update("has_internet", has_internet)

        # Update device awareness text so agent knows what devices they have and can use
        device_awareness = get_device_awareness_text(self.ict_devices, has_internet)
        await self.memory.status.update("ict_devices", device_awareness)

        duration = await super().forward()

        return duration

    async def step_execution(self):
        """Override step execution to handle device usage before executing the step"""
        current_plan = await self.memory.status.get("current_plan")
        if (
            current_plan is None
            or not current_plan
            or len(current_plan.get("steps", [])) == 0
        ):
            return  # No plan, no execution

        step_index = current_plan.get("index", 0)
        current_step = current_plan.get("steps", [])[step_index]

        # Debug: Log current step to see if device_usage is present
        if current_step:
            print(f"$DEBUG$ - {self.name} executing step: {current_step.get('intention', 'Unknown')}")
            if "device_usage" in current_step:
                print(f"$DEBUG$ - Device usage field present: {current_step['device_usage']}")
            else:
                print(f"$DEBUG$ - No device_usage field in step {current_step}")

        # Check if current step includes device usage
        if current_step and "device_usage" in current_step and current_step["device_usage"]:
            device_usage = current_step["device_usage"]

            # Log device usage if internet is available
            if self.connected_antenna:
                self.log_device_action(
                    task_type=device_usage.get("action_type", "browse"),
                    action_description=device_usage.get("device_action", "Use device for task"),
                    task_target=current_step.get("intention", "Unknown task"),
                    metadata={
                        "step_type": current_step.get("type", "other"),
                        "step_index": step_index,
                        "plan_target": current_plan.get("target", "Unknown")
                    }
                )
            else:
                print(f"$DEVICE$ - {self.name} planned to use device for '{current_step.get('intention')}' but has no internet")

        # Call parent step execution to actually execute the step
        await super().step_execution()

    async def _initialize_ict_devices(self):
        """Initialize ICT devices based on agent demographics"""
        # Get agent demographics from memory
        age = await self.memory.status.get("age", default_value=30)
        occupation = await self.memory.status.get("occupation", default_value="Other")

        # Assign devices based on demographics
        self.ict_devices = assign_devices_to_agent(age, occupation)

        device_names = [d.name for d in self.ict_devices if d.device_type.value != "none"]
        print(f"$ANTENA$ - {self.name} owns ICT devices: {', '.join(device_names) if device_names else 'none'}")

    def _select_device_for_task(self, task_type: str) -> ICTDevice:
        """
        Select the most appropriate device for a given task type.

        Args:
            task_type: Type of task (browse, shop, work, stream, social, call)

        Returns:
            The selected device, or None device if no suitable device available
        """
        # Filter devices that can perform this task
        capable_devices = [d for d in self.ict_devices if d.can_perform_task(task_type)]

        if not capable_devices:
            return None

        # Preference order: smartphone (most portable), laptop, tablet, desktop
        preference_order = ["smartphone", "laptop", "tablet", "desktop"]

        for device_type in preference_order:
            for device in capable_devices:
                if device.device_type.value == device_type:
                    return device

        # Fallback to first capable device
        return capable_devices[0]

    def log_device_action(self, task_type: str, action_description: str, task_target: str = None, metadata: dict = None):
        """
        Log that the agent used a device to perform an action.

        Args:
            task_type: Type of task (browse, shop, work, stream, social, call)
            action_description: What the agent did
            task_target: What task was being solved
            metadata: Additional information
        """
        # Check if agent has internet
        if not self.connected_antenna:
            print(f"$DEVICE$ - {self.name} tried to use device but has no internet connection")
            return

        # Select appropriate device
        device = self._select_device_for_task(task_type)

        if not device or device.device_type.value == "none":
            print(f"$DEVICE$ - {self.name} has no device capable of task: {task_type}")
            return

        device_id = f"{self.id}_{device.device_type.value}"

        # Log the device usage
        log_device_usage(
            agent_id=self.id,
            agent_name=self.name,
            device_id=device_id,
            device_type=device.device_type.value,
            device_name=device.name,
            action_type=task_type,
            action_description=action_description,
            task_target=task_target,
            success=True,
            metadata=metadata or {}
        )

        print(f"$DEVICE$ - {self.name} used {device.name} to: {action_description}")

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

            # Log the device usage for browsing
            self.log_device_action(
                task_type="browse",
                action_description=f"Browse {website}",
                task_target="Access information online",
                metadata={"website": website, "expected_duration": duration}
            )

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
            # Pass device information when connecting
            nearest_antenna.connect_agent(
                agent_id=self.id,
                agent_name=self.name,
                devices=self.ict_devices
            )
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