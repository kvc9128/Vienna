from flask import Flask, send_file, abort, request, redirect, url_for, render_template
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


def querySQL(query):
    cnx = mysql.get_db()
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()
    data = cursor.fetchone()
    cursor.close()
    return data


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/handle_register', methods=['POST'])
def handle_register():
    username = request.form['username']
    email = request.form['email']
    passwordHash = hashlib.sha256(request.form['password'].encode()).hexdigest()
    userType = request.form['Register'].lower()

    query = "INSERT INTO users VALUES('{}', '{}', '{}', '{}')".format(username, email, passwordHash, userType)
    querySQL(query)

    return redirect(url_for('getpage', path='Login.html'))


@app.route('/handle_login', methods=['POST'])
def handle_login():
    email = request.form['email']
    passwordHash = hashlib.sha256(request.form['password'].encode()).hexdigest()

    query = "SELECT pass_hash FROM users WHERE email='{}'".format(email)
    data = querySQL(query)

    return str(data[0] == passwordHash)


@app.route('/images/<image>')
def images(image):
    if not os.path.isfile("images/" + image):
        abort(404)
    return send_file("images/" + image, mimetype='image/gif')


@app.route('/<path>')
def getpage(path):
    if path in ["Register.html", "Login.html", "Student.html"]:
        return render_template(path)
    else:
        abort(404)
