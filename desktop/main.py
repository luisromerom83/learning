import os
import sys
import webview
import json

import settings as cfg

# Initialize debug log
cfg.setup_logging()


class Api:
    def __init__(self):
        self.viewer_win = None
        self.test_win = None

    def get_settings(self):
        print("API: get_settings requested")
        return cfg.load_settings()

    def save_settings(self, settings):
        print(f"API: save_settings -> {settings}")
        cfg.save_settings(settings)
        return {"status": "ok"}

    def open_url(self, label, url):
        print(f"API: open_url requested -> {label}: {url}")
        
        # Close old viewer window if open
        if self.viewer_win:
            try:
                self.viewer_win.destroy()
            except Exception:
                pass

        # Create a new, clean window utilizing native WebView2 (Edge Chromium)
        # That runs maximized and has default browser behaviors (codecs, WebRTC, etc.)
        self.viewer_win = webview.create_window(
            title=label,
            url=url,
            width=1200,
            height=800,
            resizable=True
        )

    def test_devices(self):
        print("API: test_devices requested")
        if self.test_win:
            try:
                self.test_win.destroy()
            except Exception:
                pass
        
        # Load a secure WebRTC test site to verify hardware
        self.test_win = webview.create_window(
            title="Prueba de Dispositivos",
            url="https://webcamtests.com",
            width=800,
            height=600,
            resizable=True
        )


def main():
    # Load index.html from resources path (works with PyInstaller temp folder)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    html_path = os.path.join(base_dir, "index.html")

    print(f"Loading local HTML from: {html_path}")

    api = Api()

    # Main Hub window
    main_win = webview.create_window(
        title="Education Space Junior",
        url=html_path,
        width=1000,
        height=700,
        resizable=True,
        js_api=api
    )

    # Starts pywebview engine loop.
    # On Windows, this runs WebView2 automatically.
    webview.start(debug=False)


if __name__ == "__main__":
    main()
