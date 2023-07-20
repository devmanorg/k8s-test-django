import os
from pydos2unix import dos2unix

base_dir = 'backend_main_django'
filename = os.path.join(base_dir, input())

buffer = ''
with open(filename, 'rb') as file:
    buffer = dos2unix(file)

with open(filename, 'wb') as file:
    file.write(buffer)