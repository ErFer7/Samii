'''
Obtém os dados do bot no servidor.
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

sftp.get('Samii/system/internal_settings.json', '../system/internal_settings.json')
sftp.get('Samii/database/SamiiDB.sqlite', '../database/SamiiDB.sqlite')

sftp.close()
ssh.close()
