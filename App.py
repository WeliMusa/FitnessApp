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
        if user and check_password(password, user[1]):
            st.session_state["user_id"] = user[0]
            st.session_state["email"] = email
            st.success("✅ Erfolgreich angemeldet!")
            st.experimental_rerun()
        else:
            st.error("❌ Falsche E-Mail oder Passwort")

    # 🔹 Admin-Bereich: Nur du kannst neue Benutzer hinzufügen!
    if email == "weli.musa@outlook.com":
        st.sidebar.subheader("👤 Benutzerverwaltung (Admin)")
        new_user_email = st.sidebar.text_input("Neue Benutzer-E-Mail")
        new_user_password = st.sidebar.text_input("Neues Passwort", type="password")

        if st.sidebar.button("Benutzer hinzufügen"):
            cursor.execute("SELECT id FROM users WHERE email=?", (new_user_email,))
            if cursor.fetchone():
                st.sidebar.error("❌ Diese E-Mail ist bereits registriert!")
            else:
                hashed_pw = hash_password(new_user_password)
                cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (new_user_email, hashed_pw))
                conn.commit()
                st.sidebar.success(f"✅ Benutzer {new_user_email} wurde angelegt!")

# Starte Login
login()
