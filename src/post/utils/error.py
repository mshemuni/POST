class CommandError(Exception):
    """Raised when a command raises an error"""


class AlreadyExist(Exception):
    """Raised when already exist"""


class Nope(Exception):
    """Someone trying to inject!"""


class NotFound(Exception):
    """Something was not found"""


class NumberOfElementsError(Exception):
    """Insufficient number of elements"""
