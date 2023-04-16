# -*- codsing: utf-8 -*-

'''
Limpa os arquivos de cache do projeto.
'''

import os
import shutil

# navigate to the root directory
os.chdir('../')

# remove all __pycache__ directories
for root, dirs, files in os.walk(".", topdown=False):
    for name in dirs:
        if name == '__pycache__':
            shutil.rmtree(os.path.join(root, name))

# remove all .pytest_cache directories
for root, dirs, files in os.walk(".", topdown=False):
    for name in dirs:
        if name == '.pytest_cache':
            shutil.rmtree(os.path.join(root, name))

# navigate back to the original directory
os.chdir('./scripts')
