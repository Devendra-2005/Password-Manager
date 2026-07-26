import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox
from utils import THEME, FONTS, copy_to_clipboard, show_toast, center_window

def generate_password(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True
) -> str:
    """
    Generates a cryptographically strong random password using secrets module.
    Guarantees at least one character from each selected category.
    """
    length = max(8, min(32, length))
    
    pools = []
    guaranteed = []

    if use_upper:
        pools.append(string.ascii_uppercase)
        guaranteed.append(secrets.choice(string.ascii_uppercase))
    if use_lower:
        pools.append(string.ascii_lowercase)
        guaranteed.append(secrets.choice(string.ascii_lowercase))
    if use_digits:
        pools.append(string.digits)
        guaranteed.append(secrets.choice(string.digits))
    if use_symbols:
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        pools.append(symbols)
        guaranteed.append(secrets.choice(symbols))

    if not pools:
        # Default fallback if nothing selected
        pools = [string.ascii_letters + string.digits]
        guaranteed = [secrets.choice(string.ascii_letters)]

    combined = "".join(pools)
    remaining_length = length - len(guaranteed)
    
    random_chars = [secrets.choice(combined) for _ in range(remaining_length)]
    full_list = guaranteed + random_chars
    
    # Shuffle cryptographically using system randomness
    secrets.SystemRandom().shuffle(full_list)
    return "".join(full_list)


class PasswordGeneratorDialog(tk.Toplevel):
    def __init__(self, parent, target_entry=None):
        super().__init__(parent)
        self.title("Secure Password Generator")
        self.target_entry = target_entry
        self.resizable(False, False)
        self.configure(bg=THEME["bg_main"])
        self.transient(parent)
        self.grab_set()

        # Variables
        self.length_var = tk.IntVar(value=16)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.password_var = tk.StringVar()

        self._build_ui()
        self._generate()
        center_window(self, 440, 420)

    def _build_ui(self):
        main_frame = tk.Frame(self, bg=THEME["bg_main"], padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Header
        lbl_title = tk.Label(
            main_frame,
            text="⚡ Password Generator",
            font=FONTS["title"],
            bg=THEME["bg_main"],
            fg=THEME["text_dark"]
        )
        lbl_title.pack(anchor="w", pady=(0, 15))

        # Result Card
        res_card = tk.Frame(
            main_frame,
            bg=THEME["bg_card"],
            padx=15,
            pady=15,
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        res_card.pack(fill="x", pady=(0, 15))

        self.pwd_entry = tk.Entry(
            res_card,
            textvariable=self.password_var,
            font=FONTS["mono_bold"],
            bg=THEME["bg_alt"],
            fg=THEME["primary"],
            bd=1,
            relief="solid",
            justify="center",
            state="readonly"
        )
        self.pwd_entry.pack(fill="x", ipady=6, pady=(0, 10))

        # Generator Action Buttons inside Card
        btn_box = tk.Frame(res_card, bg=THEME["bg_card"])
        btn_box.pack(fill="x")

        btn_regen = tk.Button(
            btn_box,
            text="🔄 Regenerate",
            font=FONTS["body_bold"],
            bg=THEME["bg_alt"],
            fg=THEME["text_dark"],
            activebackground=THEME["bg_hover"],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._generate
        )
        btn_regen.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_copy = tk.Button(
            btn_box,
            text="📋 Copy to Clipboard",
            font=FONTS["body_bold"],
            bg=THEME["primary"],
            fg="#FFFFFF",
            activebackground=THEME["primary_hover"],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._copy_and_notify
        )
        btn_copy.pack(side="right", expand=True, fill="x", padx=(5, 0))

        # Controls Card
        ctrl_card = tk.Frame(
            main_frame,
            bg=THEME["bg_card"],
            padx=15,
            pady=15,
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        ctrl_card.pack(fill="x", pady=(0, 15))

        # Length Slider
        len_frame = tk.Frame(ctrl_card, bg=THEME["bg_card"])
        len_frame.pack(fill="x", pady=(0, 10))

        lbl_len = tk.Label(
            len_frame,
            text="Password Length:",
            font=FONTS["body_bold"],
            bg=THEME["bg_card"],
            fg=THEME["text_dark"]
        )
        lbl_len.pack(side="left")

        self.lbl_len_val = tk.Label(
            len_frame,
            text="16",
            font=FONTS["body_bold"],
            bg=THEME["bg_card"],
            fg=THEME["primary"]
        )
        self.lbl_len_val.pack(side="right")

        slider = ttk.Scale(
            ctrl_card,
            from_=8,
            to=32,
            variable=self.length_var,
            orient="horizontal",
            command=self._on_slider_change
        )
        slider.pack(fill="x", pady=(0, 15))

        # Checkbox Options
        opts_frame = tk.Frame(ctrl_card, bg=THEME["bg_card"])
        opts_frame.pack(fill="x")

        cb_upper = tk.Checkbutton(
            opts_frame,
            text="Uppercase (A-Z)",
            variable=self.upper_var,
            font=FONTS["body"],
            bg=THEME["bg_card"],
            activebackground=THEME["bg_card"],
            command=self._generate
        )
        cb_upper.grid(row=0, column=0, sticky="w", pady=2, padx=(0, 15))

        cb_lower = tk.Checkbutton(
            opts_frame,
            text="Lowercase (a-z)",
            variable=self.lower_var,
            font=FONTS["body"],
            bg=THEME["bg_card"],
            activebackground=THEME["bg_card"],
            command=self._generate
        )
        cb_lower.grid(row=0, column=1, sticky="w", pady=2)

        cb_digits = tk.Checkbutton(
            opts_frame,
            text="Numbers (0-9)",
            variable=self.digits_var,
            font=FONTS["body"],
            bg=THEME["bg_card"],
            activebackground=THEME["bg_card"],
            command=self._generate
        )
        cb_digits.grid(row=1, column=0, sticky="w", pady=2, padx=(0, 15))

        cb_symbols = tk.Checkbutton(
            opts_frame,
            text="Special (!@#$)",
            variable=self.symbols_var,
            font=FONTS["body"],
            bg=THEME["bg_card"],
            activebackground=THEME["bg_card"],
            command=self._generate
        )
        cb_symbols.grid(row=1, column=1, sticky="w", pady=2)

        # Apply / Fill Button (if called from Add/Edit credential form)
        if self.target_entry is not None:
            btn_use = tk.Button(
                main_frame,
                text="✓ Use This Password",
                font=FONTS["body_bold"],
                bg=THEME["success"],
                fg="#FFFFFF",
                activebackground=THEME["success_hover"],
                bd=0,
                pady=8,
                cursor="hand2",
                command=self._use_password
            )
            btn_use.pack(fill="x")

    def _on_slider_change(self, val):
        length = int(float(val))
        self.lbl_len_val.config(text=str(length))
        self._generate()

    def _generate(self):
        pwd = generate_password(
            length=self.length_var.get(),
            use_upper=self.upper_var.get(),
            use_lower=self.lower_var.get(),
            use_digits=self.digits_var.get(),
            use_symbols=self.symbols_var.get()
        )
        self.password_var.set(pwd)

    def _copy_and_notify(self):
        pwd = self.password_var.get()
        if pwd:
            copy_to_clipboard(pwd, self)
            show_toast(self, "Generated password copied to clipboard!", is_success=True)

    def _use_password(self):
        pwd = self.password_var.get()
        if self.target_entry is not None and pwd:
            if isinstance(self.target_entry, tk.StringVar):
                self.target_entry.set(pwd)
            elif hasattr(self.target_entry, 'delete'):
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, pwd)
        self.destroy()
