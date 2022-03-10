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

    def __init__(self, bot):

        self.bot = bot

        print(f"[{datetime.now()}][Evento]: Sistema de eventos inicializado")

    @commands.Cog.listener()
    async def on_message(self, message):
        '''
        Evento de mensagens.
        '''

        print(f"[{datetime.now()}][Evento]: "
              f"[{message.author.name}] enviou uma mensagem no canal [{message.channel}]")

    @commands.Cog.listener()
    async def on_connect(self):
        '''
        Evento de conexão.
        '''

        print(f"[{datetime.now()}][Evento]: Conectado")

    @commands.Cog.listener()
    async def on_disconnect(self):
        '''
        Evento de desconexão.
        '''

        print(f"[{datetime.now()}][Evento]: Desconectado")

    @commands.Cog.listener()
    async def on_resumed(self):
        '''
        Evento de retorno.
        '''

        print(f"[{datetime.now()}][Evento]: Resumido")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        '''
        Evento de atualização de usuário.
        '''

        print(f"[{datetime.now()}][Evento]: "
              f"[{after.name}] ficou [{after.status}] no servidor [{after.guild.name}]")
