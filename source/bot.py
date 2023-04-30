# -*- coding: utf-8 -*-

'''
Módulo que contém a lógica interna do bot.
'''

from os.path import join

import discord
from discord.ext.commands import HelpCommand

from source.guild import CustomGuild
from source.meeting_management_cog import MeetingManagementCog

from discpybotframe.bot import Bot
from discpybotframe.admin_cog import AdminCog
from discpybotframe.help_cog import HelpCog
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
                 version: str,
                 dev_env: bool) -> None:
        intents = intents = discord.Intents.all()

        database_path = join('database', 'DevenvDB.sqlite') if dev_env else join('database', 'SamiiDB.sqlite')

        super().__init__(command_prefix,
                         help_command,
                         name,
                         join('system', 'internal_settings.json'),
                         intents,
                         version,
                         database_path,
                         dev_env)
        self._voice_controller = VoiceController(self)

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
        self.log('CustomBot', 'Adding cogs...')

        help_text = ''

        with open(join('system', 'help.txt'), 'r', encoding='utf-8') as help_file:
            help_text = help_file.read()

        await self.add_cog(AdminCog(self, 'Tchau!'))
        await self.add_cog(HelpCog(self, help_text))
        await self.add_cog(MeetingManagementCog(self))

    def add_guild(self, guild_id: int) -> None:
        self.custom_guilds[str(guild_id)] = CustomGuild(guild_id, self)

    def remove_guild(self, guild_id: int) -> None:
        self.custom_guilds[str(guild_id)].remove()
        del self.custom_guilds[str(guild_id)]
