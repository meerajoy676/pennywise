from tkinter import messagebox

import customtkinter as ctk

from pages.base import BasePage
from theme import BG, PURPLE, PURPLE_DARK, BORDER, TEXT, MUTED, RED


class SettingsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.build()

    def build(self):
        self.heading("Settings", "Set your expected monthly income.")
        settings = self.db.get_settings()

        card = self.make_card(self)
        card.pack(fill="x", pady=(22, 16))
        self.label(card, "Monthly income", 16, TEXT, "bold").pack(
            anchor="w", padx=20, pady=(20, 6)
        )
        self.label(
            card,
            "This is your monthly income target. It is saved on this computer and is not counted as money received.",
            11, MUTED
        ).pack(anchor="w", padx=20, pady=(0, 18))

        fields = ctk.CTkFrame(card, fg_color="transparent")
        fields.pack(fill="x", padx=20, pady=(0, 20))
        self.label(fields, "Expected monthly income (₹)", 12, MUTED).pack(
            anchor="w", pady=(0, 7)
        )
        self.expected_entry = ctk.CTkEntry(
            fields, font=ctk.CTkFont(size=15), height=42, fg_color=BG, border_color=BORDER
        )
        self.expected_entry.pack(fill="x")
        self.expected_entry.insert(0, str(settings["expected_income"]))

        ctk.CTkButton(
            card, text="Save settings", height=40, fg_color=PURPLE,
            hover_color=PURPLE_DARK, text_color="#21182A",
            font=ctk.CTkFont(size=14, weight="bold"), command=self.save
        ).pack(anchor="w", padx=20, pady=(0, 20))

        info = self.make_card(self)
        info.pack(fill="x", pady=(0, 14))
        self.label(info, "How the numbers work", 15, TEXT, "bold").pack(
            anchor="w", padx=20, pady=(18, 10)
        )
        notes = [
            ("Monthly income target", "The amount you expect to receive each month. It is only a target."),
            ("Remaining balance", "All recorded income minus all recorded expenses."),
            ("Monthly totals", "Income and expenses are calculated from transactions dated in that month.")
        ]
        for heading, explanation in notes:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=6)
            self.label(row, heading, 12, PURPLE, "bold").pack(anchor="w")
            self.label(row, explanation, 11, MUTED).pack(anchor="w", pady=(2, 0))
        ctk.CTkFrame(info, height=10, fg_color="transparent").pack()

        reset_card = self.make_card(self)
        reset_card.pack(fill="x", pady=(0, 16))
        self.label(reset_card, "Reset all data", 16, RED, "bold").pack(
            anchor="w", padx=20, pady=(18, 6)
        )
        self.label(
            reset_card,
            "Permanently delete every saved transaction and reset your monthly income target.",
            12, MUTED
        ).pack(anchor="w", padx=20, pady=(0, 14))
        ctk.CTkButton(
            reset_card,
            text="Reset all data",
            height=44,
            fg_color="#713B50",
            hover_color="#8A405E",
            text_color=TEXT,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.reset_all_data
        ).pack(anchor="w", padx=20, pady=(0, 20))

    def save(self):
        try:
            expected = float(self.expected_entry.get().strip())
            if expected < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid monthly income",
                "Enter a valid amount of zero or more.",
                parent=self.app
            )
            return

        # The opening-balance setting is no longer used by the app.
        self.db.save_settings(0, expected)
        messagebox.showinfo(
            "Settings saved", "Your monthly income target has been saved.",
            parent=self.app
        )


    def reset_all_data(self):
        confirmed = messagebox.askyesno(
            "Reset all data?",
            "This will permanently delete all transactions and reset your expected monthly income to ₹0.\n\nThis cannot be undone. Do you want to continue?",
            parent=self.app
        )
        if not confirmed:
            return

        self.db.reset_all_data()
        self.app.show_page("Settings")
