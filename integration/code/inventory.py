"""
inventory.py
------------
Module 3 – Inventory
Tracks cars, spare parts, tools, and the global cash balance.
Business rule: Cash balance cannot go below 0.
"""

from data_store import store, next_id

VALID_CONDITIONS = {"good", "damaged", "wrecked"}


def add_car(name: str, speed: int, condition: str = "good") -> str:
    """Add a new car to the inventory.

    Args:
        name:      Car name/model.
        speed:     Speed rating (1–10).
        condition: 'good', 'damaged', or 'wrecked'.

    Returns:
        Generated car ID (e.g. 'car_1').

    Raises:
        ValueError: If speed or condition are invalid.
    """
    name = name.strip()
    condition = condition.strip().lower()

    if not name:
        raise ValueError("Car name cannot be empty.")
    if not (1 <= speed <= 10):
        raise ValueError("Speed must be between 1 and 10.")
    if condition not in VALID_CONDITIONS:
        raise ValueError(
            f"Invalid condition '{condition}'. Use: {', '.join(sorted(VALID_CONDITIONS))}."
        )

    car_id = next_id("car")
    store["cars"][car_id] = {
        "name":      name,
        "speed":     speed,
        "condition": condition,
    }
    return car_id


def get_car(car_id: str) -> dict:
    """Return the car dict for the given ID.

    Raises:
        KeyError: If car_id does not exist.
    """
    if car_id not in store["cars"]:
        raise KeyError(f"Car '{car_id}' not found in inventory.")
    return store["cars"][car_id]


def update_car_condition(car_id: str, condition: str) -> None:
    """Update the condition of a car.

    Raises:
        KeyError:   If car_id not found.
        ValueError: If condition string is invalid.
    """
    car = get_car(car_id)
    condition = condition.strip().lower()
    if condition not in VALID_CONDITIONS:
        raise ValueError(
            f"Invalid condition '{condition}'. Use: {', '.join(sorted(VALID_CONDITIONS))}."
        )
    car["condition"] = condition


def add_part(name: str, qty: int, car_id: str = None) -> str:
    """Add a spare part to inventory, optionally linked to a car.

    Returns:
        Generated part ID (e.g. 'part_1').
    """
    name = name.strip()
    if not name:
        raise ValueError("Part name cannot be empty.")
    if qty < 1:
        raise ValueError("Quantity must be at least 1.")

    part_id = next_id("part")
    store["parts"][part_id] = {
        "name":   name,
        "qty":    qty,
        "car_id": car_id,
    }
    return part_id


def add_tool(tool_name: str) -> None:
    """Add a tool to the tools list."""
    tool_name = tool_name.strip()
    if not tool_name:
        raise ValueError("Tool name cannot be empty.")
    store["tools"].append(tool_name)


def get_cash() -> float:
    """Return current cash balance."""
    return store["cash"]


def update_cash(amount: float) -> None:
    """Add (or subtract) cash from the balance.

    Args:
        amount: Positive to add, negative to subtract.

    Raises:
        ValueError: If the resulting balance would drop below 0.
    """
    new_balance = store["cash"] + amount
    if new_balance < 0:
        raise ValueError(
            f"Insufficient funds. Balance: ${store['cash']:.2f}, "
            f"requested change: ${amount:.2f}."
        )
    store["cash"] = new_balance


def list_inventory() -> None:
    """Print a full inventory report."""
    print(f"\n  {'═' * 42}")
    print(f"  INVENTORY REPORT")
    print(f"  {'═' * 42}")

    # Cash
    print(f"  💰 Cash Balance: ${store['cash']:.2f}")

    # Cars
    print(f"\n  🚗 Cars ({len(store['cars'])})")
    if store["cars"]:
        print(f"  {'ID':<10} {'Name':<20} {'Speed':>5} {'Condition'}")
        print("  " + "-" * 46)
        for cid, c in store["cars"].items():
            print(f"  {cid:<10} {c['name']:<20} {c['speed']:>5}  {c['condition']}")
    else:
        print("  No cars in inventory.")

    # Parts
    print(f"\n  🔧 Spare Parts ({len(store['parts'])})")
    if store["parts"]:
        print(f"  {'ID':<10} {'Name':<20} {'Qty':>5} {'Car'}")
        print("  " + "-" * 46)
        for pid, p in store["parts"].items():
            car = p["car_id"] or "—"
            print(f"  {pid:<10} {p['name']:<20} {p['qty']:>5}  {car}")
    else:
        print("  No spare parts.")

    # Tools
    print(f"\n  🛠  Tools ({len(store['tools'])})")
    if store["tools"]:
        for t in store["tools"]:
            print(f"  • {t}")
    else:
        print("  No tools.")
