import sqlite3
from datetime import datetime


DB_NAME = 'walks6.db'  

def init_db():
    conn = sqlite3.connect(DB_NAME)  
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS walks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  username TEXT,
                  city TEXT,
                  text TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

def save_walk(user_id, username, city, text):
    conn = sqlite3.connect(DB_NAME)  
    c = conn.cursor()
    c.execute("INSERT INTO walks (user_id, username, city, text, timestamp) VALUES (?, ?, ?, ?, ?)",
              (user_id, username, city.lower(), text, datetime.now()))
    conn.commit()
    conn.close()


def get_walks_by_city(city):
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute("SELECT * FROM walks WHERE city = ? ORDER BY timestamp DESC", (city,))
    result = c.fetchall()
    conn.close()
    return result

def get_user_walks(user_id):
    """
    Получает все заявки пользователя по его user_id.
    """
    conn = sqlite3.connect(DB_NAME)  
    c = conn.cursor()
    c.execute("SELECT * FROM walks WHERE user_id = ?", (int(user_id),))  
    result = c.fetchall()
    conn.close()
    return result

def delete_walk(walk_id):
    """
    Удаляет заявку по её ID.
    """
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute("DELETE FROM walks WHERE id = ?", (int(walk_id),))  
    conn.commit()
    conn.close()
