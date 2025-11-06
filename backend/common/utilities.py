"""
Common utility functions used across the application.
"""


def round_to_pt5(value):
    """
    Round a number to the nearest 0.5.

    Examples:
        5.3 -> 5.5
        5.2 -> 5.0
        5.75 -> 6.0
        4.0 -> 4.0

    Args:
        value: The number to round

    Returns:
        The rounded value to the nearest 0.5
    """
    return round(value * 2) / 2
