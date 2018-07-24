import logging
import os

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from color import Color
from manifest import Manifest


BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',
        variable_end_string='%%',
    ))


app = CustomFlask(__name__, template_folder=TEMPLATE_DIR)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_new_connection():
    print('connected!')


@socketio.on('update')
def handle_update(event):
    frame_color = Color(event['frameColor'])
    frame_scale = event.get('frameScale', -0.1)
    toolbar_color = Color(event['toolbarColor'])
    toolbar_scale = event.get('toolbarScale', 0.1)
    emit('update', {
        'frameColor': frame_color.hex,
        'toolbarColor': toolbar_color.hex,
        'frameFontColor': frame_color.alternative.hex,
        'toolbarFontColor': toolbar_color.alternative.hex,
        'autoFrameColor': toolbar_color.add_light(1, frame_scale).hex,
        'autoToolbarColor': frame_color.add_light(1, toolbar_scale).hex,
    })


@socketio.on('save')
def save_manifest(event):
    frame_color = Color(event['frameColor'])
    toolbar_color = Color(event['toolbarColor'])
    fp = event.get('path', './manifest.json')
    try:
        m = Manifest()
        m.setup(frame_color, toolbar_color)
        m.save(fp)
    except Exception as e:
        emit('error', str(e))


if __name__ == '__main__':
    logging.basicConfig(level=30)
    socketio.run(app, host='0.0.0.0', port=8000, debug=False)
