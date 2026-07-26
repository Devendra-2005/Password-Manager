# SecureVault – Desktop Password Manager

![SecureVault Logo](assets/logo.png)

**SecureVault** is a secure, modern desktop password management application built with **Python 3**, **Tkinter**, and **SQLite**. It allows users to safely store, manage, generate, and retrieve login credentials for various websites and applications through an intuitive light-themed user interface.

---

## 🌟 Features

- 🔒 **Master Password Authentication**: First-time setup & login authentication protected with salted SHA-256 (PBKDF2 HMAC SHA-256).
- 📊 **Credential Dashboard**: Displays saved accounts in a searchable `ttk.Treeview` table with category filtering.
- ⚡ **Secure Password Generator**: Generates strong random passwords with customizable length (8–32) and character sets (uppercase, lowercase, numbers, special characters).
- 📋 **One-Click Copy**: Instantly copy passwords to the clipboard with visual toast confirmation.
- 🔍 **Real-Time Search & Filtering**: Instant search by website name or username, plus category filtering (Social, Banking, Shopping, Education, Work, Other).
- 🛡️ **Validation & Security**: Prevents empty fields and duplicate entries for the same website and username.
- 🎨 **Modern Light Theme**: Styled UI with cohesive typography, color accents, and responsive layout.

---

## 🛠️ Tech Stack & Required Libraries

- **Python 3.11+**
- **Tkinter** (Standard Library GUI toolkit)
- **SQLite3** (Standard Library relational database)
- **hashlib & secrets** (Standard Library cryptographic utilities)
- **pyperclip** (`>=1.8.2` for cross-platform clipboard copy)
- **Pillow** (`>=9.0.0` for image icon rendering)

---

## 🚀 Installation & Setup

1. **Clone or Download the Repository**:
   ```bash
   git clone https://github.com/yourusername/SecureVault.git
   cd SecureVault
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 How to Run

Launch the application via Python:
```bash
python main.py
```

### Initial Run:
1. When launched for the first time, SecureVault prompts you to create a **Master Password**.
2. Once set, enter your Master Password to unlock the vault dashboard.

---

## 📂 Project Structure

```
SecureVault/
│
├── main.py                # Main application entry point
├── login.py               # Master Password login & setup window
├── dashboard.py           # Dashboard UI with Treeview & CRUD modals
├── database.py            # SQLite database manager & CRUD queries
├── password_generator.py # Password generation logic & dialog UI
├── auth.py                # PBKDF2 HMAC SHA-256 hashing & strength evaluator
├── utils.py               # Theme system, clipboard helper & toast popups
├── requirements.txt       # Project dependencies
├── password_manager.db    # SQLite database (created on runtime)
├── test_app.py            # Backend automated test suite
│
├── assets/
│   ├── logo.png           # App branding logo
│   └── icons/             # Custom icon assets
│
└── README.md              # Documentation
```

---

## 📸 Screenshots Placeholder

| Master Login | Vault Dashboard | Password Generator |
| :---: | :---: | :---: |
| *(Login Screen)* | *(Dashboard Table)* | *(Generator Modal)* |

---

## 🔮 Future Improvements

- 🔑 **AES-256 Master Key Encryption**: Encrypt stored credential passwords at rest using Fernet / AES-256.
- 📤 **Export & Backup**: CSV / JSON encrypted vault export and import.
- ⏰ **Auto-Lock Timer**: Lock the vault automatically after a configurable period of user inactivity.
- 🌐 **Browser Extension Integration**: Auto-fill credentials in web browsers via local API bridge.
