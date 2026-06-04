"""Output utilities for report folder setup, GUI logging, and screen log export."""

import sys
from datetime import datetime
from pathlib import Path


class GuiWindow:
    """Holds the GUI window handle when running with the Tkinter interface."""
    window_handle = None  # static variable

    @staticmethod
    def set_progress_bar(n):
        """Set the GUI progress bar value if a window handle is available.
        Args:
            n (int | float): Progress value to display.
        """
        if GuiWindow.window_handle:
            progress_bar = GuiWindow.window_handle.nametowidget("progress_bar_frame.progress_bar")
            progress_bar.config(value=n)


class OutputParameters:
    """Stores shared output paths and initializes report directory structure.

    Class Attributes:
        nl (str): Newline marker used by HTML screen output.
        screen_output_file_path (Path | str): Path to the main screen output log.
    """
    # static parameters
    nl = "\n"
    screen_output_file_path = ""

    def __init__(self, output_folder, custom_folder_name=None):
        """Create output paths and required subfolders for an iLEAPP report.

        Args:
            output_folder (str | Path): Base folder where the report folder is created.
            custom_folder_name (str | None): Optional explicit report folder name.
        """
        now = datetime.now()
        currenttime = str(now.strftime("%Y-%m-%d_%A_%H%M%S"))
        if custom_folder_name:
            folder_name = custom_folder_name
        else:
            folder_name = "iLEAPP_Reports_" + currenttime
        self.output_folder_base = Path(output_folder).joinpath(folder_name)
        self.data_folder = Path(self.output_folder_base).joinpath("data")
        self.media_folder = Path(self.output_folder_base).joinpath("media")
        self.html_media_folder = Path(self.output_folder_base).joinpath("_HTML", "media")
        OutputParameters.screen_output_file_path = Path(self.output_folder_base).joinpath(
            "_HTML", "_Script_Logs", "Screen_Output.html")
        OutputParameters.screen_output_file_path_devinfo = Path(self.output_folder_base).joinpath(
            "_HTML", "_Script_Logs", "DeviceInfo.html")
        OutputParameters.screen_output_file_path_lava_only = Path(self.output_folder_base).joinpath(
            "_HTML", "_Script_Logs", "Lava_only_artifacts_log.html")

        Path.mkdir(Path(self.output_folder_base).joinpath("_HTML", "_Script_Logs"))
        Path.mkdir(self.data_folder)
        Path.mkdir(self.media_folder, exist_ok=True)
        Path.mkdir(self.html_media_folder, exist_ok=True)


def redirect_logs_in_gui(log_text):
    """Return a writer function that redirects text to a GUI log widget.

    Args:
        log_text: Tkinter text widget used for log display.

    Returns:
        callable: Function that accepts a string and appends it to the widget.
    """
    def redirect_logs(string):
        """Append text to the GUI log widget and keep it scrolled to the end."""
        log_text.insert("end", string)
        log_text.see("end")
        log_text.update()
    return redirect_logs


def logfunc(message=""):
    """Write a message to GUI log, HTML screen log, and standard output.

    Args:
        message (str): Text to log.
    """
    if GuiWindow.window_handle:
        log_text = GuiWindow.window_handle.nametowidget("logs_frame.log_text")
        sys.stdout.write = redirect_logs_in_gui(log_text)

    if OutputParameters.screen_output_file_path:
        with open(OutputParameters.screen_output_file_path, "a", encoding="utf8") as a:
            a.write(message + "<br>" + OutputParameters.nl)

    print(message)
