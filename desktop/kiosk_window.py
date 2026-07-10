import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy, QStackedWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, Qt, QSize
from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPainter, QBrush

import settings as cfg
from admin_dialog import PasscodeDialog, AdminDialog


# ─────────────────────────────────────────────────────────────────
#  Gradient background widget
# ─────────────────────────────────────────────────────────────────
class GradientWidget(QWidget):
    """Vertical gradient background: #0F2027 → #203A43 → #2C5364"""

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#0F2027"))
        gradient.setColorAt(0.5, QColor("#203A43"))
        gradient.setColorAt(1.0, QColor("#2C5364"))
        painter.fillRect(self.rect(), QBrush(gradient))


# ─────────────────────────────────────────────────────────────────
#  Kiosk main window
# ─────────────────────────────────────────────────────────────────
class KioskWindow(QMainWindow):

    CTRL_BAR_HEIGHT = 52
    CARD_COLORS = ["#E67E22", "#9B59B6", "#27AE60", "#2980B9"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Education Space Junior")
        self.setMinimumSize(900, 600)
        self._settings = cfg.load_settings()
        self._active_url: dict | None = None
        self._fullscreen_web = False

        self._build_ui()
        self.showMaximized()

    # ─── Build UI ────────────────────────────────────────────────

    def _build_ui(self):
        # Root layout: top bar + stacked content
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        # ── Persistent top bar (visible on onboarding + hub) ──
        self._top_bar = self._make_top_bar()
        root_layout.addWidget(self._top_bar)

        # ── Stacked content area ──
        self._stack = QStackedWidget()
        root_layout.addWidget(self._stack, stretch=1)

        self._screen_onboarding = self._make_onboarding_screen()
        self._screen_hub = self._make_hub_screen()
        self._screen_viewer = self._make_viewer_screen()

        self._stack.addWidget(self._screen_onboarding)  # index 0
        self._stack.addWidget(self._screen_hub)          # index 1
        self._stack.addWidget(self._screen_viewer)       # index 2

        self._show_correct_screen()

    # ─── Persistent top bar (onboarding + hub) ──────────────────

    def _make_top_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(self.CTRL_BAR_HEIGHT)
        bar.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #0F2027, stop:0.5 #203A43, stop:1 #2C5364);"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(8)

        self._top_bar_title = QLabel("Education Space Junior")
        self._top_bar_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._top_bar_title.setStyleSheet("color: #34C0D1; background: transparent;")
        layout.addWidget(self._top_bar_title, stretch=1)

        btn_admin = self._make_icon_btn("⚙", "Administración (Ctrl+Alt+A)", self._open_admin, parent=bar)
        layout.addWidget(btn_admin)
        return bar

    # ─── Screen: Onboarding ──────────────────────────────────────

    def _make_onboarding_screen(self) -> QWidget:
        root = GradientWidget()
        outer = QVBoxLayout(root)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedWidth(480)
        card.setStyleSheet(
            "QFrame { background: rgba(255,255,255,0.93); border-radius: 24px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 36, 40, 36)
        card_layout.setSpacing(16)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel("🔒")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 42))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        card_layout.addWidget(icon_lbl)

        title = QLabel("Education Space Junior Kiosk")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #0F2027; background: transparent;")
        title.setWordWrap(True)
        card_layout.addWidget(title)

        sub = QLabel("Configure la URL de destino para comenzar.")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color: #555; background: transparent;")
        sub.setWordWrap(True)
        card_layout.addWidget(sub)

        hint_box = QFrame()
        hint_box.setStyleSheet("QFrame { background: #EFEFEF; border-radius: 12px; }")
        hint_layout = QVBoxLayout(hint_box)
        hint_layout.setContentsMargins(16, 14, 16, 14)

        hint = QLabel(
            "👉 Haz clic en el botón ⚙ de la barra superior\n"
            "    para abrir el Panel de Administrador.\n\n"
            "🔑 Contraseña por defecto: 1234"
        )
        hint.setFont(QFont("Segoe UI", 10))
        hint.setStyleSheet("color: #333; background: transparent;")
        hint_layout.addWidget(hint)
        card_layout.addWidget(hint_box)

        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        return root

    # ─── Screen: Hub ─────────────────────────────────────────────

    def _make_hub_screen(self) -> QWidget:
        root = GradientWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # (No separate top bar needed — shared _top_bar handles it)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        content_layout.setContentsMargins(24, 40, 24, 48)
        content_layout.setSpacing(0)

        # Lion badge
        badge = QLabel("🦁")
        badge.setFont(QFont("Segoe UI Emoji", 52))
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            "background: rgba(255,255,255,0.15); border-radius: 28px;"
            " padding: 12px 18px;"
        )
        content_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addSpacing(20)

        brand = QLabel("Education Space")
        brand.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("color: #34C0D1; background: transparent;")
        content_layout.addWidget(brand)

        subtitle = QLabel("Junior Kiosk")
        subtitle.setFont(QFont("Segoe UI", 18))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: rgba(255,255,255,0.85); background: transparent;")
        content_layout.addWidget(subtitle)
        content_layout.addSpacing(8)

        greeting = QLabel("¡Hola! ¿Qué quieres aprender hoy?")
        greeting.setFont(QFont("Segoe UI", 13))
        greeting.setAlignment(Qt.AlignmentFlag.AlignCenter)
        greeting.setStyleSheet("color: rgba(255,255,255,0.65); background: transparent;")
        content_layout.addWidget(greeting)
        content_layout.addSpacing(28)

        # URL cards container (rebuilt when settings change)
        self._cards_container = QWidget()
        self._cards_container.setStyleSheet("background: transparent;")
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(10)
        content_layout.addWidget(self._cards_container)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        self._hub_content_layout = content_layout
        return root

    def _rebuild_cards(self):
        """Recreate URL shortcut cards from current settings."""
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        urls = self._settings.get("urls", [])
        COLORS = self.CARD_COLORS
        for idx, entry in enumerate(urls):
            card = self._make_url_card(entry, idx, COLORS[idx % len(COLORS)])
            self._cards_layout.addWidget(card)

    def _make_url_card(self, entry: dict, idx: int, color: str) -> QFrame:
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(
            "QFrame { background: rgba(255,255,255,0.92); border-radius: 16px; }"
            " QFrame:hover { background: rgba(255,255,255,1.0); }"
        )
        card.setFixedHeight(72)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        h = QHBoxLayout(card)
        h.setContentsMargins(14, 10, 14, 10)
        h.setSpacing(14)

        badge = QLabel(entry["label"][0].upper() if entry["label"] else "?")
        badge.setFixedSize(48, 48)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        badge.setStyleSheet(
            f"background: {color}; color: white; border-radius: 12px;"
        )
        h.addWidget(badge)

        col = QVBoxLayout()
        col.setSpacing(2)
        lbl = QLabel(entry["label"])
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #2C3E50; background: transparent;")
        url_lbl = QLabel(entry["url"])
        url_lbl.setFont(QFont("Segoe UI", 10))
        url_lbl.setStyleSheet("color: gray; background: transparent;")
        col.addWidget(lbl)
        col.addWidget(url_lbl)
        h.addLayout(col)
        h.addStretch()

        # Clickable via mousePressEvent
        card.mousePressEvent = lambda _e, e=entry: self._open_url(e)
        return card

    # ─── Screen: Viewer (WebView) ────────────────────────────────

    def _make_viewer_screen(self) -> QWidget:
        root = QWidget()
        root.setStyleSheet("background: #0F2027;")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Control bar (replaces the shared top bar while viewer is active) ──
        self._ctrl_bar = QWidget()
        self._ctrl_bar.setFixedHeight(self.CTRL_BAR_HEIGHT)
        self._ctrl_bar.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #0F2027, stop:0.5 #203A43, stop:1 #2C5364);"
        )
        bar_layout = QHBoxLayout(self._ctrl_bar)
        bar_layout.setContentsMargins(10, 0, 10, 0)
        bar_layout.setSpacing(4)

        btn_back = self._make_icon_btn("◀", "Volver al Hub", self._go_hub, parent=self._ctrl_bar)
        bar_layout.addWidget(btn_back)
        bar_layout.addSpacing(6)

        self._title_label = QLabel("")
        self._title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self._title_label.setStyleSheet("color: white; background: transparent;")
        bar_layout.addWidget(self._title_label, stretch=1)

        btn_reload = self._make_icon_btn("↻", "Recargar página", self._reload_page, parent=self._ctrl_bar)
        bar_layout.addWidget(btn_reload)

        # ── Admin button (next to refresh) ──
        btn_admin = self._make_icon_btn("⚙", "Administración", self._open_admin, parent=self._ctrl_bar)
        bar_layout.addWidget(btn_admin)

        btn_fs = self._make_icon_btn("⤢", "Pantalla completa", self._toggle_fullscreen_web, parent=self._ctrl_bar)
        bar_layout.addWidget(btn_fs)
        self._btn_fs = btn_fs

        layout.addWidget(self._ctrl_bar)

        # ── WebView ──
        self._webview = QWebEngineView()
        self._webview.page().featurePermissionRequested.connect(self._grant_permission)
        layout.addWidget(self._webview, stretch=1)

        return root

    # ─── Navigation helpers ───────────────────────────────────────

    def _show_correct_screen(self):
        urls = self._settings.get("urls", [])
        self._top_bar.show()
        if not urls:
            self._stack.setCurrentIndex(0)  # onboarding
        else:
            self._rebuild_cards()
            self._stack.setCurrentIndex(1)  # hub
        self._active_url = None
        self._top_bar_title.setText("Education Space Junior")

    def _open_url(self, entry: dict):
        self._active_url = entry
        self._title_label.setText(entry["label"])
        self._webview.load(QUrl(entry["url"]))
        self._top_bar.hide()          # viewer has its own ctrl bar
        self._ctrl_bar.show()
        self._stack.setCurrentIndex(2)  # viewer
        self._fullscreen_web = False

    def _go_hub(self):
        self._webview.stop()
        self._top_bar.show()
        self._show_correct_screen()

    def _reload_page(self):
        self._webview.reload()

    def _toggle_fullscreen_web(self):
        self._fullscreen_web = not self._fullscreen_web
        self._ctrl_bar.setVisible(not self._fullscreen_web)
        self._btn_fs.setText("✕" if self._fullscreen_web else "⤢")
        if self._fullscreen_web:
            self.showFullScreen()
        else:
            self.showMaximized()

    # ─── Admin panel ─────────────────────────────────────────────

    def _open_admin(self):
        passcode = self._settings.get("passcode", "1234")
        pwd_dlg = PasscodeDialog(passcode, self)
        if pwd_dlg.exec() != PasscodeDialog.DialogCode.Accepted:
            return
        dlg = AdminDialog(self._settings, self)
        if dlg.exec() == AdminDialog.DialogCode.Accepted:
            self._settings = dlg.result_settings()
            cfg.save_settings(self._settings)
            self._show_correct_screen()

    def _grant_permission(self, url, feature):
        """Auto-grant camera and microphone permissions."""
        print(f"Permission requested for origin: {url.toString()}, feature: {feature}")
        try:
            ALLOWED = {
                QWebEnginePage.Feature.MediaAudioCapture,
                QWebEnginePage.Feature.MediaVideoCapture,
                QWebEnginePage.Feature.MediaAudioVideoCapture,
            }
            if feature in ALLOWED:
                policy = QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
                print(f"-> Granting permission: {feature}")
            else:
                policy = QWebEnginePage.PermissionPolicy.PermissionDeniedByUser
                print(f"-> Denying permission: {feature}")
            self._webview.page().setFeaturePermission(url, feature, policy)
        except Exception as e:
            print(f"ERROR in _grant_permission: {e}")

    # ─── Key events ──────────────────────────────────────────────

    def keyPressEvent(self, event):
        # Ctrl+Alt+A → admin (secondary hotkey for convenience)
        if (
            event.key() == Qt.Key.Key_A
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
            and event.modifiers() & Qt.KeyboardModifier.AltModifier
        ):
            self._open_admin()
            return
        # Escape exits fullscreen web view
        if event.key() == Qt.Key.Key_Escape and self._fullscreen_web:
            self._toggle_fullscreen_web()
            return
        super().keyPressEvent(event)

    # ─── Widget factory ──────────────────────────────────────────

    @staticmethod
    def _make_icon_btn(icon: str, tooltip: str, callback, parent=None) -> QPushButton:
        btn = QPushButton(icon, parent)
        btn.setToolTip(tooltip)
        btn.setFixedSize(38, 38)
        btn.setFont(QFont("Segoe UI Emoji", 15))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { border: none; border-radius: 8px; background: transparent; color: white; }"
            " QPushButton:hover { background: rgba(255,255,255,0.18); }"
            " QPushButton:pressed { background: rgba(255,255,255,0.30); }"
        )
        btn.clicked.connect(callback)
        return btn
