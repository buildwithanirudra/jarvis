; E.V.O Inno Setup Script
; This script packages the PyInstaller 'dist\EVO' folder into a professional installer (EVO_Setup.exe).

#define MyAppName "E.V.O"
#define MyAppVersion "0.01V"
#define MyAppPublisher "THINK EVO & ANIRUDRA GUPTA"
#define MyAppExeName "EVO.exe"

[Setup]
; App Metadata
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\EVO
DisableProgramGroupPage=yes

; Output settings
OutputDir=dist
OutputBaseFilename=EVO_Setup

; Icons and Images
SetupIconFile=evo_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardImageFile=evo_banner.bmp

; Installer behavior
Compression=lzma2/ultra
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copy all files and folders from the PyInstaller output directory
Source: "dist\EVO\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "evo_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu Icon
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\evo_icon.ico"
; Desktop Icon (if selected)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\evo_icon.ico"; Tasks: desktopicon

[Run]
; Option to launch the app on the final setup screen
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
