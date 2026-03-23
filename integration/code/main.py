"""
StreetRace Manager – CLI entrypoint.
Provides an interactive menu. Each module is imported and wired
into the corresponding sub-menu as it is implemented.
"""

import sys

# Module Imports
import registration
import crew_management

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

MENU_OPTIONS = {
    "1": ("Registration",       menu_registration),
    "2": ("Crew Management",    menu_crew),
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
