# -*- coding: utf-8 -*-

'''
Bot para Discord - 2022-03-09 - ErFer
Projeto: Samii
Bot: Samii
'''
import sys
import asyncio

from bot_system import CustomBot
from admin_cog import AdminCog
from help_cog import HelpCog
from meeting_management_cog import MeetingManagementCog
from settings_cog import SettingsCog
from event_cog import EventCog

# Constantes
NAME = "Samii"
VERSION = "0.2.1"

# Corrige o erro de saída temporáriamente.
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot = CustomBot(command_prefix="++",
                help_command=None,
                name=NAME,
                version=VERSION)

bot.add_cog(AdminCog(bot))
bot.add_cog(HelpCog(bot))
bot.add_cog(SettingsCog(bot))
bot.add_cog(EventCog(bot))
bot.add_cog(MeetingManagementCog(bot))
bot.loop.create_task(bot.setup())
bot.run(bot.token)
