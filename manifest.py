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

    def setup_colors(self):
        colors = self.colors
        fcol = colors['frame'].alternative
        tcol = colors['toolbar'].alternative

        colors['bookmark_text'] = tcol + 0.6
        colors['tab_text'] = tcol + 0.9
        colors['tab_background_text'] = fcol + 0.6

        colors['ntp_header'] = tcol + 0.6
        colors['ntp_link'] = tcol + 0.6
        colors['ntp_text'] = tcol + 0.6
        colors['ntp_section'] = tcol + 0.6
        colors['ntp_section_link'] = tcol + 0.6
        colors['ntp_section_text'] = tcol + 0.6

    def setup_tints(self):
        toolbar_color = self.colors['toolbar']
        if not toolbar_color.light:
            self.tints['buttons'] = [1, 1, 1]

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
