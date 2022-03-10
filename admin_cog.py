# -*- coding:utf-8 -*-

'''
Módulo para a cog dos comandos de administrador.
'''

from datetime import datetime

import discord

from discord.ext import commands


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

        if ctx.author.id in self.bot.admins_id:

            # Envia uma mensagem de saída
            embed = discord.Embed(description="❱❱❱ **Encerrando**",
                                  color=discord.Color.dark_purple())

            await ctx.send(embed=embed)

            # Salva todos os servidores
            print(f"[{datetime.now()}][Admin]: Registrando as definições dos servidores")

            for key in self.bot.guild_dict:
                self.bot.guild_dict[key].write_settings()

            # Encerra o bot
            print(f"[{datetime.now()}][Admin]: Encerrando")
            await self.bot.close()
        else:

            embed = discord.Embed(description="❌  **Comando inválido**\n\n"
                                  "*Você não tem permissão para usar este comando*",
                                  color=discord.Color.red())

            await ctx.send(embed=embed)

    @commands.command(name="info")
    async def info(self, ctx):
        '''
        Exibe informações
        '''

        print(f"[{datetime.now()}][Admin]: <info> (Autor: {ctx.author.name})")

        header = f"**{self.bot.name} {self.bot.version}** - Criado em 09/03/2022"
        http_loop = f"**Loop HTTP:** {self.bot.loop}"
        latency = f"**Latência interna:** {self.bot.latency}"
        guild_count = f"**Servidores conectados:** {len(self.bot.guilds)}"
        voice_clients = f"**Instâncias de voz:** {self.bot.voice_clients}"

        embed = discord.Embed(description="❱❱❱ **Informações**\n\n"
                              f"⬩ {header}\n\n"
                              f"⬩ {http_loop}\n\n"
                              f"⬩ {latency}\n\n"
                              f"⬩ {guild_count}\n\n"
                              f"⬩ {voice_clients}",
                              color=discord.Color.dark_purple())
        await ctx.send(embed=embed)

    @commands.command(name="save")
    async def save(self, ctx):
        '''
        Salva os servidores
        '''

        print(f"[{datetime.now()}][Admin]: <save> (Autor: {ctx.author.name})")

        self.bot.guild_dict[str(ctx.guild.id)].write_settings()

        embed = discord.Embed(description="❱❱❱ **Salvando...**",
                              color=discord.Color.dark_purple())

        await ctx.send(embed=embed)
