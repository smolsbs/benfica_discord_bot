""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.
Version: 5.5.0
"""
import json
import os

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from time import sleep


from discord import (File, Embed, EntityType,
                     PrivacyLevel)
from discord.ext import commands, tasks
from discord.ext.commands import Context

from helpers import covers, utils, next_match

SUCCESS_COLOR = 0x00cc00
FAIL_COLOR = 0xff0000

# Here we name the cog and create a new class for the cog.


class Comandos(commands.Cog, name="comandos"):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 300.0)
    @commands.hybrid_command(
        name='capas',
        description='Busca as capas desportivas do dia'
    )
    async def capas(self, context: Context):
        await context.defer()
        _path = covers.sports_covers()
        if isinstance(_path, int):
            self.bot.logger.info(f'capas returned a Status Code {_path}')
            emb = Embed(color=FAIL_COLOR)
            emb.add_field(name='', value="Erro ao buscar as capas!")
            await context.reply(embed=emb)
            return
        with open(_path, 'rb') as fp:
            _file = File(fp, 'collage.jpg')
            await context.reply(file=_file)

    @tasks.loop(hours=24)
    async def atc_info(self):
        status = next_match.req_get_next_match()
        if not status:
            self.bot.logger.info("Erro ao buscar a info do próximo jogo.")

    @commands.has_permissions(administrator=True)
    @commands.hybrid_command(
        name='atualizar_info',
        description='busca nova info de jogo')
    async def atualizar_info(self, context: Context):
        await context.defer()
        status = next_match.req_get_next_match()
        if status:
            _color = SUCCESS_COLOR
            _ret = f'Informação atualizada com sucesso!\n{status}'
        else:
            _color = FAIL_COLOR
            _ret = 'Atualização da informação não foi atualizada devido a um erro!'

        emb = Embed(color=_color)
        emb.add_field(name='', value=_ret)
        await context.reply(embed=emb)

    @commands.has_permissions(administrator=True)
    @commands.hybrid_command(
        name='criar_eventos',
        with_app_command=True,
        description='Cria uma lista de eventos pelos ids, separados por ","')
    async def criar_eventos(self, context: Context, _ids:str):
        events = _ids.split(',')
        await context.defer()

        info = utils.read_config()
        if info is None:
            emb = Embed(color=FAIL_COLOR)
            emb.add_field(name='',
                          value='Não existe informação para criar o evento.')
            await context.send(embed=emb)
            return

        _guild = context.guild

        for ev in events:
            match_info = info[ev]
            match = next_match.make_event_helper(match_info)

            try:
                await _guild.create_scheduled_event(name=match[0],
                                                  description=match[1],
                                                  start_time=match[3],
                                                  end_time=match[4],
                                                  privacy_level=PrivacyLevel.guild_only,
                                                  entity_type=EntityType.external,
                                                  location=match[2])
            except TypeError:
                emb = Embed(color=FAIL_COLOR)
                emb.add_field(name='', value='Erro ao criar o evento!')
                await context.reply(embed=emb)
                return
            sleep(2)

        emb = Embed(color=SUCCESS_COLOR)
        emb.add_field(name='', value='Eventos criados')
        await context.reply(embed=emb)
        return


    @commands.has_permissions(administrator=True)
    @commands.hybrid_command(
        name='criar_evento',
        with_app_command=True,
            description='Cria o evento para o próximo jogo')
    async def criar_evento(self, context: Context, _id=None):
        if _id is None:
            _id = "0"
        else:
            _id = str(_id)

        info = utils.read_config()
        if info is None:
            emb = Embed(color=FAIL_COLOR)
            emb.add_field(name='',
                          value='Não existe informação para criar o evento.')
            await context.send(embed=emb)
            return

        await context.defer()
        try:
            info = info[_id]
        except KeyError:
            emb = Embed(color=FAIL_COLOR)
            emb.add_field(name='',
                          value='Erro ao encontrar id do evento.')
            await context.send(embed=emb)
            return

        _guild = context.guild
        match = next_match.make_event_helper(info)

        try:
            _status = await _guild.create_scheduled_event(name=match[0],
                                                          description=match[1],
                                                          start_time=match[3],
                                                          end_time=match[4],
                                                          privacy_level=PrivacyLevel.guild_only,
                                                          entity_type=EntityType.external,
                                                          location=match[2])
        except TypeError:
            emb = Embed(color=FAIL_COLOR)
            emb.add_field(name='', value='Erro ao criar o evento!')
            await context.reply(embed=emb)
            return

        event_url = f"{_status.url}"
        await context.reply(content=event_url)

async def setup(bot):
    await bot.add_cog(Comandos(bot))
