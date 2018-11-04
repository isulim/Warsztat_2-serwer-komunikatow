from models import User
from psycopg2 import connect, OperationalError


def get_connection(base='warsztat2'):
    username = 'postgres'
    password = 'coderslab'
    host = 'localhost'

    try:
        conn = connect(host=host, user=username, password=password, database=base)
        return conn
    except OperationalError:
        return None


if __name__ == '__main__':

    conn = get_connection()
    if conn:
        cursor = conn.cursor()

        # u = User()
        # u.set_hashed_password('siemanko')
        # u.email = 'andrzej@andrzej.pl'
        # u.username = 'andrzejmiszcz'
        # u.save_to_db(cursor)
        # print(u.hashed_password)
        # print(u.id)
        # conn.commit()
        #
        u2 = User.load_user_by_id(cursor, 4)
        u2.set_hashed_password('siemaneczko')
        u2.email = 'andrzej4@andrzej.pl'
        u2.username = 'andrzej4arcymiszcz'
        u2.save_to_db(cursor)
        print(u2.hashed_password)
        print(u2.id)
        conn.commit()

        u3 = User.load_user_by_id(cursor, 4)
        print(u3)

        u3.delete(cursor)
        conn.commit()
        print(u3.id)

        ua = User.load_all_users(cursor)
        for user in ua:
            print(user)

        cursor.close()
        conn.close()
    else:
        print('Nie udało się połączyć')
