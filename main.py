import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from database import setup_database
from pagina_start import PaginaStart


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskFlow - Management Notițe")
        self.resize(900, 600)

        self.pagina_start = PaginaStart()
        self.setCentralWidget(self.pagina_start)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    if not setup_database():
        sys.exit(1)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())