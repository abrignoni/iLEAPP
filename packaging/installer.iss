; Inno Setup script for iLEAPP  (https://jrsoftware.org/isdl.php)
;   python packaging\build.py installer      (passes /DAppVer and /DAppVerNumeric from scripts\version_info.py)
; Expects a one-folder PyInstaller build at dist\iLEAPP\, holding ileapp.exe

#define AppName "iLEAPP"
#ifndef AppVer
  #error Pass the version in with /DAppVer=<version>. packaging\build.py reads it from scripts\version_info.py and does this for you.
#endif
#ifndef AppVerNumeric
  #error Pass the numeric part of the version in with /DAppVerNumeric=<n.n.n>. packaging\build.py does this for you.
#endif
#define AppPublisher "Alexis Brignoni"
; One executable: started without arguments, as the shortcuts start it, it opens the
; window; given arguments it is the command line.
#define AppExe "ileapp.exe"

[Setup]
AppId={{1FFB67AE-CD3C-4C02-9B2D-0A1F6B628C5B}
AppName={#AppName}
AppVersion={#AppVer}
; Windows keeps only numbers in a file's version resource, so -dev and the like stay out of it.
VersionInfoVersion={#AppVerNumeric}
AppPublisher={#AppPublisher}
AppPublisherURL=https://github.com/abrignoni/iLEAPP
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=iLEAPP-Setup-{#AppVer}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=ileapp.ico
UninstallDisplayIcon={app}\{#AppExe}
#ifdef AppArm64
; packaging\build.py passes AppArm64 when it runs on ARM64 Windows. That build runs only
; there, and x64compatible would let an x64 machine install it too.
ArchitecturesAllowed=arm64
ArchitecturesInstallIn64BitMode=arm64
#else
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
#endif
PrivilegesRequiredOverridesAllowed=dialog
#ifdef SignToolName
; Signs the installer and its uninstaller at compile time with the Sign Tool configured
; under this name in Inno Setup (Tools > Configure Sign Tools). build.py installer
; --sign-tool <name> passes it in. ileapp.exe inside must already be signed.
SignTool={#SignToolName}
SignedUninstaller=yes
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "..\dist\iLEAPP\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
