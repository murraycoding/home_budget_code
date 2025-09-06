from datetime import datetime, date
import re

def format_date(month, day, year = None):
    """
    Returns the date as a date object regardless of the input
    """

    # establishes current year
    try:
        if year is None:
            now = datetime.now()
            year = now.year

        int_year = int(year)
    except ValueError as value_error:
        print(f"Error: Cannot convert year to a integer. ERROR = {value_error}")
        raise value_error
    except Exception as error:
        print(f"Unknown exception occured. ERROR = {error}")
        raise error

    if len(str(year)) == 2:
        int_year = int(year) + 2000

    if int_year < 2000 or int_year > 2100:
        print("Year is out of range.")
        return False

    try:
        int_month = int(month)
        int_day = int(day)
        date_obj = date(int_year, int_month, int_day)
    except ValueError as value_error:
        print(f"Could not convert month or day to integers. ERROR = {value_error}")
        raise value_error

    return date_obj

def extract_date_from_string(string, date_format= 'YYYY-MM-DD'):
    """
    Extracts the date from a string
    """
    try:
        if date_format == 'YYYY-MM-DD':
            date_regex = re.compile(r'(\d{4})-(\d{2})-(\d{2})')
            match = date_regex.search(string)
            if match:
                year, month, day = match.groups()
                return format_date(month, day, year)
        elif date_format == 'MM-DD-YYYY':
            date_regex = re.compile(r'(\d{2})-(\d{2})-(\d{4})')
            match = date_regex.search(string)
            if match:
                month, day, year = match.groups()
                return format_date(month, day, year)
        elif date_format == 'YYYYMMDD':
            print("Testing")
            date_regex = re.compile(r'(\d{4})(\d{2})(\d{2})')
            match = date_regex.search(string)
            if match:
                year, month, day = match.groups()
                return format_date(month, day, year)
        else:
            date_regex = re.compile(r'(\d{2})-(\d{2})-(\d{2})')
            match = date_regex.search(string)
            if match:
                month, day, year = match.groups()
                return format_date(month, day, year)
            
    except Exception as error:
        print(f"An error occurred while extracting the date. ERROR = {error}")
        raise error