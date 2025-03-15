import streamlit as st
import sqlite3
import bcrypt

# 🔹 Verbindung zur Datenbank
conn = sqlite3.connect("fitness_app.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        email TEXT UNIQUE, 
        password TEXT
    )
""")
conn.commit()

# 🔐 Passwort-Hashing-Funktion
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# 🔑 Geheimcode für Registrierung
REGISTRATION_CODE = "438925069Ff2025+"

# 🌟 **Login & Registrierung**
def login():
    st.sidebar.header("🔐 Login / Registrierung")

    menu = ["Login", "Registrieren"]
    choice = st.sidebar.selectbox("Option wählen", menu)

    if choice == "Login":
        email = st.sidebar.text_input("E-Mail")
        password = st.sidebar.text_input("Passwort", type="password")

        if st.sidebar.button("Anmelden"):
            cursor.execute("SELECT id, password FROM users WHERE email=?", (email,))
            user = cursor.fetchone()
            if user and check_password(password, user[1]):
                st.session_state["user_id"] = user[0]
                st.session_state["email"] = email
                st.success("✅ Erfolgreich angemeldet!")
                st.experimental_rerun()
            else:
                st.error("❌ Falsche E-Mail oder Passwort")

    elif choice == "Registrieren":
        email = st.sidebar.text_input("E-Mail")
        password = st.sidebar.text_input("Passwort", type="password")
        reg_code = st.sidebar.text_input("Registrierungscode", type="password")

        if st.sidebar.button("Registrieren"):
            if reg_code != REGISTRATION_CODE:
                st.error("❌ Falscher Registrierungscode! Bitte den richtigen Code eingeben.")
            else:
                cursor.execute("SELECT id FROM users WHERE email=?", (email,))
                if cursor.fetchone():
                    st.error("❌ Diese E-Mail ist bereits registriert!")
                else:
                    hashed_pw = hash_password(password)
                    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_pw))
                    conn.commit()
                    st.success("✅ Registrierung erfolgreich! Jetzt anmelden.")

# Starte Login
login()
