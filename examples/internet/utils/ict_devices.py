"""
ICT Device definitions for internet simulation agents.
Devices have different capabilities and enable different types of internet usage.
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass


class DeviceType(Enum):
    """Types of ICT devices available to agents"""
    SMARTPHONE = "smartphone"
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    TABLET = "tablet"
    NONE = "none"


@dataclass
class DeviceCapabilities:
    """Capabilities of an ICT device"""
    can_browse_web: bool = True
    can_use_social_media: bool = True
    can_shop_online: bool = True
    can_stream_media: bool = True
    can_work_remotely: bool = False
    can_video_call: bool = False
    portability: float = 0.0  # 0.0 = not portable, 1.0 = fully portable
    battery_dependent: bool = False

    def get_description(self) -> str:
        """Get a human-readable description of device capabilities"""
        capabilities = []
        if self.can_browse_web:
            capabilities.append("browse websites")
        if self.can_use_social_media:
            capabilities.append("use social media")
        if self.can_shop_online:
            capabilities.append("shop online")
        if self.can_stream_media:
            capabilities.append("stream videos and music")
        if self.can_work_remotely:
            capabilities.append("work remotely")
        if self.can_video_call:
            capabilities.append("make video calls")

        if not capabilities:
            return "no internet capabilities"

        return ", ".join(capabilities)


@dataclass
class ICTDevice:
    """Represents an ICT device owned by an agent"""
    device_type: DeviceType
    capabilities: DeviceCapabilities
    name: str

    def can_perform_task(self, task_type: str) -> bool:
        """Check if this device can perform a specific task type"""
        task_mapping = {
            "browse": self.capabilities.can_browse_web,
            "social": self.capabilities.can_use_social_media,
            "shop": self.capabilities.can_shop_online,
            "stream": self.capabilities.can_stream_media,
            "work": self.capabilities.can_work_remotely,
            "call": self.capabilities.can_video_call,
        }
        return task_mapping.get(task_type, False)

    def get_description(self) -> str:
        """Get full device description for agent awareness"""
        portability_desc = "portable" if self.capabilities.portability > 0.5 else "stationary"
        battery_desc = "battery-powered" if self.capabilities.battery_dependent else "needs power outlet"

        return (
            f"{self.name} ({portability_desc}, {battery_desc}). "
            f"You can use it to: {self.capabilities.get_description()}."
        )


# Predefined device configurations
DEVICE_CONFIGS = {
    DeviceType.SMARTPHONE: ICTDevice(
        device_type=DeviceType.SMARTPHONE,
        name="Smartphone",
        capabilities=DeviceCapabilities(
            can_browse_web=True,
            can_use_social_media=True,
            can_shop_online=True,
            can_stream_media=True,
            can_work_remotely=True,
            can_video_call=True,
            portability=1.0,
            battery_dependent=True,
        )
    ),
    DeviceType.LAPTOP: ICTDevice(
        device_type=DeviceType.LAPTOP,
        name="Laptop",
        capabilities=DeviceCapabilities(
            can_browse_web=True,
            can_use_social_media=True,
            can_shop_online=True,
            can_stream_media=True,
            can_work_remotely=True,
            can_video_call=True,
            portability=0.7,
            battery_dependent=True,
        )
    ),
    DeviceType.DESKTOP: ICTDevice(
        device_type=DeviceType.DESKTOP,
        name="Desktop Computer",
        capabilities=DeviceCapabilities(
            can_browse_web=True,
            can_use_social_media=True,
            can_shop_online=True,
            can_stream_media=True,
            can_work_remotely=True,
            can_video_call=True,
            portability=0.0,
            battery_dependent=False,
        )
    ),
    DeviceType.TABLET: ICTDevice(
        device_type=DeviceType.TABLET,
        name="Tablet",
        capabilities=DeviceCapabilities(
            can_browse_web=True,
            can_use_social_media=True,
            can_shop_online=True,
            can_stream_media=True,
            can_work_remotely=False,
            can_video_call=True,
            portability=0.9,
            battery_dependent=True,
        )
    ),
    DeviceType.NONE: ICTDevice(
        device_type=DeviceType.NONE,
        name="No device",
        capabilities=DeviceCapabilities(
            can_browse_web=False,
            can_use_social_media=False,
            can_shop_online=False,
            can_stream_media=False,
            can_work_remotely=False,
            can_video_call=False,
            portability=0.0,
            battery_dependent=False,
        )
    ),
}


def assign_devices_to_agent(age: int, occupation: str) -> list[ICTDevice]:
    """
    Assign ICT devices to an agent based on their demographics.

    Args:
        age: Agent's age
        occupation: Agent's occupation

    Returns:
        List of ICTDevice objects owned by the agent
    """
    import random

    devices = []

    # Almost everyone has a smartphone (95% for age 18-65)
    if age < 70 and random.random() < 0.95:
        devices.append(DEVICE_CONFIGS[DeviceType.SMARTPHONE])
    elif age >= 70 and random.random() < 0.60:
        devices.append(DEVICE_CONFIGS[DeviceType.SMARTPHONE])

    # Work-related devices
    work_occupations = ["Engineer", "Manager", "Teacher", "Doctor", "Businessman"]
    if occupation in work_occupations:
        # 80% chance of having a laptop
        if random.random() < 0.80:
            devices.append(DEVICE_CONFIGS[DeviceType.LAPTOP])
        # 30% chance of having a desktop at home
        if random.random() < 0.30:
            devices.append(DEVICE_CONFIGS[DeviceType.DESKTOP])

    # Students often have laptops
    if occupation == "Student":
        if random.random() < 0.95:
            devices.append(DEVICE_CONFIGS[DeviceType.LAPTOP])

    # Artists might have tablets
    if occupation == "Artist":
        if random.random() < 0.40:
            devices.append(DEVICE_CONFIGS[DeviceType.TABLET])

    # Some people just have desktop at home
    if not devices or (len(devices) == 1 and devices[0].device_type == DeviceType.SMARTPHONE):
        if random.random() < 0.80:
            devices.append(DEVICE_CONFIGS[DeviceType.DESKTOP])

    # If no devices assigned (rare for elderly), they have no device
    if not devices:
        devices.append(DEVICE_CONFIGS[DeviceType.NONE])

    return devices


def get_device_awareness_text(devices: list[ICTDevice], has_internet: bool) -> str:
    """
    Generate text for agent memory about their device ownership and capabilities.

    Args:
        devices: List of devices owned by the agent
        has_internet: Whether the agent currently has internet connectivity

    Returns:
        Text description for agent awareness
    """
    if not devices or (len(devices) == 1 and devices[0].device_type == DeviceType.NONE):
        return "You do not own any internet-capable devices."

    device_descriptions = [device.get_description() for device in devices if device.device_type != DeviceType.NONE]

    internet_status = ""
    if has_internet:
        internet_status = " You currently have internet access and can use your devices to browse websites, use apps, shop online, etc."
    else:
        internet_status = " You currently do NOT have internet access (out of antenna range), so your devices cannot connect to the internet."

    return (
        f"You own the following ICT devices: {', '.join([d.name for d in devices if d.device_type != DeviceType.NONE])}. "
        f"{' '.join(device_descriptions)}{internet_status}"
    )
