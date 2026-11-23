"""
The Case screen: the data of the case, which only decorates the header of the report.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from leapp_functions import leapp
from leapp_functions.app.gui import images, themes
from leapp_functions.app.gui.app_state import CASE_KEYS
from leapp_functions.app.gui.custom_widgets import (GAP, Caption, Card, Field, FileField,
                                                    LabeledEntry, OutlineButton, two_columns,
                                                    wrap_to_width)
from leapp_functions.data_sources.json_files import (get_json_file_content,
                                                     save_content_to_json_file)

# Report preview colors whatever the window's palette is.
PAPER = "#FFFFFF"
INK = "#212529"
GRID = "#DEE2E6"
HINT = "#6C757D"

CAPTION = "The Case Information of the HTML report's first page. Updates as you type."
EMPTY = "No case data"
KEY_WIDTH = 78
VALUE_WIDTH = 150
LOGO_MIN_WIDTH, LOGO_MAX_WIDTH = 50, 200
LOGO_SHARE = 4
LOGO_MAX_HEIGHT = 120
MAX_SHOWN = 240


class CaseScreen(tk.Frame):
    """ The fields of the Case screen, which edit the variables of the window's state. """

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors.main_bg)
        self.app = app
        self.state = app.app_state

        main, side = two_columns(self, app)
        self.build_cards(main)
        self.build_buttons(main)
        self.build_preview(side)
        self.watch_case()

    def build_cards(self, main):
        """ The cards containing the fields, one under another. """
        case = self.state.case
        cards = (
            ("CASE", None, (
                Field("Case number", case.number),)),
            ("AGENCY", 300, (
                Field("Agency / unit", case.agency),
                Field("Logo", case.logo_path, pick=self.choose_logo))),
            ("EXAMINER", 200, (
                Field("Examiner", case.examiner),
                Field("Notes", case.notes))),
        )
        for row, (title, first_width, fields) in enumerate(cards):
            card = Card(main, self.app, title)
            card.grid(row=row, column=0, sticky="ew", pady=(0 if row == 0 else GAP, 0))
            if first_width is None:
                card.body.columnconfigure(0, weight=1)
            else:
                card.body.columnconfigure(0, minsize=first_width,
                                          weight=1 if len(fields) > 1 else 0)
                card.body.columnconfigure(1, weight=2)
            for column, field in enumerate(fields):
                widget_class = FileField if field.pick else LabeledEntry
                widget = widget_class(card.body, self.app, field)
                widget.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else GAP, 0))

    def build_buttons(self, main):
        """ Case data buttons. """
        files = tk.Frame(main, bg=self.app.colors.main_bg)
        files.grid(row=3, column=0, sticky="w", pady=(GAP, 0))
        buttons = {}
        for text, command in (("Load case data", self.load_case), ("Save case data", self.save_case),
                              ("Clear", self.clear_case)):
            buttons[text] = OutlineButton(files, self.app, text=text, command=command, style="quiet")
            buttons[text].pack(side="left", padx=(0, 10))
        self.clear_button = buttons["Clear"]

    def build_preview(self, side):
        """ The card on the right: what the fields give in the Case Information part of the HTML report. """
        self.preview = ReportPreview(side, self.app)
        self.preview.pack(fill="x")

    def watch_case(self):
        """ Clear is only available while a field holds something. """
        self.traces = [(variable, variable.trace_add("write", self.update_clear))
                       for variable in vars(self.state.case).values()]
        self.bind("<Destroy>", self.remove_traces)
        self.update_clear()

    def update_clear(self, *_args):
        """ Let Clear be used unless every field is empty. """
        self.clear_button.set_enabled(not self.state.case_is_empty())

    def remove_traces(self, event):
        """ Stop watching the variables. """
        if event.widget is self:
            for variable, trace in self.traces:
                variable.trace_remove("write", trace)

    def clear_case(self):
        """ Empty every field once the user has confirmed. """
        if messagebox.askyesno("Clear case data", "Clear every field of the case data?",
                               icon="warning", default="no", parent=self.winfo_toplevel()):
            self.state.clear_case()

    def choose_logo(self):
        """ Ask for a picture and take it as the agency logo. """
        path = filedialog.askopenfilename(
            parent=self.winfo_toplevel(), title="Choose the agency logo",
            filetypes=(("Pictures", "*.png *.jpg *.jpeg *.gif"),))
        if not path:
            return
        try:
            self.state.set_logo(path)
        except ValueError as error:
            messagebox.showerror("Agency logo", str(error), parent=self.winfo_toplevel())

    def save_case(self):
        """ Write the case data to a case data file. """
        path = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(), title="Save the case data",
            filetypes=(("LEAPP Case Data", f"*{leapp.casedata_extension}"),),
            defaultextension=leapp.casedata_extension)
        if not path:
            return
        saved = save_content_to_json_file(
            path, {"leapp": "case_data", "case_data_values": self.state.case_values()})
        if saved:
            messagebox.showinfo("Save case data", f"Case data saved: {path}",
                                parent=self.winfo_toplevel())
        else:
            messagebox.showerror("Save case data", f"Unable to write {path}.",
                                 parent=self.winfo_toplevel())

    def load_case(self):
        """ Fill the fields from a case data file. """
        path = filedialog.askopenfilename(
            parent=self.winfo_toplevel(), title="Load case data",
            filetypes=(("LEAPP Case Data", f"*{leapp.casedata_extension}"),))
        if not path:
            return
        content = get_json_file_content(path)
        if not isinstance(content, dict) or content.get("leapp") != "case_data":
            message = "File was not a valid case data file"
        elif not isinstance(content.get("case_data_values"), dict):
            message = "File was not a valid case data file: invalid format"
        else:
            self.state.load_case_values(content["case_data_values"])
            return
        messagebox.showerror("Load case data", message, parent=self.winfo_toplevel())


class LogoCell(tk.Frame):
    """ The cell of the table that holds the agency logo. """

    def __init__(self, parent):
        super().__init__(parent, bg=PAPER)
        self.label = tk.Label(self, bg=PAPER, borderwidth=0)
        self.label.pack(expand=True, padx=6, pady=4)
        self.picture = None
        self.key = None

    def show(self, encoded, width):
        """ Show the picture of a base64 string. """
        if (encoded, width) != self.key:
            self.key = (encoded, width)
            self.picture = images.from_base64(encoded, width, LOGO_MAX_HEIGHT) if encoded else None
            self.label.configure(image=self.picture or "")
        return self.picture is not None


class ReportPreview(tk.Frame):
    """ A white sheet showing, as the report does, a row for each field of the case that is filled in. """

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors.main_bg)
        self.case = app.app_state.case
        card = Card(self, app, "REPORT PREVIEW", accent=True)
        card.pack(fill="x")

        sheet = tk.Frame(card.body, bg=PAPER, highlightthickness=1, highlightbackground=GRID,
                         highlightcolor=GRID)
        sheet.pack(fill="x")
        inner = tk.Frame(sheet, bg=PAPER)
        inner.pack(fill="x", padx=12, pady=12)
        tk.Label(inner, text="Case Information", anchor="w", bg=PAPER, fg=INK,
                 font=themes.sans(15, "bold")).pack(fill="x", pady=(0, 8))
        self.table = tk.Frame(inner, bg=GRID)
        self.table.pack(fill="x")
        self.rows = tk.Frame(self.table, bg=GRID)
        self.rows.pack(fill="x", padx=(0, 1), pady=(0, 1))
        self.rows.columnconfigure(2, weight=1)
        self.build_rows()
        self.rows.bind("<Configure>", self.refresh_logo)

        Caption(card.body, app, CAPTION, card.background).pack(fill="x", pady=(10, 0))

        # What is typed shows at once
        self.traces = [(variable, variable.trace_add("write", self.refresh))
                       for variable in vars(self.case).values()]
        self.bind("<Destroy>", self.remove_traces)
        self.refresh()

    def build_rows(self):
        """ A row for each field of the report. """
        self.empty = tk.Label(self.table.master, text=EMPTY, anchor="w", justify="left", width=1,
                              bg=PAPER, fg=HINT, font=themes.sans(11))
        self.empty.bind("<Configure>", wrap_to_width)
        fields = [name for name in CASE_KEYS.values() if not name.startswith("logo_")]

        # The logo is in a cell of its own, as high as all the rows
        self.logo_cell = LogoCell(self.rows)
        self.logo_cell.grid(row=1, column=0, rowspan=len(fields), sticky="nsew", padx=(1, 0), pady=(1, 0))
        self.logo_cell.grid_remove()

        self.cells = {}
        for line, name in enumerate(fields):
            key = next(key for key, field in CASE_KEYS.items() if field == name)
            cells = []
            for column, wrap in enumerate((KEY_WIDTH, VALUE_WIDTH)):
                cell = tk.Frame(self.rows, bg=PAPER)
                cell.grid(row=line + 1, column=column + 1, sticky="nsew", padx=(1, 0), pady=(1, 0))
                label = tk.Label(cell, text=key if column == 0 else "", anchor="w", justify="left",
                                 wraplength=wrap, bg=PAPER, fg=INK, font=themes.sans(11))
                label.pack(fill="both", expand=True, padx=6, pady=4)
                if column == 1:
                    label.configure(width=1)
                    label.bind("<Configure>", wrap_to_width)
                cells.append((cell, label))
            self.cells[name] = cells

    def refresh_logo(self, *_args):
        """ Show the agency logo in its cell, or hide the cell when there is no picture. """
        width = min(max(self.rows.winfo_width() // LOGO_SHARE - 14, LOGO_MIN_WIDTH), LOGO_MAX_WIDTH)
        shown = self.logo_cell.show(self.case.logo_base64.get(), width)
        if shown:
            self.logo_cell.grid()
        else:
            self.logo_cell.grid_remove()
        return shown

    def refresh(self, *_args):
        """ Show a row for each field with something in it, in the order of the report. """
        filled = self.refresh_logo()
        for row, (name, cells) in enumerate(self.cells.items(), start=1):
            value = getattr(self.case, name).get().strip()
            self.rows.rowconfigure(row, weight=1 if value else 0)
            if len(value) > MAX_SHOWN:
                value = value[:MAX_SHOWN].rstrip() + "…"
            for cell, _label in cells:
                if value:
                    cell.grid()
                else:
                    cell.grid_remove()
            cells[1][1].configure(text=value)
            filled = filled or bool(value)
        lines = GRID if any(getattr(self.case, name).get().strip() for name in self.cells) else PAPER
        self.table.configure(bg=lines)
        self.rows.configure(bg=lines)
        if filled:
            self.empty.pack_forget()
            self.table.pack(fill="x")
        else:
            self.table.pack_forget()
            self.empty.pack(fill="x")

    def remove_traces(self, event):
        """ Stop watching the variables. """
        if event.widget is self:
            for variable, trace in self.traces:
                variable.trace_remove("write", trace)
