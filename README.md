# KeySave
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

## Warnings

* **KeySave has been developed on and for Linux. It has not been tested for Windows.**
* **KeySave stores the Values as a plain Text file (~/.savekey/master.json). It is not reccomendet to store verry private data with KeySave** 
