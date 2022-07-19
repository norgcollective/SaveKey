#!/usr/bin/python3
import sys
import json
import gi
import os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

NC_APPINFO = (
    'SaveKey 1.0',
    'de.norgcollective.savekey',
    '1.0'
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
        if bool(str(self.dict.get(keyname))): return True
        else: return False

    def read(self, keyname):
        if self.exists(keyname):
            
            if not type(True) is type(self.dict.get(keyname)):
                return self.dict.get(keyname)
            else:
                return str(self.dict.get(keyname))
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
    def __init__(self, conf):
        self.conf = conf
        super().__init__(title="SaveKey")
        self.connect('destroy', Gtk.main_quit)
        self.set_default_size(900,100)
        self.set_resizable(False)
        self.set_border_width(3)


        self.metadatainfolabel = Gtk.Label() # This Variable needs to be defined BEFORE self.create_savekey('default') is executed. Otherwise, there will be errors.

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
        self.bar.set_subtitle("Version " + NC_APPINFO[2])
        self.bar.props.title = self.get_title()
        self.bar.pack_start(self.stackswitch)
        self.set_titlebar(self.bar)

        ### Header Bar - Hamburg Menu ########################################
        ######################################################################

        self.popover_hamburger = Gtk.Popover()
        self.popover_hamburger.set_position(Gtk.PositionType.BOTTOM)

        self.hamburger_menuvbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.hamburger_cdbtn = Gtk.ModelButton(label="Quit Application")
        self.hamburger_cdbtn.connect('clicked', Gtk.main_quit)
        self.hamburger_menuvbox.pack_start(self.hamburger_cdbtn, True, True, 0)

        self.hamburger_aboutbtn = Gtk.ModelButton(label="About Savekey")
        self.hamburger_aboutbtn.connect('clicked', self.about)
        self.hamburger_aboutbtn.set_image(Gtk.Image.new_from_icon_name('help-about-symbolic',Gtk.IconSize.MENU))
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
        self.keyname_save.connect('activate', self.savekey)
        self.tbox_save.pack_start(self.keyname_save, True, True, 0)

        self.btn_save = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.MENU)
        self.btn_save.connect('clicked', self.savekey)
        self.tbox_save.pack_start(self.btn_save, True, True, 0)
        
        self.keyvalue_save = Gtk.Entry()
        self.keyvalue_save.set_placeholder_text('Value')
        self.keyvalue_save.connect('activate', self.savekey)
        self.vbox_save.pack_start(self.keyvalue_save, True, True, 0)

        ### Stack - Load #####################################################
        ######################################################################

        self.vbox_load = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.stack.add_titled(self.vbox_load, 'load', 'Load')

        self.tbox_load = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.vbox_load.pack_start(self.tbox_load, True, True, 0)

        self.keyname_load = Gtk.Entry()
        self.keyname_load.set_placeholder_text('Key Name')
        self.keyname_load.connect('activate', self.loadkey)
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
        self.keyname_delete.connect('activate', self.deletekey)
        self.box_delete.pack_start(self.keyname_delete, True, True, 0)

        self.btn_delete = Gtk.Button.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.MENU)

        self.btn_delete.connect('clicked', self.deletekey)
        self.box_delete.pack_start(self.btn_delete, True, True, 0)

        ### Stack - BookCtrl #################################################
        ######################################################################

        self.hbox_bookctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.vbox_bookctrl = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.btnnew_ctrl   = Gtk.Button(label="Create New Notebook")
        self.btnnew_ctrl.connect('clicked', self.newbook)

        self.btndel_ctrl   = Gtk.Button(label="Delete Notebook")
        self.btndel_ctrl.connect('clicked',self.delbook)
        if self.book == 'default':
            self.btndel_ctrl.set_sensitive(False)
            self.btndel_ctrl.set_tooltip_text('You cannot delete this notebook')
        else: 
            self.btndel_ctrl.set_sensitive(True)
            self.btndel_ctrl.set_tooltip_text('This will delete the "' + self.book + '.json" notebook.')

        self.btncd_ctrl    = Gtk.Button(label="Switch notebook")
        self.btncd_ctrl.connect('clicked',self.switchfile)

        self.vbox_bookctrl.pack_start(self.btnnew_ctrl,True,True,3)
        self.vbox_bookctrl.pack_start(self.btncd_ctrl, True,True,3)
        self.vbox_bookctrl.pack_start(self.btndel_ctrl,True,True,3)
        self.hbox_bookctrl.pack_start(self.metadatainfolabel, True, True, 3)
        self.hbox_bookctrl.pack_start(self.vbox_bookctrl, True, True, 0)
        self.stack.add_titled(self.hbox_bookctrl, 'bookctrl', 'Book Controls')

        ### Window - Finished ################################################
        ######################################################################

        self.add(self.stack)
        self.show_all()

    def delbook(self, widget):
        if self.book != 'default':
            dlgwarn = Gtk.MessageDialog(
                parent=self,
                modal=True,
                destroy_with_parent=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="This will delete the '" + self.book + "' notebook, are you sure that you want to do that?"
            )
            dlgwarn.format_secondary_text('This cannot be undone!')
            response = dlgwarn.run()
            dlgwarn.destroy()

            if response == -6:
                return False

            if os.path.exists(os.environ.get('HOME') + '/.local/share/savekey/notebooks/' + self.book + '.json'):
                os.remove(os.environ.get('HOME') + '/.local/share/savekey/notebooks/' + self.book + '.json')

            self.create_savekey('default')

        else:
            dlgwarn = Gtk.MessageDialog(
                parent=self,
                modal=True,
                destroy_with_parent=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="You cannot delete the default Notebook."
            )
            dlgwarn.run()
            dlgwarn.destroy()
            return False

        

    def newbook(self, widget):


        dlgwarn = Gtk.MessageDialog(
            parent=self,
            modal=True,
            destroy_with_parent=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="This might overwrite an existent Notebook, are you sure that you want to do that?"
        )
        response = dlgwarn.run()
        dlgwarn.destroy()

        if response == -6:
            return False

        self.mkdir = None
        self.mkdir = {
            'win'   : Gtk.Dialog(
                parent=self,
                modal=True,
                destroy_with_parent=True,
            ),
            'entry' : Gtk.Entry(),
            'btnok' : Gtk.Button.new_from_icon_name("document-open-symbolic", Gtk.IconSize.MENU),
            'btnno' : Gtk.Button(label='Cancel'),
            'label' : Gtk.Label(),
            'bar'   : Gtk.HeaderBar(),
            'vbox'  : None,
            'hbox'  : Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        }

        self.mkdir['bar'].set_show_close_button(True)
        self.mkdir['bar'].set_has_subtitle(True)
        self.mkdir['bar'].set_subtitle('Create a new Notebook')
        self.mkdir['bar'].props.title = "Savekey"
        self.mkdir['bar'].pack_start(self.mkdir['btnno'])
        self.mkdir['bar'].pack_end(self.mkdir['btnok'])
        self.mkdir['win'].set_titlebar(self.mkdir['bar'])


        self.mkdir['win'].set_border_width(3)
        self.mkdir['vbox'] = self.mkdir['win'].get_content_area()
        self.mkdir['vbox'].set_spacing(5)

        self.mkdir['label'].set_text('Please enter the Notebook name: ')

        self.mkdir['entry'].set_placeholder_text('Notebook Name')
        self.mkdir['entry'].connect('activate', self.new_yes)

        self.mkdir['btnok'].connect('clicked', self.new_yes)
        self.mkdir['btnok'].set_label(' Open')

        self.mkdir['btnno'].connect('clicked', self.new_no)

        self.mkdir['vbox'].pack_start(self.mkdir['label'], True, True, 0)
        self.mkdir['vbox'].pack_start(self.mkdir['entry'], True, True, 0)

        self.mkdir['vbox'].show_all()
        
        self.mkdir['win'].show_all()
        self.mkdir['win'].run()
        self.mkdir['win'].destroy()

    def new_yes(self, widget):
        r = True
        try:
            newbook = open(os.environ['HOME'] + '/.local/share/savekey/notebooks/' + self.mkdir['entry'].get_text() + '.json', 'w')
            newbook.write(
                json.dumps(
                    {
                        'Metadata': {
                            "creator":os.environ.get('USER'),
                            "Encrypted":False
                        }
                    }
                )
            )
            newbook.close()
            self.create_savekey(self.mkdir['entry'].get_text())
        except:
            dlgerr = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.ERROR,buttons=Gtk.ButtonsType.OK,text='Error occured')
            dlgerr.format_secondary_text("SaveKey was unable to create the new notebook, because of an error")
            dlgerr.run()
            dlgerr.destroy()
            r = False
        else:
            self.mkdir['win'].destroy()
        finally:
            return r

    def new_no(self, widget):
        self.mkdir['win'].destroy()
        self.mkdir = None

    def loadbookctrl(self):
        data = self.sk.read('Metadata')
        msg  = 'Notebook is saved in <i>{book}.json</i>\nNotebook has been <u>created</u> by {author}\nNotebook is <b>{cryptstatus}</b>'
        iscrypt = ('not encrypted', 'encrypted')

        if type(data) is not type(dict()):
            dlgerr = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.WARNING,buttons=Gtk.ButtonsType.OK,text='Unable to Access Metadata key.')
            dlgerr.format_secondary_text("This notebook may be damaged.")
            dlgerr.run()
            dlgerr.destroy()
            self.metadatainfolabel.set_markup('<b>Warning: </b>Unable to load the Metadata Key of the current Notebook (<i>' + self.book + '.json</i>).')
            return False

        else:
            msg = msg.format(book=self.book,author=data.get('creator'), cryptstatus=iscrypt[data.get('Encrypted')])
        self.metadatainfolabel.set_markup(msg)

    def create_savekey(self, book):
        self.book = book
        self.sk = SaveKey(os.environ.get('HOME') + '/.local/share/savekey/notebooks/' + self.book + '.json')
        self.loadbookctrl()

    def savekey(self, widget): # Dialogs: dialogow (DialogOverWrite) and dialoginfo (DialogInformation)
        if self.keyname_save.get_text() == 'Metadata':
            dlgerr = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.ERROR,buttons=Gtk.ButtonsType.OK,text='Access denid')
            dlgerr.format_secondary_text("This key is accessable only in readonly mode.")
            dlgerr.run()
            dlgerr.destroy()
            return False
        

        if not bool(self.keyvalue_save.get_text()) or not bool(self.keyvalue_save.get_text()):
            dlgerr = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.ERROR,buttons=Gtk.ButtonsType.OK,text='Name or Value is empty')
            dlgerr.format_secondary_text("Please add text to both fields.")
            dlgerr.run()
            dlgerr.destroy()
            return False


        if self.sk.exists(self.keyname_save.get_text()) is not False:
            dlgow = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.YES_NO,text='Key Already exists. Do you want to overwrite it?')
            dlgow.format_secondary_text("The current data will be lost.")
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
            dlgerr.format_secondary_text("Plese add a Name to the Textfield.")
            dlgerr.run()
            dlgerr.destroy()
            return False

        skbuffer = self.sk.read(self.keyname_load.get_text())
        if bool(skbuffer):
            if type(skbuffer) is type(str('string')):
                self.keyvalue_load.set_text(skbuffer)
            elif type(skbuffer) is type(dict()):
                dlgmeta = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.ERROR,buttons=Gtk.ButtonsType.CLOSE,text='Access denid')
                dlgmeta.format_secondary_text("If you want to access the Metadata, you have to access the 'Book Controls' via the Main Window.")
                dlgmeta.run()
                dlgmeta.destroy()
                self.keyvalue_load.set_text(str(skbuffer))
        else:
            dlgwarn = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.WARNING,buttons=Gtk.ButtonsType.OK,text='The Key does not exist or is empty.')
            dlgwarn.format_secondary_text("It may have been deleted.")
            dlgwarn.run()
            dlgwarn.destroy()
    def deletekey(self, widget):
        if self.keyname_delete.get_text() == 'Metadata': 
            dlgerr = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.ERROR,buttons=Gtk.ButtonsType.OK,text='You cannot delete the Metadata Key.')
            dlgerr.format_secondary_text("This key is accessable only in readonly mode.")
            dlgerr.run()
            dlgerr.destroy()
        elif not bool(self.keyname_delete.get_text()):
            dlgerr = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.ERROR,buttons=Gtk.ButtonsType.OK,text='Name is empty')
            dlgerr.format_secondary_text("Plese add a Name to the Textfield.")
            dlgerr.run()
            dlgerr.destroy()
            return False
        else:
            self.sk.write(SaveKeyWriteDelete, {'name':self.keyname_delete.get_text()})
    def switchfile(self, widget):
        self.cd = None
        self.cd = {
            'win'   : Gtk.Dialog(
                parent=self,
                modal=True,
                destroy_with_parent=True,
            ),
            'entry' : Gtk.Entry(),
            'btnok' : Gtk.Button.new_from_icon_name("document-open-symbolic", Gtk.IconSize.MENU),
            'btnno' : Gtk.Button(label='Cancel'),
            'label' : Gtk.Label(),
            'bar'   : Gtk.HeaderBar(),
            'vbox'  : None,
            'hbox'  : Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        }

        self.cd['bar'].set_show_close_button(True)
        self.cd['bar'].set_has_subtitle(True)
        self.cd['bar'].set_subtitle('Switch Notebook')
        self.cd['bar'].props.title = "Savekey"
        self.cd['bar'].pack_start(self.cd['btnno'])
        self.cd['bar'].pack_end(self.cd['btnok'])
        self.cd['win'].set_titlebar(self.cd['bar'])


        self.cd['win'].set_border_width(3)
        self.cd['vbox'] = self.cd['win'].get_content_area()
        self.cd['vbox'].set_spacing(5)

        self.cd['label'].set_text('Please enter the Notebook name: ')

        self.cd['entry'].set_placeholder_text('Notebook Name')
        self.cd['entry'].connect('activate', self.switch_yes)

        self.cd['btnok'].connect('clicked', self.switch_yes)
        self.cd['btnok'].set_label(' Open')

        self.cd['btnno'].connect('clicked', self.switch_no)

        self.cd['vbox'].pack_start(self.cd['label'], True, True, 0)
        self.cd['vbox'].pack_start(self.cd['entry'], True, True, 0)

        self.cd['vbox'].show_all()
        
        self.cd['win'].show_all()
        self.cd['win'].run()
        self.cd['win'].destroy()

    def switch_no(self, widget):
        self.cd['win'].destroy()

    def switch_yes(self, widget):
        r = True
        try:
            self.create_savekey(book=str(self.cd['entry'].get_text()))
        except FileNotFoundError:
            dlgerr = Gtk.MessageDialog(parent=self, modal=True, destroy_with_parent=True,message_type=Gtk.MessageType.ERROR,buttons=Gtk.ButtonsType.OK,text='File Not Found')
            dlgerr.format_secondary_text("The file does not exist or savekey is not allowed to access it.")
            dlgerr.run()
            dlgerr.destroy()
            r = False
        else:
            self.cd['win'].destroy()
        finally:
            if self.book == 'default':
                self.btndel_ctrl.set_sensitive(False)
                self.btndel_ctrl.set_tooltip_text('You cannot delete this notebook')
            else: 
                self.btndel_ctrl.set_sensitive(True)
                self.btndel_ctrl.set_tooltip_text('This will delete the "' + self.book + '.json" notebook.')
            return r

    def about(self, widget):

        licensepath = '/usr/share/norgcollective/savekey/License'

        f = open(licensepath)
        l = f.read()
        f.close()

        self.aboutdlg = Gtk.AboutDialog(parent=self, modal=True, destroy_with_parent=True)
        self.aboutdlg.set_program_name('SaveKey')
        self.aboutdlg.set_version(NC_APPINFO[2])
        self.aboutdlg.set_authors(
            ['Henry Schynol']
        )
        self.aboutdlg.set_comments("A simple Notebook Manager")
        self.aboutdlg.set_website("https://norgcollective.github.io/SaveKey/")
        self.aboutdlg.set_license(l)

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

def new(madebysys=False, name='default'):
    author =  (os.environ['USER'], NC_APPINFO[1]  + '.startup.check', 'savekey')
    newbook = open(os.environ['HOME'] + '/.local/share/savekey/notebooks/' + name + '.json', 'w')
    newbook.write(
        json.dumps(
            {
                'Metadata': {
                    "creator":author[int(madebysys)],
                    "Encrypted":False
                }
            }
        )
    )
    newbook.close()

if __name__ == '__main__':
    props = {
        "IsGuiMode": False,
        "ShowWelcomeScreen": True,
        "OnlyShowVersion": False,
        "CheckFiles": True,
        "ShowLogOfStartupCheck": False
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
            txt={'gtk':'\tHelp for ' + NC_APPINFO[0] + '\n\n--enable-gtk   - Launch Savekeys GTK3 GUI (Graphical User Interface) instead of the CLI (Command Line Interface)\n\n--hide-welcome - Hid the default Welcome/Goodbye Messages.\n\n--version      - Terminate Application after Displaying version information\n\n--skip-check   - Skip the Startup Check. It is not reccomended to do so, because it might cause critical errors. \n\n--help         - Show this help\n\n--docs         - Opens the Documentation  in your Webbrowser.\n\n--docs-gui     - Opens the specific part of the documentation, wich is about the GUI, in your Webbrowser.\n\n--docs-cli     - Opens the specific part of the documentation, wich is about the CLI, in your Webbrowser.\n\n--bug          - Report a bug\n\n\nIt is not important to pass the parameters in a specific order.\n\nSome parameters might prevent the application from using the other parameters.',
                'cli':'Help for ' + NC_APPINFO[0] + '\n\t\t--enable-gtk   - Launch Savekeys GTK3 GUI (Graphical User Interface) instead of the CLI (Command Line Interface)\n\t\t--hide-welcome - Hid the default Welcome/Goodbye Messages.\n\t\t--version      - Terminate Application after Displaying version information\n[Critical]\t--skip-check   - Skip the Startup Check. It is not reccomended to do so, because it might cause critical errors. \n\t\t--help         - Show this help\n\t\t--docs         - Opens the Documentation  in your Webbrowser.\n[Specific]\t--docs-gui     - Opens the specific part of the documentation, wich is about the GUI, in your Webbrowser.\n[Specific]\t--docs-cli     - Opens the specific part of the documentation, wich is about the CLI, in your Webbrowser.\n[Important]\t--bug          - Report a bug\n\n\nIt is not important to pass the parameters in a specific order.\nSome parameters might prevent the application from using the other parameters.'},
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
    
    if '--bug' in sys.argv:
        os.system('xdg-open https://github.com/norgcollective/SaveKey/issues')
    
    if '--hide-welcome' in sys.argv:
        props["ShowWelcomeScreen"] = False;
    if '--skip-check' in sys.argv:
        props['CheckFiles'] = False
    elif '--log-check' in sys.argv:
        props['ShowLogOfStartupCheck'] = True;

    # Property reading finished. ##########################################################################
    #######################################################################################################

    if not props.get('CheckFiles'):
        info(
            txt='It is dangerous to skip the default startup check.',
            msgtype='warning', 
            conf=props
        )
    else:
        if not os.path.exists(os.environ['HOME'] + '/.local/share/savekey'):
            os.makedirs(os.environ['HOME'] + '/.local/share/savekey')

        if not os.path.exists(os.environ['HOME'] + '/.local/share/savekey/notebooks'):
            os.makedirs(os.environ['HOME'] + '/.local/share/savekey/notebooks')
        
        try:
            open(os.environ['HOME'] + '/.local/share/savekey/notebooks/default.json', 'x')
        except FileExistsError:
            if props['ShowLogOfStartupCheck']: print("[Log] File default.json exists")
        else:
            print("[Log] File default.json didn't exist. Created default.json and inserted standart Metadata")
            new(madebysys=True)

            

    
    # Start Application          ##########################################################################
    #######################################################################################################

    if props['ShowWelcomeScreen'] and not props['IsGuiMode']:
        print('Welcome to the NorgCollective SaveKey CLI!\n')
    
    if props["IsGuiMode"]:
        MainWin = SaveKeyGui(props)
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
                new(name=entry[6:len(entry)], madebysys=2)
            elif entry[0:3] == 'rm ':
                sk.write(SaveKeyWriteDelete, {'name':entry[3:len(entry)]})
            elif entry in sig_stop:
                if props['ShowWelcomeScreen']: print('Goodbye, see you later!')
            else:
                print('[Error] Unknown Command "' + entry + '". Savekey will ignore this Command.')
