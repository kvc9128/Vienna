from flask import Flask, send_file, abort, request, redirect, url_for, render_template, make_response
from flaskext.mysql import MySQL
from flask_socketio import SocketIO
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

socketio = SocketIO(app)

# Ticket format: username, course, budget, duration
tickets = []
connectedTutors = {}


def querySQL(query):
    cnx = mysql.get_db()
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()
    data = cursor.fetchone()
    cursor.close()
    return data


def checkTutorConnected(username):
    if username not in connectedTutors:
        connectedTutors[username] = {}
        connectedTutors[username]['declined'] = []
        connectedTutors[username]['waiting'] = False


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

    query = "SELECT username, pass_hash, user_type FROM users WHERE email='{}'".format(email)
    SQLresponse = querySQL(query)
    if SQLresponse is None:
        return redirect(url_for('getpage', path='Login.html'))
    username = SQLresponse[0]
    checkHash = SQLresponse[1]
    userType = SQLresponse[2]

    if checkHash == passwordHash:
        if userType == 'student':
            path = 'Student.html'
        else:
            path = 'Tutor.html'

        resp = make_response(redirect(url_for('getpage', path=path)))
        resp.set_cookie('email', email)
        resp.set_cookie('username', username)
        return resp
    else:
        return redirect(url_for('getpage', path='Login.html'))


@app.route('/request_tutor', methods=['POST'])
def request_tutor():
    username = request.cookies.get('username')
    course = request.form['subject']
    budget = request.form['budget']
    duration = request.form['duration']

    tickets.append((username, course, budget, duration))
    return redirect(url_for('getpage', path='Chat.html'))


def tutorTicketFinder(username):
    checkTutorConnected(username)
    connectedTutors[username]['waiting'] = True

    while connectedTutors[username]['waiting']:
        for ticket in tickets:
            if ticket not in connectedTutors[username]['declined']:
                socketio.emit('TICKET', {'username': ticket[0], 'course': ticket[1], 'budget': ticket[2], 'duration': ticket[3]})


@socketio.on('TUTOR')
def tutor():
    socketio.start_background_task(target=tutorTicketFinder)


@app.route('/images/<image>')
def images(image):
    if not os.path.isfile("images/" + image):
        abort(404)
    return send_file("images/" + image, mimetype='image/gif')


@app.route('/<path>')
def getpage(path):
    if path in ["Register.html", "Login.html", "Student.html", "Tutor.html", "Chat.html"]:
        print(tickets)
        return render_template(path)
    else:
        abort(404)


if __name__ == "__main__":
    socketio.run(app, debug=True)
