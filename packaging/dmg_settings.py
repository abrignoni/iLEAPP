# pylint: disable=invalid-name,undefined-variable,redefined-builtin
"""dmgbuild settings for the macOS disk image, read by packaging/build.py.

dmgbuild executes this file with `defines` in scope and reads the names it assigns.
build.py passes every path through `defines`, because the file is exec'd rather than
imported and so has no __file__ to resolve anything against.
"""

import os.path

application = defines["app"]
appname = os.path.basename(application)

format = "UDZO"
files = [application]
symlinks = {"Applications": "/Applications"}

icon = defines["icon"]
background = defines["background"]

# The background is 960x540; the window bounds include the title bar.
window_rect = ((200, 120), (960, 568))
default_view = "icon-view"
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
show_icon_preview = False

icon_size = 144
text_size = 14
label_pos = "bottom"
# Either side of the arrow, whose centre is at x=479 on the background. The arrow moved 44
# points right with the background of 2026-10-01, and the icons with it, from (260, 290)
# and (610, 290).
icon_locations = {appname: (304, 290), "Applications": (654, 290)}
