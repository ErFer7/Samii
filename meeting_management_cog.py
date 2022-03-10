# -*- coding: utf-8 -*-

'''
Módulo de gerenciamento de reuniões.
'''

from os.path import join
from asyncio import tasks
from datetime import datetime

import discord

from discord.ext import commands, tasks

# TODO: Adicionar a remoção de tópicos
# TODO: Adcionar o comando de ecerramento da reunião


class MeetingManagementCog(commands.Cog):

    '''
    Cog de gerenciamento de reuniões.
    '''

    bot: None
    active_meeting: None
    active_text_channel: None
    active_voice_channel: None
    voice_client: None
    low_time_notified: bool

    def __init__(self, bot):

        self.bot = bot
        self.active_meeting = None
        self.active_text_channel = None
        self.active_voice_channel = None
        self.voice_client = None
        self.low_time_notified = False

        self.run_meeting.start()

        print(f"[{datetime.now()}][Meeting]: Sistema de gerenciamento de reuniões inicializado")

    @tasks.loop(seconds=1.0)
    async def run_meeting(self):
        '''
        Executa uma reunião.
        '''

        if self.active_meeting is not None:

            self.active_meeting.increment_time(1.0)

            if self.active_meeting.topic_has_changed:

                if self.voice_client is not None and self.voice_client.is_connected():

                    if self.voice_client.is_playing():
                        self.voice_client.stop()

                    source = join("Audio", "Notificação de troca de tópico.wav")
                    executable = join("System", "ffmpeg.exe")

                    self.voice_client.play(discord.FFmpegPCMAudio(source=source,
                                                                  executable=executable))

                embed = discord.Embed(description=f"❱❱❱ **Tópico atual: {self.active_meeting.current_topic}**",
                                      color=discord.Color.dark_purple())

                await self.active_text_channel.send(embed=embed)

            if self.active_meeting.check_time_remaining() <= 0:

                self.active_meeting.reset()

                if self.voice_client is not None and self.voice_client.is_connected():

                    await self.voice_client.disconnect()

                    for member in self.active_voice_channel.members:
                        await member.move_to(None)

                    self.voice_client = None

                embed = discord.Embed(description=f"❱❱❱ **A reunião \"{self.active_meeting.name}\" acabou**",
                                      color=discord.Color.dark_purple())

                await self.active_text_channel.send(embed=embed)

                self.active_meeting = None
                self.active_text_channel = None
                self.active_voice_channel = None
                self.low_time_notified = 0
            elif self.active_meeting.check_time_remaining() <= 10:

                if self.voice_client is not None and self.voice_client.is_connected():

                    if self.voice_client.is_playing():
                        self.voice_client.stop()

                    source = join("Audio", "Notificação final.ogg")
                    executable = join("System", "ffmpeg.exe")

                    self.voice_client.play(discord.FFmpegPCMAudio(source=source,
                                                                  executable=executable))
            elif self.active_meeting.check_time_remaining() <= 600 and not self.low_time_notified:

                self.low_time_notified = True

                if self.voice_client is not None and self.voice_client.is_connected():

                    if self.voice_client.is_playing():
                        self.voice_client.stop()

                    source = join("Audio", "Notificação de tempo.wav")
                    executable = join("System", "ffmpeg.exe")

                    self.voice_client.play(discord.FFmpegPCMAudio(source=source,
                                                                  executable=executable))

                embed = discord.Embed(description="❱❱❱ **A reunião acaba em menos de 10 minutos!**",
                                      color=discord.Color.dark_purple())

                await self.active_text_channel.send(embed=embed)

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

                    text_channel = self.bot.guild_dict[str(ctx.guild.id)].main_channel
                    voice_channel = self.bot.guild_dict[str(ctx.guild.id)].voice_channel

                    if text_channel is None:
                        text_channel = ctx.channel

                    self.active_meeting = meeting
                    self.active_text_channel = text_channel
                    self.active_voice_channel = voice_channel

                    if voice_channel is not None and self.voice_client is None:
                        self.voice_client = await voice_channel.connect()

                        if self.voice_client is not None and self.voice_client.is_connected():

                            if self.voice_client.is_playing():
                                self.voice_client.stop()

                            source = join("Audio", "Notificação de troca de tópico.wav")
                            executable = join("System", "ffmpeg.exe")

                            self.voice_client.play(discord.FFmpegPCMAudio(source=source,
                                                                          executable=executable))

                    embed = discord.Embed(description=f"❱❱❱ **O primeiro tópico é: {meeting.current_topic}**",
                                          color=discord.Color.dark_purple())

                    await text_channel.send(embed=embed)

                    embed = discord.Embed(description=f"❱❱❱ **Reunião \"{args[0]}\" iniciada**",
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

        self.current_topic_id_index = 0
        self.current_topic = ''
        self.current_time = 0
        self.topic_has_changed = False
