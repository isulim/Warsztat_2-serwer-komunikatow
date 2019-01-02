from models import User, Message
from psycopg2 import connect, OperationalError
from datetime import datetime
from flask import Flask, request, render_template, abort


def get_connection(base='warsztat2'):
    username = 'postgres'
    password = 'coderslab'
    host = 'localhost'

    try:
        conn = connect(host=host, user=username, password=password, database=base)
        return conn
    except OperationalError:
        return None


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def users():

    if request.method == 'GET':
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            users = User.load_all_users(cursor)
            cursor.close()
            conn.close()
        else:
            users = "Błąd połączenia z bazą."
        return render_template('users.html', users=users)
    else:
        return abort(403)


@app.route('/user/<int:userID>', methods=['GET', 'POST'])
def userMessages(userID):

    if request.method == 'GET':
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            messages = Message.load_messages_with_usernames(cursor, userID)
            cursor.close()
            conn.close()
        else:
            users = "Błąd połączenia z bazą."
        return render_template('user_messages.html', messages=messages)
    else:
        pass


if __name__ == '__main__':

    app.run(debug=True)
