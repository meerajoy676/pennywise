import customtkinter as ctk

from theme import BG, CARD, BORDER, TEXT, MUTED


class BasePage(ctk.CTkScrollableFrame):
    """Common page helpers and layout for each separate app screen."""

    def __init__(self, parent, app):
        super().__init__(
            parent, fg_color=BG, corner_radius=0,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color="#8F70C8"
        )
        self.app = app
        self.db = app.db

    def make_card(self, parent, **kwargs):
        return ctk.CTkFrame(
            parent, fg_color=CARD, corner_radius=16,
            border_width=1, border_color=BORDER, **kwargs
        )

    def label(self, parent, text, size=13, color=TEXT, weight="normal"):
        return ctk.CTkLabel(
            parent, text=text, text_color=color,
            font=ctk.CTkFont(size=size + 2, weight=weight)
        )

    def heading(self, title, subtitle):
        self.label(self, title, 27, TEXT, "bold").pack(anchor="w")
        self.label(self, subtitle, 12, MUTED).pack(anchor="w", pady=(4, 0))
