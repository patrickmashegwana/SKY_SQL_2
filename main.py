import csv
import os
import time
from datetime import datetime
from typing import Callable, Dict, List, Optional

import sqlalchemy

import flights_data
import plotting

IATA_LENGTH = 3


class Colors:
    """ANSI color codes for CLI output."""
    END = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def type_writer(text: str, delay: float = 0.03) -> None:
    """Print text with a typewriter effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def show_welcome() -> None:
    """Display a colorful welcome message with ASCII logo."""
    clear_screen()
    logo = f"""
{Colors.CYAN}{Colors.BOLD}
  ____  _  ____   __  ____   ___  _
 / ___|| |/ /\ \ / / / ___| / _ \| |
 \___ \| ' /  \ V /  \___ \| | | | |
  ___) | . \   | |    ___) | |_| | |___
 |____/|_|\_\  |_|   |____/ \__\_\_____|
{Colors.END}
"""
    print(logo)
    type_writer(f"{Colors.YELLOW}{Colors.BOLD}Welcome to Sky SQL 2!{Colors.END}", 0.05)
    type_writer(f"{Colors.MAGENTA}Your ultimate flight data analyzer CLI tool.{Colors.END}",
                0.03)
    type_writer(f"{Colors.GREEN}Get ready to explore flight delays, schedules, and "
                "graphs!{Colors.END}\n", 0.03)
    time.sleep(0.5)


def delayed_flights_by_airline() -> None:
    """Show delayed flights filtered by airline."""
    airline_input = input("Enter airline name: ").strip()
    results = flights_data.get_delayed_flights_by_airline(airline_input)
    safe_airline = airline_input.lower().replace(" ", "_")
    filename_hint = f"delayed_by_{safe_airline}.csv"
    print_results(results, filename_hint=filename_hint)


def delayed_flights_by_airport() -> None:
    """Show delayed flights filtered by origin airport IATA code."""
    while True:
        airport_input = input("Enter origin airport IATA code: ").strip().upper()
        if airport_input.isalpha() and len(airport_input) == IATA_LENGTH:
            break
        print("Invalid IATA code. Try again...")
    results = flights_data.get_delayed_flights_by_airport(airport_input)
    filename_hint = f"delayed_from_{airport_input}.csv"
    print_results(results, filename_hint=filename_hint)


def flight_by_id() -> None:
    """Show flight information by flight ID."""
    while True:
        try:
            id_input = int(input("Enter flight ID: "))
            break
        except ValueError:
            print("Invalid ID. Try again...")
    results = flights_data.get_flight_by_id(id_input)
    filename_hint = f"flight_{id_input}.csv"
    print_results(results, filename_hint=filename_hint)


def flights_by_date() -> None:
    """Show flights scheduled on a specific date."""
    while True:
        try:
            date_input = input("Enter date (DD/MM/YYYY): ")
            date = datetime.strptime(date_input, "%d/%m/%Y")
            break
        except ValueError:
            print("Invalid date format. Try again...")
    results = flights_data.get_flights_by_date(date.day, date.month, date.year)
    filename_hint = f"flights_on_{date.strftime('%Y%m%d')}.csv"
    print_results(results, filename_hint=filename_hint)


def print_results(results: List[sqlalchemy.engine.Row],
                  filename_hint: Optional[str] = None) -> None:
    """Display flight results and optionally export to CSV."""
    print(f"\n{Colors.BLUE}Found {len(results)} results.{Colors.END}\n")
    if not results:
        return

    rows: List[Dict[str, str]] = []

    for result in results:
        r = result._mapping
        try:
            delay = int(r['DELAY']) if r['DELAY'] else 0
            origin, dest, airline = (
                r['ORIGIN_AIRPORT'], r['DESTINATION_AIRPORT'], r['AIRLINE']
            )
        except (ValueError, sqlalchemy.exc.SQLAlchemyError) as e:
            print(f"{Colors.RED}Error showing results:{Colors.END} {e}")
            return

        if delay > 0:
            print(f"{Colors.RED}{r['ID']}. {origin} -> {dest} by {airline}, "
                  f"Delay: {delay} min{Colors.END}")
        else:
            print(f"{Colors.GREEN}{r['ID']}. {origin} -> {dest} by {airline}{Colors.END}")

        rows.append({
            "ID": r['ID'],
            "Origin": origin,
            "Destination": dest,
            "Airline": airline,
            "Delay": delay
        })

    export_choice = input("\nExport data to CSV? (y/n): ").strip().lower()
    if export_choice != 'y':
        return

    if filename_hint:
        use_hint = input(f"Use suggested filename '{filename_hint}'? (y/n): ").strip().lower()
        filename = filename_hint if use_hint == 'y' else input("Enter filename: ").strip()
    else:
        filename = input("Enter filename: ").strip()

    if not filename.lower().endswith(".csv"):
        filename += ".csv"

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ["ID", "Origin", "Destination", "Airline", "Delay"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"{Colors.CYAN}Results saved to {filename}{Colors.END}\n")
    except Exception as e:
        print(f"{Colors.RED}Failed to write CSV:{Colors.END} {e}")


def plot_delayed_by_airline() -> None:
    """Plot delayed flight percentages per airline."""
    plotting.delayed_percentage_per_airline()


def plot_delayed_by_hour() -> None:
    """Plot delayed flight percentages per hour of day."""
    plotting.delayed_percentage_per_hour()


def show_menu_and_get_input() -> Callable:
    """Show menu and return the selected function."""
    print(f"{Colors.YELLOW}Menu:{Colors.END}")
    for key, value in FUNCTIONS.items():
        print(f"{Colors.CYAN}{key}. {value[1]}{Colors.END}")

    while True:
        try:
            choice = int(input(f"{Colors.GREEN}Select an option: {Colors.END}"))
            if choice in FUNCTIONS:
                return FUNCTIONS[choice][0]
        except ValueError:
            pass
        print(f"{Colors.RED}Invalid choice. Try again...{Colors.END}")


FUNCTIONS = {
    1: (flight_by_id, "Show flight by ID"),
    2: (flights_by_date, "Show flights by date"),
    3: (delayed_flights_by_airline, "Delayed flights by airline"),
    4: (delayed_flights_by_airport, "Delayed flights by origin airport"),
    5: (plot_delayed_by_airline, "Graph: Delayed flight % per airline"),
    6: (plot_delayed_by_hour, "Graph: Delayed flight % per hour of day"),
    7: (exit, "Exit")
}


def main() -> None:
    """Main loop of the Sky SQL CLI application."""
    show_welcome()
    while True:
        choice_func = show_menu_and_get_input()
        choice_func()


if __name__ == "__main__":
    main()
