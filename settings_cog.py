# -*- coding:utf-8 -*-

'''
Módulo para a cog dos comandos de configurações.
'''

from datetime import datetime

import discord

from discord.ext import commands


class SettingsCog(commands.Cog):

    '''
    Cog dos comandos de configurações.
    '''

    def __init__(self, bot):

        self.bot = bot

        print(f"[{datetime.now()}][Config]: Sistema de comandos de configurações inicializado")

    @commands.command(name="canal", aliases=("channel", "ch"))
    async def channel_modifier(self, ctx):
        '''
        Define o canal principal de bots.
        '''

        print(f"[{datetime.now()}][Config]: <canal> (Autor: {ctx.author.name})")

        if len(ctx.message.channel_mentions) == 1:

            key = str(ctx.guild.id)

            self.bot.guild_dict[key]. \
                settings["Main channel ID"] = ctx.message.channel_mentions[0].id

            self.bot.guild_dict[key].update_main_channel(self.bot)

            embed = discord.Embed(description=f"❱❱❱ **Canal redefinido para:** "
                                  f"{self.bot.guild_dict[key].main_channel}**",
                                  color=discord.Color.dark_purple())

            await ctx.send(embed=embed)
        else:

            embed = discord.Embed(description="❌  **Comando inválido**\n\n"
                                  "*Uso correto*\n~canal #canal",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
