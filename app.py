import tkinter as tk
from datetime import date

import customtkinter as ctk
from tkinter import ttk

from database import FinanceDatabase
from pages.dashboard import DashboardPage
from pages.transactions import TransactionsPage
from pages.reports import ReportsPage
from pages.settings_page import SettingsPage
from theme import BG, SIDEBAR, CARD, CARD_ALT, BORDER, PINK, PINK_BRIGHT, PURPLE, TEXT, MUTED


class PennywiseApp(ctk.CTk):
    """Main window, sidebar navigation, and page switching."""

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Pennywise | Personal Finance Manager")
        self.geometry("1200x780")
        self.minsize(1000, 680)
        self.configure(fg_color=BG)

        self.db = FinanceDatabase()
        self.pages = {}
        self.setup_treeview_style()
        self.build_layout()
        self.show_page("Dashboard")
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def setup_treeview_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Pennywise.Treeview", background=CARD, fieldbackground=CARD,
            foreground=TEXT, rowheight=64, borderwidth=0,
            font=("Segoe UI", 18)
        )
        style.configure(
            "Pennywise.Treeview.Heading", background=CARD_ALT,
            foreground=PURPLE, relief="flat", font=("Segoe UI", 16, "bold")
        )
        style.map("Pennywise.Treeview", background=[("selected", "#59416C")],
                  foreground=[("selected", TEXT)])
        style.map("Pennywise.Treeview.Heading", background=[("active", BORDER)])

    def build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=SIDEBAR, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(28, 36))
        ctk.CTkLabel(brand, text="✿", text_color=PINK, font=ctk.CTkFont(size=31, weight="bold")).pack(side="left", padx=(0, 10))
        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left")
        ctk.CTkLabel(brand_text, text="Pennywise", text_color=TEXT, font=ctk.CTkFont(size=21, weight="bold")).pack(anchor="w")

        self.nav_buttons = {}
        for page_name, symbol in [
            ("Dashboard", "⌂"), ("Transactions", "↕"),
            ("Reports", "◔"), ("Settings", "⚙")
        ]:
            button = ctk.CTkButton(
                self.sidebar, text=f"  {symbol}     {page_name}", anchor="w",
                height=44, corner_radius=10, font=ctk.CTkFont(size=15),
                fg_color="transparent", hover_color=CARD_ALT, text_color=MUTED,
                command=lambda name=page_name: self.show_page(name)
            )
            button.pack(fill="x", padx=13, pady=4)
            self.nav_buttons[page_name] = button

        main_area = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        main_area.pack(side="left", fill="both", expand=True)
        topbar = ctk.CTkFrame(main_area, height=66, fg_color=BG, corner_radius=0)
        topbar.pack(fill="x", padx=30, pady=(15, 0))
        topbar.pack_propagate(False)
        self.page_title = ctk.CTkLabel(
            topbar, text="Dashboard", text_color=TEXT,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.page_title.pack(side="left", anchor="center")
        ctk.CTkLabel(
            topbar, text=date.today().strftime("%A, %d %B %Y"),
            text_color=MUTED, font=ctk.CTkFont(size=13)
        ).pack(side="right", anchor="center")

        self.page_host = ctk.CTkFrame(main_area, fg_color=BG, corner_radius=0)
        self.page_host.pack(fill="both", expand=True, padx=30, pady=(8, 24))

    def show_page(self, page_name):
        self.page_title.configure(text=page_name)
        for name, button in self.nav_buttons.items():
            if name == page_name:
                button.configure(
                    fg_color="#493452", text_color=PINK_BRIGHT,
                    font=ctk.CTkFont(size=15, weight="bold")
                )
            else:
                button.configure(
                    fg_color="transparent", text_color=MUTED,
                    font=ctk.CTkFont(size=15, weight="normal")
                )

        # Rebuild the selected page so its totals always reflect current data.
        for widget in self.page_host.winfo_children():
            widget.destroy()
        page_classes = {
            "Dashboard": DashboardPage,
            "Transactions": TransactionsPage,
            "Reports": ReportsPage,
            "Settings": SettingsPage
        }
        page = page_classes[page_name](self.page_host, self)
        page.pack(fill="both", expand=True)
        self.pages[page_name] = page

    def close_app(self):
        self.db.close()
        self.destroy()
