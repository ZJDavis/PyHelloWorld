# main.py

import pkgutil
import importlib
import inspect
from PyProgramBase import ProgramBase


def discover_programs():
    """Auto-load all ProgramBase subclasses from modules starting with 'Py'."""
    programs = []
    package = "programs"

    # iterate through modules inside 'programs'
    for loader, module_name, _ in pkgutil.iter_modules([package]):
        # only load modules beginning with "Py"
        if not module_name.startswith("Py"):
            continue

        module = importlib.import_module(f"{package}.{module_name}")

        # inspect module for subclasses of ProgramBase
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, ProgramBase) and obj is not ProgramBase:
                programs.append(obj)

    return programs


def build_menu(program_classes):
    """Map numbers → (label, class)."""
    menu = {}
    for i, cls in enumerate(program_classes, start=1):
        menu[i] = (cls.__name__, cls)
    return menu


def show_menu(menu):
    print("""
========================
        MAIN MENU
========================
""")
    for number, (label, _) in menu.items():
        print(f"{number}. {label}")
    print("0. Exit\n")


def main():
    program_classes = discover_programs()
    menu = build_menu(program_classes)

    while True:
        show_menu(menu)
        choice = input("Enter option: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        if not choice.isdigit() or int(choice) not in menu:
            print("Invalid selection.\n")
            continue

        _, program_cls = menu[int(choice)]
        instance = program_cls()
        instance.run()

        print("\n--- Finished ---\n")


if __name__ == "__main__":
    main()

