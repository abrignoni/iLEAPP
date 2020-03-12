# iLEAPP
iOS Logs, Events, And Preferences Parser  
Details in blog post here: https://abrignoni.blogspot.com/2019/12/ileapp-ios-logs-events-and-properties.html

Supports iOS 11, 12 & 13.
Select parsing directly from a compressed .tar/.zip file or a decompressed directory.

## Features

Parses:  
⚙️ Mobile Installation Logs  
⚙️ iOS 11, 12 & 13 Notifications  
⚙️ Build Info (iOS version, etc.)  
⚙️ Wireless cellular service info (IMEI, number, etc.)  
⚙️ Screen icons list by screen and in grid order.  
⚙️ ApplicationState.db support for app bundle ID to data container GUID correlation.   
⚙️ User and computer names that the iOS device connected to. Function updated by Jack Farley (@JackFarley248, http://farleyforensics.com/).  
⚙️ KnowldgeC + Powerlog artifacts.
And many, many more...


## Installation

Pre-requisites:
This project requires you to have Python > 3.7 installed on your system.

To install dependencies, run:

```
pip install -r requirements.txt
```

## Usage

### CLI

```
$ python ileapp.py <path_to_image>
```

### GUI

```
$ python ileapp.py --gui
```

### Help

```
$ python ileapp.py --help
```


The GUI will open in another window.


## Development

### Development environment

The repository uses Python 3, and expects that you have a `virtualenv` set up.

Furthermore, development has solely been done on macOS so far, so if there are
issues, please log them on the [bug
tracker](https://github.com/abrignoni/iLEAPP/issues).

### Navigating the code

`./ileapp.py` and `./ileappGUI.py` are the entry points for each type of program,
the former being for the CLI and latter for the GUI.

The actual business logic of the code is split between `./ilapfuncs.py` and in
`contrib/`. The goal is to port all plugin code to `contrib/` and source from
there.

In the current model, all plugins ported to `contrib/` are imported to
the `ilapfuncs` module so the CLI/GUI frontends do not need to be refactored
immediately.

The directory structure of an example plugin which reads from sqlite and writes
an HTML template at the end is as follows:

```
$ tree contrib/aggregated_dictionary/
contrib/aggregated_dictionary/
├── __init__.py
├── html
│   └── passcode_type.html
├── main.py
└── sql.py
```

In this, the business logic is in `main.py`, any sql queries are sourced from
`sql.py` and all HTML is saved as `jinja2` templates in `html/`.

### Adding a new plugin to `contrib/`

**NOTE:** Currently external plugins are not supported, they must be merged into iLEAPP
into `contrib/`.

To add a new plugin, some scaffolding code has been provided. 

One can run:

```
make add_plugin name=the_name_of_your_plugin
```

After this, one still needs to import the plugin to `ilapfuncs`:

```python
# in ilepfuncs.py
from contrib.the_name_of_your_plugin import function_name
```
