# -*- coding: utf-8 -*-

'''
Módulo de gerenciamento de reuniões.
'''

from os.path import join
from asyncio import tasks
from datetime import datetime, timedelta

import discord

from discord.ext import commands, tasks

from utilities import DiscordUtilities


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

                    source = join("Audio", "Topic Change Notification.wav")
                    executable = join("System", "ffmpeg.exe")

                    self.voice_client.play(discord.FFmpegPCMAudio(source=source,
                                                                  executable=executable))

                await DiscordUtilities.send_message(self.active_text_channel,
                                                    "Tópico atual",
                                                    self.active_meeting.current_topic,
                                                    self.active_meeting.name)

            if self.active_meeting.check_time_remaining() <= 0:

                self.active_meeting.reset()

                if self.voice_client is not None and self.voice_client.is_connected():

                    await self.voice_client.disconnect()

                    for member in self.active_voice_channel.members:
                        await member.move_to(None)

                    self.voice_client = None

                await DiscordUtilities.send_message(self.active_text_channel,
                                                    "Reunião encerrada",
                                                    f"A reunião \"{self.active_meeting.name}\" acabou",
                                                    self.active_meeting.name)

                self.active_meeting = None
                self.active_text_channel = None
                self.active_voice_channel = None
                self.low_time_notified = 0
            elif self.active_meeting.check_time_remaining() <= 10:

                if self.voice_client is not None and self.voice_client.is_connected():

                    if self.voice_client.is_playing():
                        self.voice_client.stop()

                    source = join("Audio", "Final Notification.ogg")
                    executable = join("System", "ffmpeg.exe")

                    self.voice_client.play(discord.FFmpegPCMAudio(source=source,
                                                                  executable=executable))
            elif self.active_meeting.check_time_remaining() <= 600 and not self.low_time_notified:

                self.low_time_notified = True

                if self.voice_client is not None and self.voice_client.is_connected():

                    if self.voice_client.is_playing():
                        self.voice_client.stop()

                    source = join("Audio", "Time Notification.wav")
                    executable = join("System", "ffmpeg.exe")

                    self.voice_client.play(discord.FFmpegPCMAudio(source=source,
                                                                  executable=executable))

                await DiscordUtilities.send_message(self.active_text_channel,
                                                    "Notificação de tempo",
                                                    "A reunião acaba em menos de 10 minutos!",
                                                    self.active_meeting.name)

    @commands.command(name="meeting", aliases=("reunião", "mt", "rn"))
    async def create_meeting(self, ctx, *args):
        '''
        Adiciona uma reunião.
        '''

        print(f"[{datetime.now()}][Admin]: <create_meeting> (Autor: {ctx.author.name})")

        if args is None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Erro crítico nos argumentos!",
                                                "meeting",
                                                True)
            return

        if len(args) != 1:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome da reunião!",
                                                "meeting",
                                                True)
            return

        if args[0] in self.bot.guild_dict[str(ctx.guild.id)].meetings:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião já existe!",
                                                "meeting",
                                                True)
            return

        self.bot.guild_dict[str(ctx.guild.id)].meetings[args[0]] = Meeting(args[0])

        await DiscordUtilities.send_message(ctx,
                                            "Reunião adicionada",
                                            f"Nome da reunião: {args[0]}",
                                            "meeting")

    @commands.command(name="remove_meeting", aliases=("remover_reunião", "rmt", "rrn"))
    async def remove_meeting(self, ctx, *args):
        '''
        Remove uma reunião.
        '''

        print(f"[{datetime.now()}][Admin]: <remove_meeting> (Autor: {ctx.author.name})")

        if args is None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Erro crítico nos argumentos!",
                                                "remove meeting",
                                                True)
            return

        if len(args) != 1:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome da reunião!",
                                                "remove meeting",
                                                True)
            return

        if args[0] not in self.bot.guild_dict[str(ctx.guild.id)].meetings:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "remove meeting",
                                                True)
            return

        del self.bot.guild_dict[str(ctx.guild.id)].meetings[args[0]]

        await DiscordUtilities.send_message(ctx,
                                            "Reunião removida",
                                            f"Nome da reunião: {args[0]}",
                                            "remove meeting")

    @commands.command(name="start", aliases=("iniciar", "st", "in"))
    async def start_meeting(self, ctx, *args):
        '''
        Inicia uma reunião.
        '''

        print(f"[{datetime.now()}][Admin]: <start_meeting> (Autor: {ctx.author.name})")

        if args is None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Erro crítico nos argumentos!",
                                                "start",
                                                True)
            return

        if len(args) != 1:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome da reunião!",
                                                "start",
                                                True)
            return

        if args[0] not in self.bot.guild_dict[str(ctx.guild.id)].meetings:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "start",
                                                True)
            return

        meeting = self.bot.guild_dict[str(ctx.guild.id)].meetings[args[0]]

        if meeting.topic_count == 0:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não possui nenhum tópico!",
                                                "start",
                                                True)
            return

        if self.active_meeting is not None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Uma reunião já está em andamento!",
                                                "start",
                                                True)
            return

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

                source = join("Audio", "Topic Change Notification.wav")
                executable = join("System", "ffmpeg.exe")

                self.voice_client.play(discord.FFmpegPCMAudio(source=source,
                                                              executable=executable))

        await DiscordUtilities.send_message(ctx,
                                            "Reunião iniciada",
                                            f"Nome da reunião: {args[0]}\n"
                                            f"Duração da reunião: {timedelta(seconds=meeting.total_time)}",
                                            "start")

        await DiscordUtilities.send_message(text_channel,
                                            "Tópicos",
                                            f"O primeiro tópico é: {meeting.current_topic}\n",
                                            "start")

    @commands.command(name="stop", aliases=("parar", "s", "p"))
    async def stop_meeting(self, ctx):
        '''
        Para uma reunião.
        '''

        print(f"[{datetime.now()}][Admin]: <stop_meeting> (Autor: {ctx.author.name})")

        if self.active_meeting is None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Não há nenhuma reunião em andamento!",
                                                "start",
                                                True)
            return

        self.active_meeting.reset()

        if self.voice_client is not None and self.voice_client.is_connected():

            await self.voice_client.disconnect()
            self.voice_client = None

        await DiscordUtilities.send_message(self.active_text_channel,
                                            "Reunião encerrada",
                                            f"A reunião \"{self.active_meeting.name}\" foi cancelada",
                                            self.active_meeting.name)

        self.active_meeting = None
        self.active_text_channel = None
        self.active_voice_channel = None
        self.low_time_notified = 0

    @commands.command(name="add", aliases=("adicionar", "a"))
    async def add_topic(self, ctx, *args):
        '''
        Adiciona um tópico à uma reunião.
        '''

        print(f"[{datetime.now()}][Admin]: <add_topic> (Autor: {ctx.author.name})")

        if args is None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Erro crítico nos argumentos!",
                                                "add",
                                                True)
            return

        if len(args) != 3:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome da reunião, "
                                                "nome do tópico e a duração do tópico em minutos!",
                                                "add",
                                                True)
            return

        if args[0] not in self.bot.guild_dict[str(ctx.guild.id)].meetings:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "add",
                                                True)
            return

        if self.bot.guild_dict[str(ctx.guild.id)].meetings[args[0]].has_topic(args[1]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "O tópico já existe!",
                                                "add",
                                                True)
            return

        if not args[2].isnumeric():

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "O tempo precisa ser um número inteiro positivo!",
                                                "add",
                                                True)
            return

        meeting = self.bot.guild_dict[str(ctx.guild.id)].meetings[args[0]]

        meeting.add_topic(args[1], int(args[2]) * 60)

        await DiscordUtilities.send_message(ctx,
                                            "Tópico adicionado",
                                            f"Tópico \"{args[1]}\" com {args[2]} minuto(s) adicionado em "
                                            f"\"{args[0]}\"",
                                            "add")

    @commands.command(name="remove", aliases=("remover", "r"))
    async def remove_topic(self, ctx, *args):
        '''
        Remove um tópico.
        '''

        print(f"[{datetime.now()}][Admin]: <remove_topic> (Autor: {ctx.author.name})")

        if args is None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Erro crítico nos argumentos!",
                                                "remove",
                                                True)
            return

        if len(args) != 2:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome da reunião e o tópico a ser removido!",
                                                "remove",
                                                True)
            return

        if args[0] not in self.bot.guild_dict[str(ctx.guild.id)].meetings:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "remove",
                                                True)
            return

        if not self.bot.guild_dict[str(ctx.guild.id)].meetings[args[0]].has_topic(args[1]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "O tópico não foi encontrado",
                                                "remove",
                                                True)
            return

        self.bot.guild_dict[str(ctx.guild.id)].meetings[args[0]].remove_topic(args[1])

        await DiscordUtilities.send_message(ctx,
                                            "Tópico removido",
                                            f"Nome da reunião: {args[0]}\nNome do tópico {args[1]}",
                                            "remove")


class Meeting():

    '''
    Reunião.
    '''

    name: str
    total_time: int
    topic_count: int
    current_topic_id_index: int
    current_topic: str
    cummulative_topic_time: int
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
        self.cummulative_topic_time = 0
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

    def has_topic(self, topic: str):
        '''
        Verifica se o tópíco existe.
        '''

        for topic_tuple in self.topics.values():

            if topic_tuple[0] == topic:
                return True

        return False

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
        self.cummulative_topic_time = self.topics[list(self.topics.keys())[self.current_topic_id_index]][1]

    def increment_time(self, time: int):
        '''
        Passa o tempo.
        '''

        self.topic_has_changed = False
        self.current_time += time

        if self.cummulative_topic_time <= self.current_time:

            self.current_topic_id_index += 1

            if self.current_topic_id_index < self.topic_count:

                self.current_topic = self.topics[list(self.topics.keys())[self.current_topic_id_index]][0]
                self.cummulative_topic_time += self.topics[list(self.topics.keys())[self.current_topic_id_index]][1]
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
