import json
from typing import Any, Dict, List

from color import Color


def json_default(o):
    if isinstance(o, Color):
        return o.to_json()
    raise TypeError


class Manifest:
    def __init__(self):
        self.name = 'theme'
        self.version = '1.0'
        self.images = {}  # type: Dict[str, str]
        self.colors = {}  # type: Dict[str, Color]
        self.tints = {}  # type: Dict[str, List[float]]
        self.properties = {}  # type: Dict[str, Any]

        self._ready = False

    def setup(self, frame: Color, toolbar: Color):
        self.setup_frame(frame)
        self.setup_toolbar(toolbar)
        self.setup_colors()
        self.setup_tints()

    def setup_frame(self, frame: Color):
        self.colors['frame'] = frame
        self.colors['frame_inactive'] = frame.add_light(m=0.9, a=-0.1)
        self.colors['frame_incognito'] = frame.add_light(m=0.9, a=-0.1)
        self.colors['frame_incognito_inactive'] = frame.add_light(m=0.9, a=-0.2)

    def setup_toolbar(self, toolbar: Color):
        self.colors['toolbar'] = toolbar
        self.colors['ntp_background'] = toolbar

    def setup_colors(self):
        self.check()
        fcol = self.colors['frame'].alternative
        tcol = self.colors['toolbar'].alternative

        self.colors['bookmark_text'] = tcol + 0.6
        self.colors['button_background'] = tcol + 0.6
        self.colors['control_background'] = tcol + 0.6

        self.colors['tab_text'] = tcol + 0.9
        self.colors['tab_background_text'] = fcol + 0.7

        self.colors['ntp_header'] = tcol + 0.6
        self.colors['ntp_text'] = tcol + 0.6
        self.colors['ntp_link'] = tcol + 0.6
        self.colors['ntp_link_underline'] = tcol + 0.8

        self.colors['ntp_section'] = tcol + 0.6
        self.colors['ntp_section_text'] = tcol + 0.6
        self.colors['ntp_section_link'] = tcol + 0.6
        self.colors['ntp_section_link_underline'] = tcol + 0.8

    def setup_tints(self):
        self.check()
        toolbar_color = self.colors['toolbar']
        if not toolbar_color.is_light:
            self.tints['buttons'] = [1, 1, 1]
        # self.tints['frame'] = [0.5, 0.5, 0.5]
        # self.tints['frame_inactive'] = [0.5, 0.5, 0.5]
        # self.tints['frame_incognito'] = [0.5, 0.5, 0.5]
        # self.tints['frame_incognito_inactive'] = [0.5, 0.5, 0.5]
        # self.tints['background_tab'] = [0.5, 0.5, 0.5]

    @property
    def ready(self):
        return self.colors['frame'] and self.colors['toolbar']

    def check(self):
        if not self.ready:
            raise Exception('manifest is not ready')

    @classmethod
    def from_file(cls, fp: str):
        with open(fp) as f:
            data = json.load(f)
        m = Manifest()
        m.name = data['name']
        m.version = data['version']
        m.images = data['theme']['images']
        m.colors = data['theme']['colors']
        m.tints = data['theme']['tints']
        m.properties = data['theme']['properties']
        return m

    def save(self, fp, indent=4):
        data = self.to_dict()
        with open(fp, 'w') as f:
            json.dump(data, f, indent=indent, default=json_default)
        print('saved to', fp)

    def to_dict(self):
        return {
            'manifest_version': 2,
            'version': self.version,
            'name': self.name,
            'theme': {
                'images': self.images,
                'colors': self.colors,
                'tints': self.tints,
                'properties': {
                    'ntp_logo_alternate': 0,
                },
            }
        }

    def to_json(self, indent=4):
        data = self.to_dict()
        return json.dumps(data, indent=indent, default=json_default)
