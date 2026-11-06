import calendar
from datetime import date, datetime

import customtkinter as ctk

from theme import BG, CARD, CARD_ALT, BORDER, PURPLE_DARK, PINK, TEXT, MUTED


class CalendarPopup(ctk.CTkToplevel):
    """A simple date picker built with CustomTkinter."""

    def __init__(self, parent, initial_date, on_select):
        super().__init__(parent)
        self.title("Choose a date")
        self.geometry("320x330")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.transient(parent)
        self.grab_set()

        try:
            self.current = datetime.strptime(initial_date, "%Y-%m-%d").date()
        except ValueError:
            self.current = date.today()

        self.on_select = on_select
        self.year = self.current.year
        self.month = self.current.month
        self.calendar_area = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14)
        self.calendar_area.pack(fill="both", expand=True, padx=12, pady=12)
        self.draw_calendar()

    def change_month(self, amount):
        self.month += amount
        if self.month < 1:
            self.month = 12
            self.year -= 1
        elif self.month > 12:
            self.month = 1
            self.year += 1
        self.draw_calendar()

    def draw_calendar(self):
        for widget in self.calendar_area.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.calendar_area, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(10, 6))
        ctk.CTkButton(
            header, text="<", width=38, height=34,
            fg_color=CARD_ALT, hover_color=BORDER,
            font=ctk.CTkFont(size=14),
            command=lambda: self.change_month(-1)
        ).pack(side="left")
        ctk.CTkLabel(
            header, text=f"{calendar.month_name[self.month]} {self.year}",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT
        ).pack(side="left", expand=True)
        ctk.CTkButton(
            header, text=">", width=38, height=34,
            fg_color=CARD_ALT, hover_color=BORDER,
            font=ctk.CTkFont(size=14),
            command=lambda: self.change_month(1)
        ).pack(side="right")

        grid = ctk.CTkFrame(self.calendar_area, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        for column, day_name in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            ctk.CTkLabel(
                grid, text=day_name, text_color=MUTED,
                font=ctk.CTkFont(size=13, weight="bold")
            ).grid(row=0, column=column, padx=1, pady=3, sticky="nsew")

        for row_index, week in enumerate(calendar.monthcalendar(self.year, self.month), start=1):
            for column, day_number in enumerate(week):
                if day_number == 0:
                    continue
                chosen = (
                    self.year == self.current.year
                    and self.month == self.current.month
                    and day_number == self.current.day
                )
                today = (
                    self.year == date.today().year
                    and self.month == date.today().month
                    and day_number == date.today().day
                )
                ctk.CTkButton(
                    grid, text=str(day_number), width=36, height=32,
                    corner_radius=7,
                    fg_color=PINK if chosen else (CARD_ALT if today else CARD),
                    hover_color=PURPLE_DARK,
                    text_color=BG if chosen else TEXT,
                    font=ctk.CTkFont(size=14),
                    command=lambda d=day_number: self.pick_day(d)
                ).grid(row=row_index, column=column, padx=1, pady=1)

        for column in range(7):
            grid.grid_columnconfigure(column, weight=1)

        ctk.CTkButton(
            self.calendar_area, text="Today", height=34,
            fg_color=CARD_ALT, hover_color=BORDER,
            font=ctk.CTkFont(size=14),
            command=lambda: self.pick_day(date.today().day, today=True)
        ).pack(fill="x", padx=12, pady=(0, 10))

    def pick_day(self, day_number, today=False):
        selected = date.today() if today else date(self.year, self.month, day_number)
        self.on_select(selected.strftime("%Y-%m-%d"))
        self.destroy()
