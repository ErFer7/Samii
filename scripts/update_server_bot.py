# -*- codsing: utf-8 -*-

'''
Atualiza a versão no servidor.
'''

import paramiko

HOSTNAME = ''
USERNAME = ''
with open('server_login.txt', 'r', encoding='utf-8') as file:
    USERNAME, HOSTNAME = file.read().splitlines()

# create an SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# connect to the server
ssh.connect(HOSTNAME, username=USERNAME)

# navigate to the Samii directory and execute git fetch and git pull
stdin, stdout, stderr = ssh.exec_command('cd Samii && git fetch && git pull')

# print the output of the command
print(f'STDOUT: {stdout.read().decode()}')
print(f'STDERR: {stderr.read().decode()}')

# close the SSH client
ssh.close()
