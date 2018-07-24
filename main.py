import argparse
import configparser
import json
import os
from functools import wraps
from pprint import pprint

from color import Color


def meta(msg, key):
    def dec(f):
        f.msg = msg
        f.key = key

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    return dec


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


def get_font_color(color: Color) -> Color:
    if color.light:
        col = Color([0, 0, 0])
    else:
        col = Color([255, 255, 255])
    return col


def setup_colors(colors: dict):
    fcol = get_font_color(colors['frame'])
    tcol = get_font_color(colors['toolbar'])

    colors['bookmark_text'] = tcol.add_alpha(0.6)
    colors['tab_text'] = tcol.add_alpha(0.9)
    colors['tab_background_text'] = fcol.add_alpha(0.6)

    colors['ntp_header'] = tcol.add_alpha(0.6)
    colors['ntp_link'] = tcol.add_alpha(0.6)
    colors['ntp_text'] = tcol.add_alpha(0.6)
    colors['ntp_section'] = tcol.add_alpha(0.6)
    colors['ntp_section_link'] = tcol.add_alpha(0.6)
    colors['ntp_section_text'] = tcol.add_alpha(0.6)


def setup_tints(tints: dict, toolbar_color: Color):
    if not toolbar_color.light:
        tints['buttons'] = [1, 1, 1]


def read_config(config_fp):
    if not config_fp:
        return {}
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
    name = name or 'theme'
    m['name'] = name
    return True


@meta("google logo (choose: color | white, default 'color')", 'logo')
def set_logo(m: dict, value: str):
    if value == 'white':
        m['theme']['properties']['ntp_logo_alternate'] = 1
    return True


@meta("set frame color (hex or rgb)", 'frame-color')
def set_frame_color(m: dict, value: str):
    try:
        m['frame'] = Color(value)
        return True
    except Exception as e:
        print(e, '- hex or rgb are acceptable')
        return False


@meta("set toolbar color (default is slightly lighter version of frame color)", 'toolbar-color')
def set_toolbar_color(m: dict, value: str):
    if not value:
        color = m['frame'].add_light()
    else:
        try:
            color = Color(value)
        except Exception as e:
            print(e, '- hex or rgb are acceptable')
            return False
    m['ntp_background'] = m['toolbar'] = color
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', default=None, nargs='?')
    args = parser.parse_args()
    # args.config = args.config or 'config.ini'
    config_data = read_config(args.config)

    manifest = {
        'manifest_version': 2,
        'version': '1.0',
        'name': 'theme',
        'theme': {
            'images': {},
            'colors': {
                'bookmark_text': Color([255, 255, 255], 0.6),
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

    setup_colors(colors)
    setup_tints(tints, colors['toolbar'])

    pprint(manifest)
    save_manifest(manifest, path=config_data.get('save-path', None))


if __name__ == '__main__':
    main()
