"""
race_management.py
------------------
Module 4 – Race Management
Creates races and selects appropriate drivers and cars.
Business rules:
  - Only crew members with the 'driver' role may be entered in a race.
  - A car must exist in inventory with condition != 'wrecked'.
  - Starting a race marks the driver as unavailable.
"""

from data_store import store, next_id
from registration import get_member
import inventory as inv

VALID_STATUSES = {"pending", "in_progress", "completed"}


def create_race(name: str, track: str) -> str:
    """Create a new race entry.

    Args:
        name:  Human-readable race name.
        track: Track/location name.

    Returns:
        Generated race ID (e.g. 'race_1').

    Raises:
        ValueError: If name or track are empty.
    """
    name = name.strip()
    track = track.strip()
    if not name:
        raise ValueError("Race name cannot be empty.")
    if not track:
        raise ValueError("Track name cannot be empty.")

    race_id = next_id("race")
    store["races"][race_id] = {
        "name":      name,
        "track":     track,
        "driver_id": None,
        "car_id":    None,
        "status":    "pending",
    }
    return race_id


def _get_race(race_id: str) -> dict:
    if race_id not in store["races"]:
        raise KeyError(f"Race '{race_id}' not found.")
    return store["races"][race_id]


def assign_driver(race_id: str, driver_id: str) -> None:
    """Assign a driver to a race.

    Raises:
        KeyError:   If race or driver not found.
        ValueError: If driver's role is not 'driver', driver is unavailable,
                    or race is not in 'pending' status.
    """
    race = _get_race(race_id)
    if race["status"] != "pending":
        raise ValueError(f"Cannot assign driver — race is '{race['status']}'.")

    member = get_member(driver_id)
    if member["role"] != "driver":
        raise ValueError(
            f"'{member['name']}' has role '{member['role']}', not 'driver'. "
            f"Only drivers may enter a race."
        )
    if not member["available"]:
        raise ValueError(f"Driver '{member['name']}' is currently unavailable.")

    race["driver_id"] = driver_id


def assign_car(race_id: str, car_id: str) -> None:
    """Assign a car to a race.

    Raises:
        KeyError:   If race or car not found.
        ValueError: If car is wrecked or race is not pending.
    """
    race = _get_race(race_id)
    if race["status"] != "pending":
        raise ValueError(f"Cannot assign car — race is '{race['status']}'.")

    car = inv.get_car(car_id)
    if car["condition"] == "wrecked":
        raise ValueError(
            f"Car '{car['name']}' is wrecked and cannot be used in a race."
        )

    race["car_id"] = car_id


def start_race(race_id: str) -> None:
    """Start a race: validate both driver and car are assigned, mark driver busy.

    Raises:
        KeyError:   If race not found.
        ValueError: If driver or car is not assigned, or race is not pending.
    """
    race = _get_race(race_id)
    if race["status"] != "pending":
        raise ValueError(f"Race is already '{race['status']}'.")
    if race["driver_id"] is None:
        raise ValueError("No driver assigned to this race.")
    if race["car_id"] is None:
        raise ValueError("No car assigned to this race.")

    # Mark driver as unavailable during the race
    store["crew"][race["driver_id"]]["available"] = False
    race["status"] = "in_progress"


def list_races() -> None:
    """Print all races with their current status."""
    races = store["races"]
    if not races:
        print("  No races created yet.")
        return

    print(f"\n  {'ID':<10} {'Name':<20} {'Track':<16} {'Driver':<10} {'Car':<8} {'Status'}")
    print("  " + "-" * 70)
    for rid, r in races.items():
        drv = r["driver_id"] or "—"
        car = r["car_id"] or "—"
        print(
            f"  {rid:<10} {r['name']:<20} {r['track']:<16} "
            f"{drv:<10} {car:<8} {r['status']}"
        )
