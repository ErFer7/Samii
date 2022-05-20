# -*- coding:utf-8 -*-

'''
Módulo para a cog dos eventos.
'''

from datetime import datetime

from discord.ext import commands


class EventCog(commands.Cog):

    '''
    Cog dos eventos.
    '''

    # Construtor --------------------------------------------------------------
    def __init__(self) -> None:
        print(f"[{datetime.now()}][Event]: Event system initialized")

    # Eventos -----------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        '''
        Evento de mensagens.
        '''

        print(f"[{datetime.now()}][Event]: "
              f"A message was sent in the channel [{message.channel}] by [{message.author.name}]")

    @commands.Cog.listener()
    async def on_connect(self) -> None:
        '''
        Evento de conexão.
        '''

        print(f"[{datetime.now()}][Event]: Connected")

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        '''
        Evento de desconexão.
        '''

        print(f"[{datetime.now()}][Event]: Disconnected")

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        '''
        Evento de retorno.
        '''

        print(f"[{datetime.now()}][Event]: Resumed")

    @commands.Cog.listener()
    async def on_member_update(self, before, after) -> None:
        '''
        Evento de atualização de usuário.
        '''

        print(f"[{datetime.now()}][Event]: "
              f"[{after.name}] changed from [{before.status}] to [{after.status}] in the guild [{after.guild.name}]")
