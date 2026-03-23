"""
StreetRace Manager – CLI entrypoint.
Provides an interactive menu. Each module is imported and wired
into the corresponding sub-menu as it is implemented.
"""

import sys

# Module Imports
import registration
import crew_management
import inventory
import race_management

# Helpers
DIVIDER = "─" * 40

def banner():
    print("\n" + DIVIDER)
    print("  S T R E E T R A C E   M A N A G E R")
    print(DIVIDER)

def pause():
    input("\nPress Enter to continue...")

def clear():
    print("\n" * 2)

# Sub-menus
def menu_registration():
    while True:
        print(f"\n{DIVIDER}")
        print(" [1] REGISTRATION")
        print(DIVIDER)
        print("  1. Register new crew member")
        print("  2. List all crew members")
        print("  0. Back")
        choice = input("Choice: ").strip()

        if choice == "1":
            name = input("Name: ").strip()
            role = input("Role (driver/mechanic/strategist): ").strip().lower()
            try:
                mid = registration.register_member(name, role)
                print(f"  ✓ Registered '{name}' as {role} [{mid}]")
            except ValueError as e:
                print(f"  ✗ {e}")

        elif choice == "2":
            registration.list_members()

        elif choice == "0":
            break
        else:
            print("  Invalid choice.")
        pause()

def menu_crew():
    while True:
        print(f"\n{DIVIDER}")
        print(" [2] CREW MANAGEMENT")
        print(DIVIDER)
        print("  1. Assign role to member")
        print("  2. Update skill level")
        print("  3. Set availability")
        print("  4. List crew by role")
        print("  5. List available drivers")
        print("  0. Back")
        choice = input("Choice: ").strip()

        if choice == "1":
            cid = input("Crew ID: ").strip()
            role = input("New Role (driver/mechanic/strategist): ").strip().lower()
            try:
                crew_management.assign_role(cid, role)
                print(f"  ✓ Role updated.")
            except (KeyError, ValueError) as e:
                print(f"  ✗ {e}")

        elif choice == "2":
            cid = input("Crew ID: ").strip()
            try:
                lvl = int(input("Skill Level (1-10): ").strip())
                crew_management.update_skill(cid, lvl)
                print(f"  ✓ Skill updated.")
            except (KeyError, ValueError) as e:
                print(f"  ✗ {e}")

        elif choice == "3":
            cid = input("Crew ID: ").strip()
            avail = input("Available? (y/n): ").strip().lower() == "y"
            try:
                crew_management.set_availability(cid, avail)
                print(f"  ✓ Availability updated.")
            except KeyError as e:
                print(f"  ✗ {e}")

        elif choice == "4":
            role = input("Role: ").strip().lower()
            crew_management.list_by_role(role)

        elif choice == "5":
            crew_management.get_available_drivers()

        elif choice == "0":
            break
        else:
            print("  Invalid choice.")
        pause()

def menu_inventory():
    while True:
        print(f"\n{DIVIDER}")
        print(" [3] INVENTORY")
        print(DIVIDER)
        print("  1. Add car")
        print("  2. Add spare part")
        print("  3. Add tool")
        print("  4. View cash balance")
        print("  5. Update cash")
        print("  6. List full inventory")
        print("  0. Back")
        choice = input("Choice: ").strip()

        if choice == "1":
            name = input("Car name: ").strip()
            try:
                speed = int(input("Speed rating (1-10): ").strip())
                cond = input("Condition (good/damaged/wrecked): ").strip().lower()
                cid = inventory.add_car(name, speed, cond)
                print(f"  ✓ Car added [{cid}]")
            except ValueError as e:
                print(f"  ✗ {e}")

        elif choice == "2":
            name = input("Part name: ").strip()
            qty = int(input("Quantity: ").strip())
            car_id = input("Linked car ID (or blank): ").strip() or None
            pid = inventory.add_part(name, qty, car_id)
            print(f"  ✓ Part added [{pid}]")

        elif choice == "3":
            tool = input("Tool name: ").strip()
            inventory.add_tool(tool)
            print(f"  ✓ Tool added.")

        elif choice == "4":
            print(f"  Cash: ${inventory.get_cash()}")

        elif choice == "5":
            try:
                amt = float(input("Amount (+/-): ").strip())
                inventory.update_cash(amt)
                print(f"  ✓ Cash updated. New balance: ${inventory.get_cash()}")
            except ValueError as e:
                print(f"  ✗ {e}")

        elif choice == "6":
            inventory.list_inventory()

        elif choice == "0":
            break
        else:
            print("  Invalid choice.")
        pause()

def menu_race():
    while True:
        print(f"\n{DIVIDER}")
        print(" [4] RACE MANAGEMENT")
        print(DIVIDER)
        print("  1. Create race")
        print("  2. Assign driver to race")
        print("  3. Assign car to race")
        print("  4. Start race")
        print("  5. List races")
        print("  0. Back")
        choice = input("Choice: ").strip()

        if choice == "1":
            name = input("Race name: ").strip()
            track = input("Track: ").strip()
            try:
                rid = race_management.create_race(name, track)
                print(f"  ✓ Race created [{rid}]")
            except ValueError as e:
                print(f"  ✗ {e}")

        elif choice == "2":
            rid = input("Race ID: ").strip()
            did = input("Driver ID: ").strip()
            try:
                race_management.assign_driver(rid, did)
                print(f"  ✓ Driver assigned.")
            except (KeyError, ValueError) as e:
                print(f"  ✗ {e}")

        elif choice == "3":
            rid = input("Race ID: ").strip()
            cid = input("Car ID: ").strip()
            try:
                race_management.assign_car(rid, cid)
                print(f"  ✓ Car assigned.")
            except (KeyError, ValueError) as e:
                print(f"  ✗ {e}")

        elif choice == "4":
            rid = input("Race ID: ").strip()
            try:
                race_management.start_race(rid)
                print(f"  ✓ Race started!")
            except (KeyError, ValueError) as e:
                print(f"  ✗ {e}")

        elif choice == "5":
            race_management.list_races()

        elif choice == "0":
            break
        else:
            print("  Invalid choice.")
        pause()

MENU_OPTIONS = {
    "1": ("Registration",       menu_registration),
    "2": ("Crew Management",    menu_crew),
    "3": ("Inventory",          menu_inventory),
    "4": ("Race Management",    menu_race)
}

def main():
    while True:
        banner()
        print("  0. Exit")
        print(DIVIDER)
        choice = input("Select: ").strip()

        if choice == "0":
            print("\nRide safe. 🏁\n")
            sys.exit(0)
        elif choice in MENU_OPTIONS:
            clear()
            MENU_OPTIONS[choice][1]()
        else:
            print("\nInvalid choice.")
            pause()

if __name__ == "__main__":
    main()
