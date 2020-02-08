from flask import Flask
from flask import send_file
from flask import abort
import os

app = Flask(__name__)


@app.route('/')
def index():
    with open("index.html", 'r') as fd:
        return fd.read()


@app.route('/echo/<message>')
def echo(message):
    return message


@app.route('/images/<image>')
def images(image):
    if not os.path.isfile("images/" + image):
        abort(404)
    return send_file("images/" + image, mimetype='image/gif')
