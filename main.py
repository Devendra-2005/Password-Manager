import os
import sys
import tkinter as tk
from database import DatabaseManager
from login import LoginWindow
from dashboard import DashboardWindow

class SecureVaultApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SecureVault – Password Manager")

        # Initialize SQLite database
        self.db = DatabaseManager()

        # Try setting window icon if present
        self._set_icon()

        # Start with Login screen
        self.show_login()

    def _set_icon(self):
        icon_path = os.path.join("assets", "logo.png")
        if os.path.exists(icon_path):
            try:
                img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, img)
            except Exception as e:
                print(f"Could not load icon: {e}")

    def show_login(self):
        # Initialize Login View
        LoginWindow(
            root=self.root,
            db_manager=self.db,
            on_success_callback=self.show_dashboard
        )

    def show_dashboard(self):
        # Initialize Dashboard View
        DashboardWindow(
            root=self.root,
            db_manager=self.db,
            on_logout_callback=self.show_login
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SecureVaultApp()
    app.run()
