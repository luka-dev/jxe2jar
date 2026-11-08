' bootstrap.vbs - runs from the CD once: install agent.vbs, start it, keep it at logon.
Option Explicit
Dim fso, sh, src, dst, lnk
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
src = fso.GetParentFolderName(WScript.ScriptFullName)
dst = "C:\EMU\agent.vbs"
Dim proc                                            ' stop an older agent, if any (not ourselves)
For Each proc In GetObject("winmgmts:").ExecQuery("select * from Win32_Process where Name='wscript.exe'")
    If InStr(1, proc.CommandLine, "agent.vbs", 1) > 0 Then proc.Terminate
Next
If Not fso.FolderExists("C:\EMU") Then fso.CreateFolder "C:\EMU"
If fso.FileExists(dst) Then fso.GetFile(dst).Attributes = 0: fso.DeleteFile dst, True
fso.CopyFile src & "\agent.vbs", dst, True
fso.GetFile(dst).Attributes = 0                     ' CD copies arrive read-only
Set lnk = sh.CreateShortcut(sh.SpecialFolders("Startup") & "\wm5-agent.lnk")
lnk.TargetPath = "wscript.exe"
lnk.Arguments = "//B C:\EMU\agent.vbs"
lnk.Save
sh.Run "wscript.exe //B C:\EMU\agent.vbs", 0, False
