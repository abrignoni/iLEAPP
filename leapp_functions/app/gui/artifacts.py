"""
The Artifacts screen: what will be parsed.
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from types import SimpleNamespace

from PIL import ImageTk

from leapp_functions import leapp
from leapp_functions.app.artifact_list import (by_title, group_by_category, load_profile,
                                               profile_artifacts, profile_for_report, search,
                                               toggle, write_profile)
from leapp_functions.app.gui import images, themes
from leapp_functions.app.gui.custom_widgets import (GAP, SIDE_WIDTH, Caption, Card, Field,
                                                    LabeledEntry, OutlineButton, open_menu, show_example)

SEARCH_EXAMPLE = "Search an artifact or a category"
VIEWS = (("all", "All"), ("category", "Category"))
SHOW_PROFILE = "Show loaded profile"
PROFILE_DIFFERS = "The selection differs from this profile: the report will not name it."
PROFILE_FILES = ((f"{leapp.name} Profile", f"*{leapp.profile_extension}"),)
SELECT_TEXTS = {False: ("Select all", "Deselect all"), True: ("Select found", "Deselect found")}
SELECT_WIDTH = max(len(text) for texts in SELECT_TEXTS.values() for text in texts)
COUNT_WIDTH = 64
DETAILS = (("module", "Module"), ("name", "Artifact"))
ROW = "artifact:"
HEADER = "category:"


def scrolled_tree(frame, columns):
    """ A Treeview with its scroll bar on the right. """
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    tree = ttk.Treeview(frame, columns=columns, show="tree", selectmode="browse",
                        style="Card.Treeview")
    tree.column("#0", width=1, stretch=True)
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview,
                              style="Card.Vertical.TScrollbar")
    scrollbar.grid(row=0, column=1, sticky="ns", padx=(6, 0))
    tree.configure(yscrollcommand=scrollbar.set)
    return tree


def box_pictures(colors, master):
    """ The box in its three states: "off", "on" and "partial". """
    box_colors = themes.check_box_colors(colors)
    off, on = box_colors["off"], box_colors["on"]
    return {state: ImageTk.PhotoImage(images.check_box_image(
        themes.CHECK_BOX, box, themes.CHECK_BOX_GAP, mark), master=master)
        for state, box, mark in (("off", off, "check"), ("on", on, "check"),
                                 ("partial", on, "minus"))}


def bind_boxes(tree, on_box):
    """ A click on the box of a row, or Space on the row with the focus, calls on_box(row).
    A click anywhere else shows the choosen row. """
    def click(event):
        if tree.identify_element(event.x, event.y) != "image":
            return None
        on_box(tree.identify_row(event.y))
        return "break"

    tree.bind("<Button-1>", click)
    tree.bind("<space>", lambda _event: on_box(tree.focus()))


def category_of(row):
    """ The category of a category row, or None for any other row. """
    return row[len(HEADER):] if row.startswith(HEADER) else None


def choose(tree, row):
    """ Choose a row and show it. """
    tree.selection_set(row)
    tree.focus(row)
    tree.see(row)


class CategoryTree(tk.Frame):
    """ The categories: a box that selects or unselects all of its artifacts, its
    name, and how many of its artifacts are selected out of how many it holds. A category with
    none selected is greyed. A click on the name chooses the category.
    While a search is on, only the categories found are listed, and their box and their count
    are about the artifacts found only. """

    def __init__(self, parent, app, background, on_toggle):
        super().__init__(parent, bg=background)
        self.state = app.app_state
        self.on_toggle = on_toggle
        self.tree = scrolled_tree(self, ("count",))
        self.tree.column("count", anchor="e", width=COUNT_WIDTH, stretch=False)
        self.tree.tag_configure("none", foreground=app.colors.text_secondary)
        self.boxes = box_pictures(app.colors, self)
        self.groups = {}
        bind_boxes(self.tree, self.toggle)

    def show(self, groups):
        """ List the categories, and keep the one chosen if it is still listed. """
        chosen = self.chosen()
        self.tree.delete(*self.tree.get_children())
        self.groups = groups
        for category in groups:
            self.tree.insert("", "end", iid=HEADER + category, text=category)
            self.refresh_row(category)
        if chosen not in groups:
            chosen = next(iter(groups), None)
        if chosen is not None:
            choose(self.tree, HEADER + chosen)

    def chosen(self):
        """ The category chosen. """
        selection = self.tree.selection()
        return category_of(selection[0]) if selection else None

    def refresh_row(self, category):
        """ Show how many artifacts of a category are selected. """
        names = self.groups[category]
        chosen = len(self.state.artifacts.selected.intersection(names))
        box = "off" if not chosen else "on" if chosen == len(names) else "partial"
        self.tree.item(HEADER + category, image=self.boxes[box], values=(f"{chosen}/{len(names)}",),
                       tags=() if chosen else ("none",))

    def refresh_rows(self):
        """ Show how many artifacts of each category are selected. """
        for category in self.groups:
            self.refresh_row(category)

    def toggle(self, row):
        """ Select all the artifacts of a category, or none of them if they all are. """
        category = category_of(row)
        if category is None:
            return
        toggle(self.groups[category], self.state.artifacts.selected)
        self.on_toggle(category)


class SearchLine(tk.Frame):
    """ The search field, a button for each way to view the list, and a profile button. """

    def __init__(self, parent, app, variable, commands):
        background = app.colors.main_bg
        super().__init__(parent, bg=background)
        self.variable = variable
        self.columnconfigure(0, weight=1)
        field = LabeledEntry(self, app, Field("", variable), background=background)
        field.grid(row=0, column=0, sticky="ew")
        show_example(field, app, variable, SEARCH_EXAMPLE)
        self.entry = field.entry
        self.views = {}
        for column, (view, text) in enumerate(VIEWS, start=1):
            button = OutlineButton(self, app, text=text, style="in_card", width=-len(text),
                                   command=lambda view=view: commands.view(view))
            button.grid(row=0, column=column, padx=(8, 0))
            self.views[view] = button
        text = "Profile ▾"
        self.profile_button = OutlineButton(self, app, text=text, style="in_card", width=-len(text),
                                            command=self.show_profile_menu)
        self.profile_button.grid(row=0, column=len(VIEWS) + 1, padx=(8, 0))
        self.views["profile"] = self.profile_button
        self.profile_menu = tk.Menu(self, tearoff=0)
        self.profile_menu.add_command(label="Load profile…", command=commands.load)
        self.profile_menu.add_command(label="Save profile…", command=commands.save)
        self.profile_menu.add_command(label=SHOW_PROFILE,
                                      command=lambda: commands.view("profile"))
        self.state = app.app_state

    def show_profile_menu(self):
        """ Open the menu under its button. A profile can be shown once one is loaded. """
        self.profile_menu.entryconfigure(
            SHOW_PROFILE, state="normal" if self.state.artifacts.profile else "disabled")
        button = self.profile_button
        open_menu(self.profile_menu, button)

    def show_view(self, chosen):
        """ Show which view is chosen. """
        for view, button in self.views.items():
            button.set_style("chosen" if view == chosen else "in_card")


class ListHeading(tk.Frame):
    """ What are the listed artifacts, how many are selected, and buttons that select or
    unselect them all. """

    def __init__(self, parent, app, background, on_all):
        super().__init__(parent, bg=background)
        self.columnconfigure(0, weight=1)
        self.title = tk.Label(self, anchor="w", width=1, bg=background,
                              fg=app.colors.text_primary, font=themes.sans(13, "bold"))
        self.title.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.detail = tk.Label(self, anchor="w", width=1, bg=background,
                               fg=app.colors.text_secondary, font=themes.sans(11))
        self.detail.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        self.buttons = [OutlineButton(self, app, text=text, style="in_card", width=SELECT_WIDTH,
                                      command=lambda select=select: on_all(select))
                        for text, select in zip(SELECT_TEXTS[False], (True, False))]
        for column, button in enumerate(self.buttons, start=1):
            button.grid(row=0, column=column, rowspan=2, padx=(8, 0))

    def stack_buttons(self):
        """ Put the buttons under the texts for a narrow card. """
        for row, button in enumerate(self.buttons, start=2):
            button.grid(row=row, column=0, rowspan=1, sticky="ew", padx=0, pady=(8, 0))

    def refresh(self, title, detail, searching, listed):
        """ Show what is listed. """
        self.title.configure(text=title)
        self.detail.configure(text=detail)
        for button, text in zip(self.buttons, SELECT_TEXTS[searching]):
            button.set_text(text)
            button.set_enabled(listed)


class ProfilePanel(tk.Frame):
    """ The path of the profile loaded, and the names it holds that match no artifact. """

    def __init__(self, parent, app, background):
        colors = app.colors
        super().__init__(parent, bg=background)
        self.path = Caption(self, app, "", background)
        self.path.configure(fg=colors.text_primary, font=themes.mono(12))
        self.path.pack(fill="x", pady=(4, 0))
        self.differs = Caption(self, app, PROFILE_DIFFERS, background)
        self.problem = Caption(self, app, "", background)
        self.problem.configure(fg=colors.text_error)

        self.names = tk.Frame(self, bg=background)
        self.names.rowconfigure(0, weight=1)
        self.names.columnconfigure(0, weight=1)
        self.text = tk.Text(self.names, width=1, height=1, wrap="char", state="disabled", bd=0,
                            highlightthickness=0, padx=3, pady=0, spacing3=4,
                            bg=background, fg=colors.text_primary, font=themes.mono(11),
                            selectbackground=colors.line, selectforeground=colors.text_primary)
        self.text.tag_configure("name", lmargin2=12)
        self.text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(self.names, orient="vertical", command=self.text.yview,
                                  style="Card.Vertical.TScrollbar")
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(6, 0))
        self.text.configure(yscrollcommand=scrollbar.set)

    def show(self, profile):
        """ Show the profile loaded. """
        self.path.configure(text=profile.path)
        self.problem.pack_forget()
        self.names.pack_forget()
        if profile.unknown:
            self.problem.configure(text=unknown_text(profile.unknown))
            self.problem.pack(fill="x", pady=(14, 8))
            self.names.pack(fill="both", expand=True)
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", "\n".join(profile.unknown), "name")
        self.text.configure(state="disabled")

    def show_differs(self, differs):
        """ Indicate whether the selection is no longer what the profile selects. """
        if differs:
            self.differs.pack(fill="x", pady=(8, 0), after=self.path)
        else:
            self.differs.pack_forget()


def unknown_text(unknown):
    """ Artifacts that do not exist. """
    if len(unknown) == 1:
        return "1 artifact of this profile is not in this version and will not run."
    return f"{len(unknown)} artifacts of this profile are not in this version and will not run."


def found_text(groups, with_categories):
    """ How many artifacts a search found. """
    found = sum(len(names) for names in groups.values())
    if not found:
        return "No artifact found"
    artifacts = "artifact" if found == 1 else "artifacts"
    if not with_categories:
        return f"{found} {artifacts} found"
    categories = "category" if len(groups) == 1 else "categories"
    return f"{found} {artifacts} found in {len(groups)} {categories}"


def wrap_to_width(event):
    """ Make the text of a label go to the next line. """
    label = event.widget
    margins = 2 * (int(label.cget("borderwidth")) + int(label.cget("padx"))
                   + int(label.cget("highlightthickness")))
    label.configure(wraplength=event.width - margins)


class ArtifactDetails(tk.Frame):
    """ The module and the name of an artifact. """

    def __init__(self, parent, app, background, stacked=False):
        colors = app.colors
        super().__init__(parent, bg=background)
        self.columnconfigure(1, weight=1)
        tk.Frame(self, height=1, bg=colors.line).grid(row=0, column=0, columnspan=2, sticky="ew",
                                                      pady=(0, 8))
        self.values = {}
        for row, (key, text) in enumerate((("category", "Category"),) + DETAILS if stacked
                                          else DETAILS):
            label = tk.Label(self, text=text, anchor="w", bg=background, fg=colors.text_secondary,
                             font=themes.sans(11))
            value = tk.Label(self, anchor="w", justify="left", width=1, bg=background,
                             fg=colors.text_primary, font=themes.mono(12))
            if stacked:
                label.grid(row=2 * row + 1, column=0, columnspan=2, sticky="w",
                           pady=(8 if row else 0, 0))
                value.grid(row=2 * row + 2, column=0, columnspan=2, sticky="ew")
                value.bind("<Configure>", wrap_to_width)
            else:
                label.grid(row=row + 1, column=0, sticky="w", padx=(0, 16))
                value.grid(row=row + 1, column=1, sticky="ew")
            self.values[key] = value

    def show(self, artifact):
        """ Show the details of an artifact. """
        values = {"category": artifact.category, "module": f"{artifact.module}.py",
                  "name": artifact.name} if artifact else {}
        for key, value in self.values.items():
            value.configure(text=values.get(key, ""))


class ArtifactTree(tk.Frame):
    """ A list of artifacts with a box that selects or unselects it and its title, greyed when it is
    not selected. Under the list, the details of the artifact chosen, unless they are shown
    elsewhere. The artifacts can be listed under the name of their category. """

    def __init__(self, parent, app, background, on_toggle):
        colors = app.colors
        super().__init__(parent, bg=background)
        self.state = app.app_state
        self.on_toggle = on_toggle
        self.by_name = {artifact.name: artifact for artifact in self.state.artifacts.listed}
        self.shown = {}  # the artifacts in the list, by row

        rows = tk.Frame(self, bg=background)
        rows.pack(fill="both", expand=True)
        self.tree = scrolled_tree(rows, ())
        self.tree.tag_configure("none", foreground=colors.text_secondary)
        self.tree.tag_configure("header", foreground=colors.text_secondary,
                                font=themes.sans(12, "bold"))
        self.boxes = box_pictures(colors, self)
        bind_boxes(self.tree, self.toggle)
        self.tree.bind("<<TreeviewSelect>>", lambda _event: self.show_details())

        self.details = [ArtifactDetails(self, app, background)]

    def add_details(self, details):
        """ Show the details of the artifact chosen in another place. """
        self.details.append(details)

    def show_details_below(self, shown):
        """ Show the details under the list or not. """
        if shown:
            self.details[0].pack(fill="x", pady=(10, 0))
        else:
            self.details[0].pack_forget()

    def show(self, groups, headers):
        """ List the artifacts of groups, and choose the first one.
        Args:
            groups (dict): the names of the artifacts to list, by category.
            headers (bool): whether to list them under the name of their category.
        """
        self.tree.delete(*self.tree.get_children())
        self.shown = {}
        for category, names in groups.items():
            parent = ""
            if headers:
                parent = self.tree.insert("", "end", iid=HEADER + category, text=category,
                                          open=True, tags=("header",))
            for name in names:
                row = ROW + name
                self.shown[row] = self.by_name[name]
                self.tree.insert(parent, "end", iid=row, text=self.shown[row].title)
        self.refresh_rows()
        first = next(iter(self.shown), None)
        if first is not None:
            choose(self.tree, first)
            self.tree.yview_moveto(0)
        self.show_details()

    def reveal(self, category):
        """ Scroll the list so that the artifacts of a category come first. """
        header = HEADER + category
        if not self.tree.exists(header):
            return
        headers = self.tree.get_children()
        rows = len(headers) + len(self.shown)
        before = 0
        for other in headers[:headers.index(header)]:
            before += 1 + len(self.tree.get_children(other))
        self.tree.yview_moveto(before / rows)
        first = self.tree.get_children(header)[0]
        self.tree.selection_set(first)
        self.tree.focus(first)

    def refresh_rows(self):
        """ Show which artifacts of the list are selected. """
        selected = self.state.artifacts.selected
        for row, artifact in self.shown.items():
            on = artifact.name in selected
            self.tree.item(row, image=self.boxes["on" if on else "off"],
                           tags=() if on else ("none",))

    def show_details(self):
        """ Show the module and the name of the artifact chosen. """
        selection = self.tree.selection()
        artifact = self.shown.get(selection[0]) if selection else None
        for details in self.details:
            details.show(artifact)

    def toggle(self, row):
        """ Select an artifact, or unselect it if it is selected. A category name has no box. """
        artifact = self.shown.get(row)
        if artifact is None:
            return
        toggle([artifact.name], self.state.artifacts.selected)
        self.on_toggle(artifact.category)


class ArtifactsScreen(tk.Frame):
    """ The artifacts screen layout. """

    def __init__(self, parent, app):
        colors = app.colors
        super().__init__(parent, bg=colors.main_bg)
        self.app = app
        self.groups = {}  # the names of the artifacts found, by category

        self.columnconfigure(0, minsize=SIDE_WIDTH)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        search_text = tk.StringVar(value=app.app_state.artifacts.search)
        self.search_line = SearchLine(self, app, search_text, SimpleNamespace(
            view=self.view_chosen, load=self.choose_profile, save=self.save_profile))
        self.search_line.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, GAP))

        categories = Card(self, app, "BY CATEGORY")
        categories.grid(row=1, column=0, sticky="nsew")
        self.category_list = CategoryTree(categories.body, app, categories.background,
                                          self.toggled)
        self.category_list.pack(fill="both", expand=True)

        summary = Card(self, app)
        summary.grid(row=1, column=0, sticky="nsew")
        summary_heading = ListHeading(summary.body, app, summary.background, self.select_listed)
        summary_heading.stack_buttons()
        summary_heading.pack(fill="x")

        profile = Card(self, app, "PROFILE")
        profile.grid(row=1, column=0, sticky="nsew")
        self.profile_panel = ProfilePanel(profile.body, app, profile.background)
        self.profile_panel.pack(fill="both", expand=True)

        artifacts = Card(self, app)
        artifacts.grid(row=1, column=1, sticky="nsew", padx=(GAP, 0))
        list_heading = ListHeading(artifacts.body, app, artifacts.background, self.select_listed)
        self.sides = {"all": (summary, summary_heading), "category": (categories, list_heading),
                      "profile": (profile, list_heading)}
        self.artifact_list = ArtifactTree(artifacts.body, app, artifacts.background, self.toggled)
        self.artifact_list.pack(fill="both", expand=True)

        summary_details = ArtifactDetails(summary.body, app, summary.background, stacked=True)
        summary_details.pack(fill="x", pady=(14, 0))
        self.artifact_list.add_details(summary_details)

        self.category_list.tree.bind("<<TreeviewSelect>>", lambda _event: self.category_chosen())
        trace = search_text.trace_add("write", lambda *_args: self.searched())
        self.bind("<Destroy>", lambda event: event.widget is self and search_text.trace_remove(
            "write", trace))
        self.view_chosen(app.app_state.artifacts.view)

    def searching(self):
        """ Whether a search is on. """
        return bool(self.search_line.variable.get())

    def viewing(self, view):
        """ Is this view chosen. """
        return self.app.app_state.artifacts.view == view

    def listing_all(self):
        """ Does the list hold everything found rather than one category. """
        return self.searching() or not self.viewing("category")

    def listed_groups(self):
        """ The names of the artifacts listed, by category. """
        if self.listing_all():
            return self.groups
        category = self.category_list.chosen()
        return {category: self.groups[category]} if category in self.groups else {}

    def refresh_heading(self):
        """ What is listed and how many of them are selected. """
        artifacts = self.app.app_state.artifacts
        groups = self.listed_groups()
        names = [name for group in groups.values() for name in group]
        if self.searching():
            title = "Search results"
            detail = found_text(self.groups, with_categories=self.viewing("category"))
        else:
            chosen = len(artifacts.selected.intersection(names))
            detail = f"{chosen} of {len(names)} selected"
            if self.viewing("all"):
                title = "All artifacts"
            elif self.viewing("category"):
                title = next(iter(groups), "")
            else:
                title = Path(artifacts.profile.path).name
        _card, heading = self.sides[artifacts.view]
        heading.refresh(title, detail, self.searching(), bool(names))
        if self.viewing("profile"):
            self.profile_panel.show_differs(profile_for_report(artifacts) is None)

    def view_chosen(self, view):
        """ A way to view the chosen list chosen. """
        self.app.app_state.artifacts.view = view
        self.search_line.show_view(view)
        self.place_cards()
        self.searched()

    def place_cards(self):
        """ Show the card on the left of the view chosen, and the heading above the artifacts
        unless that card holds it. """
        viewing_all = self.viewing("all")
        if self.viewing("profile"):
            self.profile_panel.show(self.app.app_state.artifacts.profile)
        for view, (card, _heading) in self.sides.items():
            if self.viewing(view):
                card.grid()
            else:
                card.grid_remove()
        self.artifact_list.show_details_below(not viewing_all)
        list_heading = self.sides["category"][1]
        if viewing_all:
            list_heading.pack_forget()
        else:
            list_heading.pack(fill="x", pady=(0, 10), before=self.artifact_list)

    def searched(self):
        """ The text searched or the view changed. """
        state = self.app.app_state
        state.artifacts.search = self.search_line.variable.get()
        listed = (profile_artifacts(state.artifacts) if self.viewing("profile")
                  else state.artifacts.listed)
        found = search(listed, state.artifacts.search)
        self.groups = group_by_category(found)
        self.category_list.show(self.groups)
        if not self.viewing("category"):
            self.artifact_list.show({"": by_title(found)}, headers=False)
            self.refresh_heading()
        elif self.searching():
            self.artifact_list.show(self.groups, headers=True)
            self.refresh_heading()
        else:
            self.category_chosen()

    def category_chosen(self):
        """ Chosen category: show its artifacts, or scroll to them if the list holds them
        with others. Only the view "Category" shows categories to choose from. """
        if not self.viewing("category"):
            return
        category = self.category_list.chosen()
        if category is not None:
            if self.listing_all():
                self.artifact_list.reveal(category)
            else:
                self.artifact_list.show({category: self.groups.get(category, [])}, headers=False)
        self.refresh_heading()

    def toggled(self, category):
        """ Artifacts of a category were selected or unselected. """
        self.category_list.refresh_row(category)
        self.artifact_list.refresh_rows()
        self.refresh_heading()
        self.app.app_state.on_change()

    def select_listed(self, select):
        """ Select every artifact listed, or unselect them all. """
        selected = self.app.app_state.artifacts.selected
        for names in self.listed_groups().values():
            if select:
                selected.update(names)
            else:
                selected.difference_update(names)
        self.selection_changed()

    def selection_changed(self):
        """ Show the artifacts selected everywhere on the screen and in the status bar. """
        self.category_list.refresh_rows()
        self.artifact_list.refresh_rows()
        self.refresh_heading()
        self.app.app_state.on_change()

    def choose_profile(self):
        """ Select the artifacts of a profile file, and show them in the view "Profile". """
        window = self.winfo_toplevel()
        path = filedialog.askopenfilename(parent=window, title="Load a profile",
                                          filetypes=PROFILE_FILES)
        if not path:
            return
        artifacts = self.app.app_state.artifacts
        try:
            load_profile(path, artifacts)
        except ValueError as error:
            messagebox.showerror("Load a profile", str(error), parent=window)
            return
        self.search_line.variable.set("")
        self.view_chosen("profile")
        self.app.app_state.on_change()
        self.update_idletasks()
        if artifacts.profile.unknown:
            messagebox.showwarning("Profile loaded", unknown_text(artifacts.profile.unknown)
                                   + "\n\nThe PROFILE card lists them.", parent=window)

    def save_profile(self):
        """ Write the artifacts selected to a profile file. """
        window = self.winfo_toplevel()
        path = filedialog.asksaveasfilename(parent=window, title="Save a profile",
                                            filetypes=PROFILE_FILES,
                                            defaultextension=leapp.profile_extension)
        if not path:
            return
        if write_profile(path, self.app.app_state.artifacts):
            messagebox.showinfo("Save a profile", f"Profile saved: {path}", parent=window)
        else:
            messagebox.showerror("Save a profile", f"Unable to write {path}.", parent=window)

    def focus_search(self):
        """ Put the cursor in the search field: Ctrl+F """
        self.search_line.entry.focus_set()
