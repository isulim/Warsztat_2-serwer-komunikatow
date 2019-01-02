from clcrypto import password_hash
from wtforms import Form, BooleanField, StringField, IntegerField, PasswordField, validators

class User:
    __id = None
    username = None
    __hashed_password = None
    email = None

    def __init__(self):
        self.__id = -1
        self.username = ''
        self.__hashed_password = ''
        self.email = ''

    @property
    def id(self):
        return self.__id

    @property
    def hashed_password(self):
        return self.__hashed_password

    def set_hashed_password(self, password, salt=None):
        self.__hashed_password = password_hash(password, salt)

    def save_to_db(self, cursor):
        if self.__id == -1: 
            # zapisywanie nowej instancji
            sql = """INSERT INTO Users(username, email, hashed_password)
            VALUES(%s, %s, %s) RETURNING id"""
            values = (self.username, self.email, self.hashed_password)
            cursor.execute(sql, values)
            self.__id = cursor.fetchone()[0]  # albo cursor.fetchone()['id']
            return True

        else:
            sql = """UPDATE Users SET username = %s, email = %s, hashed_password = %s
            WHERE id = %s"""
            values = (self.username, self.email, self.hashed_password, self.id)
            cursor.execute(sql, values)
            return True

    def delete(self, cursor):
        sql = "DELETE FROM Users WHERE id=%s"
        cursor.execute(sql, (self.__id,))
        # usuwamy wpis z bazy, nie obiekt z programu
        self.__id = -1
        return True

    @classmethod
    def load_user_by_id(cls, cursor, user_id):
        sql = """SELECT id, username, email, hashed_password
                 FROM users WHERE id=%s"""

        cursor.execute(sql, (user_id,))  # (user_id, ) - bo tworzymy krotkę
        data = cursor.fetchone()
        if data:
            loaded_user = cls()
            loaded_user.__id = data[0]
            loaded_user.username = data[1]
            loaded_user.email = data[2]
            loaded_user.__hashed_password = data[3]
            return loaded_user
        else:
            return None

    @classmethod
    def load_user_by_email(cls, cursor, email):
        sql = """SELECT id, username, email, hashed_password
                     FROM users WHERE email=%s"""

        cursor.execute(sql, (email,))
        data = cursor.fetchone()
        if data:
            loaded_user = cls()
            loaded_user.__id = data[0]
            loaded_user.username = data[1]
            loaded_user.email = data[2]
            loaded_user.__hashed_password = data[3]
            return loaded_user
        else:
            return None

    @classmethod
    def load_all_users(cls, cursor):
        sql = "SELECT id, username, email, hashed_password FROM Users ORDER BY id"
        ret = []
        cursor.execute(sql)
        for row in cursor.fetchall():
            loaded_user = cls()
            loaded_user.__id = row[0]
            loaded_user.username = row[1]
            loaded_user.email = row[2]
            loaded_user.__hashed_password = row[3]
            ret.append(loaded_user)
        return ret

    def __str__(self):
        return "User ({}, {}, {})".format(self.id, self.username, self.email)

    @classmethod
    def load_user_by_username(cls, cursor, username):
        sql = """SELECT id, username, email, hashed_password
                             FROM users WHERE username=%s"""

        cursor.execute(sql, (username,))
        data = cursor.fetchone()
        if data:
            loaded_user = cls()
            loaded_user.__id = data[0]
            loaded_user.username = data[1]
            loaded_user.email = data[2]
            loaded_user.__hashed_password = data[3]
            return loaded_user
        else:
            return None

    

class Message:
    __id = None
    from_id = None
    to_id = None
    text = None
    creation_date = None

    def __init__(self):
        self.__id = -1
        self.from_id = 0
        self.to_id = 0
        self.text = ''
        self.creation_date = 0

    

    @property
    def id(self):
        return self.__id

    @classmethod
    def load_message_by_id(cls, cursor, message_id):
        sql = """SELECT id, from_id, to_id, text, creation_date
                         FROM messages WHERE id=%s"""

        cursor.execute(sql, (message_id,))
        data = cursor.fetchone()
        if data:
            loaded_message = cls()
            loaded_message.__id = data[0]
            loaded_message.from_id = data[1]
            loaded_message.to_id = data[2]
            loaded_message.text = data[3]
            loaded_message.creation_date = data[4]
            return loaded_message
        else:
            return None


    @classmethod
    def load_messages_with_usernames(cls, cursor, user_id):
        sql = """SELECT messages.id, users.username, messages.text, messages.creation_date
                FROM messages JOIN users ON messages.from_id = users.id
                WHERE messages.to_id=%s
                ORDER BY creation_date DESC;"""
        ret = []

        cursor.execute(sql, (user_id,))

        for row in cursor.fetchall():
            loaded_message = cls()
            loaded_message.__id = row[0]
            loaded_message.from_id = row[1]
            loaded_message.text = row[2]
            loaded_message.creation_date = row[3]
            ret.append(loaded_message)
        return ret


    @classmethod
    def load_all_messages_for_user_by_id(cls, cursor, user_id):
        sql = """SELECT id, from_id, to_id, text, creation_date
                    FROM messages WHERE to_id=%s ORDER BY creation_date DESC;"""
        ret = []
        cursor.execute(sql, (user_id,))

        for row in cursor.fetchall():
            loaded_message = cls()
            loaded_message.__id = row[0]
            loaded_message.from_id = row[1]
            loaded_message.to_id = row[2]
            loaded_message.text = row[3]
            loaded_message.creation_date = row[4]
            ret.append(loaded_message)
        return ret

    @classmethod
    def load_all_messages_for_user_by_username(cls, cursor, username):
        sql_1 = """SELECT id FROM users WHERE username=%s"""
        sql_2 = """SELECT id, from_id, to_id, text, creation_date
                                     FROM messages WHERE to_id=%s
                                     ORDER BY creation_date asc;"""
        ret = []
        cursor.execute(sql_1, (username,))
        id = cursor.fetchone()[0]

        cursor.execute(sql_2, (id,))
        for row in cursor.fetchall():
            loaded_message = cls()
            loaded_message.__id = row[0]
            loaded_message.from_id = row[1]
            loaded_message.to_id = row[2]
            loaded_message.text = row[3]
            loaded_message.creation_date = row[4]
            ret.append(loaded_message)
        return ret

    @classmethod
    def load_all_messages(cls, cursor):
        sql = """SELECT id, from_id, to_id, text, creation_date
                    FROM messages"""
        ret = []
        cursor.execute(sql)

        for row in cursor.fetchall():
            loaded_message = cls()
            loaded_message.__id = row[0]
            loaded_message.from_id = row[1]
            loaded_message.to_id = row[2]
            loaded_message.text = row[3]
            loaded_message.creation_date = row[4]
            ret.append(loaded_message)

        return ret

    @staticmethod
    def get_user_id_by_username(cursor, username):
        sql = """SELECT id FROM users WHERE username=%s"""

        cursor.execute(sql, (username,))
        user_id = cursor.fetchone()

        return user_id

    @staticmethod
    def get_username(cursor, id):
        sql = """SELECT username FROM users WHERE id=%s"""
        cursor.execute(sql, (id,))
        username = cursor.fetchone()
        return username    

    def save_to_db(self, cursor):
        if self.__id == -1:
            # zapisywanie nowej wiadomości
            sql = """INSERT INTO messages (from_id, to_id, text, creation_date)
            VALUES(%s, %s, %s, %s) RETURNING id"""
            values = (self.from_id, self.to_id, self.text, self.creation_date)
            cursor.execute(sql, values)
            self.__id = cursor.fetchone()[0]
            return True

    def delete(self, cursor):
        sql = "DELETE FROM messages WHERE id=%s"
        cursor.execute(sql, (self.__id,))
        self.__id = -1
        return True

    def __str__(self):
        return "Message ({}, {}, {}, {}, {})".format(self.id,
                                                     self.from_id,
                                                     self.to_id,
                                                     self.text,
                                                     self.creation_date)


class NewUserForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Hasła muszą się zgadzać')
    ])
    confirm = PasswordField('Repeat Password')


class SendForm(Form):
    reciever = StringField("Reciever's name", [validators.DataRequired()])
    message = StringField("Message", [validators.DataRequired()])
    password = PasswordField("Your password", [validators.DataRequired()])