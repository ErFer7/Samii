# -*- coding: utf-8 -*-

'''
Módulo que contém a lógica interna do bot.
'''

import os
import json

from os.path import exists, join
from time import time_ns
from random import choice, seed
from datetime import datetime
from typing import Callable

import discord

from discord.ext import commands

from Source.meeting_management_cog import Meeting


class CustomBot(commands.Bot):

    '''
    Bot customizado.
    '''

    # Atributos privados ------------------------------------------------------
    __name: str
    __version: str
    __guild_dict: dict
    __admins_id: int
    __token: str
    __activity_str: str

    # Construtor --------------------------------------------------------------
    def __init__(self, command_prefix: str, help_command: Callable, name: str, version: str) -> None:

        super().__init__(command_prefix=command_prefix,
                         help_command=help_command)

        self.__name = name
        self.__version = version
        self.__guild_dict = {}
        self.__admins_id = []
        self.__token = ""
        self.__activity_str = ""

        print(f"[{datetime.now()}][System]: Initializing {self.__name} {self.__version}")
        print(f"[{datetime.now()}][System]: Initializing the RNG")

        seed(time_ns())

        print(f"[{datetime.now()}][System]: Loading internal definitions")

        if exists(join("System", "internal_settings.json")):

            with open(join("System", "internal_settings.json"),
                      'r+',
                      encoding="utf-8") as internal_settings_file:

                internal_settings_json = internal_settings_file.read()

            internal_settings = json.loads(internal_settings_json)

            self.__admins_id = list(map(int, internal_settings["ADM_ID"]))
            self.__token = internal_settings["TOKEN"]
            self.__activity_str = choice(internal_settings["Activities"])
        else:
            print(f"[{datetime.now()}][System]: The loading operation has failed."
                  "The file \"internal_settings.json\" should be in the system directory")

    # Métodos assícronos ------------------------------------------------------
    async def setup(self) -> None:
        '''
        Setup do bot.
        '''

        print(f"[{datetime.now()}][System]: Waiting...")
        await self.wait_until_ready()

        print(f"[{datetime.now()}][System]: Loading guilds definitions")
        for guild in self.guilds:
            self.__guild_dict[str(guild.id)] = CustomGuild(guild.id, self)

        print(f"[{datetime.now()}][System]: {self.__name} {self.__version} ready to operate")
        print(f"[{datetime.now()}][System]: Logged as {self.user.name}, with the id: {self.user.id}")

        await self.set_activity()

    async def set_activity(self, activity: str = None) -> None:
        '''
        Define a atividade.
        '''

        if activity is not None:
            await self.change_presence(activity=discord.Game(name=activity))
        else:
            await self.change_presence(activity=discord.Game(name=self.__activity_str))

    # Métodos -----------------------------------------------------------------
    def run(self, *args: tuple, **kwargs: tuple) -> None:
        '''
        Roda o bot.
        '''

        args += (self.__token,)

        return super().run(*args, **kwargs)

    def write_settings_for_guild(self, guild_id: int) -> None:
        '''
        Salva as configurações do servidor específico.
        '''

        self.__guild_dict[str(guild_id)].write_settings()

    def write_settings_for_all(self) -> None:
        '''
        Salva as configurações de todos os servidores.
        '''

        for guild in self.__guild_dict.values():
            guild.write_settings()

    def is_admin(self, author_id: int) -> bool:
        '''
        Checa se o autor é um administrador.
        '''

        return author_id in self.__admins_id

    def get_info(self) -> dict:
        '''
        Retorna um dicionário com informações.
        '''

        info = {"Name": self.__name,
                "Version": self.__version,
                "HTTP loop": self.http,
                "Latency": self.latency,
                "Guild count": len(self.guilds),
                "Voice clients": self.voice_clients}

        return info

    def get_custom_guild(self, guild_id: int):
        '''
        Retorna um server personalizado.
        '''

        return self.__guild_dict[str(guild_id)]


class CustomGuild():

    '''
    Definição de um server.
    '''

    # Atributos privados ------------------------------------------------------
    __identification: int
    __bot: CustomBot
    __settings: dict
    __guild: discord.Guild
    __main_channel: discord.TextChannel
    __voice_channel: discord.VoiceChannel
    __meetings: dict

    # Construtor --------------------------------------------------------------
    def __init__(self, identification: int, bot: CustomBot) -> None:

        self.__identification = identification
        self.__bot = bot

        if os.path.exists(os.path.join("Guilds", f"{self.__identification}.json")):

            with open(os.path.join("Guilds", f"{self.__identification}.json"), 'r+', encoding="utf-8") as settings_file:
                settings_json = settings_file.read()

            self.__settings = json.loads(settings_json)
        else:

            self.__settings = {"Guild ID": self.__identification,
                               "Main channel ID": 0,
                               "Voice channel ID": 0,
                               "Meetings": {}}

        self.__guild = self.__bot.get_guild(self.__identification)
        self.__main_channel = self.__bot.get_channel(self.__settings["Main channel ID"])
        self.__voice_channel = self.__bot.get_channel(self.__settings["Voice channel ID"])

        self.__meetings = {}

        for meeting_name, meeting_topics in self.__settings["Meetings"].items():

            self.__meetings[meeting_name] = Meeting(meeting_name)

            for topic in meeting_topics:
                self.__meetings[meeting_name].add_topic(topic[0], topic[1])

        print(f"[{datetime.now()}][System]: Guild {self.__identification} initialized")

    # Métodos -----------------------------------------------------------------
    def write_settings(self) -> None:
        '''
        Escreve as configurações do servidor.
        '''

        self.__settings["Meetings"].clear()

        for meeting_name, meeting in self.__meetings.items():
            self.__settings["Meetings"][meeting_name] = list(meeting.topics.values())

        with open(os.path.join("Guilds", f"{self.__identification}.json"), 'w+', encoding="utf-8") as settings_file:

            settings_json = json.dumps(self.__settings, indent=4)
            settings_file.write(settings_json)

        print(f"[{datetime.now()}][System]: Guild {self.__identification} saved")

    def get_main_channel(self) -> discord.TextChannel:
        '''
        Retorna o canal principal caso ele exista.
        '''

        if self.__bot.get_channel(self.__settings["Main channel ID"]) is None:
            self.__main_channel = self.__guild.text_channels[0]

        return self.__main_channel

    def update_main_channel(self, main_channel_id: int) -> None:
        '''
        Atualiza o canal principal.
        '''

        self.__settings["Main channel ID"] = main_channel_id
        self.__main_channel = self.__bot.get_channel(self.__settings["Main channel ID"])

        print(f"[{datetime.now()}][System]: The main channel of the guild {self.__identification} has been updated")

    def get_voice_channel(self) -> discord.VoiceChannel:
        '''
        Retorna o canal de voz principal caso ele exista.
        '''

        if self.__bot.get_channel(self.__settings["Voice channel ID"]):
            self.__voice_channel = self.__guild.voice_channels[0]

        return self.__voice_channel

    def update_voice_channel(self, voice_channel_id: int) -> None:
        '''
        Atualiza o canal de voz principal.
        '''

        self.__settings["Voice channel ID"] = voice_channel_id
        self.__voice_channel = self.__bot.get_channel(self.__settings["Voice channel ID"])

        print(f"[{datetime.now()}][System]: The main voice channel of the guild "
              f"{self.__identification} has been updated")

    def add_meeting(self, name: str, meeting: Meeting) -> None:
        '''
        Adiciona uma reunião.
        '''

        self.__meetings[name] = meeting

    def remove_meeting(self, name: str) -> None:
        '''
        Remove uma reunião.
        '''

        del self.__meetings[name]

    def get_meeting(self, name: str) -> Meeting:
        '''
        Retorna uma reunião.
        '''

        return self.__meetings[name]

    def meeting_exist(self, name: str) -> bool:
        '''
        Retorna verdadeiro se a reunião existir.
        '''

        return name in self.__meetings
