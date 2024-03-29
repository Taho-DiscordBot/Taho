"""
The MIT License (MIT)

Copyright (c) 2022-present Taho-DiscordBot

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

__all__ = (
    "TahoException",
    "BadFormat",
    "AlreadyExists",
    "QuantityException",
    "NPCException",
    "RoleException",
    "DoesNotExist",
    "MissingPermissions",
    "ValidationException",
)

class TahoException(Exception):
    """
    Raised when an error occurs in the Taho framework.
    """
    pass

class BadFormat(TahoException):
    """
    Raised when a format is not respected.
    """
    pass

class AlreadyExists(TahoException):
    """
    Raised when an object already exists.
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

class DoesNotExist(TahoException):
    """
    Raised when an object does not exist.
    """
    pass

class MissingPermissions(TahoException):
    """
    Raised when a user is missing permissions.
    """
    pass

class ValidationException(TahoException):
    """
    Raised when a validation fails.
    """
    pass