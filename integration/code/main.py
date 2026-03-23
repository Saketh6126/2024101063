"""
StreetRace Manager – CLI entrypoint.
Provides an interactive menu. Each module is imported and wired
into the corresponding sub-menu as it is implemented.
"""

import sys

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

MENU_OPTIONS = {
    "1": ("Registration",       menu_registration),
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
