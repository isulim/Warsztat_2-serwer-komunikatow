import argparse
from main import get_connection
from models import User
from clcrypto import check_password

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help='Nazwa użytkownika')
parser.add_argument("-m", "--mail", help='Adres e-mail')
parser.add_argument("-p", "--password", help='Hasło użytkownika')
parser.add_argument("-n", "--new-pass", help='Nowe hasło użytkownika')
parser.add_argument("-l", "--list", action='store_true', help='Lista użytkowników')
parser.add_argument("-d", "--delete", help='Login użytkownika do usunięcia')
parser.add_argument("-e", "--edit", action='store_true', help='Login użytkownika do edycji')
args = parser.parse_args()

conn = get_connection()

if conn:
    cursor = conn.cursor()

    # Dodawanie użytkownika
    if (args.username and args.mail and args.password) and \
            (not args.edit and not args.delete and not args.new_pass):
        u = User.load_user_by_username(cursor, args.username)
        if u:
            raise Exception("Użytkownik już istnieje")
        nowy = User()
        nowy.username = args.username
        nowy.email = args.mail
        nowy.set_hashed_password(args.password)
        nowy.save_to_db(cursor)
        conn.commit()
        print("Dodano użytkownika {}".format(args.username))
    else:
        print("Nie dodano użytkownika. Sprawdź parametry.")

    # Zmiana hasła
    if args.username and args.password and args.edit and args.new_pass:
        u = User.load_user_by_username(cursor, args.username)
        if u and check_password(args.password, u.hashed_password):
            u.set_hashed_password(args.new_pass)
            u.save_to_db(cursor)
            conn.commit()
            print("Zmieniono hasło.")
        else:
            print("Nie udało się.")

    # Usuwanie użytkownika
    if args.username and args.password and args.delete:
        u = User.load_user_by_email(cursor, args.username)
        if u and check_password(args.password, u.hashed_password):
            u.delete(cursor)
            conn.commit()
            print("Użytkownik usunięty")
        else:
            print("Nie udało się")

    # Lista użytkowników
    if args.list:
        u = User.load_all_users(cursor)
        for user in u:
            print(user)

    cursor.close()
    conn.close()

else:
    print("Błąd połączenia z bazą.")
