import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import customtkinter as ctk

from pages.base import BasePage
from theme import BG, CARD, CARD_ALT, BORDER, PINK, PURPLE_DARK, TEXT, MUTED
from theme import EXPENSE_CATEGORIES, INCOME_CATEGORIES
from utils import money, valid_date
from widgets.calendar_popup import CalendarPopup


class TransactionsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.build()

    def build(self):
        self.heading("Transactions", "Record income and expenses in one place.")
        form_card = self.make_card(self)
        form_card.pack(fill="x", pady=(20, 16))
        self.label(form_card, "Add a transaction", 16, TEXT, "bold").pack(
            anchor="w", padx=18, pady=(17, 12)
        )

        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="x", padx=18, pady=(0, 18))
        form.grid_columnconfigure((0, 1, 2), weight=1, uniform="form")
        for col, text in enumerate(["Type", "Amount (₹)", "Category"]):
            self.label(form, text, 11, MUTED).grid(
                row=0, column=col, sticky="w", padx=(0 if col == 0 else 10, 0), pady=(0, 6)
            )

        self.kind_var = tk.StringVar(value="Expense")
        self.category_var = tk.StringVar(value=EXPENSE_CATEGORIES[0])
        self.kind_menu = ctk.CTkOptionMenu(
            form, font=ctk.CTkFont(size=15), variable=self.kind_var, values=["Expense", "Income"], height=36,
            fg_color=CARD_ALT, button_color=PURPLE_DARK,
            button_hover_color="#A789D8", text_color=TEXT,
            command=self.change_type
        )
        self.kind_menu.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.amount_entry = ctk.CTkEntry(
            form, font=ctk.CTkFont(size=15), placeholder_text="e.g. 250.00", height=36,
            fg_color=BG, border_color=BORDER
        )
        self.amount_entry.grid(row=1, column=1, sticky="ew", padx=10)
        self.category_menu = ctk.CTkOptionMenu(
            form, font=ctk.CTkFont(size=15), variable=self.category_var, values=EXPENSE_CATEGORIES,
            height=36, fg_color=CARD_ALT, button_color=PURPLE_DARK,
            button_hover_color="#A789D8", text_color=TEXT
        )
        self.category_menu.grid(row=1, column=2, sticky="ew", padx=(10, 0))

        self.label(form, "Date", 11, MUTED).grid(row=2, column=0, sticky="w", pady=(14, 6))
        self.label(form, "Description (optional)", 11, MUTED).grid(
            row=2, column=1, columnspan=2, sticky="w", padx=10, pady=(14, 6)
        )
        date_frame = ctk.CTkFrame(form, fg_color="transparent")
        date_frame.grid(row=3, column=0, sticky="ew", padx=(0, 10))
        date_frame.grid_columnconfigure(0, weight=1)
        self.date_entry = ctk.CTkEntry(
            date_frame, font=ctk.CTkFont(size=15), height=36, fg_color=BG, border_color=BORDER,
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            date_frame, text="▦", width=38, height=36,
            fg_color=CARD_ALT, hover_color=BORDER, command=self.open_calendar
        ).grid(row=0, column=1)
        self.description_entry = ctk.CTkEntry(
            form, font=ctk.CTkFont(size=15), placeholder_text="What was it for?", height=36,
            fg_color=BG, border_color=BORDER
        )
        self.description_entry.grid(row=3, column=1, columnspan=2, sticky="ew", padx=10)

        actions = ctk.CTkFrame(form_card, fg_color="transparent")
        actions.pack(fill="x", padx=18, pady=(0, 17))
        ctk.CTkButton(
            actions, text="＋  Add transaction", height=38,
            fg_color=PINK, hover_color="#D989B8", text_color="#271A2B",
            font=ctk.CTkFont(size=14, weight="bold"), command=self.save_transaction
        ).pack(side="left")
        table_card = self.make_card(self)
        table_card.pack(fill="both", expand=True)
        header = ctk.CTkFrame(table_card, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(16, 10))
        self.label(header, "All transactions", 15, TEXT, "bold").pack(side="left")
        columns = ("date", "type", "category", "description", "amount")
        self.tree = ttk.Treeview(
            table_card, columns=columns, show="headings",
            style="Pennywise.Treeview", selectmode="browse", height=13
        )
        headings = {
            "date": ("Date", 135), "type": ("Type", 110),
            "category": ("Category", 165), "description": ("Description", 320),
            "amount": ("Amount", 155)
        }
        for col, (heading, width) in headings.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=65,
                             anchor="e" if col == "amount" else "w",
                             stretch=(col == "description"))
        self.tree.tag_configure("Income", foreground="#C7A8FF")
        self.tree.tag_configure("Expense", foreground="#F0A5D0")
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(14, 0), pady=(0, 14))
        scrollbar.pack(side="right", fill="y", padx=(0, 14), pady=(0, 14))
        self.refresh_table()

    def change_type(self, new_type):
        categories = INCOME_CATEGORIES if new_type == "Income" else EXPENSE_CATEGORIES
        self.category_menu.configure(values=categories)
        self.category_var.set(categories[0])

    def open_calendar(self):
        CalendarPopup(self.app, self.date_entry.get(), self.set_date)

    def set_date(self, selected_date):
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, selected_date)

    def save_transaction(self):
        try:
            amount = float(self.amount_entry.get().strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter an amount greater than zero.", parent=self.app)
            return

        transaction_date = self.date_entry.get().strip()
        if not valid_date(transaction_date):
            messagebox.showerror("Invalid date", "Choose a valid date using YYYY-MM-DD.", parent=self.app)
            return

        self.db.add_transaction(
            self.kind_var.get(), amount, self.category_var.get(),
            self.description_entry.get().strip(), transaction_date
        )
        self.amount_entry.delete(0, "end")
        self.description_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.db.fetch_transactions():
            sign = "+" if row["kind"] == "Income" else "-"
            self.tree.insert(
                "", "end", iid=str(row["id"]),
                values=(row["transaction_date"], row["kind"], row["category"],
                        row["description"] or "-", f"{sign}{money(row['amount'])}"),
                tags=(row["kind"],)
            )

