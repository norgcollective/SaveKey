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

from sys import exit
import os
import json

def is_json(myjson):
  try:
    json.loads(myjson)
  except json.JSONDecodeError:
    return False
  else:
      return True

helpstr = """[savekey -s KEY_NAME KEY_VALUE] saves KEY_VALUE as KEY_NAME
[savekey -l KEY_NAME]           prints the value of KEY_NAME"""

def addkey(newkey, newvalue):
    # First create a dictionary based on the old file.
    f = open(os.environ['HOME'] + '/.savekey/master.json','r')
    oldcontent = f.read()
    f.close()

    keymap = json.loads(oldcontent)

    #Then extend the Dictionary
    if bool(keymap.get(newkey)):
        if input('Key "' + newkey + '" already exists. Wont to override? (Y/n) ') in ['Y', 'y']:
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

def printkey(keyname):
    f = open(os.environ['HOME'] + '/.savekey/master.json','r')
    keymap = json.loads(f.read())
    f.close()

    print("Key '" + keyname + "' contains '" + keymap[keyname] + "'. ")
    return 0

def main(argv):
    if len(argv) == 1:
        print('savekey needs at least one parameter.\nExecute savekey -? to get more informations.')
    elif len(argv) == 2:
        if argv[1] == '-v' or argv[1] == '--version': exit(0)
        elif argv[1] == '-?' or argv[1] == '-h' or argv[1] == '--help': print(helpstr)
        else: print('Invalid Argument' + str(argv[1]))
    elif len(argv) == 3:
        if argv[1] == '-l' or argv[1] == '--load':
            printkey(argv[2])
        elif argv[1] == '-d' or argv[1] == '--delete':
            if input('Are you sure you want to delete the data of "' + argv[2] + '"? (Y/n) ') in ['Y', 'y']:
                delkey(argv[2])
    elif len(argv) == 4:
        if argv[1] == '-s' or argv[1] == '--save':
            addkey(argv[2], argv[3])
    else:
        print('Invalid list of arguments.\nExecute savekey -? to get more informations.')
    return 0
