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
"""
from __future__ import absolute_import, annotations
import os
from typing import Dict, Tuple, Generator
from babel import support, Locale
from discord import Interaction
from taho.utils.context import TahoContext

from .speaklater import LazyString
current_bot = None
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
    
    def get_translations(self, locale:Locale=None, ctx=None) -> support.Translations:
        cache = self.get_translations_cache()
        if not locale:
            locale = ctx.babel_locale
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
    
    def gettext(self, locale:Locale, string:str, **variables):
        """Translates a string with the current locale and passes in the
        given keyword arguments as mboting to a string formatting string.

        ::

            gettext(u'Hello World!')
            gettext(u'Hello %(name)s!', name='World')
        """
        t = self.get_translations(locale=locale)
        s = t.ugettext(string)
        return s if not variables else s % variables

    def ngettext(self, locale:Locale, singular:str, plural:str, num:int, **variables):
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
        t = self.get_translations(locale=locale)
        s = t.ungettext(singular, plural, num)
        return s if not variables else s % variables

    def pgettext(self, locale:Locale, context, string:str, **variables):
        """Like :func:`gettext` but with a context.

        .. versionadded:: 0.7
        """
        t = self.get_translations(locale=locale)
        s = t.upgettext(context, string)
        return s if not variables else s % variables

    def npgettext(self, locale:Locale, context, singular:str, plural:str, num:int, **variables):
        """Like :func:`ngettext` but with a context.

        .. versionadded:: 0.7
        """
        variables.setdefault('num', num)
        t = self.get_translations(locale=locale)
        s = t.unpgettext(context, singular, plural, num)
        return s if not variables else s % variables

    def lazy_gettext(self, locale:Locale, string:str, **variables):
        """Like :func:`gettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Example::

            hello = lazy_gettext(u'Hello World')

            @bot.route('/')
            def index():
                return unicode(hello)
        """
        return LazyString(self.gettext, locale, string, **variables)

    def lazy_ngettext(self, locale:Locale, singular:str, plural:str, num:int, **variables):
        """Like :func:`ngettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        Example::

            botles = lazy_ngettext(u'%(num)d botle', u'%(num)d botles', num=len(botles))

            @bot.route('/')
            def index():
                return unicode(botles)
        """
        return LazyString(self.ngettext, locale, singular, plural, num, **variables)

    def lazy_pgettext(self, locale:Locale, context, string:str, **variables):
        """Like :func:`pgettext` but the string returned is lazy which means
        it will be translated when it is used as an actual string.

        .. versionadded:: 0.7
        """
        return LazyString(self.pgettext, locale, context, string, **variables)

class Babel(object):
    def __init__(self, bot) -> None:
        self.cache = {}
        self.bot = bot
        bot.babel = self
        self.domain = Domain(
            translation_directories=list(self.translation_directories), 
            domain=domain,
            _babel=self
            )
    
    @property
    def translation_directories(self) -> Generator[str]:
        directories = self.bot.config.get(
            'BABEL_TRANSLATION_DIRECTORIES',
            'translations'
        ).split(';')

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
            result.append(Locale.parse(self._default_locale))

        return result

    def refresh(self) -> None:
        self.domain.refresh()

    def load(self) -> None:
        return self.refresh()
    
    def get_domain(self) -> Domain:
        return self.domain
    
    

def get_domain(ctx) -> Domain:
    return ctx.bot.babel.get_domain()


async def gettext(string, ctx, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mboting to a string formatting string.

    ::

        gettext(u'Hello World!')
        gettext(u'Hello %(name)s!', name='World')
    """
    if isinstance(ctx, Interaction):
        ctx = await TahoContext.from_interaction(ctx)
    locale = ctx.babel_locale
    return get_domain(ctx).gettext(locale, string, **variables)
_ = gettext

def ngettext(singular, plural, num, ctx, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mboting to a string formatting string.
    The `num` parameter is used to dispatch between singular and various
    plural forms of the message.  It is available in the format string
    as ``%(num)d`` or ``%(num)s``.  The source language should be
    English or a similar language which only has one plural form.

    ::

        ngettext(u'%(num)d botle', u'%(num)d botles', num=len(botles))
    """
    if isinstance(ctx, Interaction):
        ctx = TahoContext.from_interaction(ctx)
    locale = ctx.babel_locale
    return get_domain(ctx).ngettext(locale, singular, plural, num, **variables)


def pgettext(context, string, ctx, **variables):
    """Like :func:`gettext` but with a context.

    .. versionadded:: 0.7
    """
    if isinstance(ctx, Interaction):
        ctx = TahoContext.from_interaction(ctx)
    locale = ctx.babel_locale
    return get_domain(ctx).pgettext(locale, context, string, **variables)


def npgettext(context, singular, plural, num, ctx, **variables):
    """Like :func:`ngettext` but with a context.

    .. versionadded:: 0.7
    """
    if isinstance(ctx, Interaction):
        ctx = TahoContext.from_interaction(ctx)
    locale = ctx.babel_locale
    return get_domain(ctx).npgettext(locale, context, singular, plural, num, **variables)


def lazy_gettext(string, ctx, **variables):
    """Like :func:`gettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    Example::

        hello = lazy_gettext(u'Hello World')

        @bot.route('/')
        def index():
            return unicode(hello)
    """
    if isinstance(ctx, Interaction):
        ctx = TahoContext.from_interaction(ctx)
    locale = ctx.babel_locale
    return get_domain(ctx).lazy_gettext(locale, string, **variables)


def lazy_pgettext(context, string, ctx, **variables):
    """Like :func:`pgettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    .. versionadded:: 0.7
    """
    if isinstance(ctx, Interaction):
        ctx = TahoContext.from_interaction(ctx)
    locale = ctx.babel_locale
    return get_domain(ctx).lazy_pgettext(locale, context, string, **variables)


def lazy_ngettext(singular, plural, num, ctx, **variables):
    """Like :func:`ngettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    Example::

        botles = lazy_ngettext(u'%(num)d botle', u'%(num)d botles', num=len(botles))

        @bot.route('/')
        def index():
            return unicode(botles)
    """
    if isinstance(ctx, Interaction):
        ctx = TahoContext.from_interaction(ctx)
    locale = ctx.babel_locale
    return get_domain(ctx).lazy_ngettext(locale, singular, plural, num, **variables)
