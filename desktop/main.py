import sys
import os

import settings
settings.setup_logging()

# Use safer Chromium flags to prevent rendering issues on hybrid GPUs
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--ignore-gpu-blocklist")

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
