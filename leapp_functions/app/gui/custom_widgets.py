"""Custom widgets for the new LEAPPs GUI window that Tk does not offer as they are."""

from collections import namedtuple
from pathlib import PureWindowsPath
import sys
import tkinter as tk
from tkinter import ttk

from leapp_functions.app.gui import images, themes


BORDER = 2
TOOLTIP_DELAY = 500
TOOLTIP_WIDTH = 520
ENTRY_PADX = 12
ENTRY_PADY = 4
MAIN_WIDTH = 640
SIDE_WIDTH = 320
GAP = 14
MARGIN = 16
MARK_SIZE = 16
WHEEL_STEP = 24
WHEEL_NOTCH = 1 if sys.platform == "darwin" and tk.TkVersion < 8.7 else 120
MARKS = {"ok": ("circle-check", "text_primary"), "todo": ("circle", "text_primary"),
         "attention": ("alert-triangle", "text_primary"), "problem": ("circle-x", "text_error"),
         "optional": ("circle-minus", "text_secondary")}

Field = namedtuple("Field", "label variable mono pick", defaults=(False, None))


BUTTON_STYLES = {"outline": "Primary.TButton", "filled": "Filled.TButton",
                 "quiet": "Quiet.TButton", "in_card": "Field.TButton",
                 "chosen": "Chosen.TButton"}


class OutlineButton(tk.Frame):
    """ A button with a border round it, on the window's background. Its style is one of:
    - "outline": the colour of the header for its border and its text, the default;
    - "filled": the colour of its border for its background instead;
    - "quiet": for the content of a screen: a grey border, no fill;
    - "in_card": for next to the inputs of a card: a grey fill;
    - "chosen": an "in_card" button that shows the choice made, filled with the colour of the
      header.
    The other options, such as text and command, are those of the ttk.Button inside.
    """
    def __init__(self, parent, app, style="outline", **button_options):
        self.colors = app.colors
        self.border = self.border_of(style)
        super().__init__(parent, bg=self.border)
        self.button = ttk.Button(self, style=BUTTON_STYLES[style], **button_options)
        self.button.pack(fill="both", expand=True, padx=BORDER, pady=BORDER)

    def border_of(self, style):
        """ The border colour of a style. """
        colors = self.colors
        return colors.button_border if style in ("quiet", "in_card") else colors.header_bg

    def set_style(self, style):
        """ Change the style of the button. """
        self.border = self.border_of(style)
        self.button.configure(style=BUTTON_STYLES[style])
        self.configure(bg=self.border)

    def set_text(self, text):
        """ Set the text of the button. """
        self.button.configure(text=text)

    def set_enabled(self, enabled):
        """ Let the button be used or not. """
        self.button.state(["!disabled" if enabled else "disabled"])
        self.configure(bg=self.border if enabled else self.colors.line)

    def is_enabled(self):
        """ Whether the button can be used. """
        return self.button.instate(["!disabled"])

    def invoke(self):
        """ Click the button, as the user would. Does nothing if it is disabled."""
        self.button.invoke()


# Time for the window manager to move the focus before it is given back, in milliseconds.
FOCUS_DELAY = 50


def open_menu(menu, button):
    """ Open a menu under its button. """
    x, y = button.winfo_rootx(), button.winfo_rooty() + button.winfo_height()
    if menu.tk.call("tk", "windowingsystem") != "x11":
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()
        return

    window = button.winfo_toplevel()
    bound = []
    before = window.focus_get()

    def give_focus_back():
        if not window.winfo_exists() or window.state() != "normal":
            return
        current = window.focus_displayof()
        if current is not None and current is not menu and current.winfo_toplevel() is not window:
            return
        if current is None or current is menu:
            current = before if before is not None and before.winfo_exists() else window
        current.focus_force()

    def close(event=None):
        if event is not None and event.type == tk.EventType.Configure and event.widget is not window:
            return
        while bound:
            sequence, identifier = bound.pop()
            window.unbind(sequence, identifier)
        menu.unpost()
        window.after(FOCUS_DELAY, give_focus_back)

    for sequence in ("<Configure>", "<Unmap>", "<ButtonPress>"):
        bound.append((sequence, window.bind(sequence, close, add="+")))
    menu.bind("<FocusOut>", close)
    menu.bind("<Unmap>", close)
    menu.post(x, y)
    menu.focus_set()


class Tooltip:
    """ Tooltip for inputs with long text. A tooltip that has no text is not shown. """

    def __init__(self, widgets, app, text):
        self.colors = app.colors
        self.text = text
        self.window = None
        self.pending = None
        for widget in widgets:
            widget.bind("<Enter>", lambda _event, widget=widget: self.schedule(widget), add="+")
            # Leaving, clicking and destroying the widget all end the tooltip
            for sequence in ("<Leave>", "<ButtonPress>", "<Destroy>"):
                widget.bind(sequence, lambda _event: self.hide(), add="+")

    def schedule(self, widget):
        """ Show the tooltip under the widget after a short rest of the pointer. """
        self.hide()
        self.pending = (widget, widget.after(TOOLTIP_DELAY, lambda: self.show(widget)))

    def show(self, widget):
        """ Open the window under the widget, unless there is nothing to show. """
        self.pending = None
        text = self.text()
        if not text:
            return
        colors = self.colors
        self.window = tk.Toplevel(widget)
        if sys.platform == "darwin":
            try:
                self.window.tk.call("::tk::unsupported::MacWindowStyle", "style", self.window,
                                    "help", "noShadow")
            except tk.TclError:
                self.window.overrideredirect(True)
        else:
            self.window.overrideredirect(True)
        # Colours reversed: the text's colour for the background and the window's for the text,
        # so that it is not mistaken for a button, an input or a card
        frame = tk.Frame(self.window, bg=colors.text_primary)
        frame.pack()
        tk.Label(frame, text=text, bg=colors.text_primary, fg=colors.main_bg, justify="left",
                 wraplength=TOOLTIP_WIDTH, font=themes.sans(11)).pack(padx=8, pady=5)
        self.window.geometry(
            f"+{widget.winfo_rootx()}+{widget.winfo_rooty() + widget.winfo_height() + 6}")

    def hide(self):
        """ Close the window, or cancel it if it has not appeared yet. """
        if self.pending is not None:
            widget, after_id = self.pending
            widget.after_cancel(after_id)
            self.pending = None
        if self.window is not None:
            self.window.destroy()
            self.window = None


class Card(tk.Frame):
    """A panel on the window's background, with a thin border and a small title in capitals.
    What goes in the card is placed in its body, the frame below the title.
    """

    def __init__(self, parent, app, title="", accent=False):
        colors = self.colors = app.colors
        self.background = colors.card_accent if accent else colors.card_bg
        border = colors.header_bg if accent else colors.border
        super().__init__(parent, bg=self.background, highlightthickness=BORDER if accent else 1,
                         highlightbackground=border, highlightcolor=border)
        inner = tk.Frame(self, bg=self.background)
        inner.pack(fill="both", expand=True, padx=16, pady=(10, 14))
        if title:
            tk.Label(inner, text=title, anchor="w", bg=self.background, fg=colors.text_primary,
                     font=themes.sans(12, "bold")).pack(fill="x", pady=(0, 4))
        self.body = tk.Frame(inner, bg=self.background)
        self.body.pack(fill="both", expand=True)


def two_columns(screen, app):
    """ Lay a screen out in a main column on the left and a side column on the right.
    Returns the frame of each, where the screen builds its widgets. """
    screen.columnconfigure(0, weight=2, uniform="column", minsize=MAIN_WIDTH)
    screen.columnconfigure(1, weight=1, uniform="column", minsize=SIDE_WIDTH)

    main = tk.Frame(screen, bg=app.colors.main_bg)
    main.grid(row=0, column=0, sticky="new")
    main.columnconfigure(0, weight=1)

    side = tk.Frame(screen, bg=app.colors.main_bg)
    side.grid(row=0, column=1, sticky="new", padx=(GAP, 0))
    return main, side


class ScrollArea(tk.Frame):
    """ The room for a screen. When it is smaller than what the screen asks, the screen is cut and
    a scroll bar appears. """

    def __init__(self, parent, app):
        colors = app.colors
        super().__init__(parent, bg=colors.main_bg)
        self.asked = (0, 0)
        self.offset = 0
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, minsize=MARGIN)

        self.view = tk.Frame(self, bg=colors.main_bg)
        self.view.grid(row=0, column=0, sticky="nsew")
        self.content = tk.Frame(self.view, bg=colors.main_bg)
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)
        self.content.place(x=0, y=0, relwidth=1)

        self.bar = ttk.Scrollbar(self, orient="vertical", style="Card.Vertical.TScrollbar",
                                 command=self.scroll)
        self.bar.grid(row=0, column=1, sticky="ns")
        self.bar.grid_remove()

        self.view.bind("<Configure>", self.view_changed)
        self.content.bind("<Configure>", lambda _event: self.content_changed())

    def show(self, screen):
        """ Show a screen from its top. """
        screen.grid(row=0, column=0, sticky="nsew")
        self.offset = 0
        self.update_idletasks()
        self.content_changed()

    def view_changed(self, event):
        """ The window has changed size. """
        self.content.rowconfigure(0, minsize=event.height)
        self.place_content()

    def content_changed(self):
        """ The screen may ask for another size. """
        asked = (self.content.winfo_reqwidth(), self.screen_height())
        if asked != self.asked:
            self.asked = asked
            self.view.configure(width=asked[0], height=asked[1])
        self.place_content()

    def screen_height(self):
        """ The height the screen asks for. """
        return max((child.winfo_reqheight() for child in self.content.winfo_children()), default=0)

    def place_content(self):
        """ Move the content to the offset, which is kept within what can be scrolled, and show
        the scroll bar if there is something to scroll. """
        height, shown = self.screen_height(), self.view.winfo_height()
        self.offset = max(0, min(self.offset, height - shown))
        self.content.place_configure(y=-self.offset)
        if height > shown:
            self.bar.grid()
            self.bar.set(self.offset / height, (self.offset + shown) / height)
        else:
            self.bar.grid_remove()

    def scroll(self, action, value, unit=None):
        """ What the scroll bar asks. """
        if action == "moveto":
            self.offset = int(float(value) * self.screen_height())
        else:
            step = self.view.winfo_height() if unit == "pages" else WHEEL_STEP
            self.offset += int(value) * step
        self.place_content()

    def holds(self, widget):
        """ Is a widget in the screen. """
        return isinstance(widget, tk.Misc) and str(widget).startswith(f"{self.content}.")

    def scrolls(self, widget):
        """ Does the screen scroll for a wheel used on this widget. """
        return self.holds(widget) and widget.winfo_class() not in ("Treeview", "Text")

    def wheel(self, event):
        """ The mouse wheel. """
        if self.scrolls(event.widget):
            if event.num in (4, 5):
                notches = 1 if event.num == 4 else -1
            else:
                notches = event.delta / WHEEL_NOTCH
            self.offset -= int(notches * WHEEL_STEP)
            self.place_content()

    def touchpad(self, event):
        """ Two fingers on a touchpad. """
        if self.scrolls(event.widget):
            _across, down = self.tk.splitlist(self.tk.call("tk::PreciseScrollDeltas", event.delta))
            self.offset -= self.tk.getint(down)
            self.place_content()

    def reveal(self, event):
        """ Bring into view the widget that has just got the focus. """
        if not self.holds(event.widget) or self.screen_height() <= self.view.winfo_height():
            return
        top = event.widget.winfo_rooty() - self.content.winfo_rooty()
        bottom = top + event.widget.winfo_height()
        if top < self.offset or bottom - top > self.view.winfo_height():
            self.offset = top
        elif bottom > self.offset + self.view.winfo_height():
            self.offset = bottom - self.view.winfo_height()
        self.place_content()


def wrap_to_width(event):
    """ Break the lines of a text where the room for it in the widget ends. """
    widget = event.widget
    margin = 2 * sum(widget.tk.getint(widget.cget(option)) for option in ("borderwidth", "padx", "highlightthickness"))
    wraplength = max(event.width - margin, 1)
    if widget.tk.getint(widget.cget("wraplength")) != wraplength:
        widget.configure(wraplength=wraplength)


class Caption(tk.Label):
    """ A small text in the secondary colour, on as many lines as it needs. """

    def __init__(self, parent, app, text, background):
        super().__init__(parent, text=text, anchor="w", justify="left", width=1, bg=background,
                         fg=app.colors.text_secondary, font=themes.sans(11))
        self.bind("<Configure>", wrap_to_width)


def mark_line(card, app, row, status, text):
    """ A line of a card: a mark, then the text in the colour of the mark. """
    icon, role = MARKS[status]
    color = getattr(app.colors, role)
    mark = tk.Label(card.body, bg=card.background, borderwidth=0)
    mark.image = images.load_icon(icon, MARK_SIZE, color)
    mark.configure(image=mark.image)
    mark.grid(row=row, column=0, sticky="nw", pady=(2 if row else 0, 0))
    caption = Caption(card.body, app, text, card.background)
    caption.configure(fg=color)
    caption.grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=(2 if row else 0, 0))


class LabeledEntry(tk.Frame):
    """A small label above a field to type in. """

    def __init__(self, parent, app, field, background=None):
        colors = self.colors = app.colors
        background = background or colors.card_bg
        super().__init__(parent, bg=background)
        font = themes.mono(13) if field.mono else themes.sans(13)

        self.title = tk.Frame(self, bg=background)
        if field.label:
            self.title.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        tk.Label(self.title, text=field.label, anchor="w", bg=background,
                 fg=colors.text_secondary, font=themes.sans(10)).pack(side="left")

        self.box = tk.Frame(self, bg=colors.input_bg, highlightthickness=1,
                            highlightbackground=colors.line,
                            highlightcolor=colors.line)
        self.box.grid(row=1, column=0, sticky="ew")
        self.box.columnconfigure(0, weight=1)
        self.entry = tk.Entry(self.box, textvariable=field.variable, font=font, bg=colors.input_bg,
                              fg=colors.text_primary, insertbackground=colors.text_primary, relief="flat",
                              borderwidth=0, highlightthickness=0)
        self.entry.grid(row=0, column=0, sticky="ew", padx=ENTRY_PADX, ipady=ENTRY_PADY)
        self.entry.bind("<FocusIn>", lambda _event: self.set_border(colors.border))
        self.entry.bind("<FocusOut>", lambda _event: self.set_border(colors.line))

        self.columnconfigure(0, weight=1)

    def set_border(self, color):
        """Colour the box's border."""
        self.box.configure(highlightbackground=color, highlightcolor=color)


class FileField(tk.Frame):
    """ A LabeledEntry that shows a file's name and cannot be typed in, with a button to pick the file. """

    def __init__(self, parent, app, field):
        colors = app.colors
        super().__init__(parent, bg=colors.card_bg)
        self.labeled = LabeledEntry(self, app, field)
        self.labeled.grid(row=0, column=0, sticky="ew")
        self.columnconfigure(0, weight=1)

        entry = self.labeled.entry
        self.shown = tk.StringVar()
        entry.configure(textvariable=self.shown, state="readonly",
                        readonlybackground=colors.input_bg)

        # The entry shows the name only: the tooltip gives the whole path.
        hovered = self.hover_widgets()
        self.tooltip = Tooltip(hovered, app, field.variable.get)
        for widget in hovered:
            widget.bind("<Enter>", self.hover, add="+")
            widget.bind("<Leave>", self.hover, add="+")

        self.button = OutlineButton(self, app, command=field.pick, style="in_card")
        self.button.grid(row=0, column=1, padx=(14, 0), sticky="s")

        self.variable = field.variable
        trace = self.variable.trace_add("write", lambda *_args: self.refresh())
        self.bind("<Destroy>", lambda _event: self.variable.trace_remove("write", trace))
        self.refresh()

    def hover_widgets(self):
        """ The widgets that show the tooltip when the pointer is on them. """
        return (self.labeled.box, self.labeled.entry)

    def hover(self, _event=None):
        """ Colour the border of the box while the pointer is on the field and there is a tooltip to read. """
        under = self.winfo_containing(*self.winfo_pointerxy())
        highlighted = (under in self.hover_widgets() and self.variable.get()) or self.focus_get() is self.labeled.entry
        self.labeled.set_border(self.labeled.colors.border if highlighted else self.labeled.colors.line)

    def refresh(self):
        """ Show the name of the file, and Choose or Change depending on whether one has been picked. """
        path = self.variable.get()
        # PureWindowsPath reads both / and \ as separators: a path saved on Windows is
        # shown as well on another system
        self.shown.set(PureWindowsPath(path).name)
        self.button.set_text("Change" if path else "Choose")


def show_example(field, app, variable, text):
    """ A placeholder text in a LabeledEntry while it is empty. """
    example = tk.Label(field.box, text=text, anchor="w", width=1, bd=0, padx=0,
                       bg=app.colors.input_bg, fg=app.colors.text_legend,
                       font=field.entry.cget("font"))
    caret = int(field.entry.cget("insertwidth"))
    example.grid(row=0, column=0, sticky="ew", padx=(ENTRY_PADX + caret, ENTRY_PADX))
    example.bind("<Button-1>", lambda _event: field.entry.focus_set())

    def refresh(*_args):
        """ Shown only while the entry is empty. """
        if variable.get():
            example.grid_remove()
        else:
            example.grid()

    trace = variable.trace_add("write", refresh)
    example.bind("<Destroy>", lambda _event: variable.trace_remove("write", trace))
    refresh()
