# -*- coding:utf-8 -*-

'''
Módulo para o armazenamento de métodos.
'''

import discord


class DiscordUtilities():

    '''
    Utilidades.
    '''

    # Métodos estáticos -------------------------------------------------------
    @staticmethod
    async def send_message(ctx,
                           title: str,
                           description: str,
                           footer: str,
                           error: bool = False,
                           url: str = None) -> None:
        '''
        Cria um embed padronizado.
        '''

        embed = None
        prefix = "❱❱❱"
        color = discord.Color.dark_purple()

        if error:
            prefix = "❌ "
            color = discord.Color.red()

        if url is not None:

            embed = discord.Embed(title=f"{prefix} **{title}**",
                                  type="rich",
                                  url=url,
                                  description=description,
                                  color=color)
        else:

            embed = discord.Embed(title=f"{prefix} **{title}**",
                                  type="rich",
                                  description=description,
                                  color=color)

        embed.set_footer(text=f"{footer}")

        await ctx.send(embed=embed)
