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
import re
from tortoise import exceptions as t_exceptions
from taho.exceptions import BadFormat, DoesNotExist
from taho.enums import InfoType
import json

if TYPE_CHECKING:
    from ..models import BaseModel
    from typing import TypeVar, Tuple

    T = TypeVar("T")
    U = TypeVar("U")

__all__ = (
    "value_from_json",
    "value_to_json",
)

converters = {}

async def _get_converters() -> None:
    global converters
    if converters:
        return
    else:
        from .. import models
        converters = dict([(name, cls) for name, cls in models.__dict__.items() if isinstance(cls, type)])

async def _value_from_json(value: T, fetch: bool = True, silent_error: bool = False) -> U:
    await _get_converters()

    if isinstance(value, (list, tuple)):
        value = [await _value_from_json(v, fetch=False) for v in value]
        if not fetch:
            return value
        else:
            converter_map = {}
            for v in value:
                if not v[0] in converter_map:
                    converter_map[v[0]] = []
                converter_map[v[0]].append(v[1])
            
            new_value = []
            for converter, values in converter_map.items():
                new_value.extend(await converter.filter(pk__in=values))

            new_value = {
                (v.__class__, v.pk): v for v in new_value
            }
            
            return [
                new_value[v] for v in value
            ]
    elif not isinstance(value, str):
        return value
    else:
        regex = r"([A-Za-z]+)\(([0-9]+)+\)"
        match = re.findall(regex, value)
        if not match:
            return value
        else:
            match = match[0]
            converter = converters.get(match[0], None)
            if not converter:
                return value
            elif fetch:
                try:
                    return await converter.get(pk=match[1])
                except t_exceptions.DoesNotExist:
                    if silent_error:
                        return None
                    else:
                        raise DoesNotExist(f"The {converter.__class__.__name__} with the id {match[1]} does not exists.")
            else:
                return converter, int(match[1])

async def value_from_json(json_value: T, fetch: bool = True, silent_error: bool = False) -> U:
    """|coro|
    
    Transform DB objects stored in JSON formats
    to python Objects. If the value is an int, float...
    The function will just return the value.
    The value must meet this format::

        {
            "value": "the_value",
            "type": int, 
        }

    Parameters
    -----------
    value:
        The value to convert.
    fetch: :class:`bool`
        Whether to fetch from the Database (queries) the values.
        If ``False``, it will return the value under this format:
        Tuple[``Converter (DB model)``, ``pk (id, an int)``]
        Default to ``True``.
    silent_error: :class:`bool`
        Whether to raise an error if an object does not exists
        in the DB. If ``True``, an unknown object will be returned
        as ``None``.
        Default to ``False``.
    
    Raises
    -------
    ~taho.exceptions.DoesNotExist
        The value does not exist in the DB.
        Not raised if ``silent_error`` is ``True``.
    
    Returns
    --------
    The value.

    Examples
    ---------

    .. code-block:: python3

        converted_value = await value_from_json("Item(1)", fetch=True)
        >>> converted_value = <Item: 1> (db object)

        converted_value = await value_from_json("Item(1)", fetch=False)
        >>> converted_value = (<Item>, 1)

        json_format = '[["Item(1)", "Item(2)"], ["Cluster(1)", "Cluster(2)"]]'
        value = json.loads(json_format)
        converted_value = await value_from_json(value, fetch=True)
        >>> converted_value = [[<Item: 1>, <Item: 2>], [<Cluster: 1>, <Cluster: 2>]]
        ...

    """
    if isinstance(json_value, str):
        try:
            json_value = json.loads(json_value)
        except json.decoder.JSONDecodeError:
            raise BadFormat("See the function's docs.")
    try:
        value = json_value["value"]
    except IndexError:
        raise BadFormat("See the function's docs.")
    
    type = json_value.get("type", InfoType.other.value)
    type = InfoType(type)
    if type == InfoType.other:
        return await _value_from_json(value, fetch=fetch, silent_error=silent_error)
    else:
        from .converter import convert_to_type
        return convert_to_type(value, type)

def _value_to_json(value: T) -> Tuple[str, InfoType]:
    if isinstance(value, (list, tuple)):
        value = [_value_to_json(v)[0] for v in value]
        type = InfoType.other

    else:
        from .converter import get_type
        from taho.database.models import BaseModel
        type = get_type(value)
        if type == InfoType.other:
            if isinstance(value, BaseModel):
                value = f"{value.__class__.__name__}({value.pk})"
        
    return value, type

def value_to_json(value: T) -> str:
    value, type = _value_to_json(value)
    return json.dumps({
            "value": value,
            "type": type.value
        })

