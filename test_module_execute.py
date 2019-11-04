import subprocess
import sys

print('$ python -m ghia')
command = ['python', '-m', 'ghia']
p = subprocess.getoutput(command)
print(p)