# -*- coding: utf-8 -*-

'''
Bot para Discord - 2022-03-09 - ErFer
Projeto: Samii
Bot: Samii
'''

import sys
import asyncio

from Source.bot_system import CustomBot
from Source.admin_cog import AdminCog
from Source.help_cog import HelpCog
from Source.meeting_management_cog import MeetingManagementCog
from Source.settings_cog import SettingsCog
from Source.event_cog import EventCog

# Constantes
NAME = "Samii"
VERSION = "0.7"

# Corrige o erro de saída temporáriamente.
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot = CustomBot(command_prefix="++",
                help_command=None,
                name=NAME,
                version=VERSION)

bot.add_cog(AdminCog(bot))
bot.add_cog(HelpCog())
bot.add_cog(SettingsCog(bot))
bot.add_cog(EventCog())
bot.add_cog(MeetingManagementCog(bot))
bot.loop.create_task(bot.setup())
bot.run()
