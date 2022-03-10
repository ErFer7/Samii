# -*- coding: utf-8 -*-

'''
Módulo de gerenciamento de reuniões.
'''

from asyncio import tasks
from datetime import datetime

import discord

from discord.ext import commands, tasks


class MeetingManagementCog(commands.Cog):

    '''
    Cog de gerenciamento de reuniões.
    '''

    bot: None
    active_meetings: list

    def __init__(self, bot):

        self.bot = bot
        self.active_meetings = []

        self.run_meetings.start()

        print(f"[{datetime.now()}][Meeting]: Sistema de gerenciamento de reuniões inicializado")

    @tasks.loop(seconds=1.0)
    async def run_meetings(self):
        '''
        Executa uma reunião.
        '''

        for meeting_tuple in self.active_meetings:

            meeting_tuple[0].increment_time(1.0)

            if meeting_tuple[0].topic_has_changed:

                embed = discord.Embed(description=f"❱❱❱ **Tópico atual: {meeting_tuple[0].current_topic}**",
                                      color=discord.Color.dark_purple())

                await meeting_tuple[1].send(embed=embed)

            if meeting_tuple[0].check_time_remaining() <= 0:

                meeting_tuple[0].reset()
                self.active_meetings.remove(meeting_tuple)

                embed = discord.Embed(description=f"❱❱❱ **A reunião \"{meeting_tuple[0].name}\" acabou**",
                                      color=discord.Color.dark_purple())

                await meeting_tuple[1].send(embed=embed)

    @commands.command(name="meeting", aliases=("reunião", "reuniao", "mt", "rn"))
    async def create_meeting(self, ctx, *args):
        '''
        Adiciona uma reunião.
        '''

        print(f"[{datetime.now()}][Admin]: <create_meeting> (Autor: {ctx.author.name})")

        embed = discord.Embed(description="❌  **Ocorreu um erro!**\n\n",
                              color=discord.Color.red())

        if args is not None:

            if len(args) == 1:

                # TODO: Permitir duas reuniões com o mesmo nome
                self.bot.guild_dict[str(ctx.guild.id)].meetings[args[0]] = Meeting(args[0])

                embed = discord.Embed(description=f"❱❱❱ **Reunião \"{args[0]}\" adicionada**",
                                      color=discord.Color.dark_purple())

        await ctx.send(embed=embed)

    @commands.command(name="start", aliases=("iniciar", "st", "in"))
    async def start_meeting(self, ctx, *args):
        '''
        Adiciona uma reunião.
        '''

        print(f"[{datetime.now()}][Admin]: <start_meeting> (Autor: {ctx.author.name})")

        embed = discord.Embed(description="❌  **Ocorreu um erro!**\n\n",
                              color=discord.Color.red())

        if args is not None:

            if len(args) == 1 and args[0] in self.bot.guild_dict[str(ctx.guild.id)].meetings:

                meeting = self.bot.guild_dict[str(ctx.guild.id)].meetings[args[0]]

                if meeting.topic_count > 0:

                    meeting.start()

                    channel = self.bot.guild_dict[str(ctx.guild.id)].main_channel

                    if channel is None:
                        channel = ctx.channel

                    self.active_meetings.append((meeting, self.bot.guild_dict[str(ctx.guild.id)].main_channel))

                    embed = discord.Embed(description=f"❱❱❱ **O primeiro tópico é: {meeting.current_topic}**",
                                          color=discord.Color.dark_purple())

                    await channel.send(embed=embed)

                    embed = discord.Embed(description=f"❱❱❱ **Reunião \"{args[0]}\" iniciada",
                                          color=discord.Color.dark_purple())


        await ctx.send(embed=embed)

    @commands.command(name="add", aliases=("adicionar", "a"))
    async def add_topic(self, ctx, *args):
        '''
        Adiciona um tópico à uma reunião.
        '''

        print(f"[{datetime.now()}][Admin]: <add_topic> (Autor: {ctx.author.name})")

        embed = discord.Embed(description="❌  **Ocorreu um erro!**\n\n",
                              color=discord.Color.red())

        if args is not None:

            if len(args) == 3 and args[0] in self.bot.guild_dict[str(ctx.guild.id)].meetings and str.isnumeric(args[2]):

                meeting = self.bot.guild_dict[str(ctx.guild.id)].meetings[args[0]]

                meeting.add_topic(args[1], int(args[2]) * 60)

                embed = discord.Embed(description=f"❱❱❱ **Tópico \"{args[1]}\" com {args[2]} minutos adicionado em "
                                      f"\"{args[0]}\"**",
                                      color=discord.Color.dark_purple())

        await ctx.send(embed=embed)


class Meeting():

    '''
    Reunião.
    '''

    name: str
    total_time: int
    topic_count: int
    current_topic_id_index: int
    current_topic: str
    current_topic_time: int
    current_time: int
    topics: dict
    topic_has_changed: bool
    last_topic_id: int

    def __init__(self, name: str):

        self.name = name
        self.total_time = 0
        self.topic_count = 0
        self.current_topic_id_index = 0
        self.current_topic = ''
        self.current_time = 0
        self.current_topic_time = 0
        self.topics = {}
        self.topic_has_changed = False
        self.last_topic_id = 0

    def add_topic(self, topic: str, time: int):
        '''
        Adiciona um novo tópico.
        '''

        self.topics[self.last_topic_id] = (topic, time)
        self.topic_count += 1
        self.total_time += time
        self.last_topic_id += 1

    def remove_topic(self, topic: str):
        '''
        Remove um tópico.
        '''

        for topic_id, topic_tuple in self.topics.items():

            if topic_tuple[0] == topic:

                self.topic_count -= 1
                self.total_time -= topic_tuple[1]
                del self.topics[topic_id]
                break

    def start(self):
        '''
        Inicia a reunião.
        '''

        self.current_topic = self.topics[list(self.topics.keys())[self.current_topic_id_index]][0]
        self.current_topic_time = self.topics[list(self.topics.keys())[self.current_topic_id_index]][1]

    def increment_time(self, time: int):
        '''
        Passa o tempo.
        '''

        self.topic_has_changed = False
        self.current_time += time

        if self.current_topic_time <= self.current_time:

            self.current_topic_id_index += 1

            if self.current_topic_id_index < self.topic_count:

                self.current_topic = self.topics[list(self.topics.keys())[self.current_topic_id_index]][0]
                self.current_topic_time = self.topics[list(self.topics.keys())[self.current_topic_id_index]][1]
                self.topic_has_changed = True

    def check_time_remaining(self):
        '''
        Verifica o tempo restante.
        '''

        return self.total_time - self.current_time

    def reset(self):
        '''
        Reseta a reunião.
        '''

        self.current_topic = ''
        self.current_time = 0
        self.topic_has_changed = False
