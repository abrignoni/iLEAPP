""" The five stages of a run. """

import tkinter as tk

from leapp_functions.app.gui import images, themes

# (key, title, icon)
# The key is what AppState.step holds; the icon is the name of a Tabler icon.
STAGES = (
    ("case", "Case data", "briefcase"),
    ("source", "Source", "device-mobile"),
    ("artifacts", "Artifacts", "list-check"),
    ("run", "Run", "player-play"),
    ("results", "Results", "report"),
)

ICON_SIZE = 28  # pixels
MARGIN = 8      # transparent pixels around an icon: room for its tick
LINE = 2        # thickness of the line between the icons


class Steps(tk.Frame):
    """ The different steps of a run """

    def __init__(self, parent, app):
        colors = app.colors
        super().__init__(parent, bg=colors.main_bg)
        self.app = app

        self.icon_labels, self.title_labels = {}, {}
        self.left_lines, self.right_lines = {}, {}
        self.pictures = {}
        self.hovered = None

        for i, (key, title, _icon) in enumerate(STAGES):
            self.columnconfigure(i, weight=1, uniform="step")
            stage_frame = tk.Frame(self, bg=colors.main_bg)
            stage_frame.grid(row=0, column=i, sticky="ew")
            stage_frame.columnconfigure(0, weight=1)
            stage_frame.columnconfigure(2, weight=1)
            if i > 0:
                self.left_lines[key] = self.line(stage_frame, 0)
            self.icon_labels[key] = tk.Label(stage_frame, bg=colors.main_bg)
            self.icon_labels[key].grid(row=0, column=1)
            if i < len(STAGES) - 1:
                self.right_lines[key] = self.line(stage_frame, 2)

            self.title_labels[key] = tk.Label(stage_frame, text=title, bg=colors.main_bg)
            self.title_labels[key].grid(row=1, column=0, columnspan=3)

            for widget in (self.icon_labels[key], self.title_labels[key]):
                widget.bind("<Button-1>", lambda _event, key=key: self.click(key))
                widget.bind("<Enter>", lambda _event, key=key: self.hover(key))
                widget.bind("<Leave>", lambda _event: self.hover(None))

        self.refresh()

    def line(self, stage_frame, grid_column):
        """ The line to indicate the progression of valid steps. """
        line = tk.Frame(stage_frame, height=LINE, bg=self.app.colors.line)
        line.grid(row=0, column=grid_column, sticky="ew")
        return line

    def clickable(self, key):
        """ Return True if a stage is clickable otherwise False. """
        state = self.app.app_state
        return key != state.step and state.can_go(key)

    def click(self, key):
        """ Go to a stage, unless it cannot be clicked. """
        if self.clickable(key):
            self.app.go(key)

    def hover(self, key):
        """ Remember which stage is under the pointer, None for none, and show it.

        A stage that cannot be clicked is not shown as hovered: that would suggest it can.
        """
        self.hovered = key if key is not None and self.clickable(key) else None
        self.refresh()

    def show_stage(self, key, icon, active, complete):
        """ Draw the icon and the title of a stage in the state it is in. """
        colors = self.app.colors

        # The pointer may be on a stage that has just become the current one, by a click
        hovered = key == self.hovered and self.clickable(key)
        bright = active or complete or hovered

        # A step done carries a tick: a disc in the text's colour, the tick in the background's
        tick = (colors.text_primary, colors.main_bg) if complete else None
        self.pictures[key] = images.load_icon(
            icon, ICON_SIZE, colors.text_primary if bright else colors.text_secondary, MARGIN, tick)
        self.icon_labels[key].configure(image=self.pictures[key])
        font = themes.sans(12, "bold" if active else "normal")
        if hovered:
            font += ("underline",)
        self.title_labels[key].configure(fg=colors.text_primary if bright else colors.text_secondary, font=font)

    def refresh(self):
        """ Show the state: the current stage, the ones done, and the lines after the ones validated. """
        colors, state = self.app.colors, self.app.app_state
        current = [stage[0] for stage in STAGES].index(state.stage())
        validated = {key for key in state.completed() if key != state.stage() or key in state.left}
        complete = {key for key in state.completed() if key != state.stage()}

        for i, (key, _title, icon) in enumerate(STAGES):
            self.show_stage(key, icon, i == current, key in complete)
            if key in self.right_lines:
                color = colors.progress if key in validated else colors.line
                self.right_lines[key].configure(bg=color)
                self.left_lines[STAGES[i + 1][0]].configure(bg=color)
