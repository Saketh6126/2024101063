"""
analytics.py
------------
Module 7 (Extra) – Analytics
Provides cross-module statistics and insights by aggregating
data from the shared store across all other modules.
"""

from data_store import store


def top_driver() -> None:
    """Print the driver with the highest total ranking points."""
    rankings = store["rankings"]
    if not rankings:
        print("  No ranking data available yet.")
        return

    best_id, best_pts = max(rankings.items(), key=lambda x: x[1])
    name = store["crew"].get(best_id, {}).get("name", "Unknown")
    print(f"\n  🏆 Top Driver: {name} ({best_id}) — {best_pts} points")


def total_earnings() -> None:
    """Print total prize money won across all races."""
    total = sum(r["prize"] for r in store["results"])
    print(f"\n  💰 Total Race Earnings: ${total:.2f}")


def race_win_rate(driver_id: str) -> None:
    """Print the win rate (1st place finishes / total races) for a driver.

    Raises:
        KeyError: If driver_id is not registered.
    """
    if driver_id not in store["crew"]:
        raise KeyError(f"Driver '{driver_id}' not found.")

    driver_results = [r for r in store["results"] if r["driver_id"] == driver_id]
    total = len(driver_results)
    wins  = sum(1 for r in driver_results if r["position"] == 1)

    name = store["crew"][driver_id]["name"]
    if total == 0:
        print(f"  {name} has not competed in any races yet.")
    else:
        rate = (wins / total) * 100
        print(
            f"\n  Driver: {name} ({driver_id})\n"
            f"  Races: {total} | Wins: {wins} | Win Rate: {rate:.1f}%"
        )


def mission_success_rate() -> None:
    """Print the ratio of completed missions to total missions."""
    missions = store["missions"]
    total     = len(missions)
    completed = sum(1 for m in missions.values() if m["status"] == "completed")

    if total == 0:
        print("  No missions created yet.")
    else:
        rate = (completed / total) * 100
        print(
            f"\n  🎯 Mission Stats\n"
            f"  Total: {total} | Completed: {completed} | "
            f"Success Rate: {rate:.1f}%"
        )


def cash_flow_summary() -> None:
    """Print current cash balance alongside total prize money won."""
    current = store["cash"]
    earned  = sum(r["prize"] for r in store["results"])
    mission_rewards = sum(
        m["reward"] for m in store["missions"].values()
        if m["status"] == "completed"
    )
    print(
        f"\n  💵 Cash Flow Summary\n"
        f"  Current Balance:   ${current:.2f}\n"
        f"  Total Race Prizes: ${earned:.2f}\n"
        f"  Mission Rewards:   ${mission_rewards:.2f}\n"
        f"  Grand Total In:    ${earned + mission_rewards:.2f}"
    )
