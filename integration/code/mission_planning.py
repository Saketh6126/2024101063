"""
mission_planning.py
-------------------
Module 6 – Mission Planning
Assigns missions (delivery, rescue, heist) and verifies required
roles are available before a mission can start.
Business rules:
  - Missions cannot start if any required role is unavailable.
  - If a mission needs a mechanic and a damaged car is involved,
    the car condition is checked before proceeding.
  - Completing a mission adds reward to the cash balance.
"""

from data_store import store, next_id
from registration import get_member
import inventory as inv

VALID_MISSION_TYPES = {"delivery", "rescue", "heist"}
VALID_ROLES = {"driver", "mechanic", "strategist"}


def create_mission(mission_type: str, required_roles: list) -> str:
    """Create a new mission.

    Args:
        mission_type:   One of 'delivery', 'rescue', 'heist'.
        required_roles: List of role strings needed for the mission.

    Returns:
        Generated mission ID (e.g. 'mission_1').

    Raises:
        ValueError: If type or roles are invalid.
    """
    mission_type = mission_type.strip().lower()
    if mission_type not in VALID_MISSION_TYPES:
        raise ValueError(
            f"Invalid mission type '{mission_type}'. "
            f"Use: {', '.join(sorted(VALID_MISSION_TYPES))}."
        )

    cleaned_roles = []
    for r in required_roles:
        r = r.strip().lower()
        if r not in VALID_ROLES:
            raise ValueError(f"Invalid role '{r}' in required_roles.")
        cleaned_roles.append(r)

    if not cleaned_roles:
        raise ValueError("Mission must require at least one role.")

    mission_id = next_id("mission")
    store["missions"][mission_id] = {
        "type":           mission_type,
        "required_roles": cleaned_roles,
        "assigned_crew":  [],
        "status":         "pending",
        "reward":         0,
    }
    return mission_id


def _get_mission(mission_id: str) -> dict:
    if mission_id not in store["missions"]:
        raise KeyError(f"Mission '{mission_id}' not found.")
    return store["missions"][mission_id]


def assign_crew_to_mission(mission_id: str, crew_ids: list) -> None:
    """Assign a list of crew members to a mission.

    Validates that all required roles are covered by the assigned crew.

    Raises:
        KeyError:   If mission or any crew member not found.
        ValueError: If required roles are not fully covered.
    """
    mission = _get_mission(mission_id)
    if mission["status"] != "pending":
        raise ValueError(
            f"Mission is '{mission['status']}' — can only assign crew to pending missions."
        )

    # Validate all crew IDs exist
    for cid in crew_ids:
        get_member(cid)   # raises KeyError if not registered

    # Check required roles coverage
    assigned_roles = [store["crew"][cid]["role"] for cid in crew_ids]
    missing = [
        role for role in mission["required_roles"]
        if role not in assigned_roles
    ]
    if missing:
        raise ValueError(
            f"Missing required role(s): {', '.join(missing)}. "
            f"Assign crew members with these roles first."
        )

    mission["assigned_crew"] = list(crew_ids)


def start_mission(mission_id: str) -> None:
    """Start a mission after validating all assigned crew are available.

    If the mission requires a mechanic ("damaged car" scenario),
    also checks if any car in inventory is damaged.

    Raises:
        KeyError:   If mission not found.
        ValueError: If crew isn't fully assigned, any member is unavailable,
                    or mechanic needed but not available.
    """
    mission = _get_mission(mission_id)
    if mission["status"] != "pending":
        raise ValueError(f"Mission is already '{mission['status']}'.")

    if not mission["assigned_crew"]:
        raise ValueError("No crew assigned. Use assign_crew_to_mission first.")

    # Check all assigned crew are available
    unavailable = []
    for cid in mission["assigned_crew"]:
        member = store["crew"][cid]
        if not member["available"]:
            unavailable.append(f"{member['name']} ({cid})")
    if unavailable:
        raise ValueError(
            f"Cannot start mission — these crew members are unavailable: "
            f"{', '.join(unavailable)}."
        )

    # If mechanic is required, check for any damaged car in inventory
    if "mechanic" in mission["required_roles"]:
        damaged_cars = [
            cid for cid, c in store["cars"].items()
            if c["condition"] == "damaged"
        ]
        if damaged_cars:
            # Check at least one assigned mechanic is available (already done above)
            # Alert: note which cars need attention
            print(
                f"  ⚠  Mechanic required. Damaged car(s) detected: "
                f"{', '.join(damaged_cars)}. Mechanic is available — proceeding."
            )

    # Mark all crew as unavailable
    for cid in mission["assigned_crew"]:
        store["crew"][cid]["available"] = False

    mission["status"] = "active"


def complete_mission(mission_id: str, reward: float) -> None:
    """Complete a mission, award the reward, and free the crew.

    Raises:
        KeyError:   If mission not found.
        ValueError: If mission is not active, or reward is negative.
    """
    mission = _get_mission(mission_id)
    if mission["status"] != "active":
        raise ValueError(f"Mission is '{mission['status']}', not 'active'.")
    if reward < 0:
        raise ValueError("Reward cannot be negative.")

    # Add reward to cash
    inv.update_cash(reward)
    mission["reward"] = reward

    # Free all crew
    for cid in mission["assigned_crew"]:
        if cid in store["crew"]:
            store["crew"][cid]["available"] = True

    mission["status"] = "completed"


def list_missions() -> None:
    """Print all missions with status and crew assignment."""
    missions = store["missions"]
    if not missions:
        print("  No missions created yet.")
        return

    print(f"\n  {'ID':<12} {'Type':<10} {'Status':<12} {'Roles Needed':<28} {'Crew'}")
    print("  " + "-" * 72)
    for mid, m in missions.items():
        roles = ", ".join(m["required_roles"])
        crew  = ", ".join(m["assigned_crew"]) if m["assigned_crew"] else "—"
        print(
            f"  {mid:<12} {m['type']:<10} {m['status']:<12} {roles:<28} {crew}"
        )
