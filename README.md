# SaveKey
A Command Line Tool wich can save and load strings. Like a notepad, just more minialistic.

## Usage

```
savekey --save API_key IxDsLdj$2snLL&
```

This command would create a key called `API_key` and saves the Value `IxDsLdj$2snLL&` to it.
To access the key later, you should use this command:

```
savekey --load API_key
```

If you dont want to write `--save` or `--load`, then you can write `-s` or `-l`.

### Parameter List

| Short Parameter | Long Paramter | Function | Warnings |
|--|--|--|--|
| -?   | --help       | Show a help like this |  |
| -v   | --version    | Terminates the application after the Welcome-screen |  |
| -s   | --save       | Saves the Key |  |
| -l   | --load       | Loads a key |  |
| -d   | --delete     | Deletes a key |  |
| -r   | --reset      | Deletes any Key in the master.json file | - **NOT YET IMPLEMENTED** |
| -p   | --password   | Locks the -r Parameter with a password. | - **NOT YET IMPLEMENTED** <br/> - **PASSWORD SAVED IN PLAIN TEXT** |
| -chf | --switchfile | Saves into a different File instead of `master.json`. | - **NOT YET IMPLEMENTED** |
| -gui | --interface  | Starts the Programm with an UI. | - **NOT YET IMPLEMENTED** |
|      | --list       | Lists all keys. | - **NOT YETIMPLEMENTED** |

**For more information visit the [Savekey Wiki](https://github.com/heschy2/SaveKey/wiki)

## Warnings

- **Savekey has been developed as a two-file system. for github it has been compressed into one file. This might produce errors**
- **SaveKey has been developed on and for Linux. It has never been tested for Windows.**
- **SaveKey stores the Values in plain Text files (~/.savekey/*.json). It is not reccomended to store verry private data with KeySave** 
