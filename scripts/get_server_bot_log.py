'''
Obtém os logs do bot no servidor.
'''

from datetime import datetime

import paramiko

HOSTNAME = ''
USERNAME = ''
with open('server_login.txt', 'r', encoding='utf-8') as file:
    USERNAME, HOSTNAME = file.read().splitlines()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOSTNAME, username=USERNAME)

sftp = ssh.open_sftp()

log_date = datetime.now().strftime('%Y-%m-%d_%H%M%S')
sftp.get('Samii/nohup.out', f'../logs/{log_date}_log.txt')

sftp.close()
ssh.close()
