# -*- coding: utf-8 -*-

'''
Módulo para os servers.
'''

from datetime import datetime

from discpybotframe.guild import CustomGuild
from source.meeting_management_cog import Meeting


class Guild(CustomGuild):

    '''
    Definição de um server.
    '''

    # Atributos privados
    _meetings: dict

    def __init__(self, identification: int, bot) -> None:
        super().__init__(identification, {"Meetings": {}}, bot)

        self._meetings = {}

        for meeting_name, meeting_topics in self._stored_data["Meetings"].items():
            self._meetings[meeting_name] = Meeting(meeting_name)

            for topic in meeting_topics:
                self._meetings[meeting_name].add_topic(topic[0], topic[1])

        print(f"[{datetime.now()}][System]: Custom guild initialization completed")

    def write_data(self, guilds_dir: str = "guilds") -> None:
        self._stored_data["Meetings"].clear()

        for meeting_name, meeting in self._meetings.items():
            self._stored_data["Meetings"][meeting_name] = meeting.get_topics()

        super().write_data(guilds_dir)

    def add_meeting(self, name: str, meeting: Meeting) -> None:
        '''
        Adiciona uma reunião.
        '''

        self._meetings[name] = meeting

    def remove_meeting(self, name: str) -> None:
        '''
        Remove uma reunião.
        '''

        del self._meetings[name]

    def get_meeting(self, name: str) -> Meeting:
        '''
        Retorna uma reunião.
        '''

        return self._meetings[name]

    def meeting_exist(self, name: str) -> bool:
        '''
        Retorna verdadeiro se a reunião existir.
        '''

        return name in self._meetings
