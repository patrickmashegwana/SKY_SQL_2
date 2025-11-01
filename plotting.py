# plotting.py

import matplotlib.pyplot as plt
import collections
import flights_data


def delayed_percentage_per_airline():
    """
    Generate and save a bar chart showing the percentage
    of delayed flights per airline.
    """
    all_flights = flights_data.get_all_flights()
    if not all_flights:
        print("No flight data available.")
        return

    total_per_airline = collections.Counter()
    delayed_per_airline = collections.Counter()

    for flight in all_flights:
        flight = flight._mapping
        airline = flight['AIRLINE']
        delay = flight['DELAY']

        total_per_airline[airline] += 1
        if delay and delay > 0:
            delayed_per_airline[airline] += 1

    airlines = list(total_per_airline.keys())
    percentages = [
        (delayed_per_airline.get(airline, 0) / total_per_airline[airline]) * 100
        for airline in airlines
    ]

    plt.figure(figsize=(10, 6))
    plt.bar(airlines, percentages, color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Airline")
    plt.ylabel("Percentage of Delayed Flights")
    plt.title("Delayed Flights Percentage per Airline")
    plt.tight_layout()
    filename = "delayed_percentage_per_airline.png"
    plt.savefig(filename)
    plt.close()
    print(f"Chart saved as '{filename}'")


def delayed_percentage_per_hour():
    """
    Generate and save a bar chart showing the percentage of delayed
    flights per hour of the day.
    """
    results = flights_data.get_departure_times_and_delays()

    if not results:
        print("No flight data available.")
        return

    total_per_hour = collections.Counter()
    delayed_per_hour = collections.Counter()

    for row in results:
        row = row._mapping
        hour = row['HOUR']
        delay = row['DELAY']
        if hour is None:
            continue
        total_per_hour[hour] += 1
        if delay and delay > 0:
            delayed_per_hour[hour] += 1

    hours = list(range(25))  # Include 24 to handle 2400 edge case if any
    percentages = []
    for hour in hours:
        total = total_per_hour.get(hour, 0)
        delayed = delayed_per_hour.get(hour, 0)
        percent = (delayed / total) * 100 if total > 0 else 0
        percentages.append(percent)

    plt.figure(figsize=(10, 6))
    plt.bar(hours, percentages, color='coral')
    plt.xticks(hours)
    plt.xlabel("Hour of Day (0-24)")
    plt.ylabel("Percentage of Delayed Flights")
    plt.title("Delayed Flights Percentage per Hour of Day")
    plt.tight_layout()
    filename = "delayed_percentage_per_hour.png"
    plt.savefig(filename)
    plt.close()
    print(f"Chart saved as '{filename}'")


if __name__ == "__main__":
    delayed_percentage_per_airline()
    delayed_percentage_per_hour()
