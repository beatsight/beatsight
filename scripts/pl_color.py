import json
from pprint import pprint

data = {}
with open('./color.json', 'r') as file:
    # Load the JSON data into a Python dictionary
    data = json.load(file)
print(data)

from beatsight.utils.pl_ext import PL_EXT

pl_color = {}
i = 0
for _, name in PL_EXT.items():
    if name in data:
        d = data[name]
        color = d['color']
        if not color:
            continue
        print(i, name, color)
        print('rgb', Hex2Dec(color[1:3]), Hex2Dec(color[3:5]), Hex2Dec(color[5:7]))
        pl_color[name] = {
            'color': color,
            'rgb': (Hex2Dec(color[1:3]), Hex2Dec(color[3:5]), Hex2Dec(color[5:7])),
            'url': d['url']
        }
        i += 1

pprint(pl_color)

def Hex2Dec(hex_value):
    """
    Converts a hexadecimal number to its decimal equivalent.

    Parameters:
    hex_value (str): A hexadecimal number represented as a string.

    Returns:
    int: The decimal equivalent of the input hexadecimal number.
    """
    # Convert the hexadecimal string to an integer
    dec_value = int(hex_value, 16)
    return dec_value        
