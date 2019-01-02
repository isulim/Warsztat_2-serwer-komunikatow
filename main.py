from models import User, Message, NewUserForm, SendForm
from clcrypto import password_hash, check_password
from psycopg2 import connect, OperationalError
from datetime import datetime
from flask import Flask, request, render_template, abort, flash, redirect, url_for



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
app.secret_key = 'something'

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

@app.route('/new-user', methods=['GET', 'POST'])
def newUser():
    form = NewUserForm(request.form)
    if request.method == 'POST' and form.validate():
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.set_hashed_password(form.password.data)
            user.save_to_db(cursor)
            conn.commit()
            cursor.close()
            conn.close()
        else:
            flash('Błąd połączenia z bazą.')

        flash('Dodano użytkownika')
        return redirect(url_for('users'))
    return render_template('new_user.html', form=form)

@app.route('/send/<int:userID>', methods=['GET', 'POST'])
def send(userID):
    form = SendForm(request.form)
    if request.method == 'POST' and form.validate():
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            sender = User.load_user_by_id(cursor, userID)
            reciever_id = Message.get_user_id_by_username(cursor, form.reciever.data)

            if check_password(form.password.data, sender.hashed_password):
                message = Message()
                message.to_id = reciever_id
                message.from_id = userID
                message.text = form.message.data
                message.creation_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                message.save_to_db(cursor)
                conn.commit()
            else:
                flash("Błąd hasła!")
            cursor.close()
            conn.close()
            return redirect('/user/{}'.format(reciever_id[0]))
    return render_template('send_message.html', form=form)

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
        flash("Niedozwolona metoda")
        return redirect(url_for('users'))


if __name__ == '__main__':

    app.run(debug=True)
