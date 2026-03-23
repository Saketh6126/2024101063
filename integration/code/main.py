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

def main():
    while True:
        banner()
        print("  0. Exit")
        print(DIVIDER)
        choice = input("Select: ").strip()

        if choice == "0":
            print("\nRide safe. 🏁\n")
            sys.exit(0)
        else:
            print("\nInvalid choice.")
            pause()


if __name__ == "__main__":
    main()
