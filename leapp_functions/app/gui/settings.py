"""
The Settings window.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from leapp_functions import leapp
from leapp_functions.app import history
from leapp_functions.app.gui import themes
from leapp_functions.app.gui.custom_widgets import GAP, MARGIN, Caption, Card, OutlineButton

BUTTON_GAP = 8
APPEARANCES = (("dark", "Dark"), ("light", "Light"))
HISTORY_TEXT = "Enable saving paths as recent history"
HISTORY_HINT = ("Recent extraction and output paths are shared by every LEAPP tool. Each finished "
                "run is also recorded under this tool's name, for LAVA to list on its welcome "
                "screen.")


class SettingsControl:
    """ Opens the Settings window, and keeps it with the main window while it is open. """

    def __init__(self, app):
        self.app = app
        self.window = None
        app.bind("<Map>", self.on_minimize)
        app.bind("<Unmap>", self.on_minimize)
        app.bind("<Activate>", self.on_activate)
        app.bind("<<OpenSettings>>", lambda _event: self.open())

    def opened(self):
        """ The Settings window if it is open. """
        if self.window is not None and self.window.winfo_exists():
            return self.window
        return None

    def open(self):
        """ Open the Settings window, or bring it to the front if it is already open. """
        window = self.opened()
        if window is not None:
            window.lift()
            window.focus_set()
        else:
            self.window = SettingsWindow(self)

    def change_appearance(self, name):
        """ Save the appearance chosen and build both windows again in its colours. """
        history.set_appearance(leapp.name.lower(), name)
        self.app.appearance.use(name)
        window = self.opened()
        position = None
        if window is not None:
            position = "+" + window.geometry().split("+", 1)[1]
            window.destroy()
        self.app.build()
        self.window = SettingsWindow(self, position)

    def on_minimize(self, event):
        """ The main window has been minimised or brought back: the Settings window follows it. """
        window = self.opened()
        if event.widget is self.app and window is not None:
            window.follow(event.type == tk.EventType.Map)

    def on_activate(self, event):
        """ The system has made the main window the active one when it comes back.
        While the Settings window is open, it is the one that must stay active. """
        window = self.opened()
        if event.widget is self.app and window is not None:
            window.focus_force()


class SettingsWindow(tk.Toplevel):
    """ The settings, in a window of its own above the main one. The main window cannot be used
    while it is open. """

    def __init__(self, control, position=None):
        app = control.app
        super().__init__(app, bg=app.colors.main_bg)
        self.withdraw()  # hidden while it is built, so that it does not appear in a corner first
        self.app = app
        self.control = control
        self.title("Settings")
        self.resizable(False, False)
        self.transient(app)
        themes.title_bar(self, app.appearance.is_dark)

        self.appearance = tk.StringVar(self, value=app.appearance.name)
        self.build_appearance()
        self.history_enabled = tk.BooleanVar(self, value=history.is_history_enabled())
        self.clear_buttons = self.build_history()
        self.refresh_clear_buttons()

        close = OutlineButton(self, app, text="Close", command=self.destroy)
        close.pack(anchor="e", padx=MARGIN, pady=(GAP, MARGIN))
        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Map>", self.on_map)

        if position is None:
            self.place_over(app)
        else:
            self.geometry(position)
        self.deiconify()

    def on_map(self, event):
        """ The window is on screen, the first time or after the main window comes back: it takes
        the keyboard and the mouse from the main window again. """
        if event.widget is self:
            self.grab_set()
            self.focus_set()

    def follow(self, shown):
        """ Hide the window while the main window is minimised, show it again when it comes
        back. """
        if shown:
            self.deiconify()
        else:
            self.withdraw()

    def build_appearance(self):
        """ The card to choose the colours of the windows. """
        card = Card(self, self.app, "APPEARANCE")
        card.pack(fill="x", padx=MARGIN, pady=(MARGIN, 0))
        for row, (name, text) in enumerate(APPEARANCES):
            ttk.Radiobutton(card.body, text=text, value=name, variable=self.appearance,
                            style="Card.TRadiobutton",
                            command=self.choose_appearance).pack(anchor="w",
                                                                 pady=(4 if row else 0, 0))

    def choose_appearance(self):
        """ A radio button has been clicked. """
        name = self.appearance.get()
        if name != self.app.appearance.name:
            self.app.after_idle(self.control.change_appearance, name)

    def build_history(self):
        """ The card for the history of paths shared by the LEAPPs. Returns its two Clear buttons,
        the one for this LEAPP first. """
        card = Card(self, self.app, "HISTORY")
        card.pack(fill="x", padx=MARGIN, pady=(GAP, 0))
        ttk.Checkbutton(card.body, text=HISTORY_TEXT, style="Card.TCheckbutton",
                        variable=self.history_enabled,
                        command=self.save_history_enabled).pack(anchor="w", pady=(4, 0))
        Caption(card.body, self.app, HISTORY_HINT, card.background).pack(fill="x", pady=(4, 0))

        line = tk.Frame(card.body, bg=card.background)
        line.pack(anchor="w", pady=(GAP, 0))
        leapp_button = OutlineButton(line, self.app, style="in_card",
                                     text=f"Clear {leapp.name} History",
                                     command=self.clear_leapp_history)
        leapp_button.pack(side="left")
        all_button = OutlineButton(line, self.app, style="in_card", text="Clear All History",
                                   command=self.clear_all_history)
        all_button.pack(side="left", padx=(BUTTON_GAP, 0))
        return leapp_button, all_button

    def refresh_clear_buttons(self):
        """ A Clear button can be used only when there is something for it to clear. """
        leapp_button, all_button = self.clear_buttons
        leapp_button.set_enabled(history.has_single_leapp_history(leapp.name.lower()))
        all_button.set_enabled(history.has_history())

    def save_history_enabled(self):
        """ The check box has been clicked: the setting is saved at once. """
        history.set_history_enabled(self.history_enabled.get())

    def clear_leapp_history(self):
        """ Clear the paths shared by the LEAPPs and this LEAPP's recent runs, once confirmed. """
        if messagebox.askyesno(
                f"Clear {leapp.name} history",
                f"Clear shared recent input/output paths and {leapp.name} recent run entries?",
                parent=self):
            history.clear_single_leapp_history(leapp.name.lower())
            self.refresh_clear_buttons()

    def clear_all_history(self):
        """ Clear the whole history of the LEAPPs, once confirmed. """
        if messagebox.askyesno(
                "Clear all LEAPP history",
                "Clear all shared LEAPP history, including recent input and output paths?",
                parent=self):
            history.clear_history()
            self.refresh_clear_buttons()

    def place_over(self, app):
        """ Centre the window over the main window. """
        self.update_idletasks()
        x = app.winfo_rootx() + (app.winfo_width() - self.winfo_reqwidth()) // 2
        y = app.winfo_rooty() + (app.winfo_height() - self.winfo_reqheight()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
