

__all__ = (
    "TahoException",
    "QuantityException",
    "NPCException",
    "RoleException",
    "Unknown",
)

class TahoException(Exception):
    """
    Raised when an error occurs in the Taho framework.
    """
    pass

class QuantityException(TahoException):
    """
    Raised when a quantity is invalid.
    ex :
    - when you try to create a quantity with a negative value
    - when you try to take an item from an inventory and there not enough items
    - ...
    """
    pass

class NPCException(TahoException):
    """
    Raised when an exception concerns NPCs.
    """
    pass

class RoleException(TahoException):
    """
    Raised when an exception concerns roles.
    """
    pass

class Unknown(TahoException):
    """
    Raised when you are trying to get something
    that doesn't exist.
    """
    pass