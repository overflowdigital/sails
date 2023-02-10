from datetime import datetime


def years_since(date: datetime) -> int:
    """Calculate the number of years between a given date and the current date.

    :param date: The date to calculate the difference from.
    :type date: datetime
    :return: The number of years between the given date and the current date.
    :rtype: int
    """
    today = datetime.today()
    return today.year - date.year - ((today.month, today.day) < (date.month, date.day))
