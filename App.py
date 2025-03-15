import streamlit as st
import sqlite3
import bcrypt
import requests
import os

# 🔹 Verbindung zur Datenbank (richtige Speicherort-Fix!)
DB_PATH = "fitness_app.db"  # Standardverzeichnis (kein /mnt/data/)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# 🔹 Tabellen für Benutzer & Ernährung erstellen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        email TEXT UNIQUE, 
        password TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS nutrition (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        meal_name TEXT,
        calories INTEGER,
        protein REAL,
        carbs REAL,
        fats REAL
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
                st.rerun()
            else:
                st.error("❌ Falsche E-Mail oder Passwort")

    elif choice == "Registrieren":
        email = st.sidebar.text_input("E-Mail")
        password = st.sidebar.text_input("Passwort", type="password")
        reg_code = st.sidebar.text_input("Registrierungscode", type="password")

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

# 🔎 **Lebensmittel-Suche mit OpenFoodFacts API**
def search_food(food_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={food_name}&search_simple=1&action=process&json=1"
    response = requests.get(url)
    data = response.json()
    
    if "products" in data and len(data["products"]) > 0:
        product = data["products"][0]  # Erstes Suchergebnis nehmen
        name = product.get("product_name", "Unbekannt")
        nutrients = product.get("nutriments", {})

        return {
            "name": name,
            "calories": nutrients.get("energy-kcal_100g", 0),
            "protein": nutrients.get("proteins_100g", 0),
            "carbs": nutrients.get("carbohydrates_100g", 0),
            "fats": nutrients.get("fat_100g", 0)
        }
    return None

# 📊 **Kalorienzähler mit automatischer Lebensmittelsuche**
def calorie_tracker():
    st.header("🧮 Kalorienzähler")

    food_item = st.text_input("Lebensmittel eingeben")
    if st.button("Suchen"):
        result = search_food(food_item)
        if result:
            st.write(f"🍽️ **{result['name']}**")
            st.write(f"🔥 **Kalorien:** {result['calories']} kcal")
            st.write(f"💪 **Protein:** {result['protein']} g")
            st.write(f"🥖 **Kohlenhydrate:** {result['carbs']} g")
            st.write(f"🛢️ **Fette:** {result['fats']} g")
            
            if st.button("Zur Ernährung hinzufügen"):
                cursor.execute("INSERT INTO nutrition (user_id, meal_name, calories, protein, carbs, fats) VALUES (?, ?, ?, ?, ?, ?)", 
                               (st.session_state["user_id"], result["name"], result["calories"], result["protein"], result["carbs"], result["fats"]))
                conn.commit()
                st.success("✅ Lebensmittel gespeichert!")
        else:
            st.error("❌ Kein passendes Lebensmittel gefunden!")

# **Navigation & Haupt-App**
if "user_id" in st.session_state:
    st.sidebar.write(f"👤 Eingeloggt als: {st.session_state['email']}")
    menu = ["🧮 Kalorienzähler"]
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "🧮 Kalorienzähler":
        calorie_tracker()
else:
    login()
