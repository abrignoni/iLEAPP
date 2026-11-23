"""
The Review screen: what the run will read and write, before it starts.
"""

import os
import tkinter as tk
from tkinter import ttk

from leapp_functions.app import artifact_list
from leapp_functions.app.gui import themes
from leapp_functions.app.gui.app_state import SECRETS, is_waiting
from leapp_functions.app.gui.artifacts import unknown_text
from leapp_functions.app.gui.custom_widgets import (GAP, Caption, Card, mark_line, two_columns,
                                                    wrap_to_width)
from leapp_functions.app.output import default_output_folder_name
from scripts.raw_image import FOUND_AUTOMATICALLY, RawInput, repeat_note

CHECK_DELAY = 1000
KEY_WIDTH = 104
ROW_GAP = 8
NONE = "None"
HASH_TEXT = "Hash staged files (SHA-256) and record the times the evidence gives them"
HASH_HINT = ("Written to LAVA and to _TSV Exports. A folder or a single file gives the hashes "
             "only, no times.")


def slow_selected(artifacts):
    """ How many of the artifacts selected are slow or large. """
    return sum(not artifact.default and artifact.name in artifacts.selected
               for artifact in artifacts.listed)


def artifacts_text(artifacts):
    """ How many artifacts will run, and how many of them are slow or large. """
    text = f"{len(artifacts.selected)} of {len(artifacts.listed)} selected"
    slow = slow_selected(artifacts)
    return f"{text} · {slow} slow or large" if slow else text


def opened_images(state):
    """ What the source screen has opened for a disk image (RawInput). """
    unlock = state.run.unlock
    opened = unlock.result if unlock is not None else None
    return opened if isinstance(opened, RawInput) else None


def unread_members_text(state):
    """ When RAID members were found beside the image given and the examiner chose to read the
    image alone: how many will not be read. """
    opened = opened_images(state)
    search = opened.search if opened is not None else None
    if search is None or search.used or not search.added:
        return ""
    return (f"RAID members found and not read: {len(search.added)}. Only "
            f"{os.path.basename(search.given)} will be read.")


def extraction_text(state):
    """ The paths the run will read, one per line. """
    opened = opened_images(state)
    if opened is None:
        return "\n".join(state.source_paths())
    found = set(opened.found)
    lines = [path + (f" ({FOUND_AUTOMATICALLY})" if path in found else "") for path in opened.paths]
    if opened.search is not None and not opened.search.found:
        lines.append(f"({opened.search.outcome()})")
    lines += [f"({path} was given too and is {repeat_note(path, other)})"
              for path, other in opened.repeats]
    return "\n".join(lines)


def summary_rows(state):
    """ The lines of the summary: (key, value). """
    run, case = state.run, state.case
    filled = [variable.get() for variable in (case.number, case.agency, case.examiner) if variable.get()]
    return (("Case", " · ".join(filled) or "No case data"),
            ("Extraction", extraction_text(state)),
            ("Read as", run.detected.label),
            *((name.capitalize(), variable.get() or NONE) for name, variable in run.secrets.items()),
            ("Artifacts", artifacts_text(state.artifacts)),
            ("Profile", artifact_list.profile_for_report(state.artifacts) or NONE),
            ("Output folder", run.output.get().strip()),
            ("Report folder", run.folder_name.get().strip() or default_output_folder_name()))


def profile_notices(artifacts):
    """ What differs between the profile loaded, if any, and what will run. """
    profile = artifacts.profile
    if profile is None:
        return []
    if artifact_list.profile_for_report(artifacts) is None:
        name = os.path.basename(profile.path)
        return [f"The selection differs from the profile {name}: the report will not name it."]
    return [unknown_text(profile.unknown)] if profile.unknown else []


def notices(state):
    """ What the examiner should know before the run. """
    run, artifacts = state.run, state.artifacts
    problem = state.missing_for("run")
    attention = [run.detected.note] if run.detected.note else []
    if run.unlock is not None and run.unlock.shown.locked:
        attention.append("Locked volumes are not read.")
    if unread_members_text(state):
        attention.append(unread_members_text(state))
    if slow_selected(artifacts):
        attention.append(f"Slow or large artifacts selected: {slow_selected(artifacts)}. "
                         "The run may take much longer.")
    attention += profile_notices(artifacts)

    lines = [("attention", text) for text in attention]
    if problem:
        lines.insert(0, ("todo" if is_waiting(problem) else "problem", problem))
    if not lines:
        lines.append(("ok", "Nothing needs your attention."))
    if state.case_is_empty():
        lines.append(("optional", "No case data: the report only gives the details of the run."))
    for field in SECRETS.fields if SECRETS else ():
        if not run.secrets[field["name"]].get():
            lines.append(("optional", field["if_absent"]))
    return lines


class ReviewScreen(tk.Frame):
    """ The summary of the run. """

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors.main_bg)
        self.app = app
        self.problem = app.app_state.missing_for("run")
        main, side = two_columns(self, app)
        self.build_summary(main)
        self.build_options(main)
        self.notices_card = Card(side, app, "BEFORE YOU RUN", accent=True)
        self.notices_card.pack(fill="x")
        self.notices_card.body.columnconfigure(1, weight=1)
        self.show_notices()
        self.check_id = self.after(CHECK_DELAY, self.check)
        self.bind("<Destroy>", lambda _event: self.after_cancel(self.check_id))

    def check(self):
        """ Look at the disk. When the answer changes, the card, the steps and the bar are told. """
        problem = self.app.app_state.missing_for("run")
        if problem != self.problem:
            self.problem = problem
            self.show_notices()
            self.app.app_state.on_change()
        self.check_id = self.after(CHECK_DELAY, self.check)

    def build_summary(self, main):
        """ The card with what the run will read and write. """
        colors = self.app.colors
        card = Card(main, self.app, "RUN SUMMARY")
        card.grid(row=0, column=0, sticky="ew")
        card.body.columnconfigure(0, minsize=KEY_WIDTH)
        card.body.columnconfigure(1, weight=1)
        for row, (key, value) in enumerate(summary_rows(self.app.app_state)):
            tk.Label(card.body, text=key, anchor="w", bg=card.background, fg=colors.text_secondary,
                     font=themes.sans(12)).grid(row=row, column=0, sticky="nw", pady=(ROW_GAP, 0))
            shown = tk.Label(card.body, text=value, anchor="w", justify="left", width=1,
                             bg=card.background, fg=colors.text_primary, font=themes.sans(12))
            shown.grid(row=row, column=1, sticky="ew", padx=(12, 0), pady=(ROW_GAP, 0))
            shown.bind("<Configure>", wrap_to_width)

    def build_options(self, main):
        """ The card with the the command line's --hash. """
        card = Card(main, self.app, "OPTIONS")
        card.grid(row=1, column=0, sticky="ew", pady=(GAP, 0))
        ttk.Checkbutton(card.body, text=HASH_TEXT, style="Card.TCheckbutton",
                        variable=self.app.app_state.run.hash_files).pack(anchor="w", pady=(4, 0))
        Caption(card.body, self.app, HASH_HINT, card.background).pack(fill="x", pady=(4, 0))

    def show_notices(self):
        """ What the examiner should know before starting, built again from the state. """
        for child in self.notices_card.body.winfo_children():
            child.destroy()
        for row, (status, text) in enumerate(notices(self.app.app_state)):
            mark_line(self.notices_card, self.app, row, status, text)
