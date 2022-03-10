# -*- coding:utf-8 -*-

'''
Módulo para a cog dos comandos de ajuda
'''

from datetime import datetime

import discord

from discord.ext import commands


class HelpCog(commands.Cog):

    '''
    Cog dos comandos de ajuda
    '''

    def __init__(self, bot):

        self.bot = bot

        print(f"[{datetime.now()}][Ajuda]: Sistema de comandos de ajuda inicializado")

    @commands.command(name="ajuda", aliases=("help", "h", "aj"))
    async def custom_help(self, ctx):
        '''
        Envia uma mensagem de ajuda
        '''

        print(f"[{datetime.now()}][Ajuda]: <ajuda> (Autor: {ctx.author.name})")

        embed = discord.Embed(description="❱❱❱ **Ajuda**\n\n"
                              "*Comandos:*\n\n"
                              "++off\n"
                              "++info\n"
                              "++ajuda\n",
                              color=discord.Color.dark_purple())

        await ctx.send(embed=embed)
