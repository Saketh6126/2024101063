"""
results.py
----------
Module 5 – Results
Records race outcomes, updates driver rankings, handles prize money,
and marks cars as damaged.
Business rules:
  - Recording a result updates the cash balance via Inventory.
  - If a car is damaged, its condition is updated in Inventory.
  - The driver is freed (set available=True) after the race.
"""

from data_store import store
import inventory as inv


def _get_race(race_id: str) -> dict:
    if race_id not in store["races"]:
        raise KeyError(f"Race '{race_id}' not found.")
    return store["races"][race_id]


def record_result(race_id: str, position: int, prize: float) -> None:
    """Record the outcome of a completed race.

    Args:
        race_id:  ID of the race (must be 'in_progress').
        position: Finishing position (1 = 1st place).
        prize:    Prize money won (added to cash balance).

    Raises:
        KeyError:   If race not found.
        ValueError: If race is not in_progress, or position/prize invalid.
    """
    race = _get_race(race_id)
    if race["status"] != "in_progress":
        raise ValueError(
            f"Race '{race_id}' is '{race['status']}', not 'in_progress'. "
            f"Start the race first."
        )
    if position < 1:
        raise ValueError("Position must be 1 or greater.")
    if prize < 0:
        raise ValueError("Prize money cannot be negative.")

    driver_id = race["driver_id"]
    car_id    = race["car_id"]

    # ── Award prize money ────────────────────────────────────────────────────
    inv.update_cash(prize)

    # ── Update driver ranking ────────────────────────────────────────────────
    # Points: 10 for 1st, 7 for 2nd, 5 for 3rd, 3 for 4th, 1 for 5th+
    points_table = {1: 10, 2: 7, 3: 5, 4: 3}
    points = points_table.get(position, 1)
    update_ranking(driver_id, points)

    # ── Free the driver ──────────────────────────────────────────────────────
    store["crew"][driver_id]["available"] = True

    # ── Mark race completed ──────────────────────────────────────────────────
    race["status"] = "completed"

    # ── Log result ──────────────────────────────────────────────────────────
    store["results"].append({
        "race_id":     race_id,
        "race_name":   race["name"],
        "driver_id":   driver_id,
        "car_id":      car_id,
        "position":    position,
        "prize":       prize,
        "car_damaged": False,   # updated separately via handle_car_damage
    })

    print(
        f"  Result recorded: Position #{position}, "
        f"Prize ${prize:.2f}, Points +{points}"
    )


def update_ranking(driver_id: str, points: int) -> None:
    """Add points to a driver's total ranking score.

    Raises:
        KeyError: If driver_id not in crew.
    """
    if driver_id not in store["crew"]:
        raise KeyError(f"Driver '{driver_id}' not found in crew.")
    current = store["rankings"].get(driver_id, 0)
    store["rankings"][driver_id] = current + points


def handle_car_damage(race_id: str, damaged: bool) -> None:
    """Mark the car used in a race as damaged (or not).

    Should be called after record_result since it needs race["car_id"].

    Raises:
        KeyError:   If race not found.
        ValueError: If race is still pending (hasn't started).
    """
    race = _get_race(race_id)
    car_id = race.get("car_id")
    if car_id is None:
        raise ValueError(f"Race '{race_id}' has no car assigned.")

    if damaged:
        inv.update_car_condition(car_id, "damaged")
        # Update the damage flag in the last result for this race
        for result in reversed(store["results"]):
            if result["race_id"] == race_id:
                result["car_damaged"] = True
                break


def list_results() -> None:
    """Print all recorded race results."""
    results = store["results"]
    if not results:
        print("  No results recorded yet.")
        return

    print(f"\n  {'Race':<10} {'Name':<20} {'Driver':<10} {'Pos':>4} {'Prize':>8} {'Damaged'}")
    print("  " + "-" * 60)
    for r in results:
        dmg = "⚠ YES" if r["car_damaged"] else "No"
        print(
            f"  {r['race_id']:<10} {r['race_name']:<20} "
            f"{r['driver_id']:<10} {r['position']:>4} "
            f"${r['prize']:>7.2f} {dmg}"
        )


def get_leaderboard() -> None:
    """Print driver rankings sorted by total points (descending)."""
    rankings = store["rankings"]
    if not rankings:
        print("  No rankings available yet.")
        return

    sorted_rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)

    print(f"\n  🏆 LEADERBOARD")
    print(f"  {'Rank':<6} {'Driver ID':<12} {'Name':<20} {'Points':>7}")
    print("  " + "-" * 48)
    for rank, (driver_id, points) in enumerate(sorted_rankings, start=1):
        name = store["crew"].get(driver_id, {}).get("name", "Unknown")
        print(f"  {rank:<6} {driver_id:<12} {name:<20} {points:>7}")
