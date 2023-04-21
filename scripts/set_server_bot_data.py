# -*- codsing: utf-8 -*-

'''
Define os dados do bot no servidor.
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

# navigate to the system directory and upload the contents of the local system directory
sftp.put('../system/internal_settings.json', 'Samii/system/internal_settings.json')
sftp.put('../database/SamiiDB.sqlite', 'Samii/database/SamiiDB.sqlite')

# close the SFTP and SSH clients
sftp.close()
ssh.close()
