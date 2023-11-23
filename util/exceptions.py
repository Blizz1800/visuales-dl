"""Module for define Exceptions"""
class BadParameterException(Exception):
    """Throws when a parametter error appears

    Args:
        Exception (string): Error message
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        