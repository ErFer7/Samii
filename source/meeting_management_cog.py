# -*- coding: utf-8 -*-

'''
Módulo de gerenciamento de reuniões.
'''

from __future__ import annotations
from typing import TYPE_CHECKING

from os.path import join
from asyncio import tasks
from datetime import datetime

import discord

from discord.ext import commands, tasks

from discpybotframe.utilities import DiscordUtilities
from discpybotframe.cog import Cog

from source.meeting import Meeting
from source.validation import CustomValidator, ArgumentFormat, ArgumentType

if TYPE_CHECKING:
    from source.bot import CustomBot

class MeetingManagementCog(Cog):

    '''
    Cog de gerenciamento de reuniões.
    '''

    # Atributos privados
    _active_meeting: Meeting | None
    _active_text_channel: discord.TextChannel | None
    _low_time_notified: bool

    def __init__(self, bot: CustomBot) -> None:
        super().__init__(bot)
        self._active_meeting = None
        self._active_text_channel = None
        self._low_time_notified = False

        self.run_meeting.start()

        self.bot.log('MeetingManagementCog', 'Meeting system initialized')

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

                await self.bot.set_activity(f'{self._active_meeting.name}: {remaining_time:.0f} min')

            if self._active_meeting.topic_has_changed:
                self.bot.voice_controller.play_audio(join('audio', 'Topic Change Notification.wav'))  # type: ignore

                await DiscordUtilities.send_message(self._active_text_channel,
                                                    'Tópico atual',
                                                    self._active_meeting.current_topic,
                                                    self._active_meeting.name)
            if self._active_meeting.time_remaining() <= 0.0:
                self._active_meeting.stop()

                await self.bot.voice_controller.remove_all_members()  # type: ignore
                await self.bot.voice_controller.disconnect()  # type: ignore

                await DiscordUtilities.send_message(self._active_text_channel,
                                                    'Reunião encerrada',
                                                    f'A reunião \'{self._active_meeting.name}\' acabou',
                                                    self._active_meeting.name)

                self._active_meeting = None
                self._active_text_channel = None
                self._low_time_notified = False

                await self.bot.set_activity()
            elif self._active_meeting.time_remaining() <= 10.0:
                self.bot.voice_controller.play_audio(join('audio', 'Final Notification.ogg'))  # type: ignore
            elif self._active_meeting.time_remaining() <= 600.0 and not self._low_time_notified:
                self._low_time_notified = True
                self.bot.voice_controller.play_audio(join('audio', 'Time Notification.wav'))  # type: ignore

                await DiscordUtilities.send_message(self._active_text_channel,
                                                    'Notificação de tempo',
                                                    'A reunião acaba em menos de 10 minutos!',
                                                    self._active_meeting.name)

    # Comandos
    @commands.command(name='meeting', aliases=('reunião', 'mt', 'rn'))
    async def create_meeting(self, ctx, *args) -> None:
        '''
        Adiciona uma reunião.
        '''

        self.bot.log('MeetingManagementCog', f'<create_meeting> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'meeting', args=args)
        validator.require_conditions(guild=True, meeting=False)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),))

        if not await validator.validate_command():
            return

        self.bot.get_custom_guild(ctx.guild.id).add_meeting(args[0], Meeting(args[0], self.bot))  # type: ignore

        await DiscordUtilities.send_message(ctx,
                                            'Reunião adicionada',
                                            f'Nome da reunião: {args[0]}',
                                            'meeting')

    @commands.command(name='remove_meeting', aliases=('remover_reunião', 'rmt', 'rrn'))
    async def remove_meeting(self, ctx, *args) -> None:
        '''
        Remove uma reunião.
        '''

        self.bot.log('MeetingManagementCog', f'<remove_meeting> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'remove meeting', args=args)
        validator.require_conditions(guild=True, meeting=True)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),))

        if not await validator.validate_command():
            return

        self.bot.get_custom_guild(ctx.guild.id).remove_meeting(args[0])  # type: ignore

        await DiscordUtilities.send_message(ctx,
                                            'Reunião removida',
                                            f'Nome da reunião: {args[0]}',
                                            'remove meeting')

    @commands.command(name='start', aliases=('iniciar', 'st', 'in'))
    async def start_meeting(self, ctx: commands.Context, *args) -> None:
        '''
        Inicia uma reunião.
        '''

        self.bot.log('MeetingManagementCog', f'<start_meeting> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'remove meeting', args=args)
        validator.require_conditions(guild=True,
                                     meeting=True,
                                     require_topics=True,
                                     require_member_in_voice_channel=True)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),))

        if not await validator.validate_command():
            return

        if self._active_meeting is not None:
            await DiscordUtilities.send_error_message(ctx, 'Uma reunião já está em andamento!', 'start')
            return

        meeting = self.bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])  # type: ignore
        meeting.start()

        self._active_meeting = meeting
        self._active_text_channel = ctx.channel  # type: ignore

        await self.bot.voice_controller.connect(ctx.author.voice.channel)  # type: ignore
        self.bot.voice_controller.play_audio(join('audio', 'Topic Change Notification.wav'))  # type: ignore

        await DiscordUtilities.send_message(ctx,
                                            'Reunião iniciada',
                                            f'Nome da reunião: {args[0]}\n'
                                            f'Duração da reunião: {meeting.get_total_time()}',
                                            'start')

        await DiscordUtilities.send_message(ctx,
                                            'Tópicos',
                                            f'O primeiro tópico é: {meeting.current_topic}\n',
                                            'start')

    @commands.command(name='stop', aliases=('parar', 's', 'p'))
    async def stop_meeting(self, ctx) -> None:
        '''
        Para uma reunião.
        '''

        self.bot.log('MeetingManagementCog',
                     f'[{datetime.now()}][Meeting]: <stop_meeting> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'stop meeting')
        validator.require_conditions(guild=True)

        if not await validator.validate_command():
            return

        if self._active_meeting is None:
            await DiscordUtilities.send_error_message(ctx, 'Não há nenhuma reunião em andamento!', 'stop')
            return

        self._active_meeting.stop()
        await self.bot.voice_controller.disconnect()  # type: ignore
        await self.bot.set_activity()

        await DiscordUtilities.send_message(self._active_text_channel,
                                            'Reunião encerrada',
                                            f'A reunião \'{self._active_meeting.name}\' foi cancelada',
                                            self._active_meeting.name)

        self._active_meeting = None
        self._active_text_channel = None
        self._low_time_notified = False

    @commands.command(name='add', aliases=('adicionar', 'a'))
    async def add_topic(self, ctx, *args) -> None:
        '''
        Adiciona um tópico à uma reunião.
        '''

        self.bot.log('MeetingManagementCog', f'<add_topic> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'add topic', args=args)
        validator.require_conditions(guild=True,
                                     meeting=True,
                                     topic=False)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),
                                      ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),
                                      ArgumentFormat(ArgumentType.INTEGER, (1, 2147483647))))

        if not await validator.validate_command():
            return

        meeting = self.bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])  # type: ignore
        meeting.add_topic(args[1], int(args[2]) * 60)

        await DiscordUtilities.send_message(ctx,
                                            'Tópico adicionado',
                                            f'Tópico \'{args[1]}\' com {args[2]} minuto(s) adicionado em '
                                            f'\'{args[0]}\'',
                                            'add')

    @commands.command(name='remove', aliases=('remover', 'r'))
    async def remove_topic(self, ctx, *args) -> None:
        '''
        Remove um tópico.
        '''

        self.bot.log('MeetingManagementCog', f'<remove_topic> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'remove topic', args=args)
        validator.require_conditions(guild=True,
                                     meeting=True,
                                     topic=True)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),
                                      ArgumentFormat(ArgumentType.STRING, length_range=(1, 255))))

        if not await validator.validate_command():
            return

        meeting = self.bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])  # type: ignore
        meeting.remove_topic(args[1])

        await DiscordUtilities.send_message(ctx,
                                            'Tópico removido',
                                            f'Nome da reunião: {args[0]}\nNome do tópico {args[1]}',
                                            'remove')

    @commands.command(name='add_member', aliases=('adicionar_membro', 'addm', 'am'))
    async def add_member(self, ctx, *args) -> None:
        '''
        Adciona um membro à uma reunião.
        '''

        self.bot.log('MeetingManagementCog', f'<add_member> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'add member', args=args)
        validator.require_conditions(guild=True,
                                     meeting=True,
                                     member=True,
                                     require_member_in_meeting=False)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),
                                      ArgumentFormat(ArgumentType.STRING, length_range=(1, 255))))

        if not await validator.validate_command():
            return

        member_id = int(ctx.message.mentions[0].mention[2:-1])
        member = self.bot.get_guild(ctx.guild.id).get_member(member_id)  # type: ignore

        meeting = self.bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])  # type: ignore
        meeting.add_member(member_id)  # type: ignore

        await DiscordUtilities.send_message(ctx,
                                            'Membro adicionado',
                                            f'Nome da reunião: {args[0]}\nNome do membro: {member.name}',# type: ignore
                                            'add member')

    @commands.command(name='add_members', aliases=('adicionar_membros', 'addms', 'ams'))
    async def add_members(self, ctx, *args) -> None:
        '''
        Adiciona todos os membros na reunião.
        '''

        self.bot.log('MeetingManagementCog', f'<add_members> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'add members', args=args)
        validator.require_conditions(guild=True,
                                     meeting=True)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),))

        if not await validator.validate_command():
            return

        meeting = self.bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])  # type: ignore
        member_count = 0

        for member in ctx.guild.members:
            if not meeting.has_member(member.id) and member != self.bot.user and member.bot is False:
                meeting.add_member(member.id)
                member_count += 1

        await DiscordUtilities.send_message(ctx,
                                            'Membros adicionados',
                                            f'Nome da reunião: {args[0]}\nMembros adicionados: {member_count}',
                                            'add members')

    @commands.command(name='remove_member', aliases=('remover_membro', 'removem', 'rm'))
    async def remove_member(self, ctx, *args) -> None:
        '''
        Remove um membro de uma reunião.
        '''

        self.bot.log('MeetingManagementCog', f'<remove_member> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'remove member', args=args)
        validator.require_conditions(guild=True,
                                     meeting=True,
                                     member=True,
                                     require_member_in_meeting=True)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),
                                      ArgumentFormat(ArgumentType.STRING, length_range=(1, 255))))

        if not await validator.validate_command():
            return

        meeting = self.bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])  # type: ignore
        member_id = int(ctx.message.mentions[0].mention[2:-1])

        meeting.remove_member(member_id)

        await DiscordUtilities.send_message(ctx,
                                            'Membro removido',
                                            f'Membro removido da reunião {args[0]}',
                                            'remove member')

    @commands.command(name='register_frequency', aliases=('registrar_frequencia', 'rf', 'chamada'))
    async def register_frequency(self, ctx) -> None:
        '''
        Registra a frequência de um membro.
        '''

        self.bot.log('MeetingManagementCog', f'<register_frequency> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'register frequency')
        validator.require_conditions(guild=True)

        if not await validator.validate_command():
            return

        if self._active_meeting is None:
            await DiscordUtilities.send_error_message(ctx, 'Nenhuma reunião está ativa!', 'register frequency')
            return

        members = await self.bot.voice_controller.get_members() # type: ignore
        self._active_meeting.register_current_frequecy([member.id for member in members])

        await DiscordUtilities.send_message(ctx,
                                            'Frequência registrada',
                                            f'Frequência registrada na reunião {self._active_meeting.name}',
                                            'register frequency')

    @commands.command(name='show_frequency', aliases=('mostrar_frequencia', 'mf', 'sf'))
    async def show_frequency(self, ctx, *args) -> None:
        '''
        Mostra a frequência de uma reunião.
        '''

        self.bot.log('MeetingManagementCog', f'<show_frequency> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'show frequency', args=args)
        validator.require_conditions(guild=True,
                                     meeting=True)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),))

        if not await validator.validate_command():
            return

        meeting = self.bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])  # type: ignore
        compiled_frequency = meeting.compile_frequency()

        message = ''

        for member_id, frequency in compiled_frequency.items():
            member = self.bot.get_guild(ctx.guild.id).get_member(member_id) # type: ignore
            message += f'**{member.name}**: {frequency}\n' # type: ignore

        await DiscordUtilities.send_message(ctx,
                                            'Frequência acumulada',
                                            f'Esta é a frequência acumulada dos membros na reunião:\n\n{message}',
                                            'show frequency')

    @commands.command(name='meetings', aliases=('reunioes', 'rns', 'mts'))
    async def show_meetings(self, ctx) -> None:
        '''
        Exibe as reunioes de um servidor.
        '''

        self.bot.log('MeetingManagementCog', f'<show_meetings> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'show meetings')
        validator.require_conditions(guild=True)

        if not await validator.validate_command():
            return

        meetings = self.bot.get_custom_guild(ctx.guild.id).get_meeting_names() # type: ignore

        if len(meetings) == 0: # type: ignore
            await DiscordUtilities.send_message(ctx,
                                    'Reuniões registradas',
                                    'Não há reuniões registradas \'-\'',
                                    'show meetings')
            return

        message = ''

        for meeting in meetings: # type: ignore
            message += f'**{meeting}**\n'

        await DiscordUtilities.send_message(ctx,
                                            'Reuniões registradas',
                                            f'Estas são as reuniões registradas:\n\n{message}',
                                            'show meetings')

    @commands.command(name='members', aliases=('membros', 'ms'))
    async def show_members(self, ctx, *args) -> None:
        '''
        Exibe os membros de uma reunião.
        '''

        self.bot.log('MeetingManagementCog', f'<show_members> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'show members', args=args)
        validator.require_conditions(guild=True,
                                     meeting=True)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),))

        if not await validator.validate_command():
            return

        meeting = self.bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])  # type: ignore
        members_id = meeting.members_id  # type: ignore

        if len(members_id) == 0:
            await DiscordUtilities.send_message(ctx,
                                                'Membros registrados',
                                                'Não há membros registrados \'-\'',
                                                'show members')
            return

        message = ''

        for member_id in members_id:
            member = self.bot.get_guild(ctx.guild.id).get_member(member_id)  # type: ignore
            message += f'**{member.name}**\n'  # type: ignore

        await DiscordUtilities.send_message(ctx,
                                            'Membros registrados',
                                            f'Estes são os membros registrados:\n\n{message}',
                                            'show members')

    @commands.command(name='topics', aliases=('topicos', 'ts'))
    async def show_topics(self, ctx, *args) -> None:
        '''
        Exibe os tópicos de uma reunião.
        '''

        self.bot.log('MeetingManagementCog', f'<show_topics> (Author: {ctx.author.name})')

        validator = CustomValidator(self.bot, ctx, 'show members', args=args)
        validator.require_conditions(guild=True,
                                     meeting=True)
        validator.require_arg_format((ArgumentFormat(ArgumentType.STRING, length_range=(1, 255)),))

        if not await validator.validate_command():
            return

        meeting = self.bot.get_custom_guild(ctx.guild.id).get_meeting(args[0])  # type: ignore
        topics = meeting.get_topics()  # type: ignore

        if len(topics) == 0:
            await DiscordUtilities.send_message(ctx,
                                                'Tópicos registrados',
                                                'Não há tópicos registrados \'-\'',
                                                'show topics')
            return

        message = ''

        for topic in topics:
            message += f'**{topic[0]}**: {topic[1] // 60} min\n'

        await DiscordUtilities.send_message(ctx,
                                            'Tópicos registrados',
                                            f'Estes são os tópicos registrados:\n\n{message}',
                                            'show topics')
