# flights_data.py
from sqlalchemy import create_engine, text

# Define the database URL
DATABASE_URL = "sqlite:///data/flights.sqlite3"

# Create the engine
engine = create_engine(DATABASE_URL)

# Queries
QUERY_FLIGHT_BY_ID = """
SELECT flights.*,
       airlines.airline AS AIRLINE,
       flights.ID as FLIGHT_ID,
       flights.DEPARTURE_DELAY as DELAY
FROM flights
JOIN airlines ON flights.airline = airlines.id
WHERE flights.ID = :id
"""

QUERY_FLIGHTS_BY_DATE = """
SELECT flights.*,
       airlines.airline AS AIRLINE,
       flights.ID as FLIGHT_ID,
       flights.DEPARTURE_DELAY as DELAY
FROM flights
JOIN airlines ON flights.airline = airlines.id
WHERE flights.day = :day
AND flights.month = :month
AND flights.year = :year
"""

QUERY_DELAYED_BY_AIRLINE = """
SELECT flights.*,
       airlines.airline AS AIRLINE,
       flights.ID as FLIGHT_ID,
       flights.DEPARTURE_DELAY as DELAY
FROM flights
JOIN airlines ON flights.airline = airlines.id
WHERE airlines.airline LIKE :airline
AND flights.DEPARTURE_DELAY IS NOT NULL
AND flights.DEPARTURE_DELAY >= 20
"""

QUERY_DELAYED_BY_AIRPORT = """
SELECT flights.*,
       airlines.airline AS AIRLINE,
       flights.ID as FLIGHT_ID,
       flights.DEPARTURE_DELAY as DELAY
FROM flights
JOIN airlines ON flights.airline = airlines.id
WHERE flights.ORIGIN_AIRPORT = :iata
AND flights.DEPARTURE_DELAY IS NOT NULL
AND flights.DEPARTURE_DELAY >= 20
"""

QUERY_ALL_FLIGHTS = """
SELECT airlines.airline AS AIRLINE,
       flights.DEPARTURE_DELAY AS DELAY
FROM flights
JOIN airlines ON flights.airline = airlines.id
"""

QUERY_DEPARTURE_TIMES_AND_DELAYS = """
SELECT CAST(DEPARTURE_TIME / 100 AS INTEGER) AS HOUR,
       DEPARTURE_DELAY AS DELAY
FROM flights
WHERE DEPARTURE_TIME IS NOT NULL
"""

def execute_query(query, params):
    """
    Execute an SQL query with parameters provided in a dictionary.

    Args:
        query (str): SQL query string with placeholders.
        params (dict): Dictionary of parameters to bind to the query.

    Returns:
        list: A list of result rows (SQLAlchemy Row objects),
              or an empty list if an error occurs.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            return result.fetchall()
    except Exception as e:
        print("Query error:", e)
        return []

def get_flight_by_id(flight_id):
    """
    Retrieve a single flight by its flight ID.

    Args:
        flight_id (int): The ID of the flight.

    Returns:
        list: A list containing one result row, or empty if not found.
    """
    params = {'id': flight_id}
    return execute_query(QUERY_FLIGHT_BY_ID, params)

def get_flights_by_date(day, month, year):
    """
    Retrieve all flights scheduled on a specific date.

    Args:
        day (int): Day of the month (1-31).
        month (int): Month (1-12).
        year (int): Full year (e.g., 2025).

    Returns:
        list: A list of flights on that date.
    """
    params = {
        'day': day,
        'month': month,
        'year': year
    }
    return execute_query(QUERY_FLIGHTS_BY_DATE, params)

def get_delayed_flights_by_airline(airline):
    """
    Retrieve all flights delayed by 20 minutes or more
    for a specific airline.

    Args:
        airline (str): Airline name (partial or full).

    Returns:
        list: A list of delayed flights matching the airline.
    """
    params = {'airline': f"%{airline}%"}
    return execute_query(QUERY_DELAYED_BY_AIRLINE, params)

def get_delayed_flights_by_airport(iata):
    """
    Retrieve all flights delayed by 20 minutes or more
    departing from a given airport.

    Args:
        iata (str): 3-letter IATA code of the origin airport.

    Returns:
        list: A list of delayed flights from the specified airport.
    """
    params = {'iata': iata.upper()}
    return execute_query(QUERY_DELAYED_BY_AIRPORT, params)

def get_all_flights():
    """
    Retrieves all flights with airline and delay info.

    Returns:
        list: A list of rows, each containing 'AIRLINE' and 'DELAY'.
    """
    return execute_query(QUERY_ALL_FLIGHTS, {})

def get_departure_times_and_delays():
    """
    Retrieve departure hour and delay for all flights with departure times.

    Returns:
        list: Rows with 'HOUR' and 'DELAY' columns.
    """
    return execute_query(QUERY_DEPARTURE_TIMES_AND_DELAYS, {})
