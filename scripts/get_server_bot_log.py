# -*- codsing: utf-8 -*-

'''
Obtém os logs do bot no servidor.
'''

from datetime import datetime

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

# The log file name will have the date of the day that the script is executed, not the day that the log was generated
log_date = datetime.now().strftime('%Y-%m-%d_%H%M%S')
sftp.get('Samii/nohup.out', f'../logs/{log_date}_log.txt')

# close the SFTP and SSH clients
sftp.close()
ssh.close()
