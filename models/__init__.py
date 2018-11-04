from clcrypto import password_hash


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
            # saving new instance using prepared statements
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

        cursor.execute(sql, (email,))  # (user_id, ) - bo tworzymy krotkę
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
        sql = "SELECT id, username, email, hashed_password FROM Users"
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
        return "User ({}, {}, {}, {}".format(self.id, self.username, self.email, self.hashed_password)

    @classmethod
    def load_user_by_username(cls, cursor, username):
        sql = """SELECT id, username, email, hashed_password
                             FROM users WHERE username=%s"""

        cursor.execute(sql, (username,))  # (user_id, ) - bo tworzymy krotkę
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
