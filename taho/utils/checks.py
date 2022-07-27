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

if TYPE_CHECKING:
    from taho import TahoContext
    from typing import Any

__all__ = (
    "check_perm",
)

def check_perm(**perms) -> Any:
    """A :func:`discord.ext.commands.check` that checks 
    if the user has all of the permissions necessary.

    The permissions passed in must be exactly like the properties shown under
    :class:`.Permissions`.

    This check raises a special exception, 
    :exc:`~taho.exceptions.MissingPermissions`.

    Parameters
    ------------
    perms
        An argument list of permissions to check for.

    Example
    ---------

    .. code-block:: python3

        @bot.command()
        @utils.has_perm(item_use=True)
        async def test(ctx):
            await ctx.send('You can use items.')

    """

    invalid = set(perms) - set(Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    async def predicate(ctx: TahoContext):

        from .permission import has_perm
        
        return await has_perm(ctx, **perms)

    return commands.check(predicate)

