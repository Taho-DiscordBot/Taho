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

This code is based on the work of the flask_babel project:
https://pypi.org/project/Flask-Babel/
And the Py18n project:
https://pypi.org/project/Py18n/
"""
from __future__ import annotations
import contextvars
import os
from typing import TYPE_CHECKING
from babel import support, Locale

from .speaklater import LazyString

if TYPE_CHECKING:
    from typing import Dict, Tuple, Generator
    from taho import Bot

__all__ = (
    "Domain",
    "Babel",
    "get_domain",
    "gettext",
    "discord_translator_gettext",
    "_",
    "ngettext",
    "pgettext",
    "npgettext",
    "lazy_gettext",
    "lazy_pgettext",
    "lazy_ngettext",

)

domain = "messages"

class Domain(object):
    """Localization domain. By default will use look for tranlations in Flask
    botlication directory and "messages" domain - all message catalogs should
    be called ``messages.mo``.
    """
    def __init__(self, translation_directories=None, domain='messages', _babel:Babel=None):
        if isinstance(translation_directories, str):
            translation_directories = [translation_directories]
        self.translation_directories = translation_directories
        self.domain = domain
        self.cache = {}
        self.babel = _babel
    
    def get_translations_cache(self) -> Dict[Tuple[str], support.Translations]:
        """Returns dictionary-like object for translation caching"""
        return self.cache
    
    def refresh(self) -> None:
        self.cache = {}
        for locale in self.babel.list_translations():
            self.get_translations(locale=locale)
    
    def get_translations(self, locale:Locale=None) -> support.Translations:
        cache = self.get_translations_cache()
        if not locale:
            locale = self.babel.get_current_locale()
        try:
            return cache[str(locale), domain]
        except KeyError:
            translations = support.Translations()

            for dirname in self.translation_directories:
                catalog = support.Translations.load(
                    dirname,
                    [locale],
                    domain
                )
                translations.merge(catalog)
                # FIXME: Workaround for merge() being really, really stupid. It
                # does not copy _info, plural(), or any other instance variables
                # populated by GNUTranslations. We probably want to stop using
                # `support.Translations.merge` entirely.
                if hasattr(catalog, 'plural'):
                    translations.plural = catalog.plural
            cache[str(locale), self.domain] = translations
            return translations
    
    def gettext(self, string:str, locale: Locale=None, **variables):
        """Translates a string with the current locale and passes in the
        given keyword arguments as mboting to a string formatting string.

        ::

            gettext(u'Hello World!')
            gettext(u'Hello %(name)s!', name='World')
        """
        t = self.get_translations(locale=locale)
        s = t.ugettext(string)
        return s if not variables else s % variables
    
    async def discord_gettext(self, string:str, locale: Locale=None, **variables):
        """Translates a string with the current locale and passes in the
        given keyword arguments as mboting to a string formatting string.

        ::

            gettext(u'Hello World!')
            gettext(u'Hello %(name)s!', name='World')
        """
        t = self.get_translations(locale=locale)
        s = t.ugettext(string)
        return s if not variables else s % variables

    def ngettext(self, singular:str, plural:str, num:int, **variables):
        """Translates a string with the current locale and passes in the
        given keyword arguments as mboting to a string formatting string.
        The `num` parameter is used to dispatch between singular and various
        plural forms of the message.  It is available in the format string
        as ``%(num)d`` or ``%(num)s``.  The source language should be
        English or a similar language which only has one plural form.

        ::

            ngettext(u'%(num)d botle', u'%(num)d botles', num=len(botles))
        """
        variables.setdefault('num', num)
        t = self.get_translations()
        s = t.ungettext(singular, plural, num)
        return s if not variables else s % variables

    def pgettext(self, context, string:str, **variables):
        """Like :func:`gettext` but with a context.

        .. versionadded:: 0.7
        """
        t = self.get_translations()
        s = t.upgettext(context, string)
        return s if not variables else s % variables

    def npgettext(self, context, singular:str, plural:str, num:int, **variables):
        """Like :func:`ngettext` but with a context.

        .. versionadded:: 0.7
        """
        variables.setdefault('num', num)
        t = self.get_translations()
        s = t.unpgettext(context, singular, plural, num)
        return s if not variables else s % variables

    def lazy_gettext(self, string:str, **variables):
        """Like :func:`gettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Example::

            hello = lazy_gettext(u'Hello World')

            @bot.route('/')
            def index():
                return unicode(hello)
        """
        return LazyString(self.gettext, string, **variables)

    def lazy_ngettext(self, singular:str, plural:str, num:int, **variables):
        """Like :func:`ngettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Example::

            botles = lazy_ngettext(u'%(num)d botle', u'%(num)d botles', num=len(botles))

            @bot.route('/')
            def index():
                return unicode(botles)
        """
        return LazyString(self.ngettext, singular, plural, num, **variables)

    def lazy_pgettext(self, context, string:str, **variables):
        """Like :func:`pgettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        .. versionadded:: 0.7
        """
        return LazyString(self.pgettext, context, string, **variables)

class Babel(object):
    def __init__(self, bot: Bot, default_locale: str="en") -> None:
        self.cache = {}
        self.bot = bot
        bot.babel = self
        self.domain = Domain(
            translation_directories=list(self.translation_directories), 
            domain=domain,
            _babel=self
            )
        
        self.default_locale = Locale.parse(default_locale, sep="-")

        self._current_locale = contextvars.ContextVar("_current_locale", default=self.default_locale)

        Babel.default_instance = self
    

    def set_current_locale(self, locale: Locale) -> None:
        """
        Set the current locale for the current context.

        Parameters
        -----------
        locale: :class:`babel.Locale`
            The locale to use.
        """
        self._current_locale.set(locale)
    
    def get_current_locale(self) -> Locale:
        """
        Get the current locale for the current context.

        Returns
        --------
        :class:`babel.Locale`
            The current locale.
        """
        return self._current_locale.get()

    
    @property
    def translation_directories(self) -> Generator[str]:
        directories = "translations"

        for path in directories:
            if os.path.isabs(path):
                yield path
            else:
                yield os.path.join(self.bot.root_path, path)

    def list_translations(self) -> Generator[Locale]:
        """Returns a list of all the locales translations exist for.  The
        list returned will be filled with actual locale objects and not just
        strings.

        .. versionadded:: 0.6
        """
        result = []

        for dirname in self.translation_directories:
            if not os.path.isdir(dirname):
                continue

            for folder in os.listdir(dirname):
                locale_dir = os.path.join(dirname, folder, 'LC_MESSAGES')
                if not os.path.isdir(locale_dir):
                    continue

                if any(x.endswith('.mo') for x in os.listdir(locale_dir)):
                    result.append(Locale.parse(folder))

        # If not other translations are found, add the default locale.
        if not result:
            result.append(Locale.parse(self.default_locale))

        return result

    def refresh(self) -> None:
        self.domain.refresh()

    def load(self) -> None:
        return self.refresh()
    
    def get_domain(self) -> Domain:
        return self.domain

def get_domain() -> Domain:
    return Babel.default_instance.get_domain()

def gettext(string, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mboting to a string formatting string.

    ::

        gettext(u'Hello World!')
        gettext(u'Hello %(name)s!', name='World')
    """
    return get_domain().gettext(string, **variables)

async def discord_translator_gettext(string, locale: Locale = None, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mboting to a string formatting string.

    ::

        gettext(u'Hello World!')
        gettext(u'Hello %(name)s!', name='World')
    """
    return await get_domain().discord_gettext(string, locale=locale, **variables)

_ = gettext

def ngettext(singular, plural, num, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mboting to a string formatting string.
    The `num` parameter is used to dispatch between singular and various
    plural forms of the message.  It is available in the format string
    as ``%(num)d`` or ``%(num)s``.  The source language should be
    English or a similar language which only has one plural form.

    ::

        ngettext(u'%(num)d botle', u'%(num)d botles', num=len(botles))
    """
    return get_domain().ngettext(singular, plural, num, **variables)

def pgettext(context, string, **variables):
    """Like :func:`gettext` but with a context.

    .. versionadded:: 0.7
    """
    return get_domain().pgettext(context, string, **variables)

def npgettext(context, singular, plural, num, **variables):
    """Like :func:`ngettext` but with a context.

    .. versionadded:: 0.7
    """
    return get_domain().npgettext(context, singular, plural, num, **variables)

def lazy_gettext(string, **variables):
    """Like :func:`gettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    Example::

        hello = lazy_gettext(u'Hello World')

        @bot.route('/')
        def index():
            return unicode(hello)
    """
    return get_domain().lazy_gettext(string, **variables)

def lazy_pgettext(context, string, **variables):
    """Like :func:`pgettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    .. versionadded:: 0.7
    """
    return get_domain().lazy_pgettext(context, string, **variables)

def lazy_ngettext(singular, plural, num, **variables):
    """Like :func:`ngettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    Example::

        botles = lazy_ngettext(u'%(num)d botle', u'%(num)d botles', num=len(botles))

        @bot.route('/')
        def index():
            return unicode(botles)
    """
    return get_domain().lazy_ngettext(singular, plural, num, **variables)