import sys
from PyQt6.QtWidgets import QApplication

from database import setup_database

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not setup_database():
        sys.exit(1)