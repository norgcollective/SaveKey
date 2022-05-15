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
