import tkinter as tk
from tkinter import messagebox, ttk
from utils import THEME, FONTS, center_window
from auth import evaluate_password_strength

class LoginWindow:
    def __init__(self, root: tk.Tk, db_manager, on_success_callback):
        self.root = root
        self.db = db_manager
        self.on_success = on_success_callback

        self.root.title("SecureVault – Master Authentication")
        self.root.configure(bg=THEME["bg_main"])
        self.root.resizable(False, False)

        self.is_first_time = not self.db.has_master_password()
        self.show_password = False

        self._build_ui()
        center_window(self.root, 420, 500 if self.is_first_time else 420)

    def _build_ui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        main_card = tk.Frame(
            self.root,
            bg=THEME["bg_card"],
            padx=30,
            pady=30,
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        main_card.pack(fill="both", expand=True, padx=20, pady=20)

        # Header Logo & Title
        header_frame = tk.Frame(main_card, bg=THEME["bg_card"])
        header_frame.pack(fill="x", pady=(0, 20))

        lbl_icon = tk.Label(
            header_frame,
            text="🛡️",
            font=("Segoe UI", 36),
            bg=THEME["bg_card"]
        )
        lbl_icon.pack()

        lbl_title = tk.Label(
            header_frame,
            text="SecureVault",
            font=FONTS["title"],
            bg=THEME["bg_card"],
            fg=THEME["text_dark"]
        )
        lbl_title.pack()

        subtitle_text = "Create a Master Password to secure your vault." if self.is_first_time else "Enter your Master Password to unlock your credentials."
        lbl_sub = tk.Label(
            header_frame,
            text=subtitle_text,
            font=FONTS["body"],
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            wraplength=320,
            justify="center"
        )
        lbl_sub.pack(pady=(5, 0))

        # Form Fields
        form_frame = tk.Frame(main_card, bg=THEME["bg_card"])
        form_frame.pack(fill="x", pady=(0, 15))

        # Master Password Label
        lbl_pwd = tk.Label(
            form_frame,
            text="Master Password",
            font=FONTS["heading"],
            bg=THEME["bg_card"],
            fg=THEME["text_dark"]
        )
        lbl_pwd.pack(anchor="w", pady=(0, 5))

        # Password Entry Container
        pwd_box = tk.Frame(
            form_frame,
            bg=THEME["bg_alt"],
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        pwd_box.pack(fill="x", pady=(0, 10))

        self.entry_pwd = tk.Entry(
            pwd_box,
            show="•",
            font=FONTS["body"],
            bg=THEME["bg_alt"],
            fg=THEME["text_dark"],
            bd=0,
            relief="flat"
        )
        self.entry_pwd.pack(side="left", fill="x", expand=True, px=10, py=8)
        self.entry_pwd.focus()
        self.entry_pwd.bind("<Return>", lambda event: self._on_submit())

        if self.is_first_time:
            self.entry_pwd.bind("<KeyRelease>", self._on_pwd_key_release)

        # Show / Hide Toggle Button
        self.btn_toggle = tk.Button(
            pwd_box,
            text="👁",
            font=FONTS["small"],
            bg=THEME["bg_alt"],
            fg=THEME["text_muted"],
            activebackground=THEME["bg_hover"],
            bd=0,
            cursor="hand2",
            command=self._toggle_pwd_visibility
        )
        self.btn_toggle.pack(side="right", padx=5)

        # First-Time Setup specific widgets: Strength meter & Confirm password
        if self.is_first_time:
            # Strength Indicator Frame
            strength_frame = tk.Frame(form_frame, bg=THEME["bg_card"])
            strength_frame.pack(fill="x", pady=(0, 15))

            self.strength_canvas = tk.Canvas(
                strength_frame,
                height=6,
                bg=THEME["bg_alt"],
                bd=0,
                highlightthickness=0
            )
            self.strength_canvas.pack(fill="x", pady=(0, 3))

            self.lbl_strength = tk.Label(
                strength_frame,
                text="Strength: Empty",
                font=FONTS["small"],
                bg=THEME["bg_card"],
                fg=THEME["text_muted"]
            )
            self.lbl_strength.pack(anchor="w")

            # Confirm Password Field
            lbl_confirm = tk.Label(
                form_frame,
                text="Confirm Master Password",
                font=FONTS["heading"],
                bg=THEME["bg_card"],
                fg=THEME["text_dark"]
            )
            lbl_confirm.pack(anchor="w", pady=(5, 5))

            confirm_box = tk.Frame(
                form_frame,
                bg=THEME["bg_alt"],
                highlightbackground=THEME["border"],
                highlightthickness=1
            )
            confirm_box.pack(fill="x", pady=(0, 10))

            self.entry_confirm = tk.Entry(
                confirm_box,
                show="•",
                font=FONTS["body"],
                bg=THEME["bg_alt"],
                fg=THEME["text_dark"],
                bd=0,
                relief="flat"
            )
            self.entry_confirm.pack(fill="x", px=10, py=8)
            self.entry_confirm.bind("<Return>", lambda event: self._on_submit())

        # Error Message Display Label
        self.lbl_error = tk.Label(
            main_card,
            text="",
            font=FONTS["small"],
            bg=THEME["bg_card"],
            fg=THEME["danger"]
        )
        self.lbl_error.pack(pady=(0, 10))

        # Submit Action Button
        btn_text = "🔒 Set Master Password & Initialize" if self.is_first_time else "🔓 Unlock Vault"
        self.btn_submit = tk.Button(
            main_card,
            text=btn_text,
            font=FONTS["body_bold"],
            bg=THEME["primary"],
            fg="#FFFFFF",
            activebackground=THEME["primary_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._on_submit
        )
        self.btn_submit.pack(fill="x")

    def _toggle_pwd_visibility(self):
        self.show_password = not self.show_password
        show_char = "" if self.show_password else "•"
        self.entry_pwd.config(show=show_char)
        if self.is_first_time:
            self.entry_confirm.config(show=show_char)
        self.btn_toggle.config(text="🙈" if self.show_password else "👁")

    def _on_pwd_key_release(self, event):
        pwd = self.entry_pwd.get()
        score, label, color = evaluate_password_strength(pwd)

        self.strength_canvas.delete("all")
        w = self.strength_canvas.winfo_width()
        if w > 1:
            fill_w = (score / 100.0) * w
            self.strength_canvas.create_rectangle(0, 0, fill_w, 6, fill=color, outline="")

        self.lbl_strength.config(text=f"Strength: {label}", fg=color)

    def _on_submit(self):
        pwd = self.entry_pwd.get()

        if not pwd:
            self.lbl_error.config(text="Please enter your Master Password.")
            return

        if self.is_first_time:
            confirm = self.entry_confirm.get()
            if not confirm:
                self.lbl_error.config(text="Please confirm your Master Password.")
                return
            if pwd != confirm:
                self.lbl_error.config(text="Passwords do not match! Please try again.")
                return
            if len(pwd) < 6:
                self.lbl_error.config(text="Master Password should be at least 6 characters long.")
                return

            # Save master password
            self.db.set_master_password(pwd)
            messagebox.showinfo("Success", "Master Password set successfully! Vault unlocked.")
            self.on_success()

        else:
            # Login verification
            if self.db.verify_master_password(pwd):
                self.lbl_error.config(text="")
                self.on_success()
            else:
                self.lbl_error.config(text="Incorrect Master Password! Access denied.")
                self.entry_pwd.delete(0, tk.END)
                self.entry_pwd.focus()
