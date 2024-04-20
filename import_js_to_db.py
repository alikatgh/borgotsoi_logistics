import sqlite3
import json

conn = sqlite3.connect('logistics.db')
cursor = conn.cursor()

with open('supermarkets/supermarkets.json', encoding='utf-8') as f:
    data = json.load(f)

for supermarket in data:
    sql = "INSERT INTO supermarkets (id, name, address) VALUES (?, ?, ?)"
    val = (supermarket.get('id'), supermarket['name'], supermarket['address']) 
    cursor.execute(sql, val)

conn.commit()
conn.close() 
