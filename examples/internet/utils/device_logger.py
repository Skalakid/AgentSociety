"""
Device usage logging utilities for tracking when agents use ICT devices to solve tasks.
"""

import datetime
import json
import threading
from typing import Optional

# Import the log path and lock from antennas
from .antennas import FULL_DEVICE_USAGE_LOG_PATH, device_usage_lock


def log_device_usage(
    agent_id: int,
    agent_name: str,
    device_id: str,
    device_type: str,
    device_name: str,
    action_type: str,
    action_description: str,
    task_target: Optional[str] = None,
    success: bool = True,
    metadata: Optional[dict] = None
):
    """
    Log when an agent uses a device to solve a task or perform an action.

    Args:
        agent_id: Unique agent identifier
        agent_name: Human-readable agent name
        device_id: Unique device identifier (e.g., "123_smartphone")
        device_type: Type of device used (smartphone, laptop, desktop, tablet)
        device_name: Human-readable device name
        action_type: Type of action performed (e.g., "browse", "shop", "work", "social", "search")
        action_description: Description of what the agent did
        task_target: Optional - what task was being solved (e.g., "Find restaurant information")
        success: Whether the action was successful
        metadata: Optional additional metadata (e.g., website visited, time spent, etc.)
    """
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "agent_id": agent_id,
        "agent_name": agent_name,
        "device_id": device_id,
        "device_type": device_type,
        "device_name": device_name,
        "action_type": action_type,
        "action_description": action_description,
        "task_target": task_target,
        "success": success,
        "metadata": metadata or {}
    }

    with device_usage_lock:
        with open(FULL_DEVICE_USAGE_LOG_PATH, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


def log_internet_browsing(
    agent_id: int,
    agent_name: str,
    device_id: str,
    device_type: str,
    device_name: str,
    website: str,
    purpose: Optional[str] = None,
    duration_seconds: Optional[int] = None
):
    """
    Convenience function for logging internet browsing actions.

    Args:
        agent_id: Unique agent identifier
        agent_name: Human-readable agent name
        device_id: Unique device identifier
        device_type: Type of device used
        device_name: Human-readable device name
        website: Website URL being visited
        purpose: Optional - why the agent is browsing (e.g., "Check news", "Shop for groceries")
        duration_seconds: Optional - how long they browsed
    """
    metadata = {"website": website}
    if duration_seconds:
        metadata["duration_seconds"] = duration_seconds

    log_device_usage(
        agent_id=agent_id,
        agent_name=agent_name,
        device_id=device_id,
        device_type=device_type,
        device_name=device_name,
        action_type="browse",
        action_description=f"Browse {website}" + (f" - {purpose}" if purpose else ""),
        task_target=purpose,
        success=True,
        metadata=metadata
    )


def log_online_shopping(
    agent_id: int,
    agent_name: str,
    device_id: str,
    device_type: str,
    device_name: str,
    items: list[str],
    store: Optional[str] = None,
    completed: bool = True
):
    """
    Convenience function for logging online shopping actions.

    Args:
        agent_id: Unique agent identifier
        agent_name: Human-readable agent name
        device_id: Unique device identifier
        device_type: Type of device used
        device_name: Human-readable device name
        items: List of items being shopped for
        store: Optional - which online store
        completed: Whether the purchase was completed
    """
    metadata = {"items": items}
    if store:
        metadata["store"] = store

    log_device_usage(
        agent_id=agent_id,
        agent_name=agent_name,
        device_id=device_id,
        device_type=device_type,
        device_name=device_name,
        action_type="shop",
        action_description=f"Shop online for {', '.join(items)}" + (f" at {store}" if store else ""),
        task_target=f"Purchase {', '.join(items)}",
        success=completed,
        metadata=metadata
    )


def log_remote_work(
    agent_id: int,
    agent_name: str,
    device_id: str,
    device_type: str,
    device_name: str,
    work_description: str,
    duration_seconds: Optional[int] = None
):
    """
    Convenience function for logging remote work actions.

    Args:
        agent_id: Unique agent identifier
        agent_name: Human-readable agent name
        device_id: Unique device identifier
        device_type: Type of device used
        device_name: Human-readable device name
        work_description: Description of the work being done
        duration_seconds: Optional - how long they worked
    """
    metadata = {}
    if duration_seconds:
        metadata["duration_seconds"] = duration_seconds

    log_device_usage(
        agent_id=agent_id,
        agent_name=agent_name,
        device_id=device_id,
        device_type=device_type,
        device_name=device_name,
        action_type="work",
        action_description=work_description,
        task_target="Complete remote work task",
        success=True,
        metadata=metadata
    )


def log_social_media(
    agent_id: int,
    agent_name: str,
    device_id: str,
    device_type: str,
    device_name: str,
    platform: str,
    activity: str
):
    """
    Convenience function for logging social media usage.

    Args:
        agent_id: Unique agent identifier
        agent_name: Human-readable agent name
        device_id: Unique device identifier
        device_type: Type of device used
        device_name: Human-readable device name
        platform: Social media platform (e.g., "facebook.com", "instagram.com")
        activity: What they did (e.g., "Check updates", "Post message", "Chat with friend")
    """
    log_device_usage(
        agent_id=agent_id,
        agent_name=agent_name,
        device_id=device_id,
        device_type=device_type,
        device_name=device_name,
        action_type="social",
        action_description=f"{activity} on {platform}",
        task_target=activity,
        success=True,
        metadata={"platform": platform}
    )
