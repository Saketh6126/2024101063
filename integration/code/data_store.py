"""
Shared in-memory data store for StreetRace Manager.
All modules import `store` from here — this is the single
source of truth for the entire system.
"""

store = {
    # crew_id (str) -> {name, role, skill_level, available}
    "crew": {},

    # car_id (str) -> {name, speed, condition}
    # condition: "good" | "damaged" | "wrecked"
    "cars": {},

    # part_id (str) -> {name, qty, car_id (optional)}
    "parts": {},

    # list of tool name strings
    "tools": [],

    # global cash balance (int/float)
    "cash": 0,

    # race_id (str) -> {name, track, driver_id, car_id, status}
    # status: "pending" | "in_progress" | "completed"
    "races": {},

    # list of result dicts:
    # {race_id, driver_id, car_id, position, prize, car_damaged}
    "results": [],

    # driver_id (str) -> total ranking points (int)
    "rankings": {},

    # mission_id (str) -> {type, required_roles, status, assigned_crew, reward}
    # status: "pending" | "active" | "completed" | "failed"
    "missions": {},

    # list of garage event dicts:
    # {car_id, mechanic_id, cost, timestamp, status}
    "garage_log": [],
}

# ID counters (auto-increment)
_counters = {
    "crew":    0,
    "car":     0,
    "part":    0,
    "race":    0,
    "mission": 0,
}


def next_id(entity: str) -> str:
    """Return the next sequential ID string for an entity type.

    Args:
        entity: one of 'crew', 'car', 'part', 'race', 'mission'

    Returns:
        A string like 'crew_1', 'car_3', etc.
    """
    _counters[entity] += 1
    return f"{entity}_{_counters[entity]}"


def reset_store() -> None:
    """Reset the store and counters to a clean state.
    Useful for testing without side-effects between test runs.
    """
    store["crew"].clear()
    store["cars"].clear()
    store["parts"].clear()
    store["tools"].clear()
    store["cash"] = 0
    store["races"].clear()
    store["results"].clear()
    store["rankings"].clear()
    store["missions"].clear()
    store["garage_log"].clear()
    for key in _counters:
        _counters[key] = 0
