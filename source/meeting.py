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

    # Atributos privados
    _name: str
    _topic_has_changed: bool
    _topic_count: int
    _current_topic: str
    _total_time: float
    _current_topic_id_index: int
    _cummulative_topic_time: int
    _time_counter: float
    _topics: dict
    _last_topic_id: int
    _last_time: float
    _members_id: list
    _member_frequency: list
    _current_member_frequency: list
    _start_time: float

    def __init__(self, name: str) -> None:
        self._name = name
        self._total_time = 0.0
        self._topic_count = 0
        self._current_topic_id_index = 0
        self._current_topic = ''
        self._time_counter = 0.0
        self._cummulative_topic_time = 0
        self._topics = {}
        self._topic_has_changed = False
        self._last_topic_id = 0
        self._last_time = 0.0
        self._members_id = []
        self._member_frequency = []
        self._current_member_frequency = []
        self._start_time = 0.0

    # Getters e setters
    @property
    def name(self) -> str:
        '''
        Getter do nome da reunião.
        '''

        return self._name

    @property
    def topic_has_changed(self) -> bool:
        '''
        Getter do tópico atual.
        '''

        return self._topic_has_changed

    @property
    def topic_count(self) -> int:
        '''
        Getter da quantidade de tópicos.
        '''

        return self._topic_count

    @property
    def current_topic(self) -> str:
        '''
        Getter do tópico atual.
        '''

        return self._current_topic

    @property
    def members_id(self) -> list:
        '''
        Getter da lista de membros.
        '''

        return self._members_id

    @property
    def member_frequency(self) -> list:
        '''
        Getter da lista de frequência.
        '''

        return self._member_frequency

    # Métodos
    def add_topic(self, topic: str, duration: int) -> None:
        '''
        Adiciona um novo tópico.
        '''

        self._topics[self._last_topic_id] = (topic, duration)
        self._topic_count += 1
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
                self._topic_count -= 1
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

        self._current_topic = self._topics[list(self._topics.keys())[self._current_topic_id_index]][0]
        self._cummulative_topic_time = self._topics[list(self._topics.keys())[self._current_topic_id_index]][1]
        self._start_time = time()
        self._last_time = self._start_time

    def update_time(self) -> None:
        '''
        Passa o tempo.
        '''

        self._topic_has_changed = False

        current_time = time()

        self._time_counter += current_time - self._last_time
        self._last_time = current_time

        if self._cummulative_topic_time <= self._time_counter:
            self._current_topic_id_index += 1

            if self._current_topic_id_index < self._topic_count:
                self._current_topic = self._topics[list(self._topics.keys())[self._current_topic_id_index]][0]
                self._cummulative_topic_time += self._topics[list(self._topics.keys())
                                                             [self._current_topic_id_index]][1]
                self._topic_has_changed = True

    def get_total_time(self) -> timedelta:
        '''
        Retorna o tempo total.
        '''

        return timedelta(seconds=self._total_time)

    def time_remaining(self) -> float:
        '''
        Verifica o tempo restante.
        '''

        return self._total_time - self._time_counter

    def stop(self) -> None:
        '''
        Finaliza a reunião.
        '''

        self._member_frequency += self._current_member_frequency
        self._current_member_frequency.clear()
        self._current_topic_id_index = 0
        self._current_topic = ''
        self._time_counter = 0
        self._topic_has_changed = False

    def add_member(self, member_id: int) -> None:
        '''
        Adiciona um membro.
        '''

        self._members_id.append(member_id)

    def remove_member(self, member_id: int) -> None:
        '''
        Remove um membro.
        '''

        self._members_id.remove(member_id)

        # Remove a frequência histórica do membro
        for frequency in self._member_frequency:
            if frequency[1] == member_id:
                self._member_frequency.remove(frequency)

        # Remove a frequência atual do membro
        for frequency in self._current_member_frequency:
            if frequency[1] == member_id:
                self._current_member_frequency.remove(frequency)

    def has_member(self, member_id: int) -> bool:
        '''
        Verifica se o membro existe.
        '''

        return member_id in self._members_id

    def register_current_frequecy(self, members_id: list) -> None:
        '''
        Registra a frequência de uma reunião.
        '''

        registered_members_id = list(map(lambda x: x[1], self._current_member_frequency))

        for member_id in members_id:
            if member_id not in self._members_id or member_id in registered_members_id:
                continue

            self._current_member_frequency.append((self._start_time, member_id))

    def add_frequency(self, frequency: tuple[float, int]) -> None:
        '''
        Adiciona uma frequência.
        '''

        self._member_frequency.append(frequency)

    def compile_frequency(self) -> dict[int ,int]:
        '''
        Compila a frequência.
        '''

        compiled_frequency = {}

        total_member_frequency = self._member_frequency + self._current_member_frequency

        for _, member_id in total_member_frequency:
            if member_id not in compiled_frequency:
                compiled_frequency[member_id] = 1
            else:
                compiled_frequency[member_id] += 1

        return compiled_frequency
