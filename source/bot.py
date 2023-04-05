# -*- coding: utf-8 -*-

'''
Módulo que contém a lógica interna do bot.
'''

from datetime import datetime
from os.path import join

import discord
from discord.ext.commands import HelpCommand

from source.guild import CustomGuild
from source.meeting_management_cog import MeetingManagementCog

from discpybotframe.bot import Bot
from discpybotframe.admin_cog import AdminCog
from discpybotframe.help_cog import HelpCog
from discpybotframe.settings_cog import SettingsCog
from discpybotframe.voice import VoiceController


class CustomBot(Bot):

    '''
    Bot customizado.
    '''

    # Atributo privado
    _voice_controller: VoiceController

    def __init__(self,
                 command_prefix: str,
                 help_command: HelpCommand,
                 name: str,
                 version: str) -> None:

        intents = intents = discord.Intents.all()
        super().__init__(command_prefix,
                         help_command,
                         name,
                         join('system', 'internal_settings.json'),
                         intents,
                         version)
        self._voice_controller = VoiceController(self, join('system', 'ffmpeg.exe'))

    # Getters e setters
    @property
    def voice_controller(self) -> VoiceController:
        '''
        Getter do voice_controller.
        '''

        return self._voice_controller

    @voice_controller.setter
    def voice_controller(self, value: VoiceController) -> None:
        '''
        Setter do voice_controller.
        '''

        self._voice_controller = value

    # Métodos assícronos
    async def setup_hook(self) -> None:
        print(f'[{datetime.now()}][System]: Adding cogs...')

        help_text = ''

        with open(join('system', 'help.txt'), 'r', encoding='utf-8') as help_file:
            help_text = help_file.read()

        await self.add_cog(AdminCog(self, 'Tchau!'))
        await self.add_cog(HelpCog(self, help_text))
        await self.add_cog(SettingsCog(self))
        await self.add_cog(MeetingManagementCog(self))

    def load_guilds(self) -> None:
        print(f'[{datetime.now()}][System]: Loading guilds definitions')

        for guild in self.guilds:
            self.custom_guilds[str(guild.id)] = CustomGuild(guild.id, self)
