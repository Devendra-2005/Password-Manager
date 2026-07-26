import os
import tkinter as tk
from tkinter import messagebox
import pyperclip

# Modern Light Theme Color Palette & Design System
THEME = {
    "bg_main": "#F8FAFC",        # Slate 50 - Main background
    "bg_card": "#FFFFFF",        # White - Card & Container background
    "bg_alt": "#F1F5F9",         # Slate 100 - Secondary background
    "bg_hover": "#E2E8F0",       # Slate 200 - Hover highlight
    "primary": "#2563EB",        # Blue 600 - Primary action color
    "primary_hover": "#1D4ED8",  # Blue 700 - Primary hover
    "secondary": "#475569",      # Slate 600 - Secondary button
    "secondary_hover": "#334155",# Slate 700 - Secondary hover
    "success": "#10B981",        # Emerald 500 - Success status
    "success_hover": "#059669",  # Emerald 600 - Success hover
    "danger": "#EF4444",         # Red 500 - Danger / Delete
    "danger_hover": "#DC2626",   # Red 600 - Danger hover
    "accent": "#0EA5E9",         # Sky 500 - Accent highlight
    "text_dark": "#0F172A",      # Slate 900 - Primary text
    "text_muted": "#64748B",     # Slate 500 - Secondary text
    "text_light": "#F8FAFC",     # Light text on dark bg
    "border": "#E2E8F0",         # Slate 200 - Border line
    "border_focus": "#3B82F6",   # Blue 500 - Focused field border
    "categories": {
        "Social": "#3B82F6",
        "Banking": "#10B981",
        "Shopping": "#F59E0B",
        "Education": "#8B5CF6",
        "Work": "#6366F1",
        "Other": "#64748B"
    }
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "subtitle": ("Segoe UI", 13, "bold"),
    "heading": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "mono": ("Consolas", 10),
    "mono_bold": ("Consolas", 11, "bold")
}

def copy_to_clipboard(text: str, root_window=None) -> bool:
    """
    Copies text to clipboard using pyperclip with a fallback to Tkinter clipboard.
    Returns True if successful, False otherwise.
    """
    if not text:
        return False

    copied = False
    try:
        pyperclip.copy(text)
        copied = True
    except Exception:
        # Fallback to native Tkinter clipboard if pyperclip fails or backend missing
        if root_window:
            try:
                root_window.clipboard_clear()
                root_window.clipboard_append(text)
                root_window.update()
                copied = True
            except Exception as e:
                print(f"Clipboard fallback error: {e}")
                copied = False
    return copied

def show_toast(parent, message: str, duration_ms: int = 2500, is_success: bool = True):
    """
    Displays a floating non-modal toast message at the bottom center of the parent window.
    """
    toast = tk.Toplevel(parent)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)

    bg_color = THEME["success"] if is_success else THEME["danger"]
    fg_color = "#FFFFFF"

    container = tk.Frame(
        toast,
        bg=bg_color,
        padx=16,
        pady=8,
        highlightbackground="#FFFFFF",
        highlightthickness=1
    )
    container.pack(fill="both", expand=True)

    icon_str = "✓  " if is_success else "⚠  "
    lbl = tk.Label(
        container,
        text=f"{icon_str}{message}",
        font=FONTS["body_bold"],
        bg=bg_color,
        fg=fg_color
    )
    lbl.pack()

    # Position at bottom center of parent
    parent.update_idletasks()
    p_x = parent.winfo_rootx()
    p_y = parent.winfo_rooty()
    p_w = parent.winfo_width()
    p_h = parent.winfo_height()

    req_w = toast.winfo_reqwidth()
    req_h = toast.winfo_reqheight()

    pos_x = p_x + (p_w - req_w) // 2
    pos_y = p_y + p_h - req_h - 40

    toast.geometry(f"+{pos_x}+{pos_y}")

    # Fade out / destroy after duration
    toast.after(duration_ms, toast.destroy)

def center_window(window, width: int, height: int):
    """
    Centers a Tkinter window on the screen.
    """
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
