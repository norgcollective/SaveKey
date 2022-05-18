# _init_.py
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

import os
import json

def is_json(myjson):
  try:
    json.loads(myjson)
  except json.JSONDecodeError:
    return False
  else:
      return True

version = str('Development Version')
name = str('HeSchy SaveKey')

log = {
    "mkdir": False,
    "mkfile": False,
    "chkfile": False
}

# This code will be executed before the Program starts. Perfect Time to check important files.

    # Create the needed Folder if it does not exists
if not os.path.exists(os.environ['HOME'] + '/.savekey'):
    os.makedirs(os.environ['HOME'] + '/.savekey')

if os.path.exists(os.environ['HOME'] + '/.savekey'):
    log['mkdir'] = True



    # Create the JSON File if it does not exists
try:
    open(os.environ['HOME'] + '/.savekey/master.json', 'x')
except FileExistsError:
    log['mkfile'] = True



    # Check the JSON File for correct content and syntax.
try:
    f = open(os.environ['HOME'] + '/.savekey/master.json','r')
    content = f.read()
    f.close()
    if not bool(content):
        f = open(os.environ['HOME'] + '/.savekey/master.json', 'w')
        f.write(json.dumps({'savekeyversion':version}))
        f.close()
    else:
        if not is_json(content):
            f = open(os.environ['HOME'] + '/.savekey/master.json', 'w')
            f.write(json.dumps({'savekeyversion':version}))
            f.close()
        else:
            keymap = json.loads(content)
            if keymap['savekeyversion'] is not version:
                f = open(os.environ['HOME'] + '/.savekey/master.json','w')
                keymap['savekeyversion'] = version
                f.write(json.dumps(keymap))
                f.close()



except FileNotFoundError:
    log['mkfile'] = False
    log['chkfile'] = False

# Now we have to save the log.
try:
    f = open(os.environ['HOME'] + '/.savekey/startup.log', 'w')
    f.write(json.dumps(log))
    f.close()
except:
    exit(1)


# Now when anything is done, we can say Hello to the user.
print(name + ' [' + version + '] ') 
