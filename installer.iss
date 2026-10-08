#define AppName "Planner"
#define AppVersion "1.0.0"
#define AppExe "Planner.exe"

; Nuitka standalone output
#define BuildDir "build\run.dist"

[Setup]
AppId={{9F3B2C1E-6A47-4D58-8E1B-3C5D7A9E2B10}
AppName={#AppName}
AppVersion={#AppVersion}

DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}

DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=Planner_Setup_{#AppVersion}

; Application icon
SetupIconFile=app\static\img\logo.ico
UninstallDisplayIcon={app}\{#AppExe}

; Compression
Compression=lzma2/max
SolidCompression=yes

; Modern installer UI
WizardStyle=modern

; Windows architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Allow installation without administrator privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; \
    Description: "Create a desktop shortcut"; \
    Flags: unchecked

[Files]

; Copy the complete Nuitka standalone application
Source: "{#BuildDir}\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

; Optional WebView2 Evergreen Bootstrapper
; Put MicrosoftEdgeWebview2Setup.exe inside:
; redist\MicrosoftEdgeWebview2Setup.exe
#ifexist "redist\MicrosoftEdgeWebview2Setup.exe"
Source: "redist\MicrosoftEdgeWebview2Setup.exe"; \
    DestDir: "{tmp}"; \
    Flags: deleteafterinstall
#endif

[Icons]

; Start Menu shortcut
Name: "{autoprograms}\{#AppName}"; \
    Filename: "{app}\{#AppExe}"

; Optional Desktop shortcut
Name: "{autodesktop}\{#AppName}"; \
    Filename: "{app}\{#AppExe}"; \
    Tasks: desktopicon

[Run]

; Install WebView2 only if it is not already installed
#ifexist "redist\MicrosoftEdgeWebview2Setup.exe"
Filename: "{tmp}\MicrosoftEdgeWebview2Setup.exe"; \
    Parameters: "/silent /install"; \
    StatusMsg: "Installing Microsoft Edge WebView2 Runtime..."; \
    Check: not WebView2Installed; \
    Flags: waituntilterminated
#endif

; Launch Planner after installation
Filename: "{app}\{#AppExe}"; \
    Description: "Launch {#AppName}"; \
    Flags: nowait postinstall skipifsilent

[Code]

function WebView2Installed: Boolean;
var
  Version: String;
begin
  Result :=
    RegQueryStringValue(
      HKLM,
      'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}',
      'pv',
      Version
    )
    or
    RegQueryStringValue(
      HKCU,
      'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}',
      'pv',
      Version
    );

  if Result then
    Result := (Version <> '') and (Version <> '0.0.0.0');
end;
