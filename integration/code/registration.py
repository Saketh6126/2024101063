"""
Module 1 – Registration
Registers new crew members, storing name and role.
Business rule: A crew member must exist here before any other
module can reference them.
"""

from data_store import store, next_id

VALID_ROLES = {"driver", "mechanic", "strategist"}

def register_member(name: str, role: str) -> str:
    """Register a new crew member.

    Args:
        name: Full name of the crew member.
        role: One of 'driver', 'mechanic', 'strategist'.

    Returns:
        The generated crew ID string (e.g. 'crew_1').

    Raises:
        ValueError: If role is invalid or name is empty.
    """
    name = name.strip()
    role = role.strip().lower()

    if not name:
        raise ValueError("Name cannot be empty.")
    if role not in VALID_ROLES:
        raise ValueError(
            f"Invalid role '{role}'. Must be one of: {', '.join(sorted(VALID_ROLES))}."
        )

    crew_id = next_id("crew")
    store["crew"][crew_id] = {
        "name":        name,
        "role":        role,
        "skill_level": 1,       # default skill level
        "available":   True,    # available by default
    }
    return crew_id


def get_member(crew_id: str) -> dict:
    """Return the crew member dict for the given ID.

    Raises:
        KeyError: If crew_id does not exist.
    """
    if crew_id not in store["crew"]:
        raise KeyError(f"Crew member '{crew_id}' not found.")
    return store["crew"][crew_id]


def list_members() -> None:
    """Print all registered crew members to stdout."""
    crew = store["crew"]
    if not crew:
        print("  No crew members registered yet.")
        return

    print(f"\n  {'ID':<10} {'Name':<20} {'Role':<12} {'Skill':>5} {'Available'}")
    print("  " + "-" * 58)
    for cid, m in crew.items():
        avail = "✓" if m["available"] else "✗"
        print(f"  {cid:<10} {m['name']:<20} {m['role']:<12} {m['skill_level']:>5}     {avail}")
