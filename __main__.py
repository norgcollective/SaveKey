#!/usr/bin/python3
import sys
import json
import gi
import os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

NC_APPINFO = (
    'SaveKey 1.0 Alpha',
    'de.norgcollective.savekey - v1.0~alpha',
    '1.0 Alpha'
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
        
    def exists(self, keyname):
        if bool(self.dict.get(keyname)): return True
        else: return False

    def read(self, keyname):
        if self.exists(keyname):
            return self.dict[keyname]
        else:
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
        self.set_default_size(200,75)
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
        self.bar.set_has_subtitle(True)
        self.bar.set_subtitle(NC_APPINFO[2])
        self.bar.props.title = self.get_title()
        self.bar.pack_start(self.stackswitch)
        self.set_titlebar(self.bar)

        ### Header Bar - Hamburg Menu ########################################
        ######################################################################

        self.popover_hamburger = Gtk.Popover()
        self.popover_hamburger.set_position(Gtk.PositionType.BOTTOM)

        self.hamburger_menuvbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.hamburger_info = Gtk.Label()
        self.hamburger_info.set_text(NC_APPINFO[0])
        self.hamburger_menuvbox.pack_start(self.hamburger_info, True, True, 0)

        self.hamburger_cdbtn = Gtk.ModelButton(label="Switch Notebook")
        self.hamburger_cdbtn.connect('clicked', self.switchfile)
        self.hamburger_cdbtn.set_image(Gtk.Image.new_from_icon_name('view-continuous-symbolic',Gtk.IconSize.MENU))
        self.hamburger_menuvbox.pack_start(self.hamburger_cdbtn, True, True, 0)

        self.hamburger_aboutbtn = Gtk.ModelButton(label="About Savekey")
        self.hamburger_aboutbtn.connect('clicked', self.about)
        self.hamburger_aboutbtn.set_image(Gtk.Image.new_from_icon_name('view-continuous-symbolic',Gtk.IconSize.MENU))
        self.hamburger_menuvbox.pack_start(self.hamburger_aboutbtn, True, True, 0)

        self.hamburger_menuvbox.set_border_width(10)
        self.hamburger_menuvbox.show_all()
        self.popover_hamburger.add(self.hamburger_menuvbox)

        self.hamburger = Gtk.MenuButton(label="", popover=self.popover_hamburger)
        self.hamburger.set_image(Gtk.Image.new_from_icon_name('view-more-symbolic', Gtk.IconSize.MENU))
        self.bar.pack_end(self.hamburger)

        ### Stack - Save #####################################################
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

        ### Stack - Load #####################################################
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

    def savekey(self, widget): # Dialogs: dialogow (DialogOverWrite) and dialoginfo (DialogInformation)

        if not bool(self.keyvalue_save.get_text()) or not bool(self.keyvalue_save.get_text()):
            dlgerr = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.ERROR,buttons=Gtk.ButtonsType.OK,text='Name or Value is empty')
            dlgerr.run()
            dlgerr.destroy()
            return False


        if self.sk.exists(self.keyname_save.get_text()) is not False:
            dlgow = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.YES_NO,text='Key Already exists. Do you want to overwrite it?')
            dlgowbuffer = dlgow.run()
            dlgow.destroy()

            if dlgowbuffer == -9:
                return False
            elif dlgowbuffer == -8:
                self.sk.write(SaveKeyWriteAdd,{'name':self.keyname_save.get_text(),'value':self.keyvalue_save.get_text()}, True)
                dlginfo = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.INFO,buttons=Gtk.ButtonsType.OK,text='Key has been saved.')
                dlginfo.run()
                dlginfo.destroy()

    def loadkey(self, widget):

        if not bool(self.keyname_load.get_text()):
            dlgerr = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.ERROR,buttons=Gtk.ButtonsType.OK,text='Name is empty')
            dlgerr.run()
            dlgerr.destroy()
            return False

        skbuffer = self.sk.read(self.keyname_load.get_text())
        if bool(skbuffer):
            self.keyvalue_load.set_text(skbuffer)
        else:
            dlgwarn = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.WARNING,buttons=Gtk.ButtonsType.OK,text='The Key does not exist or is empty.')
            dlgwarn.run()
            dlgwarn.destroy()
    def deletekey(self, widget):
        self.sk.write(SaveKeyWriteDelete, {'name':self.keyname_delete.get_text()})
    def switchfile(self, widget):
        self.cd = None
        self.cd = {
            'win'   : Gtk.Dialog(),
            'entry' : Gtk.Entry(),
            'btnok' : Gtk.Button.new_from_icon_name("document-open-symbolic", Gtk.IconSize.MENU),
            'label' : Gtk.Label(),
            'vbox'  : Gtk.Box(orientation=Gtk.Orientation.VERTICAL),
            'hbox'  : Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        }

        self.cd['entry'].set_placeholder_text('Notebook Name')
        self.cd['btnok'].connect('clicked', self.switch_yes)

        self.cd['hbox'].pack_start(self.cd['entry'], True, True, 0)
        self.cd['hbox'].pack_start(self.cd['btnok'], True, True, 0)

        self.cd['vbox'].pack_start(self.cd['label'], True, True, 0)
        self.cd['vbox'].pack_start(self.cd['hbox'], True, True, 0)

        self.cd['vbox'].show_all()
        
        self.cd['win'].add(self.cd['vbox'])
        self.cd['win'].show_all()
        self.cd['win'].run()

    def switch_yes(self, widget):
        self.create_savekey(book=str(self.cd['entry'].get_text()))

    def about(self, widget):
        self.aboutdlg = Gtk.AboutDialog()
        self.aboutdlg.set_program_name('SaveKey')
        self.aboutdlg.set_version('1.0 Alpha')
        self.aboutdlg.set_authors(
            ['Henry Schynol']
        )

        self.aboutdlg.run()
        self.aboutdlg.destroy()
        


def info(txt, msgtype, conf, exit=False): 
    if conf['IsGuiMode']:
        msg = Gtk.MessageType.INFO

        if type(txt) is type(dict()):
            txt = txt['gtk']

        if msgtype == 'warning': msg = Gtk.MessageType.WARNING
        elif msgtype == 'error': msg = Gtk.MessageType.ERROR

        dlg = Gtk.MessageDialog(parent=None, modal=True, message_type=msg,buttons=Gtk.ButtonsType.CLOSE,text=txt)



        dlg.run()
        dlg.destroy()
    else:

        if type(txt) is type(dict()):
            txt = txt['cli']

        if msgtype == 'warning': print('[Warning]' + txt)
        elif msgtype == 'info':  print(txt)
        elif msgtype == 'error': print('[Error]' + txt)
        else: print(txt)
    if exit:
        sys.exit(0)

if __name__ == '__main__':
    props = {
        "IsGuiMode": False,
        "ShowWelcomeScreen": True,
        "OnlyShowVersion": False,
        "CheckFiles": True
    };

    abnormalstartup = False

    if '--version' in sys.argv:
        props['OnlyShowVersion'] = True
        abnormalstartup = True
    
    if '--docs-cli' in sys.argv: 
        os.system('xdg-open https://github.com/norgcollective/SaveKey/wiki/Command-Line-Interface')
        abnormalstartup = True
    elif '--docs-gui' in sys.argv: 
        os.system('xdg-open https://github.com/norgcollective/SaveKey/wiki/Graphical-User-Interface')
        abnormalstartup = True
    elif '--docs' in sys.argv:
        os.system('xdg-open https://github.com/norgcollective/SaveKey/wiki/Home')
        abnormalstartup = True

    if '--enable-gtk' in sys.argv:
        props["IsGuiMode"] = True;
    
    if '--help' in sys.argv:
        info(
            txt={'gtk':'\tHelp for ' + NC_APPINFO[0] + '\n\n--enable-gtk   - Launch Savekeys GTK3 GUI (Graphical User Interface) instead of the CLI (Command Line Interface)\n\n--hide-welcome - Hid the default Welcome/Goodbye Messages.\n\n--version      - Terminate Application after Displaying version information\n\n--skip-check   - Skip the Startup Check. It is not reccomended to do so, because it might cause critical errors. \n\n--help         - Show this help\n\n--docs         - Opens the Documentation  in your Webbrowser.\n\n--docs-gui     - Opens the specific part of the documentation, wich is about the GUI, in your Webbrowser.\n\n--docs-cli     - Opens the specific part of the documentation, wich is about the CLI, in your Webbrowser.\n\n\nIt is not important to pass the parameters in a specific order.\n\nSome parameters might prevent the application from using the other parameters.',
                'cli':'Help for ' + NC_APPINFO[0] + '\n\t\t--enable-gtk   - Launch Savekeys GTK3 GUI (Graphical User Interface) instead of the CLI (Command Line Interface)\n\t\t--hide-welcome - Hid the default Welcome/Goodbye Messages.\n\t\t--version      - Terminate Application after Displaying version information\n[Critical]\t--skip-check   - Skip the Startup Check. It is not reccomended to do so, because it might cause critical errors. \n\t\t--help         - Show this help\n\t\t--docs         - Opens the Documentation  in your Webbrowser.\n[Specific]\t--docs-gui     - Opens the specific part of the documentation, wich is about the GUI, in your Webbrowser.\n[Specific]\t--docs-cli     - Opens the specific part of the documentation, wich is about the CLI, in your Webbrowser.\n\n\nIt is not important to pass the parameters in a specific order.\nSome parameters might prevent the application from using the other parameters.'},
            msgtype='info',
            conf=props,
            exit=True
        )
    elif props['OnlyShowVersion']:
        info(
            txt=NC_APPINFO[0], 
            msgtype='info',
            conf=props, 
            exit=True
        )

    if abnormalstartup:
        sys.exit(0)
    
    
    if '--hide-welcome' in sys.argv:
        props["ShowWelcomeScreen"] = False;
    if '--skip-check' in sys.argv:
        props['CheckFiles'] = False
    # Property reading finished. ##########################################################################
    #######################################################################################################

    if not props.get('CheckFiles'):
        info(
            txt='It is dangerous to skip the default startup check.',
            msgtype='warning', 
            conf=props
        )
    else:
        pass

    
    # Start Application          ##########################################################################
    #######################################################################################################

    if props['ShowWelcomeScreen'] and not props['IsGuiMode']:
        print('Welcome to the NorgCollective SaveKey CLI!\n')
    
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
                if props['ShowWelcomeScreen']: print('Goodbye, see you later!')
            else:
                print('[Error] Unknown Command "' + entry + '". Savekey will ignore this Command.')
