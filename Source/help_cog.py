# -*- coding:utf-8 -*-

'''
Módulo para a cog dos comandos de ajuda
'''

from datetime import datetime

from discord.ext import commands

from Source.utilities import DiscordUtilities


class HelpCog(commands.Cog):

    '''
    Cog dos comandos de ajuda.
    '''

    # Construtor --------------------------------------------------------------
    def __init__(self) -> None:
        print(f"[{datetime.now()}][Help]: Help system initialized")

    # Comandos ----------------------------------------------------------------
    @commands.command(name="help", aliases=("ajuda", "h", "aj"))
    async def custom_help(self, ctx) -> None:
        '''
        Envia uma mensagem de ajuda.
        '''

        print(f"[{datetime.now()}][Help]: <help> (Author: {ctx.author.name})")

        help_text = '''*Administrativos:*


                        **++off**
                        *Encerra a execução*

                        **++info**
                        *Exibe informações técnicas*

                        **++save**
                        *Salva as configurações atuais*


                        *Gerais:*


                        **++help / ++ajuda / ++h / ++aj**
                        *Exibe os comandos*

                        **++meeting / ++reunião / ++mt / ++rn**
                        *Cria uma reunião. Ex:
                        ++meeting [Nome da reunião]*

                        **++remove_meeting / ++remover_reunião / ++rmt / ++rrn**
                        *Remove uma reunião. Ex:
                        ++remove_meeting [Nome da reunião]*

                        **++start / ++iniciar / ++st / ++in**
                        *Inicia uma reunião. Ex:
                        ++start [Nome da reunião]*

                        **++stop / ++parar / ++s / ++p**
                        *Para uma reunião*

                        **++add / ++adicionar / ++a**
                        *Adiciona um tópico em uma reunião. Ex:
                        ++add [Nome da reunião] [Nome do tópico] [Tempo de duração do tópico em minutos]*

                        **++remove / ++remover / ++r**
                        *Remove um tópico de uma reunião. Ex:
                        ++remove [Nome da reunião] [Nome do tópico]*

                        **++channel / ++canal / ++ch / ++ca**
                        *Define o canal de texto princial. Ex:
                        ++channel #[canal]*

                        **++voice_channel / ++canal_voz / ++vch / ++cav**
                        *Define o canal de voz princial. Ex:
                        ++voice_channel [Nome do canal de voz]*'''

        await DiscordUtilities.send_message(ctx, "Comandos disponíveis", help_text, "help")