import os

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from color import Color


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
    emit('hurma', {'foo': 'bar'})


@socketio.on('update')
def handle_update(event):
    print('update:', event)
    frame_color = Color(event['frameColor'])
    toolbar_color = Color(event['toolbarColor'])
    font_color = toolbar_color.alternative
    emit('update', {
        'fontColor': font_color.hex,
    })


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
