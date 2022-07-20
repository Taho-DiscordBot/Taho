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

class Shortcutable:
    """A base class for shortcutables.
    """

class StuffShortcutable(Shortcutable):
    """An ABC that brings together all the models that can be pointed 
    by a :class:`~taho.database.models.StuffShortcut`.

    See :ref:`Shortcuts <shortcut>` for more information.

    The following classes implement this ABC:

    - :class:`~taho.database.models.Item`
    - :class:`~taho.database.models.Stat`
    - :class:`~taho.database.models.Currency`
    - :class:`~taho.database.models.Role`
    - :class:`~taho.database.models.Inventory`
    """

class OwnerShortcutable:
    """An ABC that brings together all the models that can be pointed 
    by a :class:`~taho.database.models.OwnerShortcut`.

    See :ref:`Shortcuts <shortcut>` for more information.

    The following classes implement this ABC:

    - :class:`~taho.database.models.User`
    """

class AccessShortcutable(Shortcutable):
    """An ABC that brings together all the models that can be pointed 
    by a :class:`~taho.database.models.AccessShortcut`.

    See :ref:`Shortcuts <shortcut>` for more information.

    The following classes implement this ABC:

    - :class:`~taho.database.models.User`
    - :class:`~taho.database.models.Role`
    """

class TradeStuffShortcutable(Shortcutable):
    """An ABC that brings together all the models that can be pointed 
    by a :class:`~taho.database.models.TradeStuffShortcut`.

    See :ref:`Shortcuts <shortcut>` for more information.

    The following classes implement this ABC:

    - :class:`~taho.database.models.Inventory`
    """