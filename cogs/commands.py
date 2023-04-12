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

    @commands.hybrid_command(
        name='capas',
        description='Busca as capas do dia'
    )
    async def capas(self, context: Context):
        await context.defer()
        _path = covers.sports_covers()
        if isinstance(_path, int):
            self.bot.logger.info(f'capas returned a Status Code {_path}')
            emb = Embed(color=FAIL_COLOR)
            emb.add_field(name='Estado', value="Erro ao buscar as capas.")
            await context.reply(embed=emb)
            return
        with open(_path, 'rb') as fp:
            _file = File(fp, 'collage.jpg')
            await context.reply(file=_file)

    @tasks.loop(hours=24)
    async def atc_info(self):
        status = next_match.get_next_match()
        if not status:
            self.bot.logger.info("Erro ao buscar a info do próximo jogo.")

    @commands.hybrid_command(
        name='atualizar_info',
        description='busca nova info de jogo')
    async def atualizar_info(self, context: Context):
        temp = await context.send('Processando o comando...')
        status = next_match.get_next_match()
        if status:
            _color = SUCCESS_COLOR
            _ret = 'Informação atualizada com sucesso'
        else:
            _color = FAIL_COLOR
            _ret = 'Atualização da informação não foi atualizada devido a um erro'

        emb = Embed(color=_color)
        emb.add_field(name='Estado', value=_ret)
        await temp.delete()
        await context.send(embed=emb)

    @commands.hybrid_command(
        name='criar_evento',
        description='Cria o evento para o próximo jogo')
    async def criar_evento(self, context: Context):
        info = utils.read_config()
        if info is None:
            emb = Embed(color=FAIL_COLOR)
            emb.add_field(
                name='Estado', value='Não existe informação para criar o evento. Corre /atualizar_info para buscar o próximo jogo.')
            await context.send(embed=emb)
            return

        info = info['next_match']
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/../config.json") as file:
            config = json.load(file)

        nome_evento = f"{info['homeTeam']} Vs. {info['awayTeam']}"
        descricao = f"🏆 {info['competition']}\n🏟️ {info['stadium']}\n📺 {info['tv']}"
        nome_canal = f"#{utils.sanitize_str(info['homeTeam'])}_vs_{utils.sanitize_str(info['awayTeam'])}"
        inicio_jogo = datetime(year=int(info['year']),
                               month=int(info['month']),
                               day=int(info['day']),
                               hour=int(info['hour']),
                               minute=int(info['minute']),
                               tzinfo=ZoneInfo('Europe/Lisbon'))
        inicio_jogo = inicio_jogo.astimezone(tz=ZoneInfo(config['timezone']))
        fim_jogo = inicio_jogo + timedelta(hours=2)
        _guild = context.guild
        try:
            _status = await _guild.create_scheduled_event(name=nome_evento,
                                                          description=descricao,
                                                          start_time=inicio_jogo,
                                                          end_time=fim_jogo,
                                                          privacy_level=PrivacyLevel.guild_only,
                                                          entity_type=EntityType.external,
                                                          location=nome_canal)
        except TypeError:
            emb = Embed(color=FAIL_COLOR)
            emb.add_field(name='Estado', value='Erro ao criar o evento.')
            await context.send(embed=emb)
            return

        emb = Embed(color=SUCCESS_COLOR)
        emb.add_field(name='Estado', value='Evento criado com sucesso.')

        await context.send(embed=emb)


async def setup(bot):
    await bot.add_cog(Comandos(bot))
