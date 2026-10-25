import sys
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QStackedWidget, QCalendarWidget, QDialog,
    QLineEdit, QDateEdit, QSpinBox, QComboBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QBrush, QTextCharFormat
from PyQt6.QtSql import QSqlQuery

class AccessibilityDialog(QDialog):
    def __init__(self, current_font_size, current_theme_index, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setări Accesibilitate")
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<b>Dimensiune Font (pt):</b>"))
        self.font_spinbox = QSpinBox()
        self.font_spinbox.setRange(9, 24)
        self.font_spinbox.setValue(current_font_size)
        layout.addWidget(self.font_spinbox)

        layout.addWidget(QLabel("<b>Paletă de Culori / Contrast:</b>"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Implicită (Standard)",
            "Contrast Ridicat (Text Galben pe Negru)",
            "Mod Întunecat (Dark Mode)",
            "Gama Albastru / Galben (Tritanopie)",
            "Scara de Gri (Monocrom)"
        ])
        self.theme_combo.setCurrentIndex(current_theme_index)
        layout.addWidget(self.theme_combo)

        btn_layout = QHBoxLayout()
        btn_apply = QPushButton("Aplică")
        btn_cancel = QPushButton("Anulează")

        btn_apply.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 6px;")
        btn_cancel.setStyleSheet("padding: 6px;")

        btn_apply.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_apply)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_settings(self):
        return self.font_spinbox.value(), self.theme_combo.currentIndex()


class AddNoteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adaugă Notiță Nouă")
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Textul notiței...")
        layout.addWidget(self.text_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Termen limită:"))
        layout.addWidget(self.date_input)

        btn_save = QPushButton("Salvează Notiță")
        btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

    def get_data(self):
        return self.text_input.text().strip(), self.date_input.date().toString("yyyy-MM-dd")


class PaginaStart(QWidget):
    def __init__(self):
        super().__init__()
        self.calendar = None
        self.current_user_id = 1  # ID implicit fără autentificare
        self.current_font_size = 11
        self.current_theme_index = 0
        self.init_ui()
        self.load_notes()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        sidebar_layout = QVBoxLayout(sidebar)

        self.welcome_label = QLabel("Notițele Mele")
        self.welcome_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        sidebar_layout.addWidget(self.welcome_label)

        btn_all_notes = QPushButton("📝 Toate Notițele")
        btn_favorites = QPushButton("⭐ Favorite")
        btn_calendar = QPushButton("📅 Calendar")
        btn_trash = QPushButton("🗑️ Coș de gunoi")
        btn_accessibility = QPushButton("♿ Accesibilitate")

        buttons = [btn_all_notes, btn_favorites, btn_calendar, btn_trash, btn_accessibility]
        for btn in buttons:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    text-align: left;
                    padding: 10px;
                    font-size: 13px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    border-radius: 5px;
                }
            """)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        self.content_stack = QStackedWidget()

        btn_all_notes.clicked.connect(lambda: self.switch_page(0))
        btn_favorites.clicked.connect(lambda: self.switch_page(1))
        btn_calendar.clicked.connect(lambda: self.switch_page(2))
        btn_trash.clicked.connect(lambda: self.switch_page(3))
        btn_accessibility.clicked.connect(self.open_accessibility_dialog)

        # Toate Notițele
        page_notes = QWidget()
        layout_notes = QVBoxLayout(page_notes)
        btn_add_note = QPushButton("+ Adaugă Notiță Nouă")
        btn_add_note.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; font-weight: bold;")
        btn_add_note.clicked.connect(self.open_add_note_dialog)
        layout_notes.addWidget(btn_add_note)

        notes_action_layout = QHBoxLayout()
        btn_star_selected = QPushButton("⭐ Adaugă / Elimină Favorit")
        btn_delete_selected = QPushButton("🗑️ Mută în Coșul de Gunoi")
        btn_star_selected.clicked.connect(lambda: self.toggle_favorite(self.list_notes))
        btn_delete_selected.clicked.connect(lambda: self.move_to_trash(self.list_notes))
        notes_action_layout.addWidget(btn_star_selected)
        notes_action_layout.addWidget(btn_delete_selected)
        layout_notes.addLayout(notes_action_layout)

        self.list_notes = QListWidget()
        layout_notes.addWidget(self.list_notes)
        self.content_stack.addWidget(page_notes)

        # Favorite
        page_fav = QWidget()
        layout_fav = QVBoxLayout(page_fav)
        layout_fav.addWidget(QLabel("<h2>Notițe Favorite</h2>"))
        btn_unstar_fav = QPushButton(" Elimină de la Favorite")
        btn_unstar_fav.clicked.connect(lambda: self.toggle_favorite(self.list_favorites))
        layout_fav.addWidget(btn_unstar_fav)
        self.list_favorites = QListWidget()
        layout_fav.addWidget(self.list_favorites)
        self.content_stack.addWidget(page_fav)

        # Calendar
        page_cal = QWidget()
        layout_cal = QVBoxLayout(page_cal)
        layout_cal.addWidget(QLabel("<h2>Vizualizare Calendar</h2>"))
        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.on_calendar_date_selected)
        layout_cal.addWidget(self.calendar)

        self.label_cal_date = QLabel("Notițe cu termen în ziua selectată:")
        self.label_cal_date.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout_cal.addWidget(self.label_cal_date)

        self.list_calendar_notes = QListWidget()
        layout_cal.addWidget(self.list_calendar_notes)
        self.content_stack.addWidget(page_cal)

        # Trash
        page_trash = QWidget()
        layout_trash = QVBoxLayout(page_trash)
        layout_trash.addWidget(QLabel("<h2>Coș de Gunoi (Notițe Șterse)</h2>"))

        trash_action_layout = QHBoxLayout()
        btn_restore = QPushButton(" Restaurează Notița")
        btn_perm_delete = QPushButton(" Șterge Definitiv")
        btn_restore.clicked.connect(self.restore_from_trash)
        btn_perm_delete.clicked.connect(self.delete_permanently)
        trash_action_layout.addWidget(btn_restore)
        trash_action_layout.addWidget(btn_perm_delete)
        layout_trash.addLayout(trash_action_layout)

        self.list_trash = QListWidget()
        layout_trash.addWidget(self.list_trash)
        self.content_stack.addWidget(page_trash)

        main_layout.addWidget(self.content_stack)

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        self.load_notes()

    def load_notes(self):
        self.list_notes.clear()
        self.list_favorites.clear()
        self.list_trash.clear()

        blank_format = QTextCharFormat()
        self.calendar.setDateTextFormat(QDate(), blank_format)

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QBrush(QColor("#27ae60")))
        highlight_format.setForeground(QBrush(QColor("white")))

        query = QSqlQuery()
        query.prepare("SELECT id, text, datadueto, hidden, isstarred FROM notes WHERE user_id = :uid")
        query.bindValue(":uid", self.current_user_id)

        if query.exec():
            while query.next():
                note_id = query.value(0)
                text = query.value(1)
                due_date_str = query.value(2)
                hidden = query.value(3)
                is_starred = query.value(4)

                item_str = f"{text}  |  Termen: {due_date_str}" if due_date_str else text

                item = QListWidgetItem(item_str)
                item.setData(Qt.ItemDataRole.UserRole, note_id)

                if hidden == 1:
                    self.list_trash.addItem(item)
                else:
                    if is_starred == 1:
                        item.setText(f"⭐ {item_str}")
                        self.list_notes.addItem(item)

                        fav_item = QListWidgetItem(f"⭐ {item_str}")
                        fav_item.setData(Qt.ItemDataRole.UserRole, note_id)
                        self.list_favorites.addItem(fav_item)
                    else:
                        self.list_notes.addItem(item)

                    if due_date_str:
                        date_obj = QDate.fromString(due_date_str, "yyyy-MM-dd")
                        if date_obj.isValid():
                            self.calendar.setDateTextFormat(date_obj, highlight_format)

        self.on_calendar_date_selected()

    def open_add_note_dialog(self):
        dialog = AddNoteDialog(self)
        if dialog.exec():
            note_text, due_date = dialog.get_data()
            if note_text:
                query = QSqlQuery()
                query.prepare("""
                              INSERT INTO notes (user_id, text, data, datadueto, hidden, isstarred)
                              VALUES (:uid, :text, :data, :due, 0, 0)
                              """)
                query.bindValue(":uid", self.current_user_id)
                query.bindValue(":text", note_text)
                query.bindValue(":data", QDate.currentDate().toString("yyyy-MM-dd"))
                query.bindValue(":due", due_date)
                query.exec()
                self.load_notes()

    def toggle_favorite(self, list_widget):
        selected_item = list_widget.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Atenție", "Selectează o notiță din listă!")
            return

        note_id = selected_item.data(Qt.ItemDataRole.UserRole)

        query = QSqlQuery()
        query.prepare("SELECT isstarred FROM notes WHERE id = :id")
        query.bindValue(":id", note_id)
        if query.exec() and query.next():
            current_status = query.value(0)
            new_status = 0 if current_status == 1 else 1

            update_q = QSqlQuery()
            update_q.prepare("UPDATE notes SET isstarred = :st WHERE id = :id")
            update_q.bindValue(":st", new_status)
            update_q.bindValue(":id", note_id)
            update_q.exec()

            self.load_notes()

    def move_to_trash(self, list_widget):
        selected_item = list_widget.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Atenție", "Selectează o notiță pentru a o muta în coș!")
            return

        note_id = selected_item.data(Qt.ItemDataRole.UserRole)

        query = QSqlQuery()
        query.prepare("UPDATE notes SET hidden = 1 WHERE id = :id")
        query.bindValue(":id", note_id)
        query.exec()

        self.load_notes()

    def restore_from_trash(self):
        selected_item = self.list_trash.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Atenție", "Selectează o notiță din coșul de gunoi!")
            return

        note_id = selected_item.data(Qt.ItemDataRole.UserRole)

        query = QSqlQuery()
        query.prepare("UPDATE notes SET hidden = 0 WHERE id = :id")
        query.bindValue(":id", note_id)
        query.exec()

        self.load_notes()

    def delete_permanently(self):
        selected_item = self.list_trash.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Atenție", "Selectează o notiță din coșul de gunoi!")
            return

        reply = QMessageBox.question(
            self, "Confirmare ștergere",
            "Ești sigur că vrei să ștergi definitiv această notiță din baza de date?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            note_id = selected_item.data(Qt.ItemDataRole.UserRole)
            query = QSqlQuery()
            query.prepare("DELETE FROM notes WHERE id = :id")
            query.bindValue(":id", note_id)
            query.exec()
            self.load_notes()

    # -----------------------------------------------------------------
    # ACOMANIERE CALENDAR
    # -----------------------------------------------------------------
    def on_calendar_date_selected(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.label_cal_date.setText(f"Notițe cu termen limită în data de {selected_date}:")
        self.list_calendar_notes.clear()

        query = QSqlQuery()
        query.prepare("SELECT text FROM notes WHERE user_id = :uid AND datadueto = :date AND hidden = 0")
        query.bindValue(":uid", self.current_user_id)
        query.bindValue(":date", selected_date)

        found = False
        if query.exec():
            while query.next():
                found = True
                note_text = query.value(0)
                self.list_calendar_notes.addItem(f"📌 {note_text}")

        if not found:
            self.list_calendar_notes.addItem("Nicio notiță programată pentru această zi.")

    # -----------------------------------------------------------------
    # FUNCȚIONALITĂȚI ACCESIBILITATE
    # -----------------------------------------------------------------
    def open_accessibility_dialog(self):
        dialog = AccessibilityDialog(self.current_font_size, self.current_theme_index, self)
        if dialog.exec():
            font_size, theme_index = dialog.get_settings()
            self.current_font_size = font_size
            self.current_theme_index = theme_index
            self.apply_accessibility_settings()

    def apply_accessibility_settings(self):
        base_style = f"font-size: {self.current_font_size}pt;\n"

        if self.current_theme_index == 1:
            theme_style = """
                QWidget { background-color: #000000; color: #FFFF00; }
                QPushButton { background-color: #1a1a1a; color: #FFFF00; border: 2px solid #FFFF00; }
                QListWidget, QCalendarWidget { background-color: #000000; color: #FFFF00; border: 1px solid #FFFF00; }
            """
        elif self.current_theme_index == 2:
            theme_style = """
                QWidget { background-color: #1e1e1e; color: #ffffff; }
                QPushButton { background-color: #2d2d2d; color: #ffffff; border: 1px solid #3d3d3d; }
                QListWidget { background-color: #252526; color: #ffffff; }
            """
        elif self.current_theme_index == 3:
            theme_style = """
                QWidget { background-color: #002b36; color: #2aa198; }
                QPushButton { background-color: #073642; color: #b58900; border: 1px solid #b58900; }
            """
        elif self.current_theme_index == 4:
            theme_style = """
                QWidget { background-color: #f0f0f0; color: #111111; }
                QPushButton { background-color: #e0e0e0; color: #000000; border: 1px solid #888888; }
            """
        else:
            theme_style = ""

        self.setStyleSheet(base_style + theme_style)