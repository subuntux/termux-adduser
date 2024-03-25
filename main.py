#!/usr/bin/env python3

import sys
import os
import sqlite3
import hashlib
import shutil

def create_user(username):
    # Pfad zur SQLite-Datenbank
    db_path = os.path.join(os.environ.get('PREFIX', ''), 'shared', 'termux-adduser', 'db', 'user.db')

    # Passwort abfragen und hashen
    password = input("Bitte geben Sie ein Passwort ein: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Verbindung zur Datenbank herstellen und Benutzer einfügen
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

    # Ordner für den Benutzer erstellen und Dateien kopieren
    user_folder = os.path.join(os.environ.get('HOME', ''), '.termux', f'.{username}')
    os.makedirs(user_folder, exist_ok=True)
    files_to_copy = os.listdir(os.path.join(os.environ.get('PREFIX', ''), 'shared', 'termux-adduser', 'home'))
    for file_name in files_to_copy:
        shutil.copy(os.path.join(os.environ.get('PREFIX', ''), 'shared', 'termux-adduser', 'home', file_name), user_folder)

    # .user.conf erstellen
    with open(os.path.join(user_folder, '.user.conf'), 'w') as conf_file:
        conf_file.write(username)

def login_user(username):
    # Pfad zur SQLite-Datenbank
    db_path = os.path.join(os.environ.get('PREFIX', ''), 'shared', 'termux-adduser', 'db', 'user.db')

    # Passwort abfragen
    password = input("Bitte geben Sie Ihr Passwort ein: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Verbindung zur Datenbank herstellen und Benutzer überprüfen
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data and user_data[2] == hashed_password:
        # Erfolgreiche Anmeldung
        user_folder = os.path.join(os.environ.get('HOME', ''), '.termux', f'.{username}')
        os.chdir(user_folder)
        print("Anmeldung erfolgreich.")
    else:
        print("Falscher Benutzername oder Passwort.")

def main():
    if len(sys.argv) < 3:
        print("Bitte geben Sie 'create' oder 'login' als erstes Argument an, gefolgt von einem Benutzernamen.")
        return
    action = sys.argv[1]
    username = sys.argv[2]

    if action == "create":
        create_user(username)
        print("Benutzer erfolgreich erstellt.")
    elif action == "login":
        login_user(username)
    else:
        print("Ungültige Aktion.")

if __name__ == "__main__":
    main()
