from models import User, Message
from clcrypto import password_hash, check_password
from psycopg2 import connect, OperationalError
from datetime import datetime
from flask import Flask, request, render_template, abort, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SelectField, TextAreaField


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

conn = get_connection()
if conn:
    cursor = conn.cursor()
    users = User.load_users_list(cursor)
    usersList = []
    for user in users:
        usersList.append((user.id, user.username))
    print(usersList)


class NewUserForm(FlaskForm):
    username = StringField('Nazwa użytkownika', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Hasło', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Hasła muszą się zgadzać')
    ])
    confirm = PasswordField('Powtórz hasło')


class SendForm(FlaskForm):
    sender = SelectField("Nadawca", [validators.DataRequired()],
                         choices=usersList, coerce=int)
    password = PasswordField("Hasło nadawcy", [validators.DataRequired()])
    receiver = SelectField("Adresat", [validators.DataRequired()],
                           choices=usersList, coerce=int)
    message = TextAreaField("Wiadomość", [validators.DataRequired()])


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
def new_user():
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


@app.route('/send/', methods=['GET', 'POST'])
def send():
    form = SendForm(request.form)
    if request.method == 'POST' and form.validate():
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            sender_id = form.sender.data
            receiver_id = form.receiver.data
            sender = User.load_user_by_id(cursor, sender_id)

            if check_password(form.password.data, sender.hashed_password):
                message = Message()
                message.to_id = receiver_id
                message.from_id = sender_id
                message.text = form.message.data
                message.creation_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                message.save_to_db(cursor)
                conn.commit()
            else:
                flash("Błąd hasła!")
            cursor.close()
            conn.close()
            return redirect('/user/{}'.format(sender_id))
    return render_template('send_message.html', form=form)


@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user_messages(user_id):

    if request.method == 'GET':
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            rec_messages = Message.rec_messages_with_usernames(cursor, user_id)
            sent_messages = Message.sent_messages_with_usernames(cursor, user_id)
            username = Message.get_username(cursor, user_id)
            cursor.close()
            conn.close()
        else:
            users = "Błąd połączenia z bazą."
        return render_template('user_messages.html',
                               rec_messages=rec_messages,
                               sent_messages=sent_messages,
                               username=username)
    else:
        return abort(403)


if __name__ == '__main__':

    app.run(debug=True)
