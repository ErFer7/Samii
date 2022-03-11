# -*- coding:utf-8 -*-

'''
Módulo para a cog dos comandos de configurações.
'''

from datetime import datetime

from discord.ext import commands

from utilities import DiscordUtilities


class SettingsCog(commands.Cog):

    '''
    Cog dos comandos de configurações.
    '''

    def __init__(self, bot):

        self.bot = bot

        print(f"[{datetime.now()}][Config]: Sistema de comandos de configurações inicializado")

    @commands.command(name="channel", aliases=("canal", "ch", "ca"))
    async def channel_update(self, ctx):
        '''
        Define o canal principal de bots.
        '''

        print(f"[{datetime.now()}][Config]: <channel_update> (Autor: {ctx.author.name})")

        if len(ctx.message.channel_mentions) != 1:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Mencione um canal com #canal!"
                                                "channel",
                                                True)
            return

        key = str(ctx.guild.id)

        self.bot.guild_dict[key]. \
            settings["Main channel ID"] = ctx.message.channel_mentions[0].id

        self.bot.guild_dict[key].update_main_channel(self.bot)

        await DiscordUtilities.send_message(ctx,
                                            "Canal redefinido",
                                            f"Novo canal de textos: {self.bot.guild_dict[key].main_channel}",
                                            "channel")

    @commands.command(name="voice_channel", aliases=("canal_voz", "vch", "cav"))
    async def voice_channel_update(self, ctx, *args):
        '''
        Define o canal de voz do bot.
        '''

        print(f"[{datetime.now()}][Config]: <voice_channel_update> (Autor: {ctx.author.name})")

        if args is None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Erro crítico nos argumentos!",
                                                "voice_channel",
                                                True)
            return

        if len(args) != 1:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome do canal de voz!",
                                                "voice_channel",
                                                True)
            return

        key = str(ctx.guild.id)

        channel_found = False

        for channel in ctx.guild.voice_channels:

            if channel.name == args[0]:

                self.bot.guild_dict[key]. \
                    settings["Voice channel ID"] = channel.id

                self.bot.guild_dict[key].update_voice_channel(self.bot)

                channel_found = True

        if channel_found:

            await DiscordUtilities.send_message(ctx,
                                                "Canal de voz redefinido",
                                                f"Novo canal de voz: {self.bot.guild_dict[key].main_channel}",
                                                "voice_channel",
                                                True)
        else:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Canal não encontrado!",
                                                "voice_channel",
                                                True)
