from datetime import date

import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from pages.base import BasePage
from theme import CARD, CARD_ALT, BORDER, PURPLE_DARK, PINK, PURPLE, TEXT, MUTED
from theme import EXPENSE_CATEGORIES
from utils import money


class ReportsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.build()

    def build(self):
        self.heading("Reports", "See where your expenses are going.")
        selector = self.make_card(self)
        selector.pack(fill="x", pady=(20, 14))
        self.label(selector, "Report month", 12, MUTED).pack(side="left", padx=(17, 10), pady=15)

        current = date.today()
        options = []
        for offset in range(12):
            year = current.year
            month = current.month - offset
            while month <= 0:
                month += 12
                year -= 1
            options.append(f"{year:04d}-{month:02d}")
        self.month_var = tk.StringVar(value=current.strftime("%Y-%m"))
        ctk.CTkOptionMenu(
            selector, font=ctk.CTkFont(size=15), variable=self.month_var, values=options, height=34,
            fg_color=CARD_ALT, button_color=PURPLE_DARK,
            button_hover_color="#A789D8", command=self.update_report
        ).pack(side="left", pady=10)
        self.total_label = self.label(selector, "", 11, MUTED)
        self.total_label.pack(side="right", padx=17)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        chart_card = self.make_card(body)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.label(chart_card, "Expenses by category", 15, TEXT, "bold").pack(
            anchor="w", padx=18, pady=(17, 4)
        )
        self.label(chart_card, "Only expense transactions are included.", 11, MUTED).pack(anchor="w", padx=18)
        self.figure = Figure(figsize=(5.2, 4.0), dpi=100, facecolor=CARD)
        self.axis = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        details_card = self.make_card(body)
        details_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.label(details_card, "Category breakdown", 15, TEXT, "bold").pack(
            anchor="w", padx=18, pady=(17, 4)
        )
        self.category_list = ctk.CTkFrame(details_card, fg_color="transparent")
        self.category_list.pack(fill="both", expand=True, padx=16, pady=(8, 15))
        self.update_report(self.month_var.get())

    def update_report(self, selected_month):
        totals = {category: 0.0 for category in EXPENSE_CATEGORIES}
        for row in self.db.fetch_transactions(month=selected_month):
            if row["kind"] == "Expense":
                totals[row["category"]] = totals.get(row["category"], 0.0) + row["amount"]

        total = sum(totals.values())
        self.total_label.configure(text=f"Total expenses: {money(total)}")
        self.axis.clear()
        self.axis.set_facecolor(CARD)
        palette = [PINK, PURPLE, "#A78BFA", "#E9B8D4", "#9D83C6", "#D9C4EA"]
        nonzero = [(name, amount) for name, amount in totals.items() if amount > 0]
        if nonzero:
            labels = [item[0] for item in nonzero]
            values = [item[1] for item in nonzero]
            colors = [palette[EXPENSE_CATEGORIES.index(name) % len(palette)] for name in labels]
            self.axis.pie(
                values, labels=labels, colors=colors, startangle=90,
                autopct="%1.1f%%", pctdistance=0.68,
                textprops={"color": TEXT, "fontsize": 11},
                wedgeprops={"linewidth": 2, "edgecolor": CARD}
            )
            self.axis.axis("equal")
        else:
            self.axis.text(
                0.5, 0.52, "No expenses recorded\nfor this month",
                ha="center", va="center", color=MUTED, fontsize=14,
                transform=self.axis.transAxes
            )
            self.axis.set_xticks([])
            self.axis.set_yticks([])
        self.figure.tight_layout(pad=1.5)
        self.canvas.draw()

        for widget in self.category_list.winfo_children():
            widget.destroy()
        if total == 0:
            self.label(self.category_list, "No spending to break down yet.", 12, MUTED).pack(anchor="w", pady=8)
            return

        for index, category in enumerate(EXPENSE_CATEGORIES):
            amount = totals.get(category, 0.0)
            percent = amount / total * 100
            line = ctk.CTkFrame(self.category_list, fg_color="transparent")
            line.pack(fill="x", pady=10)
            color = palette[index % len(palette)]
            ctk.CTkLabel(line, text="●", text_color=color, font=ctk.CTkFont(size=15)).pack(side="left", padx=(0, 8))
            details = ctk.CTkFrame(line, fg_color="transparent")
            details.pack(side="left", fill="x", expand=True)
            self.label(details, category, 12, TEXT, "bold").pack(anchor="w")
            self.label(details, f"{percent:.1f}% of expenses", 10, MUTED).pack(anchor="w", pady=(2, 0))
            self.label(line, money(amount), 11, TEXT).pack(side="right")
            progress = ctk.CTkProgressBar(
                self.category_list, height=5, fg_color=CARD_ALT, progress_color=color
            )
            progress.pack(fill="x", pady=(0, 4))
            progress.set(percent / 100)
