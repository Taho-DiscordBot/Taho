

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
from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from permissions import Permissions
from taho import MissingPermissions

if TYPE_CHECKING:
    from taho import TahoContext
    from typing import Any

__all__ = (
    "has_perm",
)

async def has_perm(ctx: TahoContext, **perms) -> bool:
    """|coro|
    
    A function that checks if the user 
    has all of the permissions necessary.

    The permissions passed in must be exactly like the properties shown under
    :class:`.Permissions`.

    Parameters
    ------------
    ctx: :class:`~taho.TahoContext`
        The context of the command.
    perms: :class:`dict`
        An argument list of permissions to check for.
    
    Raises
    --------
    ~taho.exceptions.MissingPermissions
        If the user does not have all of the permissions.
    
    Returns
    --------
    :class:`bool`
        Whether or not the user has all of the permissions.
    """
    
    invalid = set(perms) - set(Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    if ctx.author.guild_permissions.administrator:
        return True

    user = await ctx.get_user()

    permissions = await user.get_permissions()

    missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

    if not missing:
        return True

    raise MissingPermissions(missing)

