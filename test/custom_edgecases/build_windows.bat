@echo off
setlocal

set "ROOT=%~dp0..\.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "JAVAC=%ROOT%\jvms\zulu8.78.0.19-ca-jdk8.0.412-win_x64\bin\javac.exe"
set "JAR=%ROOT%\jvms\zulu8.78.0.19-ca-jdk8.0.412-win_x64\bin\jar.exe"
set "SRC=%ROOT%\test\custom_edgecases\src"
set "OUT_CLASSES=%ROOT%\test\custom_edgecases\build\classes"
set "OUT_DIR=%ROOT%\test\custom_edgecases\out"
set "OUT_JAR=%OUT_DIR%\cases.jar"
set "SRC_LIST=%TEMP%\jxe2jar_sources.txt"

if not exist "%OUT_CLASSES%" mkdir "%OUT_CLASSES%"
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"
if exist "%SRC_LIST%" del "%SRC_LIST%"

for /r "%SRC%" %%F in (*.java) do echo %%F>>"%SRC_LIST%"

"%JAVAC%" -source 1.2 -target 1.2 -d "%OUT_CLASSES%" @"%SRC_LIST%"
"%JAR%" cf "%OUT_JAR%" -C "%OUT_CLASSES%" .

if exist "%SRC_LIST%" del "%SRC_LIST%"
echo Wrote %OUT_JAR%
