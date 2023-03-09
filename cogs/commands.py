""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.
Version: 5.5.0
"""
from discord import File
from discord.ext import commands
from discord.ext.commands import Context

from helpers import covers, utils


# Here we name the cog and create a new class for the cog.
class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(
        name='capas',
        description='Busca as capas do dia'
    )
    async def capas(self, context: Context):
        _path = covers.sports_covers()
        with open(_path, 'rb') as fp:
            _file = File(fp, 'collage.jpg')
            await context.send(file=_file)


async def setup(bot):
    await bot.add_cog(Template(bot))
