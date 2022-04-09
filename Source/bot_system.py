# -*- coding: utf-8 -*-

'''
Módulo que contém a lógica interna do bot.
'''

import os
import json

from time import time_ns
from random import choice, seed
from datetime import datetime

import discord

from discord.ext import commands

from Source.meeting_management_cog import Meeting


class CustomBot(commands.Bot):

    '''
    Bot customizado.
    '''

    name: str
    version: str
    guild_dict: dict
    admins_id: int
    token: str
    activity_str: str

    def __init__(self, command_prefix, help_command, name, version):

        super().__init__(command_prefix=command_prefix,
                         help_command=help_command)

        self.name = name
        self.version = version
        self.guild_dict = {}
        self.admins_id = []
        self.token = ""
        self.activity_str = ""

        print(f"[{datetime.now()}][System]: Initializing {self.name} {self.version}")
        print(f"[{datetime.now()}][System]: Initializing the RNG")

        seed(time_ns())

        print(f"[{datetime.now()}][System]: Loading internal definitions")

        if os.path.exists(os.path.join("System", "internal_settings.json")):

            with open(os.path.join("System", "internal_settings.json"),
                      'r+',
                      encoding="utf-8") as internal_settings_file:

                internal_settings_json = internal_settings_file.read()

            internal_settings = json.loads(internal_settings_json)

            self.admins_id = list(map(int, internal_settings["ADM_ID"]))
            self.token = internal_settings["TOKEN"]
            self.activity_str = choice(internal_settings["Activities"])
        else:
            print(f"[{datetime.now()}][System]: The loading operation has failed."
                   "The file \"internal_settings.json\" should be in the system directory")

    async def setup(self):
        '''
        Setup do bot.
        '''

        print(f"[{datetime.now()}][System]: Waiting...")
        await self.wait_until_ready()

        print(f"[{datetime.now()}][System]: Loading guilds definitions")
        for guild in self.guilds:
            self.guild_dict[str(guild.id)] = Guild(guild.id, self)

        print(f"[{datetime.now()}][System]: {self.name} {self.version} ready to operate")
        print(f"[{datetime.now()}][System]: Logged as {self.user.name}, with the id: {self.user.id}")

        await self.change_presence(activity=discord.Game(name=self.activity_str))


class Guild():

    '''
    Definição de um server.
    '''

    identification: int
    settings: dict
    guild: discord.guild
    main_channel: discord.TextChannel
    voice_channel: discord.VoiceChannel
    meetings: dict

    def __init__(self, identification, bot):

        self.identification = identification

        if os.path.exists(os.path.join("Guilds", f"{self.identification}.json")):

            with open(os.path.join("Guilds", f"{self.identification}.json"), 'r+', encoding="utf-8") as settings_file:
                settings_json = settings_file.read()

            self.settings = json.loads(settings_json)
        else:

            self.settings = {"Guild ID": self.identification,
                             "Main channel ID": 0,
                             "Voice channel ID": 0,
                             "Meetings": {}}

        self.guild = bot.get_guild(self.settings["Guild ID"])
        self.main_channel = bot.get_channel(self.settings["Main channel ID"])
        self.voice_channel = bot.get_channel(self.settings["Voice channel ID"])

        self.meetings = {}

        for meeting_name, meeting_topics in self.settings["Meetings"].items():

            self.meetings[meeting_name] = Meeting(meeting_name)

            for topic in meeting_topics:
                self.meetings[meeting_name].add_topic(topic[0], topic[1])

        print(f"[{datetime.now()}][System]: Guild {self.identification} initialized")

    def write_settings(self):
        '''
        Escreve as configurações do servidor.
        '''

        self.settings["Meetings"].clear()

        for meeting_name, meeting in self.meetings.items():
            self.settings["Meetings"][meeting_name] = list(meeting.topics.values())

        with open(os.path.join("Guilds", f"{self.identification}.json"), 'w+', encoding="utf-8") as settings_file:

            settings_json = json.dumps(self.settings, indent=4)
            settings_file.write(settings_json)

        print(f"[{datetime.now()}][System]: Guild {self.identification} saved")

    def update_main_channel(self, bot):
        '''
        Atualiza o canal principal.
        '''

        self.main_channel = bot.get_channel(self.settings["Main channel ID"])

        print(f"[{datetime.now()}][System]: The main channel of the guild {self.identification} has been updated")

    def update_voice_channel(self, bot):
        '''
        Atualiza o canal de voz principal.
        '''

        self.voice_channel = bot.get_channel(self.settings["Voice channel ID"])

        print(f"[{datetime.now()}][System]: The main voice channel of the guild "
              f"{self.identification} has been updated")
