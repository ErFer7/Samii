# -*- coding: utf-8 -*-

'''
Testes de unidade.
'''

from unittest import TestCase

from Source.meeting_management_cog import Meeting


class MeetingTests(TestCase):

    '''
    Testes do sistema de gerenciamento de reuniões.
    '''

    def test_create_meeting(self):
        '''
        ...
        '''

        meeting = Meeting("test")
        self.assertTrue(meeting.name == "test")

    def test_get_topic_a(self):
        '''
        ...
        '''

        meeting = Meeting("test")
        self.assertTrue(not meeting.get_topics())

    def test_add_topic(self):
        '''
        ...
        '''

        meeting = Meeting("test")
        meeting.add_topic("test", 60)
        topic = meeting.get_topics()[0]

        self.assertTrue(topic[0] == "test")
        self.assertTrue(topic[1] == 60)

    def test_has_topic(self):
        '''
        ...
        '''

        meeting = Meeting("test")
        meeting.add_topic("test", 60)

        self.assertTrue(meeting.has_topic("test"))

    def test_remove_topic(self):
        '''
        ...
        '''

        meeting = Meeting("test")
        meeting.add_topic("test", 60)
        meeting.remove_topic("test")

        self.assertTrue(not meeting.get_topics())

    def test_get_topics(self):
        '''
        ...
        '''

        meeting = Meeting("test")
        topics = [("test_a", 60), ("test_b", 60), ("test_c", 60)]

        for topic in topics:
            meeting.add_topic(topic[0], topic[1])

        for i, topic in enumerate(meeting.get_topics()):
            self.assertTrue(topic[0] == topics[i][0])
            self.assertTrue(topic[1] == topics[i][1])
