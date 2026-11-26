"""
The bar at the bottom of the window: what the screen is for, and back and next buttons.
A title and a subtitle on the left say what is expected of the user on this screen. The
subtitle turns red when Next is blocked, and says what is missing. During a run, the title says
how far it has gone and the progress bar takes the place of the subtitle.
Back and Next buttons on the right move through the screens in the order of state.ORDER.
The widgets are made once. refresh() changes their texts, their style and their state.
"""

import tkinter as tk
from tkinter import ttk

from leapp_functions.app.gui import themes
from leapp_functions.app.gui.app_state import is_waiting
from leapp_functions.app.gui.custom_widgets import OutlineButton
from leapp_functions.app.secret_fields import SECRETS

# For each screen: its title, its subtitle and the text of its main button. The subtitle of
# Source is the "subtitle" of "secrets" in data/leapp_config.json, none without secrets.
TEXTS = {
    "case": ("Case data is optional", "It only decorates the header of the report",
             "Continue to Source"),
    "source": ("The extraction and the output folder are required",
               getattr(SECRETS, "subtitle", ""), "Continue to Artifacts"),
    "artifacts": ("Choose what to parse", "", "Review and run"),
    "review": ("Ready to run", "The run takes place in the background: the window stays usable",
               "Start parsing"),
    "run": ("", "", "Stop"),  # during a run, BarTexts.show_progress() replaces the texts
    "results": ("Run finished", "The report opens in the default browser", "New run"),
}
# The Run screen once the run has ended, by outcome
RUN_OVER = {
    "done": ("Run finished", "The report is in the output folder", "See the results"),
    "failed": ("Run failed", "See the log", "See the results"),
    "stopped": ("Run stopped", "The report only holds the artifacts parsed before the stop",
                "See the results"),
}

BUTTON_DROP = 4


def artifacts_subtitle(artifacts):
    """ "1208 of 1210 artifacts selected · 2 slow or large ones are unselected by default" """
    subtitle = f"{len(artifacts.selected)} of {len(artifacts.listed)} artifacts selected"
    left_out = sum(not artifact.default for artifact in artifacts.listed)
    if left_out:
        ones = "one is" if left_out == 1 else "ones are"
        subtitle += f" · {left_out} slow or large {ones} unselected by default"
    return subtitle


class BarTexts(tk.Frame):
    """ On the left of the buttons: a title, and under it a subtitle or the progress of the run. """

    def __init__(self, parent, app):
        colors = app.colors
        super().__init__(parent, bg=colors.main_bg)
        self.title_label = tk.Label(self, anchor="w", bg=colors.main_bg, fg=colors.text_primary,
                                    font=themes.sans(12, "bold"))
        self.title_label.pack(fill="x")
        self.subtitle_label = tk.Label(self, anchor="w", bg=colors.main_bg, font=themes.sans(11))
        self.subtitle_label.pack(fill="x")
        self.progress_bar = ttk.Progressbar(self, style="Run.Horizontal.TProgressbar")

    def show_texts(self, title, subtitle, color):
        """ The texts of a screen. """
        self.progress_bar.pack_forget()
        self.title_label.configure(text=title)
        self.subtitle_label.configure(text=subtitle, fg=color)
        self.subtitle_label.pack(fill="x")

    def show_progress(self, title, done, total):
        """ How far the run has gone. """
        self.subtitle_label.pack_forget()
        self.title_label.configure(text=title)
        self.progress_bar.configure(maximum=max(total, 1), value=done)
        self.progress_bar.pack(fill="x", padx=(3, 0), pady=(2, 0))  # lined up with the texts


class StatusBar(tk.Frame):
    """ The title and subtitle of the screen, and the Back and Next buttons. """

    def __init__(self, parent, app):
        colors = app.colors
        super().__init__(parent, bg=colors.main_bg)
        self.app = app

        tk.Frame(self, height=1, bg=colors.border).grid(row=0, column=0, columnspan=4, sticky="ew")
        self.columnconfigure(0, weight=1)

        self.texts = BarTexts(self, app)
        self.texts.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        self.back_button = OutlineButton(self, app, text="Back", command=app.go_back)
        self.back_button.grid(row=1, column=1, padx=(16, 0), pady=(8 + BUTTON_DROP, 0))
        self.next_button = OutlineButton(self, app, command=app.go_next, style="filled")
        self.next_button.grid(row=1, column=2, padx=(10, 0), pady=(8 + BUTTON_DROP, 0))
        self.stop_button = OutlineButton(self, app, command=app.go_next)
        self.stop_button.grid(row=1, column=2, padx=(10, 0), pady=(8 + BUTTON_DROP, 0))
        self.close_button = OutlineButton(self, app, text="Close", command=app.close, style="filled")
        self.close_button.grid(row=1, column=3, padx=(10, 0), pady=(8 + BUTTON_DROP, 0))

        self.refresh()

    def refresh(self):
        """ Show the state: the texts of the screen, and which buttons can be used. """
        colors, state = self.app.colors, self.app.app_state
        title, subtitle, next_text = TEXTS[state.step]
        running = state.step == "run" and state.run_status == "running"
        if state.step == "run" and not running:
            title, subtitle, next_text = RUN_OVER[state.run.worker.shown.outcome]
        elif state.step == "results" and state.run.worker.shown.outcome != "done":
            title, subtitle, _next = RUN_OVER[state.run.worker.shown.outcome]
        elif state.step == "results":
            title = RUN_OVER["done"][0]
        if state.step == "artifacts":
            subtitle = artifacts_subtitle(state.artifacts)

        target = state.neighbour(1)
        blocked = state.step in ("source", "artifacts", "review") and not state.can_go(target)
        if blocked and state.step == "review":
            title = "Not ready to run"

        missing = state.missing_for(target) if blocked else ""
        if running:
            self.show_progress()
        else:
            self.texts.show_texts(title, missing or subtitle, colors.text_error
                                  if missing and not is_waiting(missing) else colors.text_secondary)

        if state.step == "results":
            self.next_button.set_style("outline")
            self.close_button.grid()
        else:
            self.next_button.set_style("filled")
            self.close_button.grid_remove()

        # Only one of the two is shown. grid_remove() hides a widget and keeps where it was
        # placed, which grid() brings back.
        if running:
            self.next_button.grid_remove()
            self.stop_button.grid()
            self.stop_button.set_text(next_text)
            self.stop_button.set_enabled(not state.run.worker.shown.stopping)
        else:
            self.stop_button.grid_remove()
            self.next_button.grid()
            self.next_button.set_text(next_text)
            self.next_button.set_enabled(not blocked)

        self.back_button.set_enabled(state.previous_open() is not None)

    def show_progress(self):
        """ How far the run has gone, as often as the run reports it. """
        shown = self.app.app_state.run.worker.shown
        word = "Stopping" if shown.stopping else "Progress"
        noun = "artifact" if shown.total == 1 else "artifacts"
        self.texts.show_progress(f"{word}: {shown.done:,} of {shown.total:,} {noun} done",
                                 shown.done, shown.total)
