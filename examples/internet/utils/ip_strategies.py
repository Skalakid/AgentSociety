from dataclasses import dataclass
from typing import Protocol


class AntennaIPStrategy(Protocol):
    """Strategy contract for assigning an IP to a device on an antenna network."""

    def get_ip(self, antenna_id: int, agent_id: int, device_type: str, device_id: str) -> str:
        ...


@dataclass(frozen=True)
class SharedAntennaIPStrategy:
    """All devices connected to the same antenna share one IP address."""

    host_octet: int = 1

    def get_ip(self, antenna_id: int, agent_id: int, device_type: str, device_id: str) -> str:
        octet2 = (antenna_id // 256) % 256
        octet3 = antenna_id % 256
        host = min(max(self.host_octet, 1), 254)
        return f"10.{octet2}.{octet3}.{host}"


@dataclass(frozen=True)
class DeterministicPerDeviceIPStrategy:
    """Stable per-device IPs useful for controlled experiments."""

    def get_ip(self, antenna_id: int, agent_id: int, device_type: str, device_id: str) -> str:
        octet2 = (antenna_id // 256) % 256
        octet3 = antenna_id % 256

        device_type_mapping = {
            "smartphone": 1,
            "laptop": 2,
            "desktop": 3,
            "tablet": 4,
        }
        device_offset = device_type_mapping.get(device_type, 0) * 50
        octet4 = ((agent_id + device_offset) % 254) + 1
        return f"10.{octet2}.{octet3}.{octet4}"
