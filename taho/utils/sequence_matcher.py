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
from difflib import SequenceMatcher
import unidecode as ud

if TYPE_CHECKING:
    from typing import List, Union, TypeVar, Callable


    T = TypeVar("T")

__all__ = (
    "sequence_match",
)

async def sequence_match(
    a: str,
    b: List[Union[str, T]],
    *,
    transform: Callable[[Union[str, T]], str] = lambda x: x,
    threshold: float = 0.7,
    max_results: int = 1,
    case_sensitive: bool = False,
    unidecode: bool = False,
) -> Union[Union[str, T], Union[str, T]]:
    """
    Find the best match for a string in a list of strings.
    """

    async def _transform(x: Union[str, T]) -> str:
        x = transform(x)
        if not isinstance(x, str):
            # In case of Foreign key, coroutine...
            x = await x
        if unidecode:
            x = ud.unidecode(x)
        if not case_sensitive:
            x = x.lower()
        return x

    c = {await _transform(x):x for x in b}

    if not case_sensitive:
        a = a.lower()

    if unidecode:
        a = ud.unidecode(a)
    
    results = []
    for x, y in c.items():
        ratio = SequenceMatcher(None, a, x).ratio()
        if ratio >= threshold:
            results.append((ratio, y))

    if not results:
        return None

    results.sort(key=lambda x: x[0], reverse=True)
    return results[0][1] if max_results == 1 else results[:max_results]