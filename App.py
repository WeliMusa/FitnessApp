import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import datetime

# 🔹 Datenbankverbindung & Tabellen erstellen
conn = sqlite3.connect("fitness_app.db", check_same_thread=False)
cursor = conn.cursor()

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
        workout TEXT, 
        completed BOOLEAN DEFAULT 0, 
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER, 
        date TEXT, 
        meal TEXT, 
        calories INTEGER, 
        protein INTEGER, 
        carbs INTEGER, 
        fats INTEGER, 
        completed BOOLEAN DEFAULT 0, 
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER, 
        date TEXT, 
        weight REAL, 
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS shopping_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER, 
        item TEXT, 
        quantity TEXT, 
        purchased BOOLEAN DEFAULT 0, 
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")

conn.commit()

# 🔐 Passwort-Hashing-Funktion
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

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
        if st.sidebar.button("Registrieren"):
            cursor.execute("SELECT id FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                st.error("❌ E-Mail bereits registriert!")
            else:
                hashed_pw = hash_password(password)
                cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_pw))
                conn.commit()
                st.success("✅ Registrierung erfolgreich! Jetzt anmelden.")

# Starte Login
login()

# 🔓 Falls eingeloggt, zeige Haupt-App
if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]

    # **Trainingsplan**
    st.header("📅 Trainingsplan")
    workout_date = st.date_input("Datum auswählen", datetime.date.today())
    workout_name = st.text_input("Trainingseinheit hinzufügen")
    if st.button("Hinzufügen"):
        cursor.execute("INSERT INTO workouts (user_id, date, workout) VALUES (?, ?, ?)", 
                       (user_id, workout_date, workout_name))
        conn.commit()

    st.subheader("Geplante Workouts")
    cursor.execute("SELECT id, date, workout, completed FROM workouts WHERE user_id = ?", (user_id,))
    workouts = cursor.fetchall()
    for workout in workouts:
        st.write(f"{workout[1]} - {workout[2]}")
        if st.button(f"✔️ Erledigt", key=f"workout_{workout[0]}"):
            cursor.execute("UPDATE workouts SET completed = 1 WHERE id = ?", (workout[0],))
            conn.commit()

    # **Ernährungsplan**
    st.header("🍽️ Ernährungsplan")
    meal_date = st.date_input("Datum auswählen", datetime.date.today())
    meal_name = st.text_input("Mahlzeit hinzufügen")
    calories = st.number_input("Kalorien", min_value=0)
    protein = st.number_input("Protein (g)", min_value=0)
    carbs = st.number_input("Kohlenhydrate (g)", min_value=0)
    fats = st.number_input("Fett (g)", min_value=0)
    
    if st.button("Mahlzeit speichern"):
        cursor.execute("INSERT INTO meals (user_id, date, meal, calories, protein, carbs, fats) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (user_id, meal_date, meal_name, calories, protein, carbs, fats))
        conn.commit()

    st.subheader("Geplante Mahlzeiten")
    cursor.execute("SELECT id, date, meal, completed FROM meals WHERE user_id = ?", (user_id,))
    meals = cursor.fetchall()
    for meal in meals:
        st.write(f"{meal[1]} - {meal[2]}")
        if st.button(f"✔️ Erledigt", key=f"meal_{meal[0]}"):
            cursor.execute("UPDATE meals SET completed = 1 WHERE id = ?", (meal[0],))
            conn.commit()

    # **Fortschritt tracken**
    st.header("📊 Fortschritt")
    weight_date = st.date_input("Datum", datetime.date.today(), key="weight_date")
    weight = st.number_input("Gewicht (kg)", min_value=0.0, format="%.1f")
    if st.button("Speichern", key="progress_save"):
        cursor.execute("INSERT INTO progress (user_id, date, weight) VALUES (?, ?, ?)", 
                       (user_id, weight_date, weight))
        conn.commit()

    st.subheader("Gewichtshistorie")
    cursor.execute("SELECT date, weight FROM progress WHERE user_id = ?", (user_id,))
    progress = cursor.fetchall()
    st.write(pd.DataFrame(progress, columns=["Datum", "Gewicht"]))

    # **Einkaufsliste**
    st.header("🛒 Einkaufsliste")
    item_name = st.text_input("Neues Produkt hinzufügen")
    quantity = st.text_input("Menge")
    if st.button("Produkt speichern"):
        cursor.execute("INSERT INTO shopping_list (user_id, item, quantity) VALUES (?, ?, ?)", 
                       (user_id, item_name, quantity))
        conn.commit()

    st.subheader("Aktuelle Einkaufsliste")
    cursor.execute("SELECT id, item, quantity, purchased FROM shopping_list WHERE user_id = ?", (user_id,))
    shopping_list = cursor.fetchall()
    for item in shopping_list:
        st.write(f"{item[1]} - {item[2]}")
        if st.button(f"✔️ Gekauft", key=f"item_{item[0]}"):
            cursor.execute("UPDATE shopping_list SET purchased = 1 WHERE id = ?", (item[0],))
            conn.commit()

# Verbindung schließen
conn.close()
