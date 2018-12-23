import argparse
from main import get_connection
from models import Message, User
from clcrypto import check_password
from datetime import datetime


parser = argparse.ArgumentParser()

parser.add_argument("-u", "--username", help="Login użytkownika")
parser.add_argument("-p", "--password", help="Hasło")
parser.add_argument("-l", "--list", action="store_true", help="Lista wszystkich twoich komunikatów")
parser.add_argument("-t", "--to", help="Mail odbiorcy")
parser.add_argument("-s", "--send", action="store_false", help="Treść komunikatu do wysłania")

args = parser.parse_args()


conn = get_connection()

if conn:
    cursor = conn.cursor()

    # Lista komunikatów
    if args.list:
        if args.username and args.password:
            u = User.load_user_by_username(cursor, args.username)
            if u and check_password(args.password, u.hashed_password):
                m = Message.load_all_messages_for_user_by_username(cursor, args.username)
                for message in m:
                    print(message.creation_date, message.from_id, message.text)
            else:
                raise Exception("Błąd użytkownika lub hasła.")

    # Nadawanie komunikatu
    elif args.send:
        if args.username and args.password:
            if args.to:
                if User.load_user_by_id(cursor, args.to):
                    from_id = Message.get_user_id_by_username(cursor, args.username)
                    m = Message()
                    m.from_id = from_id
                    m.to_id = args.to
                    m.text = args.send
                    m.creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    m.save_to_db(cursor)
                    conn.commit()
                else:
                    raise Exception("Nie ma takiego użytkownika!")
            else:
                raise Exception("Nie podano adresata!")
        else:
            raise Exception("Błąd użytkownika lub hasła!")
    else:
        raise Exception("Nie podano komunikatu!")



    cursor.close()
    conn.close()
