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

    def open_url(self, label, url, username=None, password=None):
        print(f"API: open_url requested -> {label}: {url} (has_credentials: {bool(username or password)})")
        
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

        if username or password:
            def on_loaded(window=None):
                js_user = json.dumps(username)
                js_pass = json.dumps(password)
                
                autofill_js = f"""
                (function() {{
                    const username = {js_user};
                    const password = {js_pass};
                    
                    function tryFill() {{
                        const passwordInput = document.querySelector('input[type="password"]');
                        if (!passwordInput) return false;
                        
                        let usernameInput = document.querySelector('input[type="email"], input[autocomplete="username"], input[autocomplete="email"]');
                        if (!usernameInput) {{
                            const inputs = Array.from(document.querySelectorAll('input'));
                            const passIdx = inputs.indexOf(passwordInput);
                            if (passIdx > 0) {{
                                for (let i = passIdx - 1; i >= 0; i--) {{
                                    if (inputs[i].type === 'text' || inputs[i].type === 'email') {{
                                        usernameInput = inputs[i];
                                        break;
                                    }}
                                }}
                            }}
                        }}
                        
                        let filled = false;
                        if (usernameInput && username) {{
                            usernameInput.value = username;
                            usernameInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            usernameInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            filled = true;
                        }}
                        if (passwordInput && password) {{
                            passwordInput.value = password;
                            passwordInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            passwordInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            filled = true;
                        }}
                        return filled;
                    }}
                    
                    if (!tryFill()) {{
                        let attempts = 0;
                        const interval = setInterval(() => {{
                            attempts++;
                            if (tryFill() || attempts > 20) {{
                                clearInterval(interval);
                            }}
                        }}, 250);
                    }}
                }})();
                """
                try:
                    self.viewer_win.evaluate_js(autofill_js)
                except Exception as e:
                    print(f"Error running autofill script: {e}")

            self.viewer_win.events.loaded += on_loaded

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
