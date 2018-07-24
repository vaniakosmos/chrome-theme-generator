import argparse
import configparser
import os
from functools import wraps
from pprint import pprint

from color import Color
from manifest import Manifest


def meta(msg, key):
    def dec(f):
        f.msg = msg
        f.key = key

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    return dec


def process_steps(manifest: Manifest, config_data: dict, steps: list):
    for func in steps:
        msg = func.msg
        key = func.key
        value_from_config = config_data.get(key, None)
        for i in range(10):
            if value_from_config:
                value = value_from_config
            else:
                value = input(msg + ' >  ')
            ok = func(manifest, value)
            if ok:
                break
        else:
            raise ValueError('way?')


def read_config(config_fp):
    if not config_fp:
        return {}
    config = configparser.ConfigParser()
    files = config.read(config_fp)
    if not files:
        return {}
    return dict(config['gen'])


def save_manifest(m: Manifest, path=None):
    if not path:
        path = input("manifest path/name >  ")
        if not path:
            path = '.'
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, 'manifest.json')
    m.save(path)


@meta("extension name (default 'theme')", 'name')
def set_name(m: Manifest, name: str):
    name = name or 'theme'
    m.name = name
    return True


@meta("google logo (0 - colorful (default), 1 - white)", 'logo')
def set_logo(m: Manifest, value: str):
    if value == '1':
        m.properties['ntp_logo_alternate'] = 1
    return True


@meta("set frame color (hex or rgb)", 'frame-color')
def set_frame_color(m: Manifest, value: str):
    try:
        m.colors['frame'] = Color(value)
        return True
    except Exception as e:
        print(e, '- hex or rgb are acceptable')
        return False


@meta("set toolbar color (default is slightly lighter version of frame color)", 'toolbar-color')
def set_toolbar_color(m: Manifest, value: str):
    if not value:
        color = m.colors['frame'].add_light()
    else:
        try:
            color = Color(value)
        except Exception as e:
            print(e, '- hex or rgb are acceptable')
            return False
    m.colors['ntp_background'] = m.colors['toolbar'] = color
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', default=None, nargs='?')
    args = parser.parse_args()
    # args.config = args.config or 'config.ini'
    config_data = read_config(args.config)

    manifest = Manifest()

    process_steps(manifest, config_data, [
        set_name,
        set_logo,
    ])
    process_steps(manifest, config_data, [
        set_frame_color,
        set_toolbar_color,
    ])

    manifest.setup_colors()
    manifest.setup_tints()

    pprint(manifest.to_dict())
    save_manifest(manifest, path=config_data.get('save-path', None))


if __name__ == '__main__':
    main()
