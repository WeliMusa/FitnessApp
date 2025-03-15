import streamlit as st
import sqlite3
import bcrypt

# 🔹 Datenbankverbindung & Benutzer-Tabelle erstellen
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

# 🌟 **Login & Admin-Verwaltung**
def login():
    st.sidebar.header("🔐 Login")

    email = st.sidebar.text_input("E-Mail")
    password = st.sidebar.text_input("Passwort", type="password")
    
    if st.sidebar.button("Anmelden"):
        cursor.execute("SELECT id, password FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        if user and check_password(password, user[1
