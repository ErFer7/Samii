# -*- coding: utf-8 -*-

'''
Módulo para os servers.
'''

from discpybotframe.guild import Guild
from source.meeting_management_cog import Meeting


class CustomGuild(Guild):

    '''
    Definição de um server.
    '''

    # Atributos privados
    _meetings: dict

    def __init__(self, identification: int, bot) -> None:
        self._meetings = {}
        super().__init__(identification, {'Meetings': {}}, bot)

    def set_loaded_data(self, settings: dict) -> None:
        for meeting_name, meeting_data in settings['Meetings'].items():
            self._meetings[meeting_name] = Meeting(meeting_name)

            for topic in meeting_data['topics']:
                self._meetings[meeting_name].add_topic(topic[0], topic[1])

            for member_id in meeting_data['members_id']:
                self._meetings[meeting_name].add_member(member_id)

            for frequency in meeting_data['frequency_control']:
                self._meetings[meeting_name].add_frequency(frequency)

    def prepare_data(self) -> dict:

        data = self.stored_data

        try:
            for meeting_name, meeting in self._meetings.items():
                data['Meetings'][meeting_name] = {'topics': meeting.get_topics(),
                                                  'members_id': meeting.members_id,
                                                  'frequency_control': meeting.member_frequency}
        except Exception as error:
            self.bot.log('CustomGuild', f'Error while preparing data for the guild {self._identification}')
            self.bot.log('CustomGuild', f'<Error>: {error}')

        return data

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

    def get_member(self, member_id: int):
        '''
        Retorna um membro.
        '''

        return self.guild.get_member(member_id)
