# -*- coding: utf-8 -*-

'''
Módulo para a validação
'''

from discpybotframe.validation import Validator, ArgumentFormat, ArgumentType
from discpybotframe.utilities import DiscordUtilities


class CustomValidator(Validator):

    '''
    Classe para validação customizada.
    '''

    _require_meeting: bool | None
    _require_topic: bool | None
    _require_member: bool | None
    _require_member_in_meeting: bool | None
    _require_topics: bool
    _require_member_in_voice_channel: bool

    def require_conditions(self,
                           adm: bool = False,
                           guild: bool = False,
                           meeting: bool | None = None,
                           topic: bool | None = None,
                           member: bool | None = None,
                           require_member_in_meeting: bool | None = None,
                           require_topics: bool = False,
                           require_member_in_voice_channel: bool = False) -> None:
        super().require_conditions(adm, guild)
        self._require_meeting = meeting
        self._require_topic = topic
        self._require_member = member
        self._require_member_in_meeting = require_member_in_meeting
        self._require_topics = require_topics
        self._require_member_in_voice_channel = require_member_in_voice_channel

    async def validate_command(self) -> bool:
        if not await super().validate_command():
            return False

        has_meeting = self._bot.get_custom_guild(self.ctx.guild.id).has_meeting(self.args[0])  # type: ignore

        if self._require_meeting is not None and self._require_meeting != has_meeting:
            await DiscordUtilities.send_error_message(self.ctx, self.error_message, self.footer)
            return False

        meeting = self.bot.get_custom_guild(self.ctx.guild.id).get_meeting(self.args[0])  # type: ignore

        if self._require_topic is not None and self._require_topic != meeting.has_topic(self.args[1]):
            await DiscordUtilities.send_error_message(self.ctx, self.error_message, self.footer)
            return False

        member_id = 0

        if self._require_member is not None and self._require_member:
            mention = self.ctx.message.mentions[0].mention

            if len(mention) != 21 and len(mention) != 22:
                await DiscordUtilities.send_error_message(self.ctx, self.error_message, self.footer)
                return False

            try:
                member_id = int(mention[2:-1])
            except TypeError:
                await DiscordUtilities.send_error_message(self.ctx, self.error_message, self.footer)
                return False

        if self._require_member_in_meeting is not None and \
           self._require_member_in_meeting != meeting.has_member(member_id):
            await DiscordUtilities.send_error_message(self.ctx, self.error_message, self.footer)
            return False

        if self._require_topics and meeting.topics_count == 0:
            await DiscordUtilities.send_error_message(self.ctx, self.error_message, self.footer)
            return False

        if self._require_member_in_voice_channel and self.ctx.author.voice is None: # type: ignore
            await DiscordUtilities.send_error_message(self.ctx, self.error_message, self.footer)
            return False

        if self._require_member_in_voice_channel and ctx.author.voice.guild.id != self.ctx.guild.id:  # type: ignore
            await DiscordUtilities.send_error_message(self.ctx, self.error_message, self.footer)
            return False

        return True
