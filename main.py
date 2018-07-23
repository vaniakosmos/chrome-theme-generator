import argparse
import configparser
import json
import os
from pprint import pprint


def set_name(m: dict, name: str):
    if name != '':
        m['name'] = 'theme'
    return True


def set_logo(m: dict, value: str):
    if value == 'white':
        m['theme']['properties']['ntp_logo_alternate'] = 1
    return True


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


def set_frame_color(m: dict, value: str):
    try:
        rgb = get_rgb(value)
        m['frame'] = rgb
        return True
    except Exception as e:
        print(e, '- hex or rgb are acceptable')
        return False


def set_bg_color(m: dict, value: str):
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


def process_steps(sub_manifest, steps):
    for info, func, value_from_config in steps:
        while True:
            if value_from_config:
                value = value_from_config
            else:
                value = input(info + ' >  ')
            ok = func(sub_manifest, value)
            if ok:
                break


def is_light(colors: dict):
    toolbar = colors['toolbar']
    return sum(toolbar) > 255 * 3 / 2


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', default=None, nargs='?')
    args = parser.parse_args()
    config_fp = args.config or 'config.ini'
    data = read_config(config_fp)

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

    steps = [
        ("name (default 'theme')",
         set_name, data.get('name', None)),
        ("google logo (default 'color', might be 'white')",
         set_logo, data.get('logo', None)),
    ]
    process_steps(manifest, steps)

    steps = [
        ("set frame color (hex or rgb)",
         set_frame_color, data.get('frame-color', None)),
        ("set toolbar color (default is lighter frame color)",
         set_bg_color, data.get('toolbar-color', None)),
    ]
    process_steps(colors, steps)

    light = is_light(colors)
    setup_colors(colors, light)
    setup_tints(tints, light)

    pprint(manifest)
    save_manifest(manifest, path=data.get('save-path', None))


if __name__ == '__main__':
    main()
