import sqlite3

# Veritabanı bağlantısı
conn = sqlite3.connect('C:\Users\win10\OneDrive\Masaüstü\aras\PHYTON LVL 3\MEZUNİYET PROJESİ\oneri_ve_sikayetler.db')
cursor = conn.cursor()

# Tabloyu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS oneriler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kullanici TEXT NOT NULL,
    mesaj TEXT NOT NULL,
    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
