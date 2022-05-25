# -*- coding: utf-8 -*-

'''
Módulo de gerenciamento de reuniões.
'''

from os.path import join
from asyncio import tasks
from datetime import datetime, timedelta
from time import time

import discord

from discord.ext import commands, tasks

from Source.utilities import DiscordUtilities


class MeetingManagementCog(commands.Cog):

    '''
    Cog de gerenciamento de reuniões.
    '''

    # Atributos privados ------------------------------------------------------
    __bot: None
    __active_meeting: None
    __active_text_channel: discord.TextChannel
    __active_voice_channel: discord.VoiceChannel
    __voice_client: discord.VoiceClient
    __low_time_notified: bool

    # Construtor --------------------------------------------------------------
    def __init__(self, bot) -> None:

        self.__bot = bot
        self.__active_meeting = None
        self.__active_text_channel = None
        self.__active_voice_channel = None
        self.__voice_client = None
        self.__low_time_notified = False

        self.run_meeting.start()

        print(f"[{datetime.now()}][Meeting]: Meeting system initialized")

    # Métodos -----------------------------------------------------------------
    def play_audio(self, source: str) -> None:
        '''
        Toca um áudio.
        '''

        if self.__voice_client is not None and self.__voice_client.is_connected():

            if self.__voice_client.is_playing():
                self.__voice_client.stop()

            executable = join("System", "ffmpeg.exe")

            self.__voice_client.play(discord.FFmpegPCMAudio(source=source,
                                                            executable=executable))

    # Loops -------------------------------------------------------------------
    @tasks.loop(seconds=1.0)
    async def run_meeting(self) -> None:
        '''
        Executa uma reunião.
        '''

        remaining_time = -1

        if self.__active_meeting is not None:

            self.__active_meeting.update_time()

            if self.__active_meeting.time_remaining() // 60 != remaining_time:

                remaining_time = self.__active_meeting.time_remaining() // 60

                await self.__bot.set_activity(f"{self.__active_meeting.name}: {remaining_time:.0f} min")

            if self.__active_meeting.topic_has_changed:

                self.play_audio(join("Audio", "Topic Change Notification.wav"))

                await DiscordUtilities.send_message(self.__active_text_channel,
                                                    "Tópico atual",
                                                    self.__active_meeting.current_topic,
                                                    self.__active_meeting.name)

            if self.__active_meeting.time_remaining() <= 0.0:

                self.__active_meeting.reset()

                if self.__voice_client is not None and self.__voice_client.is_connected():

                    for member in self.__active_voice_channel.members:

                        if member != self.__bot:
                            await member.move_to(None)

                    await self.__voice_client.disconnect()

                    self.__voice_client = None

                await DiscordUtilities.send_message(self.__active_text_channel,
                                                    "Reunião encerrada",
                                                    f"A reunião \"{self.__active_meeting.name}\" acabou",
                                                    self.__active_meeting.name)

                self.__active_meeting = None
                self.__active_text_channel = None
                self.__active_voice_channel = None
                self.__low_time_notified = 0

                await self.__bot.set_activity()
            elif self.__active_meeting.time_remaining() <= 10.0:

                self.play_audio(join("Audio", "Final Notification.ogg"))
            elif self.__active_meeting.time_remaining() <= 600.0 and not self.__low_time_notified:

                self.__low_time_notified = True

                self.play_audio(join("Audio", "Time Notification.wav"))

                await DiscordUtilities.send_message(self.__active_text_channel,
                                                    "Notificação de tempo",
                                                    "A reunião acaba em menos de 10 minutos!",
                                                    self.__active_meeting.name)

    # Comandos ----------------------------------------------------------------
    @commands.command(name="meeting", aliases=("reunião", "mt", "rn"))
    async def create_meeting(self, ctx, *args) -> None:
        '''
        Adiciona uma reunião.
        '''

        print(f"[{datetime.now()}][Meeting]: <create_meeting> (Author: {ctx.author.name})")

        if len(args) != 1:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome da reunião!",
                                                "meeting",
                                                True)
            return

        if self.__bot.get_custom_guild(ctx.guild.id).meeting_exist(args[0]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião já existe!",
                                                "meeting",
                                                True)
            return

        self.__bot.get_custom_guild(ctx.guild.id).add_meeting(args[0], Meeting(args[0]))

        await DiscordUtilities.send_message(ctx,
                                            "Reunião adicionada",
                                            f"Nome da reunião: {args[0]}",
                                            "meeting")

    @commands.command(name="remove_meeting", aliases=("remover_reunião", "rmt", "rrn"))
    async def remove_meeting(self, ctx, *args) -> None:
        '''
        Remove uma reunião.
        '''

        print(f"[{datetime.now()}][Meeting]: <remove_meeting> (Author: {ctx.author.name})")

        if len(args) != 1:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome da reunião!",
                                                "remove meeting",
                                                True)
            return

        if not self.__bot.get_custom_guild(ctx.guild.id).meeting_exist(args[0]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "remove meeting",
                                                True)
            return

        self.__bot.get_custom_guild(ctx.guild.id).remove_meeting(args[0])

        await DiscordUtilities.send_message(ctx,
                                            "Reunião removida",
                                            f"Nome da reunião: {args[0]}",
                                            "remove meeting")

    @commands.command(name="start", aliases=("iniciar", "st", "in"))
    async def start_meeting(self, ctx, *args) -> None:
        '''
        Inicia uma reunião.
        '''

        print(f"[{datetime.now()}][Meeting]: <start_meeting> (Author: {ctx.author.name})")

        if len(args) != 1:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome da reunião!",
                                                "start",
                                                True)
            return

        if not self.__bot.get_custom_guild(ctx.guild.id).meeting_exist(args[0]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "start",
                                                True)
            return

        meeting = self.__bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])

        if meeting.topic_count == 0:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não possui nenhum tópico!",
                                                "start",
                                                True)
            return

        if self.__active_meeting is not None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Uma reunião já está em andamento!",
                                                "start",
                                                True)
            return

        meeting.start()

        text_channel = self.__bot.get_custom_guild(ctx.guild.id).get_main_channel()
        voice_channel = self.__bot.get_custom_guild(ctx.guild.id).get_voice_channel()

        if text_channel is None:
            text_channel = ctx.channel

        self.__active_meeting = meeting
        self.__active_text_channel = text_channel
        self.__active_voice_channel = voice_channel

        if voice_channel is not None and self.__voice_client is None:
            self.__voice_client = await voice_channel.connect()

            if self.__voice_client is not None and self.__voice_client.is_connected():

                if self.__voice_client.is_playing():
                    self.__voice_client.stop()

                source = join("Audio", "Topic Change Notification.wav")
                executable = join("System", "ffmpeg.exe")

                self.__voice_client.play(discord.FFmpegPCMAudio(source=source,
                                                                executable=executable))

        await DiscordUtilities.send_message(ctx,
                                            "Reunião iniciada",
                                            f"Nome da reunião: {args[0]}\n"
                                            f"Duração da reunião: {meeting.get_total_time()}",
                                            "start")

        await DiscordUtilities.send_message(text_channel,
                                            "Tópicos",
                                            f"O primeiro tópico é: {meeting.current_topic}\n",
                                            "start")

    @commands.command(name="stop", aliases=("parar", "s", "p"))
    async def stop_meeting(self, ctx) -> None:
        '''
        Para uma reunião.
        '''

        print(f"[{datetime.now()}][Meeting]: <stop_meeting> (Author: {ctx.author.name})")

        if self.__active_meeting is None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Não há nenhuma reunião em andamento!",
                                                "start",
                                                True)
            return

        self.__active_meeting.reset()

        if self.__voice_client is not None and self.__voice_client.is_connected():

            await self.__voice_client.disconnect()
            self.__voice_client = None

        await DiscordUtilities.send_message(self.__active_text_channel,
                                            "Reunião encerrada",
                                            f"A reunião \"{self.__active_meeting.name}\" foi cancelada",
                                            self.__active_meeting.name)

        self.__active_meeting = None
        self.__active_text_channel = None
        self.__active_voice_channel = None
        self.__low_time_notified = 0

    @commands.command(name="add", aliases=("adicionar", "a"))
    async def add_topic(self, ctx, *args) -> None:
        '''
        Adiciona um tópico à uma reunião.
        '''

        print(f"[{datetime.now()}][Meeting]: <add_topic> (Author: {ctx.author.name})")

        if len(args) != 3:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome da reunião, "
                                                "nome do tópico e a duração do tópico em minutos!",
                                                "add",
                                                True)
            return

        if not self.__bot.get_custom_guild(ctx.guild.id).meeting_exist(args[0]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "add",
                                                True)
            return

        if self.__bot.get_custom_guild(ctx.guild.id).get_meeting(args[0]).has_topic(args[1]):

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

        meeting = self.__bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])

        meeting.add_topic(args[1], int(args[2]) * 60)

        await DiscordUtilities.send_message(ctx,
                                            "Tópico adicionado",
                                            f"Tópico \"{args[1]}\" com {args[2]} minuto(s) adicionado em "
                                            f"\"{args[0]}\"",
                                            "add")

    @commands.command(name="remove", aliases=("remover", "r"))
    async def remove_topic(self, ctx, *args) -> None:
        '''
        Remove um tópico.
        '''

        print(f"[{datetime.now()}][Meeting]: <remove_topic> (Author: {ctx.author.name})")

        if len(args) != 2:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Especifique o nome da reunião e o tópico a ser removido!",
                                                "remove",
                                                True)
            return

        if not self.__bot.get_custom_guild(ctx.guild.id).meeting_exist(args[0]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "remove",
                                                True)
            return

        if not self.__bot.get_custom_guild(ctx.guild.id).get_meeting(args[0]).has_topic(args[1]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "O tópico não foi encontrado",
                                                "remove",
                                                True)
            return

        self.__bot.get_custom_guild(ctx.guild.id).get_meeting(args[0]).remove_topic(args[1])

        await DiscordUtilities.send_message(ctx,
                                            "Tópico removido",
                                            f"Nome da reunião: {args[0]}\nNome do tópico {args[1]}",
                                            "remove")


class Meeting():

    '''
    Reunião.
    '''

    # Atributos públicos ------------------------------------------------------
    name: str
    topic_has_changed: bool
    topic_count: int
    current_topic: str

    # Atributos privados ------------------------------------------------------
    __total_time: int
    __current_topic_id_index: int
    __cummulative_topic_time: int
    __time_counter: int
    __topics: dict
    __last_topic_id: int
    __last_time: float

    # Construtor --------------------------------------------------------------
    def __init__(self, name: str) -> None:

        self.name = name
        self.__total_time = 0
        self.topic_count = 0
        self.__current_topic_id_index = 0
        self.current_topic = ''
        self.__time_counter = 0
        self.__cummulative_topic_time = 0
        self.__topics = {}
        self.topic_has_changed = False
        self.__last_topic_id = 0
        self.__last_time = None

    # Métodos -----------------------------------------------------------------
    def add_topic(self, topic: str, duration: int) -> None:
        '''
        Adiciona um novo tópico.
        '''

        self.__topics[self.__last_topic_id] = (topic, duration)
        self.topic_count += 1
        self.__total_time += duration
        self.__last_topic_id += 1

    def has_topic(self, topic: str) -> bool:
        '''
        Verifica se o tópíco existe.
        '''

        for topic_tuple in self.__topics.values():

            if topic_tuple[0] == topic:
                return True

        return False

    def remove_topic(self, topic: str) -> None:
        '''
        Remove um tópico.
        '''

        for topic_id, topic_tuple in self.__topics.items():

            if topic_tuple[0] == topic:

                self.topic_count -= 1
                self.__total_time -= topic_tuple[1]
                del self.__topics[topic_id]
                break

    def get_topics(self) -> list:
        '''
        Retorna uma lista de tópicos
        '''

        return list(self.__topics.values())

    def start(self) -> None:
        '''
        Inicia a reunião.
        '''

        self.current_topic = self.__topics[list(self.__topics.keys())[self.__current_topic_id_index]][0]
        self.__cummulative_topic_time = self.__topics[list(self.__topics.keys())[self.__current_topic_id_index]][1]
        self.__last_time = time()

    def update_time(self) -> None:
        '''
        Passa o tempo.
        '''

        self.topic_has_changed = False

        current_time = time()

        self.__time_counter += current_time - self.__last_time
        self.__last_time = current_time

        if self.__cummulative_topic_time <= self.__time_counter:

            self.__current_topic_id_index += 1

            if self.__current_topic_id_index < self.topic_count:

                self.current_topic = self.__topics[list(self.__topics.keys())[self.__current_topic_id_index]][0]
                self.__cummulative_topic_time += self.__topics[list(self.__topics.keys())
                                                               [self.__current_topic_id_index]][1]
                self.topic_has_changed = True

    def get_total_time(self) -> timedelta:
        '''
        Retorna o tempo total.
        '''

        return timedelta(seconds=self.__total_time)

    def time_remaining(self) -> int:
        '''
        Verifica o tempo restante.
        '''

        return self.__total_time - self.__time_counter

    def reset(self) -> None:
        '''
        Reseta a reunião.
        '''

        self.__current_topic_id_index = 0
        self.current_topic = ''
        self.__time_counter = 0
        self.topic_has_changed = False
