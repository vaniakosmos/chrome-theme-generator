# chrome theme generator

Generate chrome theme manifest.json based on two colors:
- frame (top browser panel) 
- toolbar (optional, by default will be slightly lighter then frame color)

If selected toolbar color is light then tab and new tab text will be black / grey, otherwise white / light grey.

## usage

```bash
# start
python main.py
# follow steps
# ...
# profit

# you can also specify config with predefined values
python main.py config.ini
# script will look for config.ini by default
```
