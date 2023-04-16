# -*- codsing: utf-8 -*-

'''
Inicia o bot no servidor.
'''

import paramiko
from paramiko import buffered_pipe

HOSTNAME = ''
USERNAME = ''
with open('server_login.txt', 'r', encoding='utf-8') as file:
    USERNAME, HOSTNAME = file.read().splitlines()

# create an SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# connect to the server
ssh.connect(HOSTNAME, username=USERNAME)

try:
    stdin, stdout, stderr = ssh.exec_command('cd Samii && nohup python3 main.py &', timeout=3.0)
    print(f'STDOUT: {stdout.read().decode()}')
    print(f'STDERR: {stderr.read().decode()}')
except (buffered_pipe.PipeTimeout, TimeoutError):
    pass

# close the SSH client
ssh.close()
