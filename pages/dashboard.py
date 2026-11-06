from datetime import date

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from pages.base import BasePage
from theme import CARD, BORDER, PURPLE, PINK, TEXT, MUTED
from utils import money


class DashboardPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.build()

    def build(self):
        self.heading("Welcome back", "Here is how your money is looking.")
        rows = self.db.fetch_transactions()
        today_text = date.today().strftime("%Y-%m-%d")
        month_text = date.today().strftime("%Y-%m")

        today_spending = sum(
            row["amount"] for row in rows
            if row["kind"] == "Expense" and row["transaction_date"] == today_text
        )
        monthly_income = sum(
            row["amount"] for row in rows
            if row["kind"] == "Income" and row["transaction_date"].startswith(month_text)
        )
        monthly_expenses = sum(
            row["amount"] for row in rows
            if row["kind"] == "Expense" and row["transaction_date"].startswith(month_text)
        )
        settings = self.db.get_settings()
        balance = sum(
            row["amount"] if row["kind"] == "Income" else -row["amount"]
            for row in rows
        )

        summary = ctk.CTkFrame(self, fg_color="transparent")
        summary.pack(fill="x", pady=(22, 16))
        summary.grid_columnconfigure((0, 1, 2), weight=1, uniform="summary")

        card = self.make_card(summary)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkFrame(card, width=4, fg_color=PURPLE, corner_radius=3).pack(
            side="left", fill="y", padx=(0, 14), pady=18
        )
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=(0, 12), pady=18)
        self.label(inner, "Remaining balance", 12, MUTED).pack(anchor="w")
        self.label(inner, money(balance), 23, TEXT, "bold").pack(anchor="w", pady=(8, 4))
        self.label(inner, "Across all recorded transactions", 10, MUTED).pack(anchor="w")

        card = self.make_card(summary)
        card.grid(row=0, column=1, sticky="nsew", padx=5)
        self.label(card, "Monthly income", 12, MUTED).pack(anchor="w", padx=17, pady=(18, 6))
        self.label(card, money(monthly_income), 21, PURPLE, "bold").pack(anchor="w", padx=17)
        self.label(card, "Actual income recorded", 10, MUTED).pack(anchor="w", padx=17, pady=(6, 18))

        card = self.make_card(summary)
        card.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        self.label(card, "Monthly expenses", 12, MUTED).pack(anchor="w", padx=17, pady=(18, 6))
        self.label(card, money(monthly_expenses), 21, PINK, "bold").pack(anchor="w", padx=17)
        self.label(card, f"Today: {money(today_spending)}", 10, MUTED).pack(anchor="w", padx=17, pady=(6, 18))

        lower = ctk.CTkFrame(self, fg_color="transparent")
        lower.pack(fill="both", expand=True, pady=(0, 15))
        lower.grid_columnconfigure(0, weight=3)
        lower.grid_columnconfigure(1, weight=2)

        chart_card = self.make_card(lower)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.label(chart_card, "Income vs expenses", 15, TEXT, "bold").pack(
            anchor="w", padx=18, pady=(17, 0)
        )
        self.label(chart_card, "A monthly comparison", 11, MUTED).pack(
            anchor="w", padx=18, pady=(3, 0)
        )
        figure = Figure(figsize=(5.2, 3.0), dpi=100, facecolor=CARD)
        axis = figure.add_subplot(111)
        axis.set_facecolor(CARD)
        axis.bar(["Income", "Expenses"], [monthly_income, monthly_expenses],
                 color=[PURPLE, PINK], width=0.52)
        axis.tick_params(axis="x", colors=MUTED, labelsize=11)
        axis.tick_params(axis="y", colors=MUTED, labelsize=10)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_color(BORDER)
        axis.spines["bottom"].set_color(BORDER)
        axis.grid(axis="y", color=BORDER, linewidth=0.6, alpha=0.6)
        axis.set_axisbelow(True)
        axis.set_ylabel("Amount (₹)", color=MUTED, fontsize=11)
        figure.tight_layout(pad=1.8)
        canvas = FigureCanvasTkAgg(figure, master=chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 8))

        recent_card = self.make_card(lower)
        recent_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.label(recent_card, "Recent transactions", 15, TEXT, "bold").pack(
            anchor="w", padx=17, pady=(17, 12)
        )
        recent = self.db.fetch_transactions(limit=5)
        if not recent:
            self.label(recent_card, "Nothing here yet.", 12, MUTED).pack(
                anchor="w", padx=17, pady=12
            )
            self.label(recent_card, "Add your first transaction\non the Transactions page.",
                       11, MUTED).pack(anchor="w", padx=17, pady=(0, 18))
        else:
            for row in recent:
                item = ctk.CTkFrame(recent_card, fg_color="transparent")
                item.pack(fill="x", padx=15, pady=6)
                left = ctk.CTkFrame(item, fg_color="transparent")
                left.pack(side="left", fill="x", expand=True)
                self.label(left, row["category"], 12, TEXT, "bold").pack(anchor="w")
                self.label(left, row["transaction_date"], 10, MUTED).pack(anchor="w", pady=(2, 0))
                color = PURPLE if row["kind"] == "Income" else PINK
                sign = "+" if row["kind"] == "Income" else "-"
                self.label(item, f"{sign}{money(row['amount'])}", 11, color, "bold").pack(side="right")

        target_card = self.make_card(self)
        target_card.pack(fill="x", pady=(0, 8))
        self.label(target_card, "Expected monthly income", 12, MUTED).pack(
            side="left", padx=17, pady=15
        )
        self.label(target_card, money(settings["expected_income"]), 13, PURPLE, "bold").pack(
            side="right", padx=17, pady=15
        )
