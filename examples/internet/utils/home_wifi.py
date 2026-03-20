"""
HomeRouter: simulates a private home WiFi router with DHCP.
Each unique home_aoi_id gets its own router and subnet (192.168.x.x).
Multiple agents sharing the same home_aoi_id share the same router.
"""

import threading
import datetime
import json
from typing import Optional

from .antennas import FULL_DEVICE_CONNECTION_LOG_PATH, device_connection_lock

HOME_ROUTERS: dict[int, "HomeRouter"] = {}
_registry_lock = threading.Lock()

HOME_AT_DISTANCE = 500.0  # meters — radius to consider agent "at home"


def get_or_create_home_router(home_aoi_id: int) -> "HomeRouter":
    with _registry_lock:
        if home_aoi_id not in HOME_ROUTERS:
            HOME_ROUTERS[home_aoi_id] = HomeRouter(home_aoi_id)
        return HOME_ROUTERS[home_aoi_id]


class HomeRouter:
    def __init__(self, home_aoi_id: int):
        self.home_aoi_id = home_aoi_id
        self.subnet_prefix = f"192.168.{home_aoi_id % 256}.{(home_aoi_id // 256) % 256}"
        self._ip_pool: set[str] = {f"{self.subnet_prefix}.{i}" for i in range(1, 255)}
        self._active_leases: dict[str, dict] = {}
        self._lock = threading.Lock()

    def connect_devices(self, agent_id: int, agent_name: str, devices: list) -> dict[str, str]:
        """Lease IPs for all devices. Returns {device_id: ip_address}."""
        leased = {}
        for device in devices:
            if device.device_type.value == "none":
                continue
            device_id = f"{agent_id}_{device.device_type.value}"
            ip = self._lease_ip(agent_id, device_id)
            if ip:
                leased[device_id] = ip
                self._log_connection(agent_id, agent_name, device, ip, "connect")
        return leased

    def disconnect_devices(self, agent_id: int, agent_name: str, devices: list, leased_ips: dict[str, str]):
        """Release leased IPs and log disconnections."""
        for device in devices:
            if device.device_type.value == "none":
                continue
            device_id = f"{agent_id}_{device.device_type.value}"
            ip = leased_ips.get(device_id)
            if ip:
                self._release_ip(ip)
                self._log_connection(agent_id, agent_name, device, ip, "disconnect")

    def _lease_ip(self, agent_id: int, device_id: str) -> Optional[str]:
        with self._lock:
            if not self._ip_pool:
                return None
            ip = self._ip_pool.pop()
            self._active_leases[ip] = {
                "agent_id": agent_id,
                "device_id": device_id,
                "leased_at": datetime.datetime.now().isoformat(),
            }
            return ip

    def _release_ip(self, ip: str):
        with self._lock:
            if ip in self._active_leases:
                del self._active_leases[ip]
                self._ip_pool.add(ip)

    def _log_connection(self, agent_id: int, agent_name: str, device, ip: str, action: str):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "network_type": "home_wifi",
            "home_aoi_id": self.home_aoi_id,
            "subnet": self.subnet_prefix,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "device_name": device.name,
            "device_type": device.device_type.value,
            "device_id": f"{agent_id}_{device.device_type.value}",
            "ip_address": ip,
        }
        with device_connection_lock:
            with open(FULL_DEVICE_CONNECTION_LOG_PATH, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
