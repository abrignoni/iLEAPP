"""
What the window shows, kept apart from the widgets that show it.
The widgets are destroyed and built again whenever the palette changes, so anything that
has to outlive them, such as the case data typed so far, lives here.
"""

import base64
import os
import tkinter as tk
from types import SimpleNamespace

from leapp_functions import leapp
from leapp_functions.app import input_type
from leapp_functions.app.disk import FILE, FOLDER, MISSING, PENDING, SILENT, ask, path_status
from leapp_functions.app.platform import validate_filename
from leapp_functions.app.unlock import UNLOCKERS, Unlock
from scripts.filetype import guess_mime
from scripts.raw_image import selected_paths, selection_text

ORDER = ("case", "source", "artifacts", "review", "run", "results")

SECRETS = getattr(leapp, "secrets", None)
STAGE_OF = {"review": "run"}
DETECT_WAIT = 0.3
NO_ANSWER = "The {} does not answer: its drive may be disconnected."
WAITING = "Waiting for the {} to answer."


def is_waiting(message):
    """ A message only says if that a drive has not answered yet. """
    return message.startswith(WAITING.partition("{")[0])


def unanswered(status, name):
    """ What to say of a path, given by its name, whose drive has not answered; else "". """
    if status == PENDING:
        return WAITING.format(name)
    return NO_ANSWER.format(name) if status == SILENT else ""


def report_folder_problem(folder, name):
    """ Why the report cannot take this name in the output folder. """
    _valid, error = validate_filename(name)
    if error:
        return error
    status = path_status(os.path.join(folder, name))
    if status == MISSING:
        return ""
    return (unanswered(status, "output folder")
            or f"A folder named {name} is already in the output folder.")

CASE_KEYS = {"Case Number": "number", "Agency": "agency", "Agency Logo Path": "logo_path",
             "Agency Logo mimetype": "logo_mimetype", "Agency Logo base64": "logo_base64",
             "Examiner": "examiner", "Notes": "notes"}


def unlock_problem(unlock):
    """ Why the sequence that opens the source leaves it unread. """
    if unlock is None:
        return ""
    if not unlock.shown.done:
        return "The source is still being opened: see DETECTED."
    return "The source could not be opened: see DETECTED." if unlock.result is None else ""


class AppState:
    """ Tk variables that widgets can show and edit directly. """

    def __init__(self, on_change):
        self.on_change = on_change
        self.step = "case"
        self.left = set()  # the steps the user has moved on from
        self.case = SimpleNamespace(number=tk.StringVar(),
                                    agency=tk.StringVar(), examiner=tk.StringVar(),
                                    notes=tk.StringVar(), logo_path=tk.StringVar(),
                                    logo_mimetype=tk.StringVar(), logo_base64=tk.StringVar())

        self.run = SimpleNamespace(source=tk.StringVar(), output=tk.StringVar(), selection=[],
                                   folder_name=tk.StringVar(),
                                   single_file=tk.BooleanVar(), hash_files=tk.BooleanVar(),
                                   detected=None, unlock=None, worker=None,
                                   secrets={field["name"]: tk.StringVar()
                                            for field in (SECRETS.fields if SECRETS else ())})
        self.artifacts = SimpleNamespace(loader=None, listed=[], selected=set(), search="")

        self.run_status = "idle"  # "idle" until a run starts, then "running", then "finished"

    def case_values(self):
        """ Return case data using the keys expected in a case data file."""
        return {key: getattr(self.case, name).get() for key, name in CASE_KEYS.items()}

    def load_case_values(self, values):
        """ Fill case data fields from CASE_KEYS dictionary. """
        for key, name in CASE_KEYS.items():
            getattr(self.case, name).set(str(values.get(key, "")))

    def case_is_empty(self):
        """ Whether every field of the case data is empty. """
        return not any(self.case_values().values())

    def clear_case(self):
        """ Empty every field of the case data. """
        self.load_case_values({})

    def set_logo(self, path):
        """
        Picture of the agency logo: its path, its MIME type and its content in base64.
        Raises:
            ValueError: the file cannot be read or is not a picture. The case data is left as it was.
        """
        try:
            mimetype = guess_mime(path)
            with open(path, "rb") as logo_file:
                encoded = base64.b64encode(logo_file.read()).decode("ascii")
        except OSError as error:
            raise ValueError(f"Unable to read {path}: {error.strerror}") from error
        if not mimetype or not mimetype.startswith("image/"):
            raise ValueError("The selected file is not a valid picture file.")
        self.case.logo_path.set(path)
        self.case.logo_mimetype.set(mimetype)
        self.case.logo_base64.set(encoded)

    def set_source(self, paths):
        """ Show the files picked in the source field: one path, or the first and how many more. """
        paths = list(paths)
        self.run.selection = paths if len(paths) > 1 else []
        self.run.source.set(selection_text(paths))

    def is_one_file(self):
        """ Whether the source is one file: only then can it be read as a single file. """
        paths = self.source_paths()
        return len(paths) == 1 and path_status(paths[0]) == FILE

    def source_paths(self):
        """ The input the source field stands for. """
        return [path for path in selected_paths(self.run.source.get().strip(), self.run.selection)
                if path]

    def detect_source(self):
        """ Look at the source. """
        paths, single_file = self.source_paths(), self.run.single_file.get()
        detected = ask(("detect", tuple(paths), single_file),
                       lambda: input_type.detect(paths, single_file=single_file),
                       wait=DETECT_WAIT, fresh=0)
        if detected == SILENT:
            detected = input_type.NO_ANSWER
        elif detected == PENDING:
            detected = input_type.LOOKING
        if detected != self.run.detected:
            self.run.detected = detected
            self.start_unlock()
            self.on_change()

    def start_unlock(self):
        """ Open the source on a worker thread when opening it may ask for something (see
        UNLOCKERS). The sequence of the previous source is stopped. """
        if self.run.unlock is not None:
            self.run.unlock.cancel()
            self.run.unlock = None
        detected = self.run.detected
        unlocker = UNLOCKERS.get(detected.kind) if detected is not None else None
        sequence = unlocker(self.source_paths(), detected) if unlocker else None
        if sequence is not None:
            self.run.unlock = Unlock(sequence)

    def poll_unlock(self):
        """ Take in what the sequence that opens the source has asked. When it ends, the source
        is done or not: the window is told. """
        unlock = self.run.unlock
        if unlock is None or unlock.shown.done:
            return
        unlock.poll()
        if unlock.shown.done:
            self.on_change()

    def missing_for_source(self):
        """ Why the source cannot be read before running processes. """
        detected = self.run.detected
        if detected is None:
            return "Select an extraction first: nothing can be parsed without one."
        if detected == input_type.LOOKING:
            return WAITING.format("extraction")
        if not detected.kind:
            return detected.problem
        statuses = [path_status(path) for path in self.source_paths()]
        for status in statuses:
            if unanswered(status, "extraction"):
                return unanswered(status, "extraction")
        if MISSING in statuses:
            return "The extraction no longer exists."
        return unlock_problem(self.run.unlock)

    def stage(self):
        """The step of the five under the header that the screen on show belongs to."""
        return STAGE_OF.get(self.step, self.step)

    def neighbour(self, offset):
        """The screen before or after the one on show, None at either end."""
        index = ORDER.index(self.step) + offset
        return ORDER[index] if 0 <= index < len(ORDER) else None

    def previous_open(self):
        """ The nearest screen before the one on show that can be opened otherwise None. """
        for step in reversed(ORDER[:ORDER.index(self.step)]):
            if self.can_go(step):
                return step
        return None

    def missing_for(self, step):
        """ What the user must still do before moving to a step. """
        if step not in ("artifacts", "review", "run"):
            return ""
        missing = self.missing_for_source() or self.missing_for_secrets() or self.missing_for_output()
        if not missing and step != "artifacts" and not self.artifacts.selected:
            return "No artifact selected."
        return missing

    def missing_for_output(self):
        """ Why the report cannot be written. An empty folder name stands for the automatic one. """
        folder = self.run.output.get().strip()
        if not folder:
            return "Choose an output folder."
        status = path_status(folder)
        if unanswered(status, "output folder"):
            return unanswered(status, "output folder")
        if status != FOLDER:
            return "This output folder does not exist."
        name = self.run.folder_name.get().strip()
        return report_folder_problem(folder, name) if name else ""

    def missing_for_secrets(self):
        """ A file chosen to decrypt apps that is no longer there. """
        for name, variable in self.run.secrets.items():
            status = path_status(variable.get()) if variable.get() else FILE
            if unanswered(status, f"{name} file"):
                return unanswered(status, f"{name} file")
            if status != FILE:
                return f"The {name} file no longer exists."
        return ""

    def can_go(self, step):
        """
        Whether the user may move to a step, given by its key.
        Case and Source are always open. Artifacts and Run need what missing_for() lists, and
        Results a run that has taken place. Once a run has started, only its screens can be
        reached: a second run in the same process would inherit what the first one has left.
        """
        if self.run_status == "running":
            return step == "run"
        if self.run_status == "finished":
            return step in ("run", "results")
        if step in ("artifacts", "review", "run"):
            return not self.missing_for(step)
        return step != "results"

    def completed(self):
        """ The steps done, shown with a tick.
        The case data is optional: the step is done once the user has moved on from it.
        A run that failed is not done, one the user stopped is.
        """
        done = set()
        if "case" in self.left or not self.case_is_empty():
            done.add("case")
        if not self.missing_for("artifacts"):
            done.add("source")
        if "artifacts" in self.left and not self.missing_for("review"):
            done.add("artifacts")
        if self.run_status == "finished" and self.run.worker.shown.outcome != "failed":
            done.add("run")
        return done
