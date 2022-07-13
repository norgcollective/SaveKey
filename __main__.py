#!/usr/bin/python3
import sys
import json
import gi
import os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

NC_APPINFO = (
    'SaveKey 1.0 Alpha by Norgcollective',
    'de.norgcollective.savekey - v1.0~alpha'
);

SaveKeyWriteAdd    = 'SK_ADDVALUE' 
SaveKeyWriteEdit   = 'SK_ADDVALUE' 
SaveKeyWriteDelete = 'SK_REMOVEKEY'

class SaveKey():
    def __init__(self, file):
        self.path   =  file
        self.source = open(self.path)
        self.dict   = json.loads(self.source.read())
        self.source.close()

    def write(self, mode, keyprop, execfromgui=False):
        buffer = self.dict
        if mode == 'SK_ADDVALUE':
            if not execfromgui:
                if bool(buffer.get(keyprop['name'])):
                    b = input('Key already exists. Do you want to overwrite it (Y/n)? ')
                    if b.upper() not in ('Y', 'YES','J','JA'):
                        return 'CANCELED_BY_USER'
            else:
                if bool(buffer.get(keyprop['name'])):
                    dlg = Gtk.MessageDialog(parent=None, flags=0,message_type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.YES_NO,text='Key Already exists. Do you want to overwrite it?')
                    b = dlg.run()
                    if b == -9:
                        return 'CANCELED_BY_USER'
            buffer[keyprop['name']] = keyprop['value']
            
            self.dict = buffer
            self.source = open(self.path, 'w')
            self.source.write(json.dumps(self.dict) + '\n')
            self.source.close()

        elif mode == 'SK_REMOVEKEY':

            if not bool(buffer.get(keyprop['name'])):
                return False
            else:
                strbuffer = input('Are you sure that you want to delete this (Y/n)?')
                if strbuffer.upper() in ('NEIN', 'NO', 'N'):
                    return 'CANCELED_BY_USER'
                buffer.pop(keyprop['name'])

                self.dict = buffer
                self.source = open(self.path, 'w')
                self.source.write(json.dumps(self.dict) + '\n')
                self.source.close()

        else:
            print("[Error] SaveKey.write has no '" + str(mode) + "' mode.")
            return 'ModeError'
        

    def read(self, keyname):
        if bool(self.dict.get(keyname)):
            return self.dict[keyname]
        else: 
            print('Key Empty')
            return False

class infowin(Gtk.Window):
    def __init__(self, infotext, infotitle):
        super().__init__(title=infotitle)
        self.connect('destroy', Gtk.main_quit)
        self.set_resizable(False)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.add(self.vbox)

        self.infotext = Gtk.Label()
        self.infotext.set_text(infotext)
        self.vbox.pack_start(self.infotext, True, True, 0)

        self.quitbtn = Gtk.Button(label="Quit Application")
        self.quitbtn.connect('clicked', Gtk.main_quit)
        self.vbox.pack_start(self.quitbtn, True, True, 0)

        self.show_all()

class SaveKeyGui(Gtk.Window):
    def __init__(self):
        super().__init__(title="SaveKey")
        self.connect('destroy', Gtk.main_quit)
        self.set_default_size(400,200)
        self.set_resizable(False)
        self.set_border_width(3)

        self.create_savekey('default')

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(250)

        ### Header Bar - Stackswitch #########################################
        ######################################################################

        self.stackswitch = Gtk.StackSwitcher()
        self.stackswitch.set_stack(self.stack)

        self.bar = Gtk.HeaderBar()
        self.bar.set_show_close_button(True)
        self.bar.props.title = self.get_title()
        self.bar.pack_start(self.stackswitch)
        self.set_titlebar(self.bar)

        ### Header Bar - Hamburg Menu ########################################
        ######################################################################

        self.popover_hamburger = Gtk.Popover()
        self.popover_hamburger.set_position(Gtk.PositionType.BOTTOM)

        self.hamburger_menuvbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.hamburger_info = Gtk.Label()
        self.hamburger_info.set_text('SaveKey 1.0 Alpha')
        self.hamburger_menuvbox.pack_start(self.hamburger_info, True, True, 0)

        self.hamburger_cdbtn = Gtk.ModelButton(label="Switch Notebook")
        self.hamburger_cdbtn.connect('clicked')

        self.hamburger_menuvbox.set_border_width(10)
        self.hamburger_menuvbox.show_all()
        self.popover_hamburger.add(self.hamburger_menuvbox)

        self.hamburger = Gtk.MenuButton(label="", popover=self.popover_hamburger)
        self.hamburger.set_image(Gtk.Image.new_from_icon_name('open-menu-symbolic', Gtk.IconSize.MENU))
        self.bar.pack_end(self.hamburger)

        ### Stack - Save ###################################################
        ######################################################################

        self.vbox_save = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.stack.add_titled(self.vbox_save, 'save', 'Save')

        self.tbox_save = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.vbox_save.pack_start(self.tbox_save, True, True, 0)

        self.keyname_save = Gtk.Entry()
        self.keyname_save.set_placeholder_text('Key Name')
        self.tbox_save.pack_start(self.keyname_save, True, True, 0)

        self.btn_save = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.MENU)
        self.btn_save.connect('clicked', self.savekey)
        self.tbox_save.pack_start(self.btn_save, True, True, 0)
        
        self.keyvalue_save = Gtk.Entry()
        self.keyvalue_save.set_placeholder_text('Value')
        self.vbox_save.pack_start(self.keyvalue_save, True, True, 0)

        ### Stack - Load ###################################################
        ######################################################################

        self.vbox_load = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.stack.add_titled(self.vbox_load, 'load', 'Load')

        self.tbox_load = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.vbox_load.pack_start(self.tbox_load, True, True, 0)

        self.keyname_load = Gtk.Entry()
        self.keyname_load.set_placeholder_text('Key Name')
        self.tbox_load.pack_start(self.keyname_load, True, True, 0)

        self.btn_load = Gtk.Button.new_from_icon_name("edit-find-symbolic", Gtk.IconSize.MENU)
        self.btn_load.connect('clicked', self.loadkey)
        self.tbox_load.pack_start(self.btn_load, True, True, 0)
        
        self.keyvalue_load = Gtk.Entry()
        self.keyvalue_load.set_placeholder_text('Value will be printed here')
        self.keyvalue_load.set_editable(False)
        self.vbox_load.pack_start(self.keyvalue_load, True, True, 0)

        ### Stack - Delete ###################################################
        ######################################################################

        self.box_delete = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.stack.add_titled(self.box_delete, 'delete', 'Delete')

        self.keyname_delete = Gtk.Entry()
        self.keyname_delete.set_placeholder_text('Key Name')
        self.box_delete.pack_start(self.keyname_delete, True, True, 0)

        self.btn_delete = Gtk.Button.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.MENU)
        self.btn_delete.connect('clicked', self.deletekey)
        self.box_delete.pack_start(self.btn_delete, True, True, 0)

        self.add(self.stack)
        self.show_all()
    def create_savekey(self, book):
        self.book = book
        self.sk = SaveKey(os.environ.get('HOME') + '/.local/share/savekey/notebooks/' + self.book + '.json')

    def savekey(self, widget):
        self.sk.write(SaveKeyWriteAdd,{'name':self.keyname_save.get_text(),'value':self.keyvalue_save.get_text()}, True)
    def loadkey(self, widget):
        skbuffer = self.sk.read(self.keyname_load.get_text())
        if bool(skbuffer):
            self.keyvalue_load.set_text(skbuffer)
        else:
            os.system("notify-send --app-name=savekey 'Savekey: Key is empty' -i dialog-warning")
    def deletekey(self, widget):
        self.sk.write(SaveKeyWriteDelete, {'name':self.keyname_delete.get_text()})
    def switchfile(self, widget):
        pass



def info(txt, title, conf, exit=False): 
    if props['IsGuiMode']:
        MainWindow = infowin(txt, title)
        Gtk.main()
    else:
        print(txt)
    if exit:
        sys.exit(0)

if __name__ == '__main__':
    props = {
        "IsGuiMode": False,
        "ShowWelcomeScreen": True,
        "OnlyShowVersion": False,
        "CheckFiles": True
    };
    
    if '--enable-gtk' in sys.argv:
        props["IsGuiMode"] = True;
    if '--hide-welcome' in sys.argv:
        props["ShowWelcomeScreen"] = False;
    elif '--version' in sys.argv:
        props['OnlyShowVersion'] = True
    if '--skip-check' in sys.argv:
        props['CheckFiles'] = False
    # Property reading finished. ##########################################################################
    #######################################################################################################

    if props['OnlyShowVersion']:
        info(NC_APPINFO[0], 'SaveKey',conf=props, exit=True)

    if not props.get('CheckFiles'):
        info('[Warning] It is dangerous to skip the default startup check.','Warning', conf=props)
    else:
        pass

    
    # Start Application          ##########################################################################
    #######################################################################################################

    if props['ShowWelcomeScreen'] and not props['IsGuiMode']:
        print('NorgCollective SaveKey\n')
    
    if props["IsGuiMode"]:
        MainWin = SaveKeyGui()
        Gtk.main()
    else:
        entry = None
        sig_stop = ('quit', 'exit')
        book = 'default'
        newbook = None
        sk = SaveKey(os.environ.get('HOME') + '/.local/share/savekey/notebooks/' + book + '.json')
        keybuffer = {'name':None, 'value':None}
        while entry not in sig_stop:
            entry = input('cli@savekey:' + book + '$ ')

            if entry[0:5] == 'save ':
                
                ctrl = 0
                for i in range(len(entry)):
                    if entry[i] == ':':
                        ctrl = i
                        break;

                keybuffer['name'] = entry[5:ctrl]
                keybuffer['value'] = entry[ctrl+1:(len(entry))]

                sk.write(SaveKeyWriteAdd, keybuffer)

            elif entry[0:5] == 'load ':
                print(sk.read(entry[5:len(entry)]))
            elif entry[0:9] == 'sudo cd ':
                print('Encrypted Storage not yet implemted.')
            elif entry[0:3] == 'cd ':
                book = entry[3:len(entry)]
                sk = SaveKey(os.environ.get('HOME') + '/.local/share/savekey/notebooks/' + book + '.json')
            elif entry[0:6] == 'mkdir ': 
                newbook = open(str(os.environ.get('HOME') + '/.local/share/savekey/notebooks/' + entry[6:len(entry)] + '.json'), 'w')
                newbook.write(
                    json.dumps(
                        {'Metadata': {"creator":os.environ.get('USER')}}
                    )
                )
                newbook.close()
            elif entry[0:3] == 'rm ':
                sk.write(SaveKeyWriteDelete, {'name':entry[3:len(entry)]})
            elif entry in sig_stop:
                print('Goodbye, see you later!')
            else:
                print('[Error] Unknown Command "' + entry + '". Savekey will ignore this Command.')
