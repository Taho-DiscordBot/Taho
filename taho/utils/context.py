from discord.ext import commands

__all__ = (
    "TahoContext",
)

def get_locale(guild):
    return "en"

class TahoContext(commands.Context):
    @property
    def babel_locale(self):
        if self.interaction:
            return str(self.interaction.locale)
        return get_locale(self.guild)