"""
garage.py
---------
Module 8 (Extra) – Garage / Maintenance
Formally manages car repair events. Requires an available mechanic
and deducts a repair cost from the cash balance.
Business rules:
  - Only damaged cars can be repaired (not 'good' or 'wrecked').
  - The assigned mechanic must be registered and available.
  - Repair costs cash; balance cannot go negative.
  - Completing a repair restores the car to 'good' condition.
"""

from datetime import datetime
from data_store import store
from registration import get_member
import inventory as inv

REPAIR_COST = 500.0   # flat repair cost per car


def schedule_repair(car_id: str, mechanic_id: str) -> None:
    """Schedule a repair for a damaged car.

    Args:
        car_id:      ID of the car to repair (must be 'damaged').
        mechanic_id: ID of the mechanic (must have 'mechanic' role & be available).

    Raises:
        KeyError:   If car or mechanic not found.
        ValueError: If car is not damaged, mechanic has wrong role,
                    mechanic is unavailable, or insufficient funds.
    """
    car = inv.get_car(car_id)

    if car["condition"] == "good":
        raise ValueError(f"Car '{car['name']}' is already in good condition.")
    if car["condition"] == "wrecked":
        raise ValueError(
            f"Car '{car['name']}' is wrecked and cannot be repaired. "
            f"Remove it from inventory instead."
        )

    mechanic = get_member(mechanic_id)
    if mechanic["role"] != "mechanic":
        raise ValueError(
            f"'{mechanic['name']}' has role '{mechanic['role']}', not 'mechanic'."
        )
    if not mechanic["available"]:
        raise ValueError(
            f"Mechanic '{mechanic['name']}' is currently unavailable."
        )
    if inv.get_cash() < REPAIR_COST:
        raise ValueError(
            f"Insufficient funds for repair. "
            f"Cost: ${REPAIR_COST:.2f}, Balance: ${inv.get_cash():.2f}."
        )

    # Mark mechanic as busy and deduct repair cost
    store["crew"][mechanic_id]["available"] = False
    inv.update_cash(-REPAIR_COST)

    # Log the repair event
    store["garage_log"].append({
        "car_id":      car_id,
        "car_name":    car["name"],
        "mechanic_id": mechanic_id,
        "mechanic_name": mechanic["name"],
        "cost":        REPAIR_COST,
        "status":      "in_progress",
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M"),
    })

    print(
        f"  🔧 Repair scheduled for '{car['name']}' "
        f"by {mechanic['name']}. Cost: ${REPAIR_COST:.2f}"
    )


def complete_repair(car_id: str) -> None:
    """Mark the most recent in-progress repair for a car as completed.

    Restores the car to 'good' condition and frees the mechanic.

    Raises:
        KeyError:   If car not found.
        ValueError: If no in-progress repair exists for this car.
    """
    inv.get_car(car_id)  # validate car exists

    # Find the latest in-progress repair for this car
    repair = None
    for entry in reversed(store["garage_log"]):
        if entry["car_id"] == car_id and entry["status"] == "in_progress":
            repair = entry
            break

    if repair is None:
        raise ValueError(
            f"No in-progress repair found for car '{car_id}'. "
            f"Schedule a repair first."
        )

    # Restore car and free mechanic
    inv.update_car_condition(car_id, "good")
    mechanic_id = repair["mechanic_id"]
    if mechanic_id in store["crew"]:
        store["crew"][mechanic_id]["available"] = True

    repair["status"] = "completed"
    print(
        f"  ✓ Repair completed. '{repair['car_name']}' restored to good condition. "
        f"Mechanic '{repair['mechanic_name']}' is now available."
    )


def list_garage_log() -> None:
    """Print all garage maintenance events."""
    log = store["garage_log"]
    if not log:
        print("  Garage log is empty.")
        return

    print(f"\n  {'Car':<10} {'Car Name':<18} {'Mechanic':<12} {'Cost':>7} {'Status':<12} {'Time'}")
    print("  " + "-" * 68)
    for entry in log:
        print(
            f"  {entry['car_id']:<10} {entry['car_name']:<18} "
            f"{entry['mechanic_name']:<12} ${entry['cost']:>6.2f} "
            f"{entry['status']:<12} {entry['timestamp']}"
        )
