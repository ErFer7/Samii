'''
Define os dados do bot no servidor.
'''

import paramiko

HOSTNAME = ''
USERNAME = ''
with open('server_login.txt', 'r', encoding='utf-8') as file:
    USERNAME, HOSTNAME = file.read().splitlines()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOSTNAME, username=USERNAME)

sftp = ssh.open_sftp()

sftp.put('../system/internal_settings.json', 'Samii/system/internal_settings.json')
sftp.put('../database/SamiiDB.sqlite', 'Samii/database/SamiiDB.sqlite')

sftp.close()
ssh.close()
