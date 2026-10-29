import sys
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import QMessageBox

def setup_database():
    #conexiune
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("app_data.db")

    if not db.open():
        QMessageBox.critical(
            None,
            "Eroare Bază de Date",
            f"Nu s-a putut deschide baza de date: {db.lastError().text()}"
        )
        return False

    query = QSqlQuery()

    # creare tabel users
    query.exec("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    #creare tabel notite
    query.exec("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            data TEXT NOT NULL,
            datadueto TEXT,
            hidden INTEGER DEFAULT 0,
            isstarred INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    #creare user implicit
    query.exec("""
        INSERT OR IGNORE INTO users (id, name, password) 
        VALUES (1, 'Utilizator Principal', 'admin')
    """)

    return True