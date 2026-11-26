"""
The Source screen: the extraction to parse, where the report goes, and the secrets that open
what some apps keep encrypted.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from leapp_functions import leapp
from leapp_functions.app import history, input_type, secret_fields
from leapp_functions.app.disk import FILE, PENDING, SILENT, path_status
from leapp_functions.app.gui import images, themes
from leapp_functions.app.gui.app_state import WAITING
from leapp_functions.app.gui.custom_widgets import (GAP, MAIN_WIDTH, MARGIN, Caption, Card, Field,
                                                    FileField, LabeledEntry, ModalWindow,
                                                    OutlineButton, Tooltip, mark_line, open_menu,
                                                    show_example, two_columns)
from leapp_functions.app.output import default_output_folder_name
from leapp_functions.app.platform import sanitize_file_name
from leapp_functions.app.secret_fields import SECRETS
from scripts.raw_image import (RAW_IMAGE_FILE_PATTERNS, RAW_IMAGE_LABEL, confirm_found_members,
                               selection_text)

# A Berla iVe export, offered only by a LEAPP that reads one (VLEAPP)
EXPORT_TYPES = (("Berla iVe export", "*.iVa"),) if "iva" in input_type.SUPPORTED else ()
FILE_TYPES = (("All supported files", " ".join(["*.tar *.zip *.gz *.xz", RAW_IMAGE_FILE_PATTERNS]
                                               + [pattern for _label, pattern in EXPORT_TYPES])),
              ("tar file", "*.tar"), ("zip file", "*.zip"), ("gz file", "*.gz"),
              ("tar.xz file", "*.xz"), (RAW_IMAGE_LABEL, RAW_IMAGE_FILE_PATTERNS)) + EXPORT_TYPES
DETECT_DELAY = 300
WATCH_DELAY = 1000
POLL_DELAY = 100
HIDDEN = "•"
# The icon of the square button that shows a password: an eye struck through while it is hidden
EYE_ICONS = {True: "eye-off", False: "eye"}
EYE_SIZE = 20
# The most read from a file for a text secret: a key or a password, never a large file
TEXT_READ_LIMIT = 4096


class SourceScreen(tk.Frame):
    """ The fields of the Source screen, which edit the variables of the window's state. """

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors.main_bg)
        self.app = app
        self.state = app.app_state
        self.single_file = None

        main, side = two_columns(self, app)
        self.build_extraction(main)
        # What a run needs comes first; the secrets, all optional, may need scrolling to.
        self.output_card = OutputCard(main, app)
        self.output_card.grid(row=1, column=0, sticky="ew", pady=(GAP, 0))
        if SECRETS is not None:
            SecretsCard(main, app, SECRETS).grid(row=2, column=0, sticky="ew", pady=(GAP, 0))
        DetectedCard(side, app).pack(fill="x")
        ChecksCard(side, app).pack(fill="x", pady=(2 * GAP, 0))

    def build_extraction(self, main):
        """ The card with the path of the extraction and the buttons that fill it in. """
        card = Card(main, self.app, "EXTRACTION")
        card.grid(row=0, column=0, sticky="ew")
        card.body.columnconfigure(0, weight=1)

        Caption(card.body, self.app, leapp.source_hint, card.background).grid(
            row=0, column=0, sticky="ew")
        field = LabeledEntry(card.body, self.app, Field("", self.state.run.source))
        field.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.entry = field.entry
        Tooltip((field.box, field.entry), self.app, self.images_text)

        buttons = tk.Frame(card.body, bg=card.background)
        buttons.grid(row=2, column=0, sticky="w", pady=(12, 0))
        created = {}
        for text, command in (("Folder…", self.choose_folder), ("Files…", self.choose_files),
                              ("Recent ▾", self.show_recent)):
            created[text] = OutlineButton(buttons, self.app, text=text, command=command,
                                          style="in_card")
            created[text].pack(side="left", padx=(0, 8))
        self.recent_button = created["Recent ▾"]

        if "file" in input_type.SUPPORTED:
            self.build_single_file(buttons)

        self.recent_menu = tk.Menu(self, tearoff=0)

    def build_single_file(self, buttons):
        """ The box that has one file read as it is (-t file), after the buttons. """
        self.single_file = ttk.Checkbutton(buttons, text="Read as a single file", style="Card.TCheckbutton",
                                           variable=self.state.run.single_file)
        self.single_file.pack(side="left", padx=(8, 0))
        self.allow_single_file()

        variable = self.state.run.source
        trace = variable.trace_add("write", lambda *_args: self.allow_single_file())
        self.single_file.bind("<Destroy>", lambda _event: variable.trace_remove("write", trace))

    def allow_single_file(self):
        """ The box can be ticked only when the source is one file. """
        one_file = self.state.is_one_file()
        if not one_file and self.state.run.single_file.get():
            self.state.run.single_file.set(False)
        self.single_file.state(["!disabled" if one_file else "disabled"])

    def focus_input(self):
        """ Put the cursor in the source field: Ctrl+I """
        self.entry.focus_set()

    def focus_output(self):
        """ Put the cursor in the output field: Ctrl+O """
        self.output_card.entry.focus_set()

    def images_text(self):
        """ What the tooltip says: the images picked together, nothing for one path. """
        paths = self.state.source_paths()
        if len(paths) < 2:
            return ""
        return f"{len(paths)} images, read together:\n" + "\n".join(paths)

    def choose_folder(self):
        """ Ask for a folder: an extraction already unpacked, an iTunes backup or an image folder. """
        folder = filedialog.askdirectory(parent=self.winfo_toplevel(), title="Select a folder")
        if folder:
            self.pick([folder])

    def choose_files(self):
        """ Ask for a file, or for several: the disk images of a RAID set. """
        picked = filedialog.askopenfilenames(
            parent=self.winfo_toplevel(), title="Select a file (or the disk images of a RAID set)",
            filetypes=FILE_TYPES)
        if picked:
            self.pick(list(self.tk.splitlist(picked)))

    def pick(self, paths):
        """ Take paths as the source and remember them in the history, as one set when there are several. """
        self.state.set_source(paths)
        if len(paths) > 1:
            history.record_input_set(paths)
        else:
            history.record_input_path(paths[0])

    def show_recent(self):
        """ Open the menu of the recent paths and sets of images under its button. """
        menu = self.recent_menu
        menu.delete(0, "end")
        if not history.is_history_enabled():
            menu.add_command(label="(History disabled - enable it in Settings)", state="disabled")
        else:
            paths = history.get_input_paths()
            if not paths:
                menu.add_command(label="(No recent paths)", state="disabled")
            for path in paths:
                menu.add_command(label=history.format_path_for_display(path),
                                 command=lambda path=path: self.state.set_source([path]))

            sets = []
            for input_set in history.get_input_sets():
                given = [path for path in input_set.get("paths", [])
                         if path not in input_set.get("found_automatically", [])]
                if len(given) > 1:
                    sets.append(given)
            if sets:
                menu.add_separator()
            for given in sets:
                menu.add_command(
                    label=selection_text([history.format_path_for_display(path) for path in given]),
                    command=lambda given=given: self.state.set_source(given))
        button = self.recent_button
        open_menu(menu, button)


class OutputCard(tk.Frame):
    """ Path for the report. """

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors.main_bg)
        self.app = app
        run = app.app_state.run
        card = Card(self, app, "OUTPUT FOLDER")
        card.pack(fill="x")
        body = card.body
        body.columnconfigure(0, weight=1)

        folder_line = tk.Frame(body, bg=card.background)
        folder_line.grid(row=0, column=0, sticky="ew")
        folder_line.columnconfigure(0, weight=1)
        field = LabeledEntry(folder_line, app, Field("", run.output))
        field.grid(row=0, column=0, sticky="ew")
        self.entry = field.entry
        Tooltip((field.box, field.entry), app, lambda: run.output.get().strip())
        OutlineButton(folder_line, app, text="Folder…", command=self.choose_folder,
                      style="in_card").grid(row=0, column=1, padx=(8, 0))
        self.recent_button = OutlineButton(folder_line, app, text="Recent ▾", command=self.show_recent,
                                           style="in_card")
        self.recent_button.grid(row=0, column=2, padx=(8, 0))
        self.recent_menu = tk.Menu(self, tearoff=0)

        name_line = tk.Frame(body, bg=card.background)
        name_line.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        name_line.columnconfigure(1, weight=1)
        tk.Label(name_line, text="Report folder name", bg=card.background,
                 fg=app.colors.text_secondary, font=themes.sans(10)).grid(row=0, column=0, padx=(0, 8))
        name = LabeledEntry(name_line, app, Field("", run.folder_name))
        name.grid(row=0, column=1, sticky="ew")
        name.entry.configure(width=8)
        # Characters a folder name cannot hold are refused as they are typed
        name.entry.configure(validate="key", validatecommand=(
            self.register(lambda proposed: sanitize_file_name(proposed) == proposed), "%P"))
        show_example(name, app, run.folder_name, default_output_folder_name())

        traces = [(variable, variable.trace_add("write", lambda *_args: app.app_state.on_change()))
                  for variable in (run.output, run.folder_name)]
        self.bind("<Destroy>", lambda _event: self.stop(traces))

    @staticmethod
    def stop(traces):
        """ The card is destroyed: the fields are no longer watched for it. """
        for variable, trace in traces:
            variable.trace_remove("write", trace)

    def choose_folder(self):
        """ Ask for the folder. """
        folder = filedialog.askdirectory(parent=self.winfo_toplevel(), title="Select the output folder")
        if folder:
            self.app.app_state.run.output.set(folder)
            history.record_output_path(folder)

    def show_recent(self):
        """ Open the menu of the recent output folders under its button. """
        menu = self.recent_menu
        menu.delete(0, "end")
        output = self.app.app_state.run.output
        if not history.is_history_enabled():
            menu.add_command(label="(History disabled - enable it in Settings)", state="disabled")
        elif not history.get_output_paths():
            menu.add_command(label="(No recent paths)", state="disabled")
        else:
            for path in history.get_output_paths():
                menu.add_command(label=history.format_path_for_display(path),
                                 command=lambda path=path: output.set(path))
        button = self.recent_button
        open_menu(menu, button)


class SecretFields:
    """ The inputs of the secrets: a file to choose, or a text to type, hidden unless shown, or to
    read from a file (see secret_fields). Built in a card of the Source screen, or in the window of
    the secrets when there are several. """

    def __init__(self, app):
        self.app = app

    def build(self, line, field, variable):
        """ The inputs of one secret, in line. """
        if secret_fields.kind(field) == "text":
            self.build_text_field(line, field, variable)
        else:
            FileField(line, self.app, Field(field["label"], variable,
                                            pick=lambda: self.choose(line, field, variable))).grid(
                row=0, column=0, sticky="ew")
            self.add_clear(line, 1, variable)

    def build_text_field(self, line, field, variable):
        """ A text to type, hidden unless shown, or to read from a file. Its help text takes the
        whole width above, as three buttons leave the input too narrow for it. """
        Caption(line, self.app, field["label"], self.app.colors.card_bg).grid(
            row=0, column=0, columnspan=4, sticky="ew", pady=(0, 5))
        labeled = LabeledEntry(line, self.app, Field("", variable))
        labeled.entry.configure(show=HIDDEN)
        labeled.grid(row=1, column=0, sticky="ew")
        labeled.box.update_idletasks()
        eye_button(line, self.app, labeled.entry, labeled.box.winfo_reqheight()).grid(
            row=1, column=1, sticky="s", padx=(8, 0))
        OutlineButton(line, self.app, text="Load from file…", style="in_card",
                      command=lambda: self.load(line, field, variable)).grid(
            row=1, column=2, sticky="s", padx=(8, 0))
        self.add_clear(line, 3, variable, row=1)

    def add_clear(self, line, column, variable, row=0):
        """ The Clear button of a field, usable only when the field holds something. """
        clear = OutlineButton(line, self.app, text="Clear", command=lambda: variable.set(""),
                              style="in_card")
        clear.grid(row=row, column=column, sticky="s", padx=(8, 0))

        def refresh(*_args):
            """ Clear can be used only when the field holds something. """
            clear.set_enabled(bool(variable.get()))

        def changed(*_args):
            """ A secret given or cleared. """
            refresh()
            self.app.app_state.on_change()

        trace = variable.trace_add("write", changed)
        clear.bind("<Destroy>", lambda _event: variable.trace_remove("write", trace))
        refresh()

    @staticmethod
    def choose(line, field, variable):
        """ Ask for the file. Cancelling leaves the field as it was. """
        path = filedialog.askopenfilename(
            parent=line.winfo_toplevel(), title=f"Choose the {secret_fields.name(field)} file",
            filetypes=secret_fields.file_types(field))
        if path:
            variable.set(path)

    @staticmethod
    def load(line, field, variable):
        """ Read the text of a secret from a file. Cancelling leaves the field as it was. An error
        names the file, never what it holds. """
        path = filedialog.askopenfilename(
            parent=line.winfo_toplevel(),
            title=f"Choose a file holding the {secret_fields.name(field)}",
            filetypes=secret_fields.file_types(field))
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                variable.set(handle.read(TEXT_READ_LIMIT).strip())
        except (OSError, UnicodeDecodeError) as error:
            messagebox.showerror("Could not read the file",
                                 f"{os.path.basename(path)}: {type(error).__name__}",
                                 parent=line.winfo_toplevel())


class SecretsCard(tk.Frame):
    """ The secrets that open what some apps keep encrypted, as the configuration file lists them.
    One secret has its inputs on the card. Several would make the screen scroll: the card then
    says which are given, and Enter… opens them in a window of their own (SecretsWindow). """

    def __init__(self, parent, app, secrets):
        super().__init__(parent, bg=app.colors.main_bg)
        self.app = app
        self.secrets = secrets
        self.window = None
        card = Card(self, app, secrets.title)
        card.pack(fill="x")
        card.body.columnconfigure(0, weight=1)
        if len(secrets.fields) == 1:
            field = secrets.fields[0]
            line = tk.Frame(card.body, bg=app.colors.card_bg)
            line.grid(row=0, column=0, sticky="ew")
            line.columnconfigure(0, weight=1)
            SecretFields(app).build(line, field, app.app_state.run.secrets[field["name"]])
        else:
            self.build_summary(card)

    def build_summary(self, card):
        """ One line that says which secrets are given, and the button that opens their window. """
        summary = Caption(card.body, self.app, "", card.background)
        summary.grid(row=0, column=0, sticky="ew")
        OutlineButton(card.body, self.app, text="Enter…", style="in_card",
                      command=self.open_window).grid(row=0, column=1, sticky="e", padx=(16, 0))
        variables = [self.app.app_state.run.secrets[field["name"]] for field in self.secrets.fields]

        def show(*_args):
            """ How many secrets are given, and which. """
            summary.configure(text=summary_text(self.secrets.fields, variables))

        traces = [(variable, variable.trace_add("write", show)) for variable in variables]
        summary.bind("<Destroy>", lambda _event: [variable.trace_remove("write", trace)
                                                  for variable, trace in traces])
        show()

    def open_window(self):
        """ Open the window of the secrets, or bring it to the front if it is open. """
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
        else:
            self.window = SecretsWindow(self.app, self.secrets)


def summary_text(fields, variables):
    """ "Optional. 1 of 4 given: Signal key." """
    given = [secret_fields.name(field) for field, variable in zip(fields, variables)
             if variable.get().strip()]
    if not given:
        return f"Optional. None of the {len(fields)} given."
    return f"Optional. {len(given)} of {len(fields)} given: {', '.join(given)}."


class SecretsWindow(ModalWindow):
    """ The secrets, when there are several, in a window of their own above the main one: one line
    for each, whose inputs show under it on demand, so the window stays short. """

    def __init__(self, app, secrets):
        super().__init__(app, secrets.title.capitalize())
        card = Card(self, app, secrets.title)
        card.pack(fill="x", padx=MARGIN, pady=(MARGIN, 0))
        card.body.columnconfigure(1, weight=1, minsize=MAIN_WIDTH - 2 * MARGIN)
        inputs = SecretFields(app)
        for row, field in enumerate(secrets.fields):
            line = tk.Frame(card.body, bg=app.colors.card_bg)
            line.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10 if row else 0, 0))
            line.columnconfigure(1, weight=1)
            detail = tk.Frame(line, bg=app.colors.card_bg)
            detail.columnconfigure(0, weight=1)
            inputs.build(detail, field, app.app_state.run.secrets[field["name"]])
            self.build_line(line, field, app.app_state.run.secrets[field["name"]], detail)
        self.show()

    def build_line(self, line, field, variable, detail):
        """ One line for a secret: its name, whether it is given, and a button that shows its
        inputs under the line, or hides them again. """
        colors = self.app.colors
        tk.Label(line, text=secret_fields.title(field), anchor="w", bg=colors.card_bg,
                 fg=colors.text_primary, font=themes.sans(13, "bold")).grid(
            row=0, column=0, sticky="w")
        status = tk.Label(line, anchor="w", bg=colors.card_bg, fg=colors.text_secondary,
                          font=themes.sans(13))
        status.grid(row=0, column=1, sticky="ew", padx=(16, 8))
        toggle = OutlineButton(line, self.app, text="Enter…", style="in_card")
        toggle.grid(row=0, column=2, sticky="e")

        def show_status(*_args):
            """ None, Given, or the name of the file chosen. """
            value = variable.get().strip()
            if not value:
                status.configure(text="None")
            elif secret_fields.kind(field) == "text":
                status.configure(text="Given")
            else:
                status.configure(text=os.path.basename(value))

        def flip():
            """ Show the inputs under the line, or hide them again. """
            if detail.grid_info():
                detail.grid_remove()
                toggle.set_text("Enter…")
            else:
                detail.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 4))
                toggle.set_text("Done")

        toggle.button.configure(command=flip)
        trace = variable.trace_add("write", show_status)
        status.bind("<Destroy>", lambda _event: variable.trace_remove("write", trace))
        show_status()


def eye_button(parent, app, entry, side):
    """ A square button of side pixels that shows the text typed in entry, or hides it again. Its
    icon tells which: an eye struck through while the text is hidden, an eye while it shows. """
    pictures = {hidden: images.load_icon(icon, EYE_SIZE, app.colors.text_primary)
                for hidden, icon in EYE_ICONS.items()}
    button = OutlineButton(parent, app, image=pictures[True], style="in_card", padding=0)
    button.pictures = pictures
    button.configure(width=side, height=side)
    button.pack_propagate(False)

    def toggle():
        """ Show the text typed, or hide it again. """
        hidden = entry.cget("show") != HIDDEN
        entry.configure(show=HIDDEN if hidden else "")
        button.button.configure(image=pictures[hidden])

    button.button.configure(command=toggle)
    return button


def secret_line(field, value):
    """ (status, text) of the BEFORE RUNNING card for a secret. A text is never shown. """
    title = secret_fields.title(field)
    text = secret_fields.kind(field) == "text"
    if not value:
        return "optional", f"{title}: optional, none {'given' if text else 'chosen'}."
    if text:
        problem = secret_fields.text_problem(field, value)
        return ("problem", problem) if problem else ("ok", f"{title}: given.")
    status = path_status(value)
    if status == PENDING:
        return "todo", f"{title}: waiting for its drive to answer."
    if status == SILENT:
        return "problem", f"{title}: the file does not answer."
    if status != FILE:
        return "problem", f"{title}: the file no longer exists."
    return "ok", f"{title}: {os.path.basename(value)}"


class ChecksCard(tk.Frame):
    """ What the Source screen still lacks for a run, one line for each card of the left column. """

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors.main_bg)
        self.app = app
        self.card = Card(self, app, "BEFORE RUNNING", accent=True)
        self.card.pack(fill="x")
        self.card.body.columnconfigure(1, weight=1)
        # Told by the window whenever the state changes (MainWindow.refresh_steps)
        app.widgets["checks"] = self
        self.bind("<Destroy>", lambda _event: self.forget_me())
        self.refresh()

    def forget_me(self):
        """ The card is destroyed. """
        if self.app.widgets.get("checks") is self:
            del self.app.widgets["checks"]

    def refresh(self):
        """ The lines, built again from the state. """
        for child in self.card.body.winfo_children():
            child.destroy()
        for row, (status, text) in enumerate(self.lines()):
            mark_line(self.card, self.app, row, status, text)

    def lines(self):
        """ (status, text) for each card of the left column, in the same order. """
        state = self.app.app_state
        if state.run.detected is None:
            lines = [("todo", "Extraction: none chosen yet.")]
        elif state.missing_for_source() == WAITING.format("extraction"):
            lines = [("todo", "Extraction: waiting for its drive to answer.")]
        elif state.missing_for_source():
            lines = [("problem", "Extraction: cannot be read yet, see DETECTED.")]
        else:
            lines = [("ok", "Extraction: ready.")]
        lines.extend(secret_line(field, state.run.secrets[field["name"]].get().strip())
                     for field in secret_fields.FIELDS)
        output = state.missing_for_output()
        if not state.run.output.get().strip() or output == WAITING.format("output folder"):
            lines.append(("todo", f"Output: {output}"))
        else:
            lines.append(("problem", f"Output: {output}") if output else ("ok", "Output: ready."))
        return lines


class DetectedCard(tk.Frame):
    """ The card on the right of the Source screen: what the source is, as the run will read it. """

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors.main_bg)
        self.app = app
        card = Card(self, app, "DETECTED", accent=True)
        card.pack(fill="x")
        self.kind = Caption(card.body, app, "", card.background)
        self.kind.configure(fg=app.colors.text_primary, font=themes.sans(13, "bold"))
        self.kind.pack(fill="x")
        self.detail = Caption(card.body, app, "", card.background)
        self.unlock_panel = UnlockPanel(card.body, app, card.background)
        self.unlock_panel.pack(fill="x")

        self.pending = None
        run = app.app_state.run
        traces = [(variable, variable.trace_add("write", lambda *_args: self.schedule()))
                  for variable in (run.source, run.single_file)]
        self.bind("<Destroy>", lambda _event: self.stop(traces))
        self.refresh()
        self.seen = self.look()
        self.watching = self.after(WATCH_DELAY, self.watch)

    def look(self):
        """ What the disk says about the source, and what the screen lacks for a run. """
        state = self.app.app_state
        return ([path_status(path) for path in state.source_paths()], state.missing_for("artifacts"))

    def watch(self):
        """ Show again what has changed on the disk, as when a drive goes or comes back, and
        ask again for a source that has not answered yet. """
        state = self.app.app_state
        if self.look() != self.seen or state.run.detected in (input_type.NO_ANSWER, input_type.LOOKING):
            self.refresh()
            state.on_change()
            self.seen = self.look()
        looking = state.run.detected == input_type.LOOKING
        self.watching = self.after(POLL_DELAY if looking else WATCH_DELAY, self.watch)

    def schedule(self):
        """ Look at the source a moment after the last change of the field. """
        if self.pending is not None:
            self.after_cancel(self.pending)
        self.pending = self.after(DETECT_DELAY, self.refresh)

    def stop(self, traces):
        """ The card is destroyed: the source is no longer watched for it. """
        for variable, trace in traces:
            variable.trace_remove("write", trace)
        self.after_cancel(self.watching)
        if self.pending is not None:
            self.after_cancel(self.pending)

    def refresh(self):
        """ Show what the source is. """
        self.pending = None
        colors, state = self.app.colors, self.app.app_state
        state.detect_source()
        detected = state.run.detected
        if detected is None:
            detected = input_type.Detected("", "Nothing selected",
                                           note="The type of the extraction shows here once it is chosen.")
        self.kind.configure(text=detected.label)
        detail = detected.problem or detected.note
        self.detail.configure(text=detail, fg=colors.text_error if detected.problem
                              else colors.text_secondary)
        if detail:
            self.detail.pack(fill="x", pady=(6, 0), before=self.unlock_panel)
        else:
            self.detail.pack_forget()
        self.unlock_panel.restart()


class UnlockPanel(tk.Frame):
    """ Under what the source is: the questions asked to open it, one at a time. """

    def __init__(self, parent, app, background):
        super().__init__(parent, bg=background)
        self.app = app
        self.background = background
        self.secret = tk.StringVar()
        self.shown = None
        self.polling = None
        self.bind("<Destroy>", lambda _event: self.stop())

    def stop(self):
        """ No more looking for questions. """
        if self.polling is not None:
            self.after_cancel(self.polling)
            self.polling = None

    def restart(self):
        """ Look for the questions of the source's sequence, a new one or the one already running. """
        self.stop()
        self.poll()

    def poll(self):
        """ Show what the sequence asks, and look again a moment later while it runs.
        The window takes the questions in (MainWindow.watch_unlock): this only shows them. """
        self.polling = None
        unlock = self.app.app_state.run.unlock
        if unlock is not None:
            if not unlock.shown.done:
                self.polling = self.after(POLL_DELAY, self.poll)
        # Built again only when what it shows has changed, so as not to clear a field being typed in
        shown = (unlock, unlock.shown.waiting, unlock.shown.message,
                 unlock.shown.done) if unlock else None
        if shown != self.shown:
            self.shown = shown
            self.build(unlock)

    def build(self, unlock):
        """ The message, then the question waiting for an answer, or what the sequence is doing. """
        for child in self.winfo_children():
            child.destroy()
        if unlock is None:
            self.configure(height=1)
            return
        tk.Frame(self, bg=self.background, height=12).pack(fill="x")
        colors = self.app.colors
        message = unlock.shown.message
        if message is not None:
            self.text(message.text, colors.text_error if message.kind == "error"
                      else colors.text_secondary)
        question = unlock.shown.waiting
        if question is None:
            self.build_status(unlock)
        elif question.kind == "secret":
            self.build_secret(unlock, question)
        elif question.kind == "file":
            self.text(question.title, colors.text_primary)
            self.buttons(("Choose…", lambda: self.choose_file(unlock, question)),
                         ("Cancel", lambda: unlock.answer(None)))
        else:
            self.text("Other members of the RAID set were found beside this image.",
                      colors.text_primary)
            self.buttons(("Review…", lambda: unlock.answer(
                confirm_found_members(self.winfo_toplevel(), question.extra))),
                         ("Cancel", lambda: unlock.answer(None)))

    def build_status(self, unlock):
        """ No question: the sequence is still reading the source, or it has ended. """
        colors = self.app.colors
        if not unlock.shown.done:
            self.text("Opening the source…", colors.text_secondary)
        elif unlock.result is not None and unlock.shown.locked:
            self.text("Opened. Locked volumes are not read.", colors.text_secondary)
        elif unlock.result is not None:
            self.text("Opened: ready to be read.", colors.text_secondary)
        else:
            self.text("Not opened.", colors.text_error)
            self.buttons(("Try again", self.try_again))

    def build_secret(self, unlock, question):
        """ A password to type, hidden unless shown, with the question above it. """
        self.text(question.text, self.app.colors.text_primary)
        line = tk.Frame(self, bg=self.background)
        line.columnconfigure(0, weight=1)
        line.pack(fill="x", pady=(8, 0))
        field = LabeledEntry(line, self.app, Field(question.title, self.secret),
                             background=self.background)
        field.entry.configure(show=HIDDEN)
        field.entry.bind("<Return>", lambda _event: self.send_secret(unlock))
        field.grid(row=0, column=0, sticky="ew")
        field.box.update_idletasks()
        eye_button(line, self.app, field.entry, field.box.winfo_reqheight()).grid(
            row=0, column=1, sticky="s", padx=(8, 0))
        self.buttons(("Unlock", lambda: self.send_secret(unlock)),
                     ("Cancel", lambda: unlock.answer(None)))

    def text(self, text, color):
        """ A line of text, on as many lines as it needs. """
        caption = Caption(self, self.app, text, self.background)
        caption.configure(fg=color)
        caption.pack(fill="x", pady=(0, 6))

    def buttons(self, *buttons):
        """ A row of buttons, each given as (text, command). Any answer shows what comes next at once. """
        row = tk.Frame(self, bg=self.background)
        row.pack(fill="x", pady=(8, 0))
        for text, command in buttons:
            OutlineButton(row, self.app, text=text, command=lambda command=command: self.then(command),
                          style="in_card").pack(side="left", padx=(0, 8))

    def then(self, command):
        """ Run a button's command, then show at once what it changed. """
        command()
        self.app.app_state.poll_unlock()
        self.restart()

    def send_secret(self, unlock):
        """ Give the password typed to the sequence, and forget it here. """
        secret = self.secret.get()
        self.secret.set("")
        unlock.answer(secret)
        self.app.app_state.poll_unlock()
        self.restart()

    def choose_file(self, unlock, question):
        """ Answer with the file chosen in a file dialog, None when it is cancelled. """
        path = filedialog.askopenfilename(parent=self.winfo_toplevel(), title=question.title,
                                          filetypes=question.extra)
        unlock.answer(path or None)

    def try_again(self):
        """ Run the sequence of the same source again. """
        self.app.app_state.start_unlock()
