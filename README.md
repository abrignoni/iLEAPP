# iLEAPP
iOS Logs, Events, And Plists Parser  
Details in blog post here: https://abrignoni.blogspot.com/2019/12/ileapp-ios-logs-events-and-properties.html

Supports iOS/iPadOS 11, 12, 13 and 14.
Select parsing directly from a compressed .tar/.zip file, or a decompressed directory, or an iTunes/Finder backup folder.

## Features

Parses:  
⚙️ Mobile Installation Logs  
⚙️ iOS 12 & 13 Notifications  
⚙️ Build Info (iOS version, etc.)  
⚙️ Wireless cellular service info (IMEI, number, etc.)  
⚙️ Screen icons list by screen and in grid order.  
⚙️ ApplicationState.db support for app bundle ID to data container GUID correlation.   
⚙️ User and computer names that the iOS device connected to. Function updated by Jack Farley (@JackFarley248, http://farleyforensics.com/).  
etc...


## Pre-requisites:
This project requires you to have Python > 3.7.4 installed on your system. **Ideally use Python 3.9 (significantly faster processing!)**

## Installation

To install dependencies, run:

```
pip install -r requirements.txt
```

To run on **Linux**, you will also need to install `tkinter` separately like so:

```
sudo apt-get install python3-tk
```

## Compile to executable

To compile to an executable so you can run this on a system without python installed.

To create ileapp.exe, run:

```
pyinstaller --onefile ileapp.spec
````

To create ileappGUI.exe, run:

```
pyinstaller --onefile --noconsole ileappGUI.spec
```

## Usage

### CLI

```
$ python ileapp.py -t <zip | tar | fs | gz | itunes> -i <path_to_extraction> -o <path_for_report_output>
```

### GUI

```
$ python ileappGUI.py 
```

### Help

```
$ python ileapp.py --help
```

The GUI will open in another window.  <br><br>


## Acknowledgements

This tool is the result of a collaborative effort of many people in the DFIR community.
