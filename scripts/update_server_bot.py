'''
Atualiza a versão no servidor.
'''

import paramiko

HOSTNAME = ''
USERNAME = ''
with open('server_login.txt', 'r', encoding='utf-8') as file:
    USERNAME, HOSTNAME = file.read().splitlines()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(HOSTNAME, username=USERNAME)

stdin, stdout, stderr = ssh.exec_command('cd Samii && git fetch && git pull --recurse-submodules')

print(f'STDOUT: {stdout.read().decode()}')
print(f'STDERR: {stderr.read().decode()}')

ssh.close()
