# -*- coding: utf-8 -*-

'''
Testes de unidade.
'''

from Source.meeting_management_cog import Meeting

def test_create_meeting():
    '''
    ...
    '''

    meeting = Meeting("test")
    assert meeting.name == "test"

def test_get_topic_a():
    '''
    ...
    '''

    meeting = Meeting("test")
    assert not meeting.get_topics()

def test_add_topic():
    '''
    ...
    '''

    meeting = Meeting("test")
    meeting.add_topic("test", 60)
    topic = meeting.get_topics()[0]

    assert topic[0] == "test"
    assert topic[1] == 60

def test_has_topic():
    '''
    ...
    '''

    meeting = Meeting("test")
    meeting.add_topic("test", 60)

    assert meeting.has_topic("test")

def test_remove_topic():
    '''
    ...
    '''

    meeting = Meeting("test")
    meeting.add_topic("test", 60)
    meeting.remove_topic("test")

    assert not meeting.get_topics()

def test_get_topics():
    '''
    ...
    '''

    meeting = Meeting("test")
    topics = [("test_a", 60), ("test_b", 60), ("test_c", 60)]

    for topic in topics:
        meeting.add_topic(topic[0], topic[1])

    for i, topic in enumerate(meeting.get_topics()):
        assert topic[0] == topics[i][0]
        assert topic[1] == topics[i][1]
