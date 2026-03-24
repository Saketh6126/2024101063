"""
crew_management.py
------------------
Module 2 – Crew Management
Manages roles and skill levels for registered crew members,
and tracks their availability status.
Business rule: Only registered crew members can have roles assigned.
"""

from data_store import store
from registration import get_member, VALID_ROLES


def assign_role(crew_id: str, role: str) -> None:
    """Assign or update the role of a registered crew member.

    Args:
        crew_id: ID of an existing crew member.
        role:    One of 'driver', 'mechanic', 'strategist'.

    Raises:
        KeyError:   If crew_id is not registered.
        ValueError: If role is invalid.
    """
    member = get_member(crew_id)   # raises KeyError if not found
    role = role.strip().lower()
    if role not in VALID_ROLES:
        raise ValueError(
            f"Invalid role '{role}'. Must be one of: {', '.join(sorted(VALID_ROLES))}."
        )
    member["role"] = role


def update_skill(crew_id: str, skill_level: int) -> None:
    """Update the skill level of a crew member (range 1–10).

    Raises:
        KeyError:   If crew_id is not registered.
        ValueError: If skill_level is out of range.
    """
    member = get_member(crew_id)
    if not (1 <= skill_level <= 10):
        raise ValueError("Skill level must be between 1 and 10.")
    member["skill_level"] = skill_level


def set_availability(crew_id: str, available: bool) -> None:
    """Mark a crew member as available or unavailable.

    Raises:
        KeyError: If crew_id is not registered.
    """
    member = get_member(crew_id)
    member["available"] = available


def list_by_role(role: str) -> None:
    """Print all crew members with the specified role."""
    role = role.strip().lower()
    matches = {
        cid: m for cid, m in store["crew"].items()
        if m["role"] == role
    }
    if not matches:
        print(f"  No crew members with role '{role}'.")
        return

    print(f"\n  Crew with role: {role}")
    print(f"  {'ID':<10} {'Name':<20} {'Skill':>5} {'Available'}")
    print("  " + "-" * 46)
    for cid, m in matches.items():
        avail = "✓" if m["available"] else "✗"
        print(f"  {cid:<10} {m['name']:<20} {m['skill_level']:>5}     {avail}")


def get_available_drivers() -> list:
    """Return (and print) all crew members who are drivers and currently available."""
    drivers = {
        cid: m for cid, m in store["crew"].items()
        if m["role"] == "driver" and m["available"]
    }
    if not drivers:
        print("  No available drivers at the moment.")
    else:
        print(f"\n  Available Drivers:")
        print(f"  {'ID':<10} {'Name':<20} {'Skill':>5}")
        print("  " + "-" * 36)
        for cid, m in drivers.items():
            print(f"  {cid:<10} {m['name']:<20} {m['skill_level']:>5}")
    return list(drivers.keys())
