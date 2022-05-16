# -*- coding:utf-8 -*-

'''
Módulo para a cog dos comandos de administrador.
'''

from datetime import datetime

from discord.ext import commands
from Source.bot_system import CustomBot

from Source.utilities import DiscordUtilities


class AdminCog(commands.Cog):

    '''
    Cog dos comandos de adminstrador.
    '''

    # Atributos ---------------------------------------------------------------
    bot: CustomBot

    # Construtor --------------------------------------------------------------
    def __init__(self, bot: CustomBot):

        self.bot = bot

        print(f"[{datetime.now()}][Admin]: Administrator command system initialized")

    # Comandos ----------------------------------------------------------------
    @commands.command(name="off")
    async def shutdown(self, ctx) -> None:
        '''
        Desliga o bot.
        '''

        print(f"[{datetime.now()}][Admin]: <off> (Author: {ctx.author.name})")

        if not self.bot.is_admin(ctx.author.id):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Você não tem permissão para usar este comando",
                                                "shutdown",
                                                True)
            return

        # Envia uma mensagem de saída
        await DiscordUtilities.send_message(ctx, "Encerrando", "Tchau!", "shutdown")

        # Salva todos os servidores
        print(f"[{datetime.now()}][Admin]: Saving definitions for every guild")

        self.bot.write_settings_for_all()

        # Encerra o bot
        print(f"[{datetime.now()}][Admin]: Exiting")
        await self.bot.close()

    @commands.command(name="info")
    async def info(self, ctx) -> None:
        '''
        Exibe informações.
        '''

        print(f"[{datetime.now()}][Admin]: <info> (Author: {ctx.author.name})")

        bot_info = self.bot.get_info()

        description = f'''⬩ **{bot_info["Name"]} {bot_info["Version"]}** - Criada em 2022-03-09

                          ⬩ **Loop HTTP:** {bot_info["HTTP loop"]}

                          ⬩ **Latência interna:** {bot_info["Latency"]} ms

                          ⬩ **Servidores conectados:** {bot_info["Guild count"]}

                          ⬩ **Instâncias de voz:** {bot_info["Voice clients"]}'''

        await DiscordUtilities.send_message(ctx, "Informações", description, "info")

    @commands.command(name="save")
    async def save(self, ctx) -> None:
        '''
        Salva os servidores.
        '''

        print(f"[{datetime.now()}][Admin]: <save> (Author: {ctx.author.name})")

        if not self.bot.is_admin(ctx.author.id):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Você não tem permissão para usar este comando",
                                                "shutdown",
                                                True)
            return

        self.bot.write_settings_for_guild(ctx.guild.id)

        await DiscordUtilities.send_message(ctx, "Salvando", "Os dados salvos são únicos para cada servidor", "save")
