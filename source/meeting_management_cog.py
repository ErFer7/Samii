# -*- coding: utf-8 -*-

'''
Módulo de gerenciamento de reuniões.
'''

from os.path import join
from asyncio import tasks
from datetime import datetime

import discord

from discord.ext import commands, tasks

from source.meeting import Meeting

from discpybotframe.utilities import DiscordUtilities


class MeetingManagementCog(commands.Cog):

    '''
    Cog de gerenciamento de reuniões.
    '''

    # Atributos privados
    _bot: None
    _active_meeting: None
    _active_text_channel: discord.TextChannel
    _low_time_notified: bool

    def __init__(self, bot) -> None:

        self._bot = bot
        self._active_meeting = None
        self._active_text_channel = None
        self._low_time_notified = False

        self.run_meeting.start()

        print(f"[{datetime.now()}][Meeting]: Meeting system initialized")

    # Loops
    @tasks.loop(seconds=1.0)
    async def run_meeting(self) -> None:
        '''
        Executa uma reunião.
        '''

        remaining_time = -1

        if self._active_meeting is not None:

            self._active_meeting.update_time()

            if self._active_meeting.time_remaining() // 60 != remaining_time:

                remaining_time = self._active_meeting.time_remaining() // 60

                await self._bot.set_activity(f"{self._active_meeting.name}: {remaining_time:.0f} min")

            if self._active_meeting.topic_has_changed:

                self._bot.voice_controller.play_audio(join("Audio", "Topic Change Notification.wav"))

                await DiscordUtilities.send_message(self._active_text_channel,
                                                    "Tópico atual",
                                                    self._active_meeting.current_topic,
                                                    self._active_meeting.name)
            if self._active_meeting.time_remaining() <= 0.0:

                self._active_meeting.reset()

                await self._bot.voice_controller.remove_all_members()
                await self._bot.voice_controller.disconnect()

                await DiscordUtilities.send_message(self._active_text_channel,
                                                    "Reunião encerrada",
                                                    f"A reunião \"{self._active_meeting.name}\" acabou",
                                                    self._active_meeting.name)

                self._active_meeting = None
                self._active_text_channel = None
                self._low_time_notified = 0

                await self._bot.set_activity()
            elif self._active_meeting.time_remaining() <= 10.0:

                self._bot.voice_controller.play_audio(join("Audio", "Final Notification.ogg"))
            elif self._active_meeting.time_remaining() <= 600.0 and not self._low_time_notified:

                self._low_time_notified = True
                self._bot.voice_controller.play_audio(join("Audio", "Time Notification.wav"))

                await DiscordUtilities.send_message(self._active_text_channel,
                                                    "Notificação de tempo",
                                                    "A reunião acaba em menos de 10 minutos!",
                                                    self._active_meeting.name)

    # Comandos
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

        if self._bot.get_custom_guild(ctx.guild.id).meeting_exist(args[0]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião já existe!",
                                                "meeting",
                                                True)
            return

        self._bot.get_custom_guild(ctx.guild.id).add_meeting(args[0], Meeting(args[0]))

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

        if not self._bot.get_custom_guild(ctx.guild.id).meeting_exist(args[0]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "remove meeting",
                                                True)
            return

        self._bot.get_custom_guild(ctx.guild.id).remove_meeting(args[0])

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

        if not self._bot.get_custom_guild(ctx.guild.id).meeting_exist(args[0]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "start",
                                                True)
            return

        meeting = self._bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])

        if meeting.topic_count == 0:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não possui nenhum tópico!",
                                                "start",
                                                True)
            return

        if self._active_meeting is not None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Uma reunião já está em andamento!",
                                                "start",
                                                True)
            return

        meeting.start()

        text_channel = self._bot.get_custom_guild(ctx.guild.id).get_main_channel()
        voice_channel = self._bot.get_custom_guild(ctx.guild.id).get_voice_channel()

        if text_channel is None:
            text_channel = ctx.channel

        self._active_meeting = meeting
        self._active_text_channel = text_channel

        await self._bot.voice_controller.connect(voice_channel)
        self._bot.voice_controller.play_audio(join("Audio", "Topic Change Notification.wav"))

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

        if self._active_meeting is None:

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "Não há nenhuma reunião em andamento!",
                                                "start",
                                                True)
            return

        self._active_meeting.reset()
        await self._bot.voice_controller.disconnect()

        await DiscordUtilities.send_message(self._active_text_channel,
                                            "Reunião encerrada",
                                            f"A reunião \"{self._active_meeting.name}\" foi cancelada",
                                            self._active_meeting.name)

        self._active_meeting = None
        self._active_text_channel = None
        self._low_time_notified = 0

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

        if not self._bot.get_custom_guild(ctx.guild.id).meeting_exist(args[0]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "add",
                                                True)
            return

        if self._bot.get_custom_guild(ctx.guild.id).get_meeting(args[0]).has_topic(args[1]):

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

        meeting = self._bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])

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

        if not self._bot.get_custom_guild(ctx.guild.id).meeting_exist(args[0]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "A reunião não foi encontrada!",
                                                "remove",
                                                True)
            return

        if not self._bot.get_custom_guild(ctx.guild.id).get_meeting(args[0]).has_topic(args[1]):

            await DiscordUtilities.send_message(ctx,
                                                "Comando inválido",
                                                "O tópico não foi encontrado",
                                                "remove",
                                                True)
            return

        self._bot.get_custom_guild(ctx.guild.id).get_meeting(args[0]).remove_topic(args[1])

        await DiscordUtilities.send_message(ctx,
                                            "Tópico removido",
                                            f"Nome da reunião: {args[0]}\nNome do tópico {args[1]}",
                                            "remove")
