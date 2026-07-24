Unicode true
RequestExecutionLevel user
SetCompressor /SOLID lzma

!include "MUI2.nsh"
!include "nsDialogs.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
!include "FileFunc.nsh"

!ifndef PROJECT_ROOT
  !error "PROJECT_ROOT tanımlanmadı."
!endif

!ifndef BUILD_DATE
  !error "BUILD_DATE tanımlanmadı."
!endif

Name "DyoDesk"
Caption "DyoDesk"
BrandingText "Powered by Dyo Bilgi Sistemleri"

OutFile "${PROJECT_ROOT}\packaging\output\DyoDesk.exe"
Icon "${PROJECT_ROOT}\res\dyodesk_icon.ico"
UninstallIcon "${PROJECT_ROOT}\res\dyodesk_icon.ico"

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "DyoDesk"
VIAddVersionKey "CompanyName" "Dyo Bilgi Sistemleri"
VIAddVersionKey "FileDescription" "DyoDesk Uzak Masaüstü"
VIAddVersionKey "FileVersion" "1.0.0"
VIAddVersionKey "ProductVersion" "1.0.0"
VIAddVersionKey "LegalCopyright" "Dyo Bilgi Sistemleri"

InstallDir "$PROGRAMFILES\DyoDesk"

ShowInstDetails show
ShowUninstDetails show
AutoCloseWindow false
WindowIcon on

!define MUI_ICON "${PROJECT_ROOT}\res\dyodesk_icon.ico"
!define MUI_UNICON "${PROJECT_ROOT}\res\dyodesk_icon.ico"
!define MUI_ABORTWARNING

Var ModePage
Var PortableButton
Var InstallButton
Var Mode
Var ResultCode
Var ServiceName
Var ArchitectureText

Page custom ModePageCreate
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Turkish"


Function IsElevated
  System::Call 'shell32::IsUserAnAdmin() i .r0'
  Push $0
FunctionEnd


Function SetArchitecture
  ${If} ${RunningX64}
    SetRegView 64
    StrCpy $INSTDIR "$PROGRAMFILES64\DyoDesk"
    StrCpy $ArchitectureText "64-bit"
  ${Else}
    SetRegView 32
    StrCpy $INSTDIR "$PROGRAMFILES\DyoDesk"
    StrCpy $ArchitectureText "32-bit Legacy"
  ${EndIf}
FunctionEnd


Function un.SetArchitecture
  ${If} ${RunningX64}
    SetRegView 64
    StrCpy $INSTDIR "$PROGRAMFILES64\DyoDesk"
    StrCpy $ArchitectureText "64-bit"
  ${Else}
    SetRegView 32
    StrCpy $INSTDIR "$PROGRAMFILES\DyoDesk"
    StrCpy $ArchitectureText "32-bit Legacy"
  ${EndIf}
FunctionEnd


Function .onInit
  Call SetArchitecture

  ${GetParameters} $0
  ${GetOptions} $0 "/MODE=" $Mode

  ${If} $Mode == "install"
    Call IsElevated
    Pop $1

    ${If} $1 == 0
      MessageBox MB_ICONSTOP|MB_OK \
        "Kurulum için yönetici yetkisi alınamadı."
      Quit
    ${EndIf}
  ${EndIf}
FunctionEnd


Function ModePageCreate
  ${If} $Mode != ""
    Abort
  ${EndIf}

  nsDialogs::Create 1018
  Pop $ModePage

  ${If} $ModePage == error
    Abort
  ${EndIf}

  GetDlgItem $0 $HWNDPARENT 1
  ShowWindow $0 ${SW_HIDE}

  ${NSD_CreateLabel} 0 0 100% 20u "DyoDesk nasıl çalıştırılsın?"
  Pop $0
  CreateFont $1 "Segoe UI" 14 700
  SendMessage $0 ${WM_SETFONT} $1 1

  ${NSD_CreateLabel} 0 22u 100% 20u \
    "Sisteminiz için $ArchitectureText DyoDesk otomatik seçildi."
  Pop $0

  ${NSD_CreateButton} 0 48u 100% 26u "Kurulumsuz Çalıştır"
  Pop $PortableButton
  ${NSD_OnClick} $PortableButton PortableClicked

  ${NSD_CreateLabel} 4u 76u 96% 18u \
    "Geçici kullanım: hizmet, kısayol ve kaldırma kaydı oluşturmaz."
  Pop $0

  ${NSD_CreateButton} 0 100u 100% 26u "Bu Bilgisayara Kur"
  Pop $InstallButton
  ${NSD_OnClick} $InstallButton InstallClicked

  ${NSD_CreateLabel} 4u 128u 96% 20u \
    "Sürekli erişim: Windows hizmeti, açılışta çalışma ve UAC desteği sağlar."
  Pop $0

  nsDialogs::Show
FunctionEnd


Function PortableClicked
  StrCpy $Mode "portable"
  SendMessage $HWNDPARENT ${WM_COMMAND} 1 0
FunctionEnd


Function InstallClicked
  Call IsElevated
  Pop $0

  ${If} $0 == 0
    ClearErrors
    ExecShell "runas" "$EXEPATH" "/MODE=install"

    IfErrors InstallElevationFailed
    Quit

    InstallElevationFailed:
      MessageBox MB_ICONSTOP|MB_OK \
        "Yönetici izni verilmediği için kurulum başlatılamadı."
      Return
  ${Else}
    StrCpy $Mode "install"
    SendMessage $HWNDPARENT ${WM_COMMAND} 1 0
  ${EndIf}
FunctionEnd


Function ExtractSelectedPayload
  InitPluginsDir
  SetOutPath "$PLUGINSDIR\DyoDesk"

  ${If} ${RunningX64}
    File /r "${PROJECT_ROOT}\packaging\payload\x64\*.*"
  ${Else}
    File /r "${PROJECT_ROOT}\packaging\payload\x86\*.*"
  ${EndIf}
FunctionEnd


Function InstallSelectedPayload
  SetOutPath "$INSTDIR"

  ${If} ${RunningX64}
    File /r "${PROJECT_ROOT}\packaging\payload\x64\*.*"
  ${Else}
    File /r "${PROJECT_ROOT}\packaging\payload\x86\*.*"
  ${EndIf}
FunctionEnd


Function RunPortable
  DetailPrint "$ArchitectureText DyoDesk kurulumsuz hazırlanıyor..."
  Call ExtractSelectedPayload

  IfFileExists "$PLUGINSDIR\DyoDesk\DyoDesk.exe" +3 0
    MessageBox MB_ICONSTOP|MB_OK \
      "DyoDesk.exe seçilen mimari paketinde bulunamadı."
    Quit

  HideWindow
  ExecWait '"$PLUGINSDIR\DyoDesk\DyoDesk.exe"' $ResultCode
  SetErrorLevel $ResultCode
  Quit
FunctionEnd


Function FindAndStartService
  StrCpy $ServiceName "DyoDesk"

  nsExec::ExecToLog '"$SYSDIR\sc.exe" query DyoDesk'
  Pop $ResultCode

  ${If} $ResultCode != 0
    StrCpy $ServiceName "RustDesk"
    nsExec::ExecToLog '"$SYSDIR\sc.exe" query RustDesk'
    Pop $ResultCode
  ${EndIf}

  ${If} $ResultCode != 0
    MessageBox MB_ICONEXCLAMATION|MB_OK \
      "DyoDesk dosyaları kuruldu ancak Windows hizmeti oluşturulamadı."
    Return
  ${EndIf}

  nsExec::ExecToLog \
    '"$SYSDIR\sc.exe" config "$ServiceName" start= auto'
  Pop $ResultCode

  nsExec::ExecToLog \
    '"$SYSDIR\sc.exe" start "$ServiceName"'
  Pop $ResultCode
FunctionEnd


Function InstallDyoDesk
  Call SetArchitecture
  SetShellVarContext all

  DetailPrint "Eski DyoDesk hizmetleri durduruluyor..."
  nsExec::ExecToLog '"$SYSDIR\sc.exe" stop DyoDesk'
  Pop $ResultCode
  nsExec::ExecToLog '"$SYSDIR\sc.exe" stop RustDesk'
  Pop $ResultCode
  Sleep 1000

  DetailPrint "$ArchitectureText DyoDesk $INSTDIR klasörüne kuruluyor..."
  CreateDirectory "$INSTDIR"
  Call InstallSelectedPayload

  IfFileExists "$INSTDIR\DyoDesk.exe" InstallFilesReady 0
    MessageBox MB_ICONSTOP|MB_OK \
      "Kurulum dosyaları çıkarıldı ancak DyoDesk.exe bulunamadı.$\r$\n$\r$\nHedef: $INSTDIR"
    Abort

  InstallFilesReady:

  WriteUninstaller "$INSTDIR\DyoDeskKaldir.exe"

  CreateDirectory "$SMPROGRAMS\DyoDesk"
  Delete "$SMPROGRAMS\DyoDesk\DyoDesk.lnk"
  Delete "$DESKTOP\DyoDesk.lnk"

  CreateShortcut "$SMPROGRAMS\DyoDesk\DyoDesk.lnk" \
    "$INSTDIR\DyoDesk.exe" "" "$INSTDIR\DyoDesk.exe" 0

  CreateShortcut "$DESKTOP\DyoDesk.lnk" \
    "$INSTDIR\DyoDesk.exe" "" "$INSTDIR\DyoDesk.exe" 0

  System::Call 'shell32::SHChangeNotify(i 0x08000000, i 0, p 0, p 0)'

  WriteRegStr HKLM "Software\Dyo Bilgi Sistemleri\DyoDesk" \
    "InstallPath" "$INSTDIR"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "DisplayName" "DyoDesk"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "DisplayIcon" "$INSTDIR\DyoDesk.exe"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "UninstallString" '"$INSTDIR\DyoDeskKaldir.exe"'

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "Publisher" "Dyo Bilgi Sistemleri"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "DisplayVersion" "1.0.0"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "Version" "1.0.0"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "Architecture" "$ArchitectureText"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "BuildDate" "${BUILD_DATE}"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "InstallLocation" "$INSTDIR"

  WriteRegDWORD HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "NoModify" 1

  WriteRegDWORD HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "NoRepair" 1

  DetailPrint "DyoDesk Windows hizmeti kuruluyor..."

  nsExec::ExecToLog \
    '"$INSTDIR\DyoDesk.exe" --install-service'
  Pop $ResultCode

  Sleep 1500
  Call FindAndStartService

  MessageBox MB_ICONINFORMATION|MB_OK \
    "DyoDesk kurulumu tamamlandı.$\r$\n$\r$\n$ArchitectureText istemci ve Windows hizmeti hazırlandı."

  Exec '"$INSTDIR\DyoDesk.exe"'
  Quit
FunctionEnd


Section "DyoDesk"
  ${If} $Mode == "portable"
    Call RunPortable
  ${ElseIf} $Mode == "install"
    Call InstallDyoDesk
  ${Else}
    MessageBox MB_ICONSTOP|MB_OK "Çalışma biçimi seçilemedi."
    Quit
  ${EndIf}
SectionEnd


Function un.onInit
  Call un.SetArchitecture
  System::Call 'shell32::IsUserAnAdmin() i .r0'

  ${If} $0 == 0
    ExecShell "runas" "$EXEPATH" "/S _?=$INSTDIR"
    Quit
  ${EndIf}
FunctionEnd


Section "Uninstall"
  Call un.SetArchitecture
  SetShellVarContext all

  nsExec::ExecToLog '"$SYSDIR\sc.exe" stop DyoDesk'
  Pop $ResultCode
  nsExec::ExecToLog '"$SYSDIR\sc.exe" delete DyoDesk'
  Pop $ResultCode
  nsExec::ExecToLog '"$SYSDIR\sc.exe" stop RustDesk'
  Pop $ResultCode
  nsExec::ExecToLog '"$SYSDIR\sc.exe" delete RustDesk'
  Pop $ResultCode
  nsExec::ExecToLog '"$SYSDIR\taskkill.exe" /F /IM DyoDesk.exe'
  Pop $ResultCode

  Delete "$DESKTOP\DyoDesk.lnk"
  RMDir /r "$SMPROGRAMS\DyoDesk"

  DeleteRegKey HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk"
  DeleteRegKey HKLM "Software\Dyo Bilgi Sistemleri\DyoDesk"

  RMDir /r "$INSTDIR"
SectionEnd
