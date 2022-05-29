#!/usr/bin/python3
from sys import argv
from os import system

place = '.'

LogOpt = [False, 0]
if len(argv) > 1:
    if argv[1] == '-PreInitOptLog=True':
        LogOpt = [True, 1]
        print('[Log] Arguments: ' + str(argv))


args = ''
for i in range(len(argv)):
    if LogOpt[0]: print('[Log] Visit for-loop. i=' + str(i))
    if i > LogOpt[1]:
        if LogOpt[0]: print('[Log] Adding Argument "' + str(argv[i]) + '" to list.')
        args += str(argv[i])
        args += ' '

# Now the Execution of the Savekey-files starts

if LogOpt[0]:
    print("[Log] Pythonscript '__init__.py' starts...")

system(place + '/__init__.py')

if LogOpt[0]:
    print("[Log] Pythonscript '__init__.py' finished.")
    print("[Log] Pythonscript 'main.py' starts with parameter '" + args + "' ...")

system(place + '/main.py ' + args)

if LogOpt[0]:
    print("[Log] Pythonscript 'main.py' finished.")
