# -*- coding: utf-8 -*-

'''
Bot para Discord - 2022-03-09 - ErFer
Projeto: Samii
Bot: Samii
'''

import sys
import asyncio

from source.bot import CustomBot

# Constantes
NAME = "Samii"
VERSION = "1.1"

# Corrige o erro de saída temporáriamente.
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot = CustomBot(command_prefix="++",
                help_command=None,  # type: ignore
                name=NAME,
                version=VERSION)

bot.run()
