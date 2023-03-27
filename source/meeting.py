# -*- coding: utf-8 -*-

'''
Módulo para a definição de reuniões.
'''

from datetime import timedelta
from time import time


class Meeting():

    '''
    Reunião.
    '''

    # TODO: Tornar privado
    # Atributos públicos
    name: str
    topic_has_changed: bool
    topic_count: int
    current_topic: str

    # Atributos privados
    _total_time: int
    _current_topic_id_index: int
    _cummulative_topic_time: int
    _time_counter: int
    _topics: dict
    _last_topic_id: int
    _last_time: float
    _members: list
    _frequency_control: dict[list]

    def __init__(self, name: str) -> None:
        self.name = name
        self._total_time = 0
        self.topic_count = 0
        self._current_topic_id_index = 0
        self.current_topic = ''
        self._time_counter = 0
        self._cummulative_topic_time = 0
        self._topics = {}
        self.topic_has_changed = False
        self._last_topic_id = 0
        self._last_time = None
        self._members = []
        self._frequency_control = {}

    def add_topic(self, topic: str, duration: int) -> None:
        '''
        Adiciona um novo tópico.
        '''

        self._topics[self._last_topic_id] = (topic, duration)
        self.topic_count += 1
        self._total_time += duration
        self._last_topic_id += 1

    def has_topic(self, topic: str) -> bool:
        '''
        Verifica se o tópíco existe.
        '''

        for topic_tuple in self._topics.values():

            if topic_tuple[0] == topic:
                return True

        return False

    def remove_topic(self, topic: str) -> None:
        '''
        Remove um tópico.
        '''

        for topic_id, topic_tuple in self._topics.items():
            if topic_tuple[0] == topic:
                self.topic_count -= 1
                self._total_time -= topic_tuple[1]

                del self._topics[topic_id]
                break

    def get_topics(self) -> list:
        '''
        Retorna uma lista de tópicos
        '''

        return list(self._topics.values())

    def start(self) -> None:
        '''
        Inicia a reunião.
        '''

        self.current_topic = self._topics[list(self._topics.keys())[self._current_topic_id_index]][0]
        self._cummulative_topic_time = self._topics[list(self._topics.keys())[self._current_topic_id_index]][1]
        self._last_time = time()

    def update_time(self) -> None:
        '''
        Passa o tempo.
        '''

        self.topic_has_changed = False

        current_time = time()

        self._time_counter += current_time - self._last_time
        self._last_time = current_time

        if self._cummulative_topic_time <= self._time_counter:
            self._current_topic_id_index += 1

            if self._current_topic_id_index < self.topic_count:
                self.current_topic = self._topics[list(self._topics.keys())[self._current_topic_id_index]][0]
                self._cummulative_topic_time += self._topics[list(self._topics.keys())
                                                               [self._current_topic_id_index]][1]
                self.topic_has_changed = True

    def get_total_time(self) -> timedelta:
        '''
        Retorna o tempo total.
        '''

        return timedelta(seconds=self._total_time)

    def time_remaining(self) -> int:
        '''
        Verifica o tempo restante.
        '''

        return self._total_time - self._time_counter

    def reset(self) -> None:
        '''
        Reseta a reunião.
        '''

        self._current_topic_id_index = 0
        self.current_topic = ''
        self._time_counter = 0
        self.topic_has_changed = False

    def add_member(self, member_id: int) -> None:
        '''
        Adiciona um membro.
        '''

        self._members.append(member_id)
        print(self._members)

    def remove_member(self, member_id: int) -> None:
        '''
        Remove um membro.
        '''

        self._members.remove(member_id)

    def has_member(self, member_id: int) -> bool:
        '''
        Verifica se o membro existe.
        '''

        return member_id in self._members
