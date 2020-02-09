from flask import Flask, send_file, abort, request, redirect, url_for
from flaskext.mysql import MySQL
import os
import hashlib

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
with open("mysql.txt") as fd:
    mySQLPass = fd.read().strip()
app.config['MYSQL_DATABASE_PASSWORD'] = mySQLPass
app.config['MYSQL_DATABASE_DB'] = 'vienna'
app.config['MYSQL_DATABASE_HOST'] = '104.196.135.244'
mysql = MySQL()
mysql.init_app(app)


@app.route('/')
def index():
    with open("index.html", 'r') as fd:
        return fd.read()


@app.route('/handle_register', methods=['POST'])
def handle_register():
    username = request.form['username']
    email = request.form['email']
    passwordHash = hashlib.sha256(request.form['password'].encode()).hexdigest()
    userType = request.form['Register'].lower()

    cnx = mysql.get_db()
    cursor = cnx.cursor()
    query = "INSERT INTO users VALUES('{}', '{}', '{}', '{}')".format(username, email, passwordHash, userType)
    cursor.execute(query)
    cnx.commit()
    cursor.close()

    return redirect(url_for('index'))


@app.route('/images/<image>')
def images(image):
    if not os.path.isfile("images/" + image):
        abort(404)
    return send_file("images/" + image, mimetype='image/gif')


@app.route('/<path>')
def getpage(path):
    if path in ["Register.html", "Login.html"]:
        with open(path) as fd:
            return fd.read()
    else:
        abort(404)
