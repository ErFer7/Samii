# -*- codsing: utf-8 -*-

'''
Obtém os dados do bot no servidor.
'''

import os
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

# navigate to the guilds directory and download its contents
REMOTE_DIR = 'Samii/guilds/'
LOCAL_DIR = '../guilds'
os.makedirs(LOCAL_DIR, exist_ok=True)
for filename in sftp.listdir(REMOTE_DIR):
    remote_path = REMOTE_DIR + filename  # Assumes that the OS is Linux
    local_path = os.path.join(LOCAL_DIR, filename)
    sftp.get(remote_path, local_path)

# close the SFTP and SSH clients
sftp.close()
ssh.close()
