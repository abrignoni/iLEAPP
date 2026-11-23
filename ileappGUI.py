"""
The new LEAPPs GUI.
"""

import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from leapp_functions.app.gui import quick_exit
from leapp_functions import leapp
from leapp_functions.app import artifact_list, history
from leapp_functions.app.gui import images, themes, window_area
from leapp_functions.app.gui.app_state import AppState
from leapp_functions.app.gui.header import Header
from leapp_functions.app.gui.steps import Steps
from leapp_functions.app.gui.artifacts import ArtifactsScreen
from leapp_functions.app.gui.case import CaseScreen
from leapp_functions.app.gui.custom_widgets import MARGIN, ScrollArea
from leapp_functions.app.gui.results import ResultsScreen
from leapp_functions.app.gui.review import ReviewScreen
from leapp_functions.app.gui.run import RunControl, RunScreen
from leapp_functions.app.gui.settings import SettingsControl
from leapp_functions.app.gui.source import SourceScreen
from leapp_functions.app.gui.status_bar import StatusBar
import ileapp
from scripts.context import Context
from scripts.version_info import check_runtime_dependencies

MIN_SIZE = (1000, 700)
UNLOCK_POLL = 100

SCREENS = {"case": CaseScreen, "source": SourceScreen, "artifacts": ArtifactsScreen,
           "review": ReviewScreen, "run": RunScreen, "results": ResultsScreen}


def crunch(request):
    """ The parser. """
    Context.set_keychain_path(request.secrets.get("keychain") or None)
    return ileapp.crunch_artifacts(request.plugins, request.detected.kind, request.input_path,
                                   request.out_params, True, request.loader, request.case, "UTC",
                                   request.profile, None, request.backup_keys,
                                   image_password=request.image_keys, found_members=request.found,
                                   hash_files=request.hash_files)


class MainWindow(tk.Tk):
    """ Main application window for the LEAPP GUI. """

    def __init__(self, show=True):
        """ Initialize the window, application state, and widgets.

        Args:
            show (bool): False builds everything but never puts the window on screen, for
                --selfcheck.
        """
        super().__init__()
        self.title(f"{leapp.name} version {leapp.version}")
        self.icon = images.load("icon.png")
        self.iconphoto(True, self.icon)
        self.screen_area = window_area.measure(self)
        self.minsize(min(MIN_SIZE[0], self.screen_area[2]), min(MIN_SIZE[1], self.screen_area[3]))

        self.app_state = AppState(self.refresh_steps)
        self.app_state.artifacts = artifact_list.load_artifacts()
        self.appearance = themes.Appearance(leapp.theme, history.get_appearance(leapp.name))
        ttk.Style(self).theme_use("clam")

        settings = SettingsControl(self)
        if sys.platform == "darwin":
            # On macOS: Settings item in the application menu and ⌘,
            self.createcommand("::tk::mac::ShowPreferences", settings.open)
            self.createcommand("::tk::mac::Quit", self.close)
        else:
            # Other platforms: Ctrl,
            self.bind_all("<Control-comma>", lambda _event: settings.open())

        self.bind("<Control-i>", lambda _event: self.focus_field("focus_input"))
        self.bind("<Control-o>", lambda _event: self.focus_field("focus_output"))
        self.bind("<Control-f>", lambda _event: self.focus_field("focus_search"))
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind(sequence, self.on_wheel)
        self.bind("<FocusIn>", self.on_focus)
        try:
            self.bind("<TouchpadScroll>", self.on_touchpad)
        except tk.TclError:
            pass

        self.protocol("WM_DELETE_WINDOW", self.close)

        self.widgets = {}
        self.unlock_watch = None
        self.run_control = RunControl(self, crunch)

        self.build()
        self.fix_size()
        if show:
            self.deiconify()
            self.watch_unlock()
            if sys.platform == "darwin":
                self.after(300, self.redraw)

    def on_wheel(self, event):
        """ The mouse wheel, anywhere in the window. """
        self.widgets["scroll"].wheel(event)

    def on_touchpad(self, event):
        """ The touchpad, anywhere in the window. """
        self.widgets["scroll"].touchpad(event)

    def on_focus(self, event):
        """ A widget has got the focus. """
        self.widgets["scroll"].reveal(event)

    def fix_size(self):
        """ Give the window the width its first screen asks for, within the display. It then keeps
        its size on every screen, unless the user changes it. """
        self.update_idletasks()
        width = min(max(self.winfo_reqwidth(), MIN_SIZE[0]), self.screen_area[2])
        height = min(MIN_SIZE[1], self.screen_area[3])
        self.geometry(f"{width}x{height}")
        window_area.place(self, self.screen_area, width, height)

    def redraw(self):
        """ On macOS, a window opened from a terminal stays empty until it is clicked:
        resizing it by one pixel and back makes it draw. Then it is brought to the front. """
        width, height = self.winfo_width(), self.winfo_height()
        self.geometry(f"{width + 1}x{height}")
        self.update_idletasks()
        self.geometry(f"{width}x{height}")

        self.activate_application()

    def activate_application(self):
        """ Make the program the active application. """
        bundle = Path(sys.base_prefix) / "Resources" / "Python.app"
        if getattr(sys, "frozen", False) or not bundle.is_dir():
            return
        try:
            subprocess.run(["open", str(bundle)], check=False, timeout=5)
        except (OSError, subprocess.SubprocessError):
            pass

    @property
    def colors(self):
        """ The palette in use """
        return self.appearance.colors

    def build(self):
        """ Build or replace every widget using the current palette. """
        for name in ("header", "body"):
            if name in self.widgets:
                self.widgets[name].destroy()
        self.configure(bg=self.colors.main_bg)
        themes.apply_styles(ttk.Style(self), self.colors)
        themes.title_bar(self, self.appearance.is_dark)

        self.widgets["header"] = Header(self, self)
        self.widgets["header"].pack(fill="x")

        body = self.widgets["body"] = tk.Frame(self, bg=self.colors.main_bg)
        body.pack(fill="both", expand=True, padx=(MARGIN, 0), pady=(16, 8))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        self.widgets["steps"] = Steps(body, self)
        self.widgets["steps"].grid(row=0, column=0, sticky="ew", padx=(0, MARGIN), pady=(0, 24))

        self.widgets["scroll"] = ScrollArea(body, self)
        self.widgets["scroll"].grid(row=1, column=0, sticky="nsew")

        self.show_screen()

        self.widgets["status_bar"] = StatusBar(body, self)
        self.widgets["status_bar"].grid(row=2, column=0, sticky="ew", padx=(0, MARGIN),
                                        pady=(16, 8))

    def show_screen(self):
        """ Build the screen of the step. """
        old = self.widgets.pop("screen", None)
        if old is not None:
            old.destroy()
        step = self.app_state.step
        screen = SCREENS[step](self.widgets["scroll"].content, self)
        self.widgets["screen"] = screen
        self.widgets["scroll"].show(screen)

    def go(self, step):
        """ Navigate to a step when the current application state allows it. """
        state = self.app_state
        if step == "run" and state.run_status == "idle":
            step = "review"
        if state.can_go(step):
            state.left.add(state.step)
            state.step = step
            self.show_screen()
            self.refresh_steps()

    def go_back(self):
        """ Navigate to the previous step. """
        previous = self.app_state.previous_open()
        if previous is not None:
            self.go(previous)

    def go_next(self):
        """ Navigate to the next step. """
        state = self.app_state
        if state.step in ("case", "source", "artifacts"):
            self.go(state.neighbour(1))
        elif state.step == "review":
            self.run_control.start()
        elif state.step == "run" and state.run_status == "running":
            self.run_control.stop()
        elif state.step == "run":
            self.go("results")
        else:
            self.run_control.new_run()

    def close(self):
        """ The window's close button. Closing during a run stops it where it is. """
        if self.app_state.run_status == "running" and not messagebox.askokcancel(
                "Processing still running",
                "A run is still in progress.\n\nClosing now stops it where it is. The report and "
                "the LAVA project will be incomplete, and temporary files may be left behind.\n\n"
                "Close anyway?", icon=messagebox.WARNING, default=messagebox.CANCEL, parent=self):
            return
        self.destroy()

    def watch_unlock(self):
        """ Follow the sequence that opens the source, whatever the screen on show. """
        self.app_state.poll_unlock()
        self.unlock_watch = self.after(UNLOCK_POLL, self.watch_unlock)

    def destroy(self):
        """ Stop following the sequence and the run before the window goes. """
        if self.unlock_watch is not None:
            self.after_cancel(self.unlock_watch)
            self.unlock_watch = None
        self.run_control.stop_watching()
        super().destroy()

    def refresh_steps(self):
        """ Redraw the steps ans status bar after the application state changes. """
        for name in ("steps", "status_bar", "checks"):
            if name in self.widgets:
                self.widgets[name].refresh()

    def focus_field(self, method):
        """ Ask the screen on show to put the cursor in one of its fields, if it has that field. """
        action = getattr(self.widgets.get("screen"), method, None)
        if action is not None:
            action()


def selfcheck():
    """ Build the window without showing it, then exit: a built binary is smoke tested with this
    (packaging/build.py smoke). The line printed is the one smoke reads. """
    window = MainWindow(show=False)
    print(f"selfcheck passed: {len(window.app_state.artifacts.loader)} artifacts, "
          f"Tk {window.tk.call('info', 'patchlevel')}")
    window.destroy()
    sys.exit(0)


check_runtime_dependencies()
if "--selfcheck" in sys.argv[1:]:
    selfcheck()
main_window = MainWindow()
main_window.mainloop()
if main_window.app_state.run_status != "running":
    quick_exit.window_closed()
