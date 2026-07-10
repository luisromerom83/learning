import sys
import os

# Enable Chromium hardware acceleration and DPI awareness
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--enable-gpu-rasterization")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from kiosk_window import KioskWindow


def main():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Education Space Junior")
    app.setOrganizationName("EducationSpace")

    window = KioskWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
