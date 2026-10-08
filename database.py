import sys
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import QApplication, QMessageBox

def setup_database():
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("app_data.db")

    if not db.open():
        QMessageBox.critical(
            None,
            "Database Error",
            f"Could not open database: {db.lastError().text()}"
        )
        return False

    query = QSqlQuery()
    query.exec("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    query.exec("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                data TEXT NOT NULL,
                datadueto TEXT,
                hidden INTEGER,
                isstarred INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

    return True