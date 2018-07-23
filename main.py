import argparse
import configparser
import json
import os
from functools import wraps
from pprint import pprint


def meta(msg, key):
    def dec(f):
        f.msg = msg
        f.key = key

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    return dec


def convert_hex(value: str):
    if value.startswith('#'):
        value = value[1:]
    if len(value) == 6:
        value = [int(value[i:i + 2], 16) for i in range(0, 6, 2)]
    elif len(value) == 3:
        value = [int(value[i:i + 1] * 2, 16) for i in range(0, 3, 1)]
    else:
        raise ValueError
    return value


def get_rgb(value: str):
    tokens = len(value.split())
    if tokens == 1:
        value = convert_hex(value)
    elif tokens == 3:
        value = value.split()
    else:
        raise ValueError
    rgb = list(map(int, value))
    return rgb


def process_steps(sub_manifest: dict, config_data: dict, steps: list):
    for func in steps:
        msg = func.msg
        key = func.key
        value_from_config = config_data.get(key, None)
        while True:
            if value_from_config:
                value = value_from_config
            else:
                value = input(msg + ' >  ')
            ok = func(sub_manifest, value)
            if ok:
                break


def is_light(colors: dict):
    toolbar_color = colors['toolbar']
    r, g, b = toolbar_color
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance > 0.5


def setup_colors(colors: dict, light: bool):
    if light:
        col = [0, 0, 0]
    else:
        col = [255, 255, 255]
    colors['bookmark_text'] = [*col, 0.6]
    colors['tab_text'] = [*col, 0.9]
    colors['tab_background_text'] = [*col, 0.7]

    colors['ntp_header'] = [*col, 0.9]
    colors['ntp_link'] = [*col, 0.9]
    colors['ntp_text'] = [*col, 0.6]
    colors['ntp_section'] = [*col, 0.6]
    colors['ntp_section_link'] = [*col, 0.6]
    colors['ntp_section_text'] = [*col, 0.6]


def setup_tints(tints: dict, light: bool):
    if not light:
        tints['buttons'] = [1, 1, 1]


def read_config(config_fp):
    config = configparser.ConfigParser()
    files = config.read(config_fp)
    if not files:
        return {}
    return dict(config['gen'])


def save_manifest(m: dict, path=None):
    if not path:
        path = input("manifest path/name >  ")
        if not path:
            path = '.'
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, 'manifest.json')
    with open(path, 'w') as f:
        json.dump(m, f, indent=4)


@meta("extension name (default 'theme')", 'name')
def set_name(m: dict, name: str):
    if name != '':
        m['name'] = 'theme'
    return True


@meta("google logo (choose: color | white, default 'color')", 'logo')
def set_logo(m: dict, value: str):
    if value == 'white':
        m['theme']['properties']['ntp_logo_alternate'] = 1
    return True


@meta("set frame color (hex or rgb)", 'frame-color')
def set_frame_color(m: dict, value: str):
    try:
        rgb = get_rgb(value)
        m['frame'] = rgb
        return True
    except Exception as e:
        print(e, '- hex or rgb are acceptable')
        return False


@meta("set toolbar color (default is slightly lighter version of frame color)", 'toolbar-color')
def set_toolbar_color(m: dict, value: str):
    if not value:
        value = list(map(lambda x: min(255, int(x * 1.1 + 20)), m['frame']))
    else:
        try:
            value = get_rgb(value)
        except Exception as e:
            print(e, '- hex or rgb are acceptable')
            return False
    m['ntp_background'] = m['toolbar'] = value
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', default=None, nargs='?')
    args = parser.parse_args()
    config_fp = args.config or 'config.ini'
    config_data = read_config(config_fp)

    manifest = {
        'manifest_version': 2,
        'version': '1.0',
        'name': 'theme',
        'theme': {
            'images': {},
            'colors': {
                'bookmark_text': [255, 255, 255, 0.6],
            },
            'tints': {},
            'properties': {
                'ntp_logo_alternate': 0,
            },
        }
    }
    colors = manifest['theme']['colors']
    tints = manifest['theme']['tints']

    process_steps(manifest, config_data, [
        set_name,
        set_logo,
    ])
    process_steps(colors, config_data, [
        set_frame_color,
        set_toolbar_color,
    ])

    light = is_light(colors)
    setup_colors(colors, light)
    setup_tints(tints, light)

    pprint(manifest)
    save_manifest(manifest, path=config_data.get('save-path', None))


if __name__ == '__main__':
    main()
