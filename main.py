#!/usr/bin/python3

import sys
import os
import json

version = str('Development Version 1.0 - OP1')

debuginfo = {
    'savekeystartuplog': str(os.environ['HOME'] + '/.savekey/startup.log'),
    'savekeyversion': str(version),
    'savekeyauthor':'Henry Schynol',
    'savekeydevstate':'development'
}

# main.py
#
# Copyright 2022 Henry Schynol
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

def is_json(myjson):
  try:
    json.loads(myjson)
  except json.JSONDecodeError:
    return False
  else:
      return True

helpstr = """savekey -s KEY_NAME KEY_VALUE saves KEY_VALUE as KEY_NAME
savekey -l KEY_NAME           prints the value of KEY_NAME
savekey -d KEY_NAME           deltes the key named KEY_NAME
savekey --list                lists all key-value pairs
savekey -r                    deletes all keys, except the debug keys
savekey -v                    Terminates Programm after printing the welcomescreen"""

def addkey(newkey, newvalue):
    # First create a dictionary based on the old file.
    f = open(os.environ['HOME'] + '/.savekey/master.json','r')
    oldcontent = f.read()
    f.close()

    keymap = json.loads(oldcontent)

    #Then extend the Dictionary
    if bool(keymap.get(newkey)):
        if input('Key "' + newkey + '" already exists. Want to override? (Y/n) ') in ['Y', 'y']:
            keymap[newkey] = newvalue
        else:
            return 0
    else:
        keymap[newkey] = newvalue

    # Write the new one into the file
    f = open(os.environ['HOME'] + '/.savekey/master.json','w')
    f.write(json.dumps(keymap))
    f.close()

    print('Saved Key "' + newkey + '".')

def delkey(keyname):
    # First create a dictionary based on the old file.
    f = open(os.environ['HOME'] + '/.savekey/master.json','r')
    oldcontent = f.read()
    f.close()

    keymap = json.loads(oldcontent)

    if keyname != 'master.json.deleteall': # --delete was executed.
        if bool(keymap.get(keyname)):
            keymap.pop(keyname)
        else:
            print('Key was already deleted.')
            return 0

        # Write the new Dictionary into the file
        f = open(os.environ['HOME'] + '/.savekey/master.json','w')
        f.write(json.dumps(keymap))
        f.close()

        print('Deleted Key "' + keyname + '"')
    else: # --reset has been executed
        f = open(os.environ['HOME'] + '/.savekey/master.json','w')
        f.write(json.dumps(debuginfo))
        f.close()

        print('Deleted notebook.')


def getkey(keyname):
    f = open(os.environ['HOME'] + '/.savekey/master.json','r')
    keymap = json.loads(f.read())
    f.close()

    return str(keymap[keyname])

def printkey(keyname):
    f = open(os.environ['HOME'] + '/.savekey/master.json','r')
    keymap = json.loads(f.read())
    f.close()


    if keyname != 'master.json.printall':
        print("Key '" + keyname + "' contains '" + keymap[keyname] + "'. ")
    else:
        for i in keymap:
            print("Key '" + i + "' provides the value '" + str(keymap[i]) + "'")
    return 0

def main(argv):
    try:
        if len(argv) == 1:
            infotext =  'savekey needs at least one parameter.\nExecute savekey -? to get more informations.'
            if getkey('savekeycmdguimgr') == 'cdialog':
                os.system("dialog --erase-on-exit --title 'Error' --msgbox '" + infotext + "' 6 30")
            elif getkey('savekeycmdguimgr') == 'zenity':
                os.system("zenity --info --text='" + infotext + "' --title='Argument Error'")
        elif len(argv) == 2:
            if argv[1] in ['-v', '-V', '--version']: exit(0)
            elif argv[1] in [ '-h', '-H', '--help']: print(helpstr)
            elif argv[1] in ['-r' , '-R','--reset','master.json.deleteall']:
                if input("Are you sure you want to delete any key in 'master.json' ? (Y/n) ") in ['Y', 'y']: delkey('master.json.deleteall')
            elif argv[1] in ['--list', '--showall', '--printall', 'master.json.printall']: printkey('master.json.printall')
            elif argv[1] in ['--debug', '--showinformation', '--info', '-?', ]:
                for i in debuginfo:
                    print(i + debuginfo[i])
            else: print('Invalid Argument ' + str(argv[1]))
        elif len(argv) == 3:
            if argv[1] in ['-l', '-L','--load']:printkey(argv[2])
            elif argv[1] == ['-d', '-D','--delete']:
                if input('Are you sure you want to delete the data of "' + argv[2] + '"? (Y/n) ') in ['Y', 'y']: delkey(argv[2])
            else: print('Invalid list of arguments.\nExecute savekey -? to get more informations.')
        elif len(argv) == 4:
            if argv[1]in ['-s', '-S', '--save']:
                addkey(argv[2], argv[3])
            else: print('Invalid list of arguments.\nExecute savekey -? to get more informations.')
        else:
            print('Invalid list of arguments.\nExecute savekey -? to get more informations.')
    except KeyError:
        print('[Error] Tried to acces a key that does not exist. Terminating program...')
        sys.exit(404)
    return 0

if __name__ == '__main__':
    main(sys.argv)
