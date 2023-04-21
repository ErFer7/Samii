# -*- codsing: utf-8 -*-

'''
Obtém os dados do bot no servidor.
'''

import paramiko

HOSTNAME = ''
USERNAME = ''
with open('server_login.txt', 'r', encoding='utf-8') as file:
    USERNAME, HOSTNAME = file.read().splitlines()

# create an SSH client and connect to the server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOSTNAME, username=USERNAME)

# create an SFTP client
sftp = ssh.open_sftp()

# navigate to the system directory and download its contents
sftp.get('Samii/system/help.txt', '../system/help.txt')
sftp.get('Samii/system/internal_settings.json', '../system/internal_settings.json')
sftp.get('Samii/database/SamiiDB.sqlite', '../database/SamiiDB.sqlite')

# close the SFTP and SSH clients
sftp.close()
ssh.close()
