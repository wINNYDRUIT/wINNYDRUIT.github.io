@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

REM ------------------------------------
REM KONFIGURACJA
REM ------------------------------------
set "GH_USER=wINNYDRUIT"
set "GH_REPO=Grechu-Install"
set "APP_NAME=Menu.bat"
set "TEMP_DIR=update_raw"

color 17
title Grechu Installer
echo Ładowanie...
timeout /t 1 >nul


REM ============================================================
REM   1. Jeśli Menu.bat istnieje → od razu uruchom
REM ============================================================
if exist "%APP_NAME%" (
    start /MAX "" "%APP_NAME%"
    goto SEND_NOTIFY
)


REM ============================================================
REM   2. Pobieranie ZIP z GitHub → ostatnie wydanie
REM ============================================================
echo Pobieranie najnowszej wersji...
powershell -NoProfile -Command ^
 "$rel = Invoke-RestMethod 'https://api.github.com/repos/%GH_USER%/%GH_REPO%/releases/latest';" ^
 "$url = $rel.assets[0].browser_download_url;" ^
 "Invoke-WebRequest $url -OutFile 'latest.zip';"

if not exist latest.zip (
    echo BŁĄD: Nie można pobrać pliku release!
    pause
    exit /b
)


REM ============================================================
REM   3. Rozpakowanie ZIP
REM ============================================================
echo Rozpakowywanie...
if exist "%TEMP_DIR%" rd /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

powershell -NoProfile -Command ^
 "Expand-Archive -LiteralPath 'latest.zip' -DestinationPath '%TEMP_DIR%' -Force"

del latest.zip


REM ============================================================
REM   4. Kopiowanie plików do katalogu instalatora
REM ============================================================
echo Instalowanie plików...
for /r "%TEMP_DIR%" %%F in (*) do (
    copy /Y "%%F" ".\" >nul
)


REM ============================================================
REM   5. Usuwamy folder tymczasowy
REM ============================================================
rd /s /q "%TEMP_DIR%"


REM ============================================================
REM   6. Uruchamiamy aplikację
REM ============================================================
if exist "%APP_NAME%" (
    start /MAX "" "%APP_NAME%"
) else (
    echo BŁĄD: Menu.bat nie znaleziono po instalacji!
    pause
)


REM ============================================================
REM   7. Toast – powiadomienie systemowe Windows
REM ============================================================
:SEND_NOTIFY
powershell -NoLogo -NoProfile -Command ^
 "$template = @'
<toast duration='short'>
    <visual>
        <binding template='ToastGeneric'>
            <text>Grechu-Install</text>
            <text>Instalacja zakonczona pomyslnie!</text>
        </binding>
    </visual>
</toast>
'@; ^
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument; ^
$xml.LoadXml($template); ^
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml); ^
$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('GrechuInstaller'); ^
$notifier.Show($toast)"

exit /b
