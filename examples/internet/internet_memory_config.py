"""
Custom memory configuration for InternetAgent that includes ICT device awareness.
"""

import copy
from agentsociety.cityagent import memory_config_societyagent
from agentsociety.agent.memory_config_generator import MemoryAttribute


def memory_config_internetagent(distributions, class_config=None):
    """
    Generate memory configuration for internet-aware society agents.
    Extends the default society agent memory with ICT device fields.
    """
    # Start with the default society agent memory config
    base_config = memory_config_societyagent(distributions, class_config)

    # Add internet-specific memory attributes
    internet_attributes = {
        "has_internet": MemoryAttribute(
            name="has_internet",
            type=bool,
            default_or_value=False,
            description="Whether the agent currently has internet connectivity (connected to antenna)",
            whether_embedding=False,
        ),
        "ict_devices": MemoryAttribute(
            name="ict_devices",
            type=str,
            default_or_value="You do not own any internet-capable devices.",
            description="Description of ICT devices owned by the agent and their capabilities",
            whether_embedding=False,
        ),
    }

    # Merge the attributes
    base_config.attributes.update(internet_attributes)

    return base_config
