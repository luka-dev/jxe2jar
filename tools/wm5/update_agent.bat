@echo off
rem update_agent.bat - sent as a job with agent.vbs: install the new agent, then restart it
rem from a detached helper (the running agent is the one executing this job).
copy /y agent.vbs C:\EMU\agent.vbs >nul
(echo @echo off
echo ping -n 6 127.0.0.1 ^>nul
echo wmic process where name='wscript.exe' delete ^>nul
echo start "" wscript //B C:\EMU\agent.vbs) > C:\EMU\restart_agent.bat
start "" /min C:\EMU\restart_agent.bat
echo agent update scheduled
