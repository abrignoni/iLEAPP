# iLEAPP
iOS Logs, Events, And Preferences Parser  
Details in blog post here: https://abrignoni.blogspot.com/2019/12/ileapp-ios-logs-events-and-properties.html

Supports iOS 11, 12 & 13.
Select parsing directly from a compressed .tar/.zip file or a decompressed directory.

Parses:  
⚙️ Mobile Installation Logs  
⚙️ iOS 11, 12 & 13 Notifications  
⚙️ Build Info (iOS version, etc.)  
⚙️ Wireless cellular service info (IMEI, number, etc.)  
⚙️ Screen icons list by screen and in grid order.  
⚙️ ApplicationState.db support for app bundle ID to data contaner GUID correlation.   
⚙️ User and computer names that the iOS device connected to. Function updated by Jack Farley (@JackFarley248, http://farleyforensics.com/).

Usage: ileapp.py [-h] -o {fs,tar,zip} pathtodir  
iLEAPP: iOS Logs, Events, and Preferences Parser.  

positional arguments:  
  pathtodir    Path to directory  

optional arguments:
  -h, --help   show this help message and exit  
  -o {fs,tar}  Directory path or TAR filename and path(required).

Experimental:  
Graphical user interface.    
Usage: ileappGUI.py
No parameter needed.
