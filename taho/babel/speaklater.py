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

class LazyString(object):
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def __getattr__(self, attr):
        if attr == "__setstate__":
            raise AttributeError(attr)

        string = str(self)
        if hasattr(string, attr):
            return getattr(string, attr)

        raise AttributeError(attr)

    def __repr__(self):
        return "l'{0}'".format(str(self))

    def __str__(self):
        return str(self._func(*self._args, **self._kwargs))

    def __len__(self):
        return len(str(self))

    def __getitem__(self, key):
        return str(self)[key]

    def __iter__(self):
        return iter(str(self))

    def __contains__(self, item):
        return item in str(self)

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)

    def __mul__(self, other):
        return str(self) * other

    def __rmul__(self, other):
        return other * str(self)

    def __lt__(self, other):
        return str(self) < other

    def __le__(self, other):
        return str(self) <= other

    def __eq__(self, other):
        return str(self) == other

    def __ne__(self, other):
        return str(self) != other

    def __gt__(self, other):
        return str(self) > other

    def __ge__(self, other):
        return str(self) >= other

    def __html__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def __mod__(self, other):
        return str(self) % other

    def __rmod__(self, other):
        return other + str(self)
