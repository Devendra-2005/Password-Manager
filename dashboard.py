import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict
from utils import THEME, FONTS, copy_to_clipboard, show_toast, center_window
from password_generator import PasswordGeneratorDialog

CATEGORIES = ["Social", "Banking", "Shopping", "Education", "Work", "Other"]

class CredentialDialog(tk.Toplevel):
    """Modal dialog for Adding or Editing a credential."""
    def __init__(self, parent, db_manager, cred_data: Optional[Dict] = None):
        super().__init__(parent)
        self.db = db_manager
        self.cred_data = cred_data
        self.is_edit = cred_data is not None

        self.title("Edit Credential" if self.is_edit else "Add New Credential")
        self.resizable(False, False)
        self.configure(bg=THEME["bg_main"])
        self.transient(parent)
        self.grab_set()

        self.show_password = False

        self._build_ui()
        if self.is_edit:
            self._prefill_data()
        center_window(self, 480, 560)

    def _build_ui(self):
        container = tk.Frame(self, bg=THEME["bg_main"], padx=25, pady=25)
        container.pack(fill="both", expand=True)

        title_text = "✏️ Edit Account Credential" if self.is_edit else "➕ Add New Credential"
        lbl_title = tk.Label(
            container,
            text=title_text,
            font=FONTS["title"],
            bg=THEME["bg_main"],
            fg=THEME["text_dark"]
        )
        lbl_title.pack(anchor="w", pady=(0, 15))

        # Form Card
        form_card = tk.Frame(
            container,
            bg=THEME["bg_card"],
            padx=20,
            pady=20,
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        form_card.pack(fill="both", expand=True, pady=(0, 15))

        # Website
        tk.Label(form_card, text="Website / App Name *", font=FONTS["heading"], bg=THEME["bg_card"], fg=THEME["text_dark"]).pack(anchor="w", pady=(0, 3))
        self.entry_website = tk.Entry(form_card, font=FONTS["body"], bg=THEME["bg_alt"], bd=1, relief="solid")
        self.entry_website.pack(fill="x", ipady=5, pady=(0, 12))

        # Username / Email
        tk.Label(form_card, text="Username or Email *", font=FONTS["heading"], bg=THEME["bg_card"], fg=THEME["text_dark"]).pack(anchor="w", pady=(0, 3))
        self.entry_username = tk.Entry(form_card, font=FONTS["body"], bg=THEME["bg_alt"], bd=1, relief="solid")
        self.entry_username.pack(fill="x", ipady=5, pady=(0, 12))

        # Password
        tk.Label(form_card, text="Password *", font=FONTS["heading"], bg=THEME["bg_card"], fg=THEME["text_dark"]).pack(anchor="w", pady=(0, 3))
        
        pwd_frame = tk.Frame(form_card, bg=THEME["bg_card"])
        pwd_frame.pack(fill="x", pady=(0, 12))

        self.entry_pwd = tk.Entry(pwd_frame, show="•", font=FONTS["body"], bg=THEME["bg_alt"], bd=1, relief="solid")
        self.entry_pwd.pack(side="left", fill="x", expand=True, ipady=5)

        self.btn_toggle_pwd = tk.Button(
            pwd_frame,
            text="👁",
            font=FONTS["small"],
            bg=THEME["bg_alt"],
            fg=THEME["text_muted"],
            bd=1,
            relief="solid",
            cursor="hand2",
            command=self._toggle_pwd
        )
        self.btn_toggle_pwd.pack(side="left", padx=(5, 5), ipady=3)

        btn_gen = tk.Button(
            pwd_frame,
            text="⚡ Generate",
            font=FONTS["small"],
            bg=THEME["accent"],
            fg="#FFFFFF",
            activebackground=THEME["primary"],
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            command=self._open_generator
        )
        btn_gen.pack(side="right", ipady=4, padx=(0, 0))

        # Category
        tk.Label(form_card, text="Category", font=FONTS["heading"], bg=THEME["bg_card"], fg=THEME["text_dark"]).pack(anchor="w", pady=(0, 3))
        self.combo_category = ttk.Combobox(form_card, values=CATEGORIES, state="readonly", font=FONTS["body"])
        self.combo_category.set(CATEGORIES[0])
        self.combo_category.pack(fill="x", ipady=4, pady=(0, 12))

        # Notes (Optional)
        tk.Label(form_card, text="Notes (Optional)", font=FONTS["heading"], bg=THEME["bg_card"], fg=THEME["text_dark"]).pack(anchor="w", pady=(0, 3))
        self.txt_notes = tk.Text(form_card, font=FONTS["body"], bg=THEME["bg_alt"], bd=1, relief="solid", height=3)
        self.txt_notes.pack(fill="x", pady=(0, 10))

        # Error Label
        self.lbl_error = tk.Label(container, text="", font=FONTS["small"], bg=THEME["bg_main"], fg=THEME["danger"])
        self.lbl_error.pack(pady=(0, 10))

        # Action Buttons
        btn_box = tk.Frame(container, bg=THEME["bg_main"])
        btn_box.pack(fill="x")

        btn_cancel = tk.Button(
            btn_box,
            text="Cancel",
            font=FONTS["body_bold"],
            bg=THEME["bg_alt"],
            fg=THEME["text_dark"],
            activebackground=THEME["bg_hover"],
            bd=0,
            pady=8,
            cursor="hand2",
            command=self.destroy
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = tk.Button(
            btn_box,
            text="💾 Save Credential",
            font=FONTS["body_bold"],
            bg=THEME["primary"],
            fg="#FFFFFF",
            activebackground=THEME["primary_hover"],
            bd=0,
            pady=8,
            cursor="hand2",
            command=self._save
        )
        btn_save.pack(side="right", expand=True, fill="x", padx=(5, 0))

    def _toggle_pwd(self):
        self.show_password = not self.show_password
        self.entry_pwd.config(show="" if self.show_password else "•")
        self.btn_toggle_pwd.config(text="🙈" if self.show_password else "👁")

    def _open_generator(self):
        PasswordGeneratorDialog(self, target_entry=self.entry_pwd)

    def _prefill_data(self):
        if not self.cred_data:
            return
        self.entry_website.insert(0, self.cred_data.get("website", ""))
        self.entry_username.insert(0, self.cred_data.get("username", ""))
        self.entry_pwd.insert(0, self.cred_data.get("password", ""))
        cat = self.cred_data.get("category", "Other")
        if cat in CATEGORIES:
            self.combo_category.set(cat)
        else:
            self.combo_category.set("Other")
        notes = self.cred_data.get("notes", "")
        if notes:
            self.txt_notes.insert("1.0", notes)

    def _save(self):
        website = self.entry_website.get()
        username = self.entry_username.get()
        password = self.entry_pwd.get()
        category = self.combo_category.get()
        notes = self.txt_notes.get("1.0", tk.END).strip()

        if self.is_edit:
            cred_id = self.cred_data["id"]
            success, msg = self.db.update_credential(cred_id, website, username, password, category, notes)
        else:
            success, msg = self.db.add_credential(website, username, password, category, notes)

        if success:
            self.destroy()
        else:
            self.lbl_error.config(text=msg)


class DashboardWindow:
    def __init__(self, root: tk.Tk, db_manager, on_logout_callback):
        self.root = root
        self.db = db_manager
        self.on_logout = on_logout_callback

        self.root.title("SecureVault – Desktop Password Manager")
        self.root.configure(bg=THEME["bg_main"])
        self.root.resizable(True, True)

        self._configure_ttk_styles()
        self._build_ui()
        self.load_data()

        center_window(self.root, 950, 620)

    def _configure_ttk_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Treeview styling
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground=THEME["text_dark"],
            fieldbackground="#FFFFFF",
            rowheight=32,
            font=FONTS["body"],
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background=THEME["bg_alt"],
            foreground=THEME["text_dark"],
            font=FONTS["heading"],
            relief="flat",
            padding=6
        )
        style.map(
            "Treeview",
            background=[("selected", THEME["primary"])],
            foreground=[("selected", "#FFFFFF")]
        )

    def _build_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Top Bar
        top_bar = tk.Frame(self.root, bg=THEME["bg_card"], padx=20, pady=12, highlightbackground=THEME["border"], highlightthickness=1)
        top_bar.pack(fill="x")

        # Brand / Title
        brand_frame = tk.Frame(top_bar, bg=THEME["bg_card"])
        brand_frame.pack(side="left")

        lbl_brand_icon = tk.Label(brand_frame, text="🛡️", font=("Segoe UI", 20), bg=THEME["bg_card"])
        lbl_brand_icon.pack(side="left", padx=(0, 8))

        lbl_brand_name = tk.Label(brand_frame, text="SecureVault", font=FONTS["title"], bg=THEME["bg_card"], fg=THEME["text_dark"])
        lbl_brand_name.pack(side="left")

        # Logout Button
        btn_logout = tk.Button(
            top_bar,
            text="🚪 Logout",
            font=FONTS["body_bold"],
            bg=THEME["bg_alt"],
            fg=THEME["text_dark"],
            activebackground=THEME["bg_hover"],
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._logout
        )
        btn_logout.pack(side="right")

        # Content Layout
        content_frame = tk.Frame(self.root, bg=THEME["bg_main"], padx=20, pady=15)
        content_frame.pack(fill="both", expand=True)

        # Control Panel (Search & Category Filter)
        ctrl_card = tk.Frame(content_frame, bg=THEME["bg_card"], padx=15, pady=12, highlightbackground=THEME["border"], highlightthickness=1)
        ctrl_card.pack(fill="x", pady=(0, 15))

        # Search Bar
        lbl_search = tk.Label(ctrl_card, text="🔍 Search:", font=FONTS["body_bold"], bg=THEME["bg_card"], fg=THEME["text_dark"])
        lbl_search.pack(side="left", padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_data())

        self.entry_search = tk.Entry(
            ctrl_card,
            textvariable=self.search_var,
            font=FONTS["body"],
            bg=THEME["bg_alt"],
            fg=THEME["text_dark"],
            bd=1,
            relief="solid",
            width=28
        )
        self.entry_search.pack(side="left", ipady=4, padx=(0, 20))

        # Category Filter
        lbl_cat_filter = tk.Label(ctrl_card, text="Category:", font=FONTS["body_bold"], bg=THEME["bg_card"], fg=THEME["text_dark"])
        lbl_cat_filter.pack(side="left", padx=(0, 8))

        self.category_var = tk.StringVar(value="All")
        cat_options = ["All"] + CATEGORIES
        self.combo_filter = ttk.Combobox(
            ctrl_card,
            textvariable=self.category_var,
            values=cat_options,
            state="readonly",
            font=FONTS["body"],
            width=14
        )
        self.combo_filter.pack(side="left", ipady=2)
        self.combo_filter.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        # Reset Filter Button
        btn_reset = tk.Button(
            ctrl_card,
            text="Clear Filters",
            font=FONTS["small"],
            bg=THEME["bg_alt"],
            fg=THEME["text_muted"],
            activebackground=THEME["bg_hover"],
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._clear_filters
        )
        btn_reset.pack(side="left", padx=(10, 0))

        # Action Buttons Toolbar
        toolbar = tk.Frame(content_frame, bg=THEME["bg_main"])
        toolbar.pack(fill="x", pady=(0, 10))

        btn_add = tk.Button(
            toolbar,
            text="➕ Add Credential",
            font=FONTS["body_bold"],
            bg=THEME["primary"],
            fg="#FFFFFF",
            activebackground=THEME["primary_hover"],
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._add_credential
        )
        btn_add.pack(side="left", padx=(0, 8))

        btn_edit = tk.Button(
            toolbar,
            text="✏️ Edit",
            font=FONTS["body_bold"],
            bg=THEME["secondary"],
            fg="#FFFFFF",
            activebackground=THEME["secondary_hover"],
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._edit_credential
        )
        btn_edit.pack(side="left", padx=(0, 8))

        btn_copy = tk.Button(
            toolbar,
            text="📋 Copy Password",
            font=FONTS["body_bold"],
            bg=THEME["success"],
            fg="#FFFFFF",
            activebackground=THEME["success_hover"],
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._copy_password
        )
        btn_copy.pack(side="left", padx=(0, 8))

        btn_gen = tk.Button(
            toolbar,
            text="⚡ Generator",
            font=FONTS["body_bold"],
            bg=THEME["accent"],
            fg="#FFFFFF",
            activebackground=THEME["primary"],
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._open_generator
        )
        btn_gen.pack(side="left", padx=(0, 8))

        btn_delete = tk.Button(
            toolbar,
            text="🗑️ Delete",
            font=FONTS["body_bold"],
            bg=THEME["danger"],
            fg="#FFFFFF",
            activebackground=THEME["danger_hover"],
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._delete_credential
        )
        btn_delete.pack(side="right")

        # Credentials Table (Treeview inside Card)
        table_card = tk.Frame(content_frame, bg=THEME["bg_card"], highlightbackground=THEME["border"], highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        columns = ("id", "website", "username", "category", "created_at")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("website", text="Website / Application")
        self.tree.heading("username", text="Username / Email")
        self.tree.heading("category", text="Category")
        self.tree.heading("created_at", text="Date Created")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("website", width=240, anchor="w")
        self.tree.column("username", width=240, anchor="w")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("created_at", width=160, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self._edit_credential())

        # Status Bar
        self.status_bar = tk.Frame(self.root, bg=THEME["bg_alt"], padx=15, pady=6)
        self.status_bar.pack(fill="x", side="bottom")

        self.lbl_status_count = tk.Label(self.status_bar, text="0 Credentials", font=FONTS["small"], bg=THEME["bg_alt"], fg=THEME["text_muted"])
        self.lbl_status_count.pack(side="left")

        self.lbl_status_msg = tk.Label(self.status_bar, text="Ready", font=FONTS["small"], bg=THEME["bg_alt"], fg=THEME["text_muted"])
        self.lbl_status_msg.pack(side="right")

    def load_data(self):
        """Loads data from DB matching current search query and category filter."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_var.get().strip()
        cat_filter = self.category_var.get()

        credentials = self.db.search_credentials(query, cat_filter)

        for row in credentials:
            self.tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    row["id"],
                    row["website"],
                    row["username"],
                    row["category"],
                    row["created_at"]
                )
            )

        count = len(credentials)
        self.lbl_status_count.config(text=f"Total: {count} credential{'s' if count != 1 else ''}")

    def _clear_filters(self):
        self.search_var.set("")
        self.category_var.set("All")
        self.load_data()

    def _get_selected_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a credential row first.")
            return None
        return int(selected[0])

    def _add_credential(self):
        dlg = CredentialDialog(self.root, self.db)
        self.root.wait_window(dlg)
        self.load_data()
        self.lbl_status_msg.config(text="Credential added.")

    def _edit_credential(self):
        cred_id = self._get_selected_id()
        if cred_id is None:
            return

        cred_data = self.db.get_credential_by_id(cred_id)
        if cred_data:
            dlg = CredentialDialog(self.root, self.db, cred_data=cred_data)
            self.root.wait_window(dlg)
            self.load_data()
            self.lbl_status_msg.config(text="Credential updated.")

    def _delete_credential(self):
        cred_id = self._get_selected_id()
        if cred_id is None:
            return

        cred_data = self.db.get_credential_by_id(cred_id)
        if not cred_data:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete credential for '{cred_data['website']}' ({cred_data['username']})?",
            icon="warning"
        )
        if confirm:
            self.db.delete_credential(cred_id)
            self.load_data()
            show_toast(self.root, f"Deleted '{cred_data['website']}'", is_success=True)
            self.lbl_status_msg.config(text="Credential deleted.")

    def _copy_password(self):
        cred_id = self._get_selected_id()
        if cred_id is None:
            return

        cred_data = self.db.get_credential_by_id(cred_id)
        if cred_data:
            pwd = cred_data["password"]
            copy_to_clipboard(pwd, self.root)
            show_toast(self.root, f"Password for '{cred_data['website']}' copied to clipboard!", is_success=True)
            self.lbl_status_msg.config(text=f"Password for {cred_data['website']} copied.")

    def _open_generator(self):
        PasswordGeneratorDialog(self.root)

    def _logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to lock SecureVault and logout?")
        if confirm:
            self.on_logout()
