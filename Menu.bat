@echo off

:: USTAWIANIE USTAWIEŃ

chcp 65001 >null

:: WERSJA 1

set Version=0.0.5

:: WEREFIKACJA WERSI (WERSJA 2)

@echo off
setlocal enabledelayedexpansion

:: Lokalna wersja
set "LOCAL_VERSION=%Version%"

:: Pobranie najnowszej wersji z GitHub
powershell -NoProfile -Command ^
    "$r=(Invoke-RestMethod -Uri 'https://api.github.com/repos/wINNYDRUIT/Grechu-Install/releases/latest' -Headers @{ 'User-Agent'='MyApp' }).tag_name; $r.Trim() | Out-File -Encoding ascii latest.txt"

:: Odczytanie wersji z pliku
set /p REMOTE_VERSION=<latest.txt
del latest.txt

:: Czyszczenie wersji
set "REMOTE_VERSION=%REMOTE_VERSION:v=%"
set "REMOTE_VERSION=%REMOTE_VERSION: =%"
for /f "delims=" %%i in ("%REMOTE_VERSION%") do set "REMOTE_VERSION=%%i"

echo Local Version: %LOCAL_VERSION%
echo New Version: %REMOTE_VERSION%

:: Rozdzielenie wersji na części
for /f "tokens=1-3 delims=." %%a in ("%LOCAL_VERSION%") do (
    set "L1=%%a"
    set "L2=%%b"
    set "L3=%%c"
)
for /f "tokens=1-3 delims=." %%a in ("%REMOTE_VERSION%") do (
    set "R1=%%a"
    set "R2=%%b"
    set "R3=%%c"
)

:: Ustawienie brakujących wartości na 0
if "%L2%"=="" set "L2=0"
if "%L3%"=="" set "L3=0"
if "%R2%"=="" set "R2=0"
if "%R3%"=="" set "R3=0"

:: Porównanie wersji i wyświetlenie Stara/Nowa
set /a L1num=L1
set /a L2num=L2
set /a L3num=L3
set /a R1num=R1
set /a R2num=R2
set /a R3num=R3

if %L1num% LSS %R1num% (
    echo [31mStara wersja!
    goto Old
) else if %L1num% GTR %R1num% (
    echo [32mNowa wersja!
    goto koniec
)

if %L2num% LSS %R2num% (
    echo [31mStara Wersja!
    goto goto Old
) else if %L2num% GTR %R2num% (
    echo [32mNowa wersja!
    goto koniec
)

if %L3num% LSS %R3num% (
    echo [31mStara wersja!
	goto Old
) else (
    echo [32mNowa wersja!
)

:koniec


:: LOADING 1

echo [37m?

timeout /t 1 /nobreak >null
color 7

echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
title Grechu Install
echo %Version%

:: MENU

timeout /t 1 /nobreak >null
:MENU
cls

echo.                                                                                                                              
echo	 [96m▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄    ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄ ▄▄▄   ▄▄▄ ▄▄▄  ▄▄▄     ▄▄▄▄▄ ▄▄▄    ▄▄▄  ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄▄▄   ▄▄▄▄   ▄▄▄      ▄▄▄        
echo	[96m███▀▀▀▀▀  ███▀▀███▄ ███▀▀▀▀▀ ███▀▀▀▀▀ ███   ███ ███  ███      ███  ████▄  ███ █████▀▀▀ ▀▀▀███▀▀▀ ▄██▀▀██▄ ███      ███        
echo	[96m███       ███▄▄███▀ ███▄▄    ███      █████████ ███  ███      ███  ███▀██▄███  ▀████▄     ███    ███  ███ ███      ███        
echo	[96m███  ███▀ ███▀▀██▄  ███      ███      ███▀▀▀███ ███▄▄███      ███  ███  ▀████    ▀████    ███    ███▀▀███ ███      ███        
echo	[96m▀██████▀  ███  ▀███ ▀███████ ▀███████ ███   ███ ▀██████▀     ▄███▄ ███    ███ ███████▀    ███    ███  ███ ████████ ████████   
echo.                                                                                                                              
echo.
echo.                                                                                                                             
echo.                                                                                                                              
echo.
echo. 
echo.                                                                                                                              
echo.
echo. 
echo.                                                                                                                              
echo.
echo. 
echo    1. Youtube Dowlander
echo    2. Installers
echo       EXIT Wyjście
echo.
echo.
set /p choice=	Select an option: 

if "%choice%"=="1" goto 1
if "%choice%"=="2" goto 2
if "%choice%"=="exit" goto EXIT

goto MENU





:1
echo.
echo Are you sure you want to choose this option?
set /p ODP= [Y/N] 
if "%ODP%"=="Y" goto yes
if "%ODP%"=="y" goto yes
if "%ODP%"=="N" goto no
if "%ODP%"=="n" goto no
goto MENU

:yes
set Selected=Youtube Dowlander
cls
echo.
echo.
echo Selected:
echo %Selected%
timeout /t 2 /nobreak >null


if exist "Installers\Yt-dlp\yt-dlp" (
    echo Są pliki EXE
) else (
    echo Nie ma plików EXE
)


start "" "%~dp0Installers\Yt-dlp\Yt-dlp installer.bat"

:no
goto MENU


:2
echo.
cls
echo.                                                                                                                              
echo	 [96m▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄    ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄ ▄▄▄   ▄▄▄ ▄▄▄  ▄▄▄     ▄▄▄▄▄ ▄▄▄    ▄▄▄  ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄▄▄   ▄▄▄▄   ▄▄▄      ▄▄▄        
echo	[96m███▀▀▀▀▀  ███▀▀███▄ ███▀▀▀▀▀ ███▀▀▀▀▀ ███   ███ ███  ███      ███  ████▄  ███ █████▀▀▀ ▀▀▀███▀▀▀ ▄██▀▀██▄ ███      ███        
echo	[96m███       ███▄▄███▀ ███▄▄    ███      █████████ ███  ███      ███  ███▀██▄███  ▀████▄     ███    ███  ███ ███      ███        
echo	[96m███  ███▀ ███▀▀██▄  ███      ███      ███▀▀▀███ ███▄▄███      ███  ███  ▀████    ▀████    ███    ███▀▀███ ███      ███        
echo	[96m▀██████▀  ███  ▀███ ▀███████ ▀███████ ███   ███ ▀██████▀     ▄███▄ ███    ███ ███████▀    ███    ███  ███ ████████ ████████   
echo.                                                                                                                              
echo.
echo.                                                                                                                             
echo.                                                                                                                              
echo.
echo. 
echo.                                                                                                                              
echo.
echo. 
echo.                                                                                                                              
echo.
echo                                 ╔═ 2.1 Instalator javy
echo    1. Youtube Dowlander         ║
echo    2. Installers	════════╬═ 2.2 Instalator pythona
echo                                 ║
echo                                 ╚═ 2.3 Opcje dla pendrajwa
echo.
echo EXIT Wyjście
echo.
set /p choice1=	Select an option: 
if "%choice1%"=="Q" goto _
if "%choice1%"=="q" goto _
if "%choice1%"=="exit" goto EXIT


goto 2























































:_
goto MENU
:OLD
echo ?
title ERROR :(
timeout /t 5 /nobreak >null
color 7
cls
echo [41mOld Version
color 7

echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
title Grechu Install
echo %Version%

timeout /t 1 /nobreak >null
color 70
timeout /t 1 /nobreak >null
cls
color 7
echo [OLD]
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo 											   	Error 0001                                                                               
echo.
echo 						[32mThe reason for the error is an old version, please update the application using the link provided below
echo.
echo. 						 			   https://github.com/wINNYDRUIT/Grechu-Install/releases
echo.
echo.
echo.
echo.
echo.
echo.
echo.
pause
exit

:EXIT
cls
color 7
echo [EXIT]
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo                                            Error 0010                                                                               
echo.
echo                     [32mExiting the Grechu Install application
echo.
echo. 
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo [37mAre you sure you want to choose this option?
set /p ODP= [Y/N] 
if "%ODP%"=="Y" goto yes1
if "%ODP%"=="y" goto yes1
if "%ODP%"=="N" goto no1
if "%ODP%"=="n" goto no1
goto MENU

:yes1
del null
timeout /t 3 /nobreak >null
title EXIT
timeout /t 1 /nobreak >null
del null
cls
exit

:no1
timeout /t 1 /nobreak >null
goto MENU

