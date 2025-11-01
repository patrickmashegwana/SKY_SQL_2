# main.py
import flights_data
from datetime import datetime
import sqlalchemy
import csv
import matplotlib.pyplot as plt
import plotting

IATA_LENGTH = 3

def delayed_flights_by_airline():
    """
    Asks the user for a textual airline name (any string will work here).
    Then runs the query using the data object method "get_delayed_flights_by_airline".
    When results are back, calls "print_results" to show them to on the screen.
    """
    airline_input = input("Enter airline name: ").strip()
    results = flights_data.get_delayed_flights_by_airline(airline_input)
    # Create a safe filename hint
    safe_airline = airline_input.strip().lower().replace(" ", "_")
    filename_hint = f"delayed_by_{safe_airline}.csv"
    print_results(results, filename_hint=filename_hint)


def delayed_flights_by_airport():
    """
    Asks the user for a textual IATA 3-letter airport code (loops until input is valid).
    Then runs the query using the data object method "get_delayed_flights_by_airport".
    When results are back, calls "print_results" to show them to on the screen.
    """
    valid = False
    while not valid:
        airport_input = input("Enter origin airport IATA code: ").strip().upper()
        if airport_input.isalpha() and len(airport_input) == IATA_LENGTH:
            valid = True
    results = flights_data.get_delayed_flights_by_airport(airport_input)
    filename_hint = f"delayed_from_{airport_input.upper()}.csv"
    print_results(results, filename_hint=filename_hint)


def flight_by_id():
    """
    Asks the user for a numeric flight ID,
    Then runs the query using the data object method "get_flight_by_id".
    When results are back, calls "print_results" to show them to on the screen.
    """
    valid = False
    while not valid:
        try:
            id_input = int(input("Enter flight ID: "))
        except Exception:
            print("Try again...")
        else:
            valid = True
    results = flights_data.get_flight_by_id(id_input)
    filename_hint = f"flight_{id_input}.csv"
    print_results(results, filename_hint=filename_hint)


def flights_by_date():
    """
    Asks the user for date input (and loops until it's valid),
    Then runs the query using the data object method "get_flights_by_date".
    When results are back, calls "print_results" to show them to on the screen.
    """
    valid = False
    while not valid:
        try:
            date_input = input("Enter date in DD/MM/YYYY format: ")
            date = datetime.strptime(date_input, '%d/%m/%Y')
        except ValueError as e:
            print("Try again...", e)
        else:
            valid = True
    results = flights_data.get_flights_by_date(date.day, date.month, date.year)
    filename_hint = f"flights_on_{date.strftime('%Y%m%d')}.csv"
    print_results(results, filename_hint=filename_hint)


def print_results(results, filename_hint=None):
    """
    Displays a list of flight results (from SQLAlchemy queries) in the terminal.

    Each result must be a dictionary-like object containing the keys:
    'ID', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT', 'AIRLINE', and 'DELAY'.
    If the delay is null, it is treated as 0.

    After displaying the results, prompts the user to optionally export the data
    to a CSV file using Python's built-in csv module.

    Parameters:
        results (list): A list of SQLAlchemy row objects (or similar) with the required fields.
        filename_hint (str, optional): Suggested filename for exporting the data.
    """

    print(f"Got {len(results)} results.")
    if not results:
        return

    rows = []

    for result in results:
        result = result._mapping
        try:
            delay = int(result['DELAY']) if result['DELAY'] else 0
            origin = result['ORIGIN_AIRPORT']
            dest = result['DESTINATION_AIRPORT']
            airline = result['AIRLINE']
        except (ValueError, sqlalchemy.exc.SQLAlchemyError) as e:
            print("Error showing results: ", e)
            return

        if delay and delay > 0:
            print(f"{result['ID']}. {origin} -> {dest} by {airline}, Delay: {delay} Minutes")
        else:
            print(f"{result['ID']}. {origin} -> {dest} by {airline}")

        row = {
            "ID": result['ID'],
            "Origin": origin,
            "Destination": dest,
            "Airline": airline,
            "Delay": delay
        }

        rows.append(row)

    export_choice = input("Would you like to export this data to a CSV file? (y/n): ").strip().lower()
    if export_choice == 'y':
        if filename_hint:
            use_hint = input(f"Use suggested filename '{filename_hint}'? (y/n): ").strip().lower()
            if use_hint == 'y':
                filename = filename_hint
            else:
                filename = input("Enter filename (e.g. results.csv): ").strip()
        else:
            filename = input("Enter filename (e.g. results.csv): ").strip()

        # Ensure filename ends with .csv
        if not filename.lower().endswith('.csv'):
            filename += '.csv'

        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
                fieldnames = ["ID", "Origin", "Destination", "Airline", "Delay"]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Failed to write CSV: {e}")


def plot_delayed_by_airline():
    plotting.delayed_percentage_per_airline()


def plot_delayed_by_hour():
    plotting.delayed_percentage_per_hour()


def show_menu_and_get_input():
    """
    Show the menu and get user input.
    If it's a valid option, return a pointer to the function to execute.
    Otherwise, keep asking the user for input.
    """
    print("Menu:")
    for key, value in FUNCTIONS.items():
        print(f"{key}. {value[1]}")

    # Input loop
    while True:
        try:
            choice = int(input())
            if choice in FUNCTIONS:
                return FUNCTIONS[choice][0]
        except ValueError as e:
            pass
        print("Try again...")

"""
Function Dispatch Dictionary
"""
FUNCTIONS = { 1: (flight_by_id, "Show flight by ID"),
              2: (flights_by_date, "Show flights by date"),
              3: (delayed_flights_by_airline, "Delayed flights by airline"),
              4: (delayed_flights_by_airport, "Delayed flights by origin airport"),
              5: (plot_delayed_by_airline, "Graph: Delayed flight % per airline"),
              6: (plot_delayed_by_hour, "Graph: Delayed flight % per hour of day"),
              7: (quit, "Exit")
             }


def main():

    # The Main Menu loop
    while True:
        choice_func = show_menu_and_get_input()
        choice_func()


if __name__ == "__main__":
    main()