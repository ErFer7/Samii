# -*- coding:utf-8 -*-

'''
Módulo para a cog dos comandos de administrador.
'''

from datetime import datetime

from discord.ext import commands

from utilities import DiscordUtilities


class AdminCog(commands.Cog):

    '''
    Cog dos comandos de adminstrador.
    '''

    bot: None

    def __init__(self, bot):

        self.bot = bot

        print(f"[{datetime.now()}][Admin]: Sistema de comandos do administrador inicializado")

    @commands.command(name="off")
    async def shutdown(self, ctx):
        '''
        Desliga o bot
        '''

        print(f"[{datetime.now()}][Admin]: <off> (Autor: {ctx.author.name})")

        if ctx.author.id not in self.bot.admins_id:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Você não tem permissão para usar este comando",
                                                "shutdown",
                                                True)
            return


        if ctx.author.id in self.bot.admins_id:

            # Envia uma mensagem de saída
            await DiscordUtilities.send_message(ctx, "Encerrando", "Tchau!", "shutdown")

            # Salva todos os servidores
            print(f"[{datetime.now()}][Admin]: Registrando as definições dos servidores")

            for key in self.bot.guild_dict:
                self.bot.guild_dict[key].write_settings()

            # Encerra o bot
            print(f"[{datetime.now()}][Admin]: Encerrando")
            await self.bot.close()

    @commands.command(name="info")
    async def info(self, ctx):
        '''
        Exibe informações
        '''

        print(f"[{datetime.now()}][Admin]: <info> (Autor: {ctx.author.name})")

        description = f'''⬩ **{self.bot.name} {self.bot.version}** - Criada em 09/03/2022

                          ⬩ **Loop HTTP:** {self.bot.loop}

                          ⬩ **Latência interna:** {self.bot.latency}

                          ⬩ **Servidores conectados:** {len(self.bot.guilds)}

                          ⬩ **Instâncias de voz:** {self.bot.voice_clients}'''

        await DiscordUtilities.send_message(ctx, "Informações", description, "info")

    @commands.command(name="save")
    async def save(self, ctx):
        '''
        Salva os servidores
        '''

        print(f"[{datetime.now()}][Admin]: <save> (Autor: {ctx.author.name})")

        self.bot.guild_dict[str(ctx.guild.id)].write_settings()

        await DiscordUtilities.send_message(ctx, "Salvando", "Os dados salvos são únicos para cada servidor", "save")
