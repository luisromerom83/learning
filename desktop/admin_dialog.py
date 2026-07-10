from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QWidget, QFrame, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette


# ─────────────────────────────────────────────
#  Passcode Gate Dialog
# ─────────────────────────────────────────────
class PasscodeDialog(QDialog):
    """Asks for the admin passcode before showing settings."""

    def __init__(self, passcode: str, parent=None):
        super().__init__(parent)
        self._correct = passcode
        self.setWindowTitle("Autorización de Administrador")
        self.setFixedSize(380, 220)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(14)

        title = QLabel("🔑 Panel de Administración")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        info = QLabel("Ingresa la contraseña para continuar:")
        info.setFont(QFont("Segoe UI", 10))
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        self._field = QLineEdit()
        self._field.setEchoMode(QLineEdit.EchoMode.Password)
        self._field.setPlaceholderText("Contraseña")
        self._field.setFont(QFont("Segoe UI", 12))
        self._field.setFixedHeight(40)
        self._field.setStyleSheet(
            "QLineEdit { border: 2px solid #203A43; border-radius: 8px; padding: 0 12px;"
            " background: #f8f8f8; } QLineEdit:focus { border-color: #34C0D1; }"
        )
        self._field.returnPressed.connect(self._confirm)
        layout.addWidget(self._field)

        self._error = QLabel("")
        self._error.setStyleSheet("color: #c0392b; font-size: 11px;")
        self._error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._error)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setStyleSheet(
            "QPushButton { border: 1px solid #ccc; border-radius: 6px; padding: 0 16px;"
            " background: #eee; } QPushButton:hover { background: #ddd; }"
        )
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Acceder")
        btn_ok.setFixedHeight(36)
        btn_ok.setStyleSheet(
            "QPushButton { border: none; border-radius: 6px; padding: 0 20px;"
            " background: #203A43; color: white; font-weight: bold; }"
            " QPushButton:hover { background: #2C5364; }"
        )
        btn_ok.clicked.connect(self._confirm)

        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _confirm(self):
        if self._field.text() == self._correct:
            self.accept()
        else:
            self._error.setText("⚠ Contraseña incorrecta")
            self._field.clear()
            self._field.setFocus()


# ─────────────────────────────────────────────
#  Admin Settings Dialog
# ─────────────────────────────────────────────
class AdminDialog(QDialog):
    """Full admin panel: manage URLs and passcode."""

    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        # Work on a deep copy so Cancel truly cancels
        import copy
        self._settings = copy.deepcopy(settings)
        self.setWindowTitle("Administración de URLs y Seguridad")
        self.setMinimumSize(520, 560)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(16)

        # ── Header ──
        header = QLabel("🛠  Configuración de Administrador")
        header.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        header.setStyleSheet("color: #0F2027;")
        root.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #ddd;")
        root.addWidget(sep)

        # ── URLs section ──
        lbl_urls = QLabel("URLs Configuradas")
        lbl_urls.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_urls.setStyleSheet("color: #0F2027;")
        root.addWidget(lbl_urls)

        # Scrollable list
        self._url_container = QWidget()
        self._url_layout = QVBoxLayout(self._url_container)
        self._url_layout.setContentsMargins(0, 0, 0, 0)
        self._url_layout.setSpacing(6)
        self._url_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(self._url_container)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(160)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #ddd; border-radius: 8px; background: #fafafa; }")
        root.addWidget(scroll)

        self._refresh_url_list()

        # ── Add URL ──
        lbl_add = QLabel("Agregar Nueva URL")
        lbl_add.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_add.setStyleSheet("color: #0F2027;")
        root.addWidget(lbl_add)

        self._new_label = QLineEdit()
        self._new_label.setPlaceholderText("Etiqueta  (ej. Plataforma A)")
        self._new_label.setFixedHeight(36)
        self._new_label.setStyleSheet(self._field_style())
        root.addWidget(self._new_label)

        self._new_url = QLineEdit()
        self._new_url.setPlaceholderText("URL  (ej. https://junior.educationspace.com)")
        self._new_url.setFixedHeight(36)
        self._new_url.setStyleSheet(self._field_style())
        root.addWidget(self._new_url)

        self._add_error = QLabel("")
        self._add_error.setStyleSheet("color: #c0392b; font-size: 11px;")
        root.addWidget(self._add_error)

        btn_add = QPushButton("＋  Añadir a la lista")
        btn_add.setFixedHeight(36)
        btn_add.setStyleSheet(
            "QPushButton { border: 2px solid #203A43; border-radius: 8px; padding: 0 16px;"
            " background: white; color: #203A43; font-weight: bold; }"
            " QPushButton:hover { background: #203A43; color: white; }"
        )
        btn_add.clicked.connect(self._add_url)
        root.addWidget(btn_add, alignment=Qt.AlignmentFlag.AlignRight)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #ddd;")
        root.addWidget(sep2)

        # ── Passcode ──
        lbl_pass = QLabel("Contraseña de Administrador")
        lbl_pass.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_pass.setStyleSheet("color: #0F2027;")
        root.addWidget(lbl_pass)

        self._passcode_field = QLineEdit(self._settings.get("passcode", "1234"))
        self._passcode_field.setFixedHeight(36)
        self._passcode_field.setStyleSheet(self._field_style())
        root.addWidget(self._passcode_field)

        root.addStretch()

        # ── Footer buttons ──
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet("color: #ddd;")
        root.addWidget(sep3)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setStyleSheet(
            "QPushButton { border: 1px solid #ccc; border-radius: 8px; padding: 0 20px;"
            " background: #eee; } QPushButton:hover { background: #ddd; }"
        )
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("💾  Guardar Todo")
        btn_save.setFixedHeight(38)
        btn_save.setStyleSheet(
            "QPushButton { border: none; border-radius: 8px; padding: 0 24px;"
            " background: #203A43; color: white; font-weight: bold; font-size: 13px; }"
            " QPushButton:hover { background: #2C5364; }"
        )
        btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_save)
        root.addLayout(btn_row)

    # ── helpers ──────────────────────────────

    @staticmethod
    def _field_style() -> str:
        return (
            "QLineEdit { border: 1px solid #ccc; border-radius: 8px; padding: 0 10px;"
            " background: #fafafa; font-size: 12px; }"
            " QLineEdit:focus { border-color: #34C0D1; }"
        )

    def _refresh_url_list(self):
        # Remove all widgets except the trailing stretch
        while self._url_layout.count() > 1:
            item = self._url_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        urls = self._settings.get("urls", [])
        for idx, entry in enumerate(urls):
            row = self._make_url_row(entry["label"], entry["url"], idx)
            self._url_layout.insertWidget(self._url_layout.count() - 1, row)

        if not urls:
            empty = QLabel("  No hay URLs configuradas.")
            empty.setStyleSheet("color: gray; font-style: italic;")
            self._url_layout.insertWidget(0, empty)

    def _make_url_row(self, label: str, url: str, idx: int) -> QWidget:
        COLORS = ["#E67E22", "#9B59B6", "#27AE60", "#2980B9"]
        color = COLORS[idx % len(COLORS)]

        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #e0e0e0;"
            " border-radius: 8px; } QFrame:hover { background: #f5f5f5; }"
        )
        h = QHBoxLayout(frame)
        h.setContentsMargins(10, 6, 10, 6)
        h.setSpacing(10)

        badge = QLabel(label[0].upper() if label else "?")
        badge.setFixedSize(36, 36)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"background: {color}; color: white; border-radius: 8px;"
            " font-weight: bold; font-size: 14px;"
        )
        h.addWidget(badge)

        col = QVBoxLayout()
        col.setSpacing(0)
        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #2C3E50; border: none; background: transparent;")
        url_lbl = QLabel(url)
        url_lbl.setFont(QFont("Segoe UI", 9))
        url_lbl.setStyleSheet("color: gray; border: none; background: transparent;")
        col.addWidget(lbl)
        col.addWidget(url_lbl)
        h.addLayout(col)
        h.addStretch()

        del_btn = QPushButton("✕")
        del_btn.setFixedSize(28, 28)
        del_btn.setStyleSheet(
            "QPushButton { border: none; border-radius: 6px; color: #c0392b;"
            " background: transparent; font-size: 14px; font-weight: bold; }"
            " QPushButton:hover { background: #fdecea; }"
        )
        del_btn.clicked.connect(lambda _, i=idx: self._delete_url(i))
        h.addWidget(del_btn)

        return frame

    def _delete_url(self, idx: int):
        self._settings["urls"].pop(idx)
        self._refresh_url_list()

    def _add_url(self):
        label = self._new_label.text().strip()
        url = self._new_url.text().strip()
        if not label or not url:
            self._add_error.setText("⚠ La etiqueta y la URL son obligatorias")
            return
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        self._settings["urls"].append({"label": label, "url": url})
        self._new_label.clear()
        self._new_url.clear()
        self._add_error.setText("")
        self._refresh_url_list()

    def _save(self):
        if not self._settings.get("urls"):
            QMessageBox.warning(self, "Error", "Debes agregar al menos una URL.")
            return
        passcode = self._passcode_field.text().strip()
        if not passcode:
            QMessageBox.warning(self, "Error", "La contraseña no puede estar vacía.")
            return
        self._settings["passcode"] = passcode
        self.accept()

    def result_settings(self) -> dict:
        return self._settings
