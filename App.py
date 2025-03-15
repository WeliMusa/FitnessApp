import streamlit as st
import sqlite3
import bcrypt
import datetime
import random

# 🎨 **App-Design**
st.set_page_config(page_title="Smart Fitness App", page_icon="💪", layout="wide")

# 📌 **Verbindung zur Datenbank**
DB_PATH = "fitness_app.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# 📌 **Tabellen für Benutzer, Workouts, Notizen & Ernährung**
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        email TEXT UNIQUE, 
        password TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        workout_name TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS nutrition (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        food TEXT,
        calories INTEGER
    )
""")

conn.commit()

# 🔐 **Passwort-Funktionen**
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# 🔑 **Geheimcode für Registrierung**
REGISTRATION_CODE = "438925069Ff2025+"

# 🌟 **Login & Registrierung**
def login():
    st.sidebar.header("🔐 Login / Registrierung")
    menu = ["Login", "Registrieren"]
    choice = st.sidebar.radio("Option wählen", menu)

    if choice == "Login":
        email = st.sidebar.text_input("📧 E-Mail")
        password = st.sidebar.text_input("🔑 Passwort", type="password")

        if st.sidebar.button("Anmelden"):
            cursor.execute("SELECT id, password FROM users WHERE email=?", (email,))
            user = cursor.fetchone()
            if user and check_password(password, user[1]):
                st.session_state["user_id"] = user[0]
                st.success("✅ Erfolgreich angemeldet!")
                st.experimental_rerun()
            else:
                st.error("❌ Falsche E-Mail oder Passwort")

    elif choice == "Registrieren":
        email = st.sidebar.text_input("📧 E-Mail")
        password = st.sidebar.text_input("🔑 Passwort", type="password")
        reg_code = st.sidebar.text_input("🔒 Registrierungscode", type="password")

        if st.sidebar.button("Registrieren"):
            if reg_code != REGISTRATION_CODE:
                st.error("❌ Falscher Registrierungscode!")
            else:
                cursor.execute("SELECT id FROM users WHERE email=?", (email,))
                if cursor.fetchone():
                    st.error("❌ Diese E-Mail ist bereits registriert!")
                else:
                    hashed_pw = hash_password(password)
                    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_pw))
                    conn.commit()
                    st.success("✅ Registrierung erfolgreich! Jetzt anmelden.")

# 🤖 **KI-Coach: Ernährung & Training**
def ai_coach():
    st.subheader("🤖 Dein smarter KI-Coach")

    user_input = st.text_input("❓ Was möchtest du wissen?")
    
    if st.button("Antwort erhalten"):
        responses = [
            "💪 Achte auf saubere Ausführung & Progression für langfristigen Erfolg!",
            "🥗 Dein Körper braucht genug Proteine, Kohlenhydrate & gesunde Fette!",
            "🏋️ Bleib konsequent – kleine Fortschritte ergeben große Erfolge!",
            "💦 Trinke genug Wasser & gönn dir ausreichend Regeneration."
        ]
        response = random.choice(responses)
        st.write(response)

    st.subheader("📆 Wochenplan von KI erstellen lassen")
    days = st.number_input("Wie viele Trainingstage pro Woche?", min_value=1, max_value=7, value=3)
    focus = st.text_input("Welchen Muskelbereich möchtest du trainieren? (z. B. Brust & Beine)")
    
    if st.button("Trainingsplan generieren"):
        plan = [f"🏋️ Trainingstag {i+1}: Fokus auf {focus}" for i in range(days)]
        for session in plan:
            st.write(session)

# 🍽 **Ernährung & Kalorien-Tracking**
def nutrition_tracker():
    st.subheader("🍽 Dein Ernährungs-Tracker")

    food_item = st.text_input("Was hast du gegessen?")
    calories = st.number_input("Kalorien (optional)", min_value=0)

    if st.button("Hinzufügen"):
        today = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO nutrition (user_id, date, food, calories) VALUES (?, ?, ?, ?)", 
                       (st.session_state["user_id"], today, food_item, calories))
        conn.commit()
        st.success("✅ Mahlzeit gespeichert!")

    st.subheader("📊 Deine heutigen Mahlzeiten")
    cursor.execute("SELECT food, calories FROM nutrition WHERE user_id=? AND date=?", 
                   (st.session_state["user_id"], datetime.date.today().strftime("%Y-%m-%d")))
    meals = cursor.fetchall()

    for meal in meals:
        st.write(f"🍽 {meal[0]} - {meal[1]} kcal")

# **Navigation & Haupt-App**
if "user_id" in st.session_state:
    st.sidebar.write(f"👤 Eingeloggt als: {st.session_state['email']}")
    tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "🤖 KI-Coach", "🍽 Ernährung"])

    with tab1:
        st.subheader("🏠 Willkommen in deinem Dashboard!")
        st.write("Hier siehst du deine Fortschritte, geplante Workouts & Notizen.")

    with tab2:
        ai_coach()

    with tab3:
        nutrition_tracker()
else:
    login()
