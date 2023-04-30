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
    _meetings_cache: dict

    def __init__(self, identification: int, bot) -> None:
        self._meetings_cache = {}
        super().__init__(identification, bot)

    def load_settings(self) -> None:
        pass

    def load_data(self) -> None:

        query = f'''
                    SELECT Name FROM Meeting WHERE GuildID = {self._identification};
                '''

        response = self.bot.database_controller.cursor.execute(query)

        for meeting_name in response.fetchall():
            self._meetings_cache[meeting_name[0]] = Meeting(meeting_name[0], self.bot)  # type: ignore

    def add_meeting(self, name: str, meeting: Meeting) -> None:
        '''
        Adiciona uma reunião.
        '''

        self._meetings_cache[name] = meeting

        query = f'''
                    INSERT INTO Meeting (Name, GuildID)
                    VALUES ('{name}', {self._identification});
                '''

        self.bot.database_controller.cursor.execute(query)
        self.bot.database_controller.connection.commit()

    def remove_meeting(self, name: str) -> None:
        '''
        Remove uma reunião.
        '''

        del self._meetings_cache[name]

        query = f'''
                    DELETE FROM Meeting WHERE Name = '{name}';
                    DELETE FROM Topic WHERE MeetingName = '{name}';
                    DELETE FROM User WHERE MeetingName = '{name}';
                    DELETE FROM UserPresence WHERE MeetingName = '{name}';
                '''

        self.bot.database_controller.cursor.executescript(query)
        self.bot.database_controller.connection.commit()

    def get_meeting(self, name: str) -> Meeting:
        '''
        Retorna uma reunião.
        '''

        return self._meetings_cache[name]

    def has_meeting(self, name: str) -> bool:
        '''
        Retorna verdadeiro se a reunião existir.
        '''

        return name in self._meetings_cache

    def get_member(self, member_id: int):
        '''
        Retorna um membro.
        '''

        return self.guild.get_member(member_id)

    def get_meeting_names(self) -> list[str]:
        '''
        Retorna uma lista de nomes de reuniões.
        '''

        return list(self._meetings_cache.keys())
