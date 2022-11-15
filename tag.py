import os
from subprocess import Popen

command = 'cat total.txt | httpx -silent -t 100 | anew alive.txt '
httpx = Popen(command, shell=True)
httpx.wait()

with open(r"alive.txt", 'r') as fp:
    line_count = len(fp.readlines())
    Lines = fp.readlines()

split_count = round(line_count / 5)

print(split_count)

os.system('split -l '+str(split_count)+' alive.txt')

commands = [
    'nuclei -l xaa -irr -json',
    'nuclei -l xab -irr -json',
    'nuclei -l xac -irr -json',
    'nuclei -l xad -irr -json',
    'nuclei -l xae -irr -json'
]

# run in parallel
processes = [Popen(cmd, shell=True) for cmd in commands]

# wait for completion
for p in processes: p.wait()


