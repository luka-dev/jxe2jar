' agent.vbs - XP-side job runner for tools/wm5/host.py (runs under wscript //B at logon).
' Polls the Mac (QEMU slirp host = 10.0.2.2) for jobs, downloads inputs, runs the command
' with cmd.exe, uploads outputs + stdout. Zero installs: WSH + MSXML3 + ADO ship with XP.
Option Explicit
Const BASE = "http://10.0.2.2:8790"
Const ROOT = "C:\EMU\jobs"
Dim sh, fso
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
If Not fso.FolderExists("C:\EMU") Then fso.CreateFolder "C:\EMU"
If Not fso.FolderExists(ROOT) Then fso.CreateFolder ROOT

Sub LogLine(msg)
    Dim f
    Set f = fso.OpenTextFile("C:\EMU\agent.log", 8, True)
    f.WriteLine Now & " " & msg
    f.Close
End Sub

Function Http(method, url, body)
    ' ServerXMLHTTP = WinHTTP: no IE cache, no proxy surprises. Returns the request.
    Dim x
    Set x = CreateObject("MSXML2.ServerXMLHTTP")
    x.Open method, url, False
    If IsNull(body) Then
        x.Send
    Else
        x.Send body
    End If
    Set Http = x
End Function

Sub Download(url, path)
    Dim x, st
    Set x = Http("GET", url, Null)
    If x.Status <> 200 Then Err.Raise 1, , "GET " & url & " -> " & x.Status
    Set st = CreateObject("ADODB.Stream")
    st.Type = 1: st.Open: st.Write x.responseBody: st.SaveToFile path, 2: st.Close
End Sub

Sub Upload(path, url)
    Dim st, x, body
    Set st = CreateObject("ADODB.Stream")
    st.Type = 1: st.Open
    On Error Resume Next
    st.LoadFromFile path
    If Err.Number <> 0 Then
        ' a GUI child started by the job still holds the handle: read it shared, as text
        Err.Clear
        On Error GoTo 0
        body = fso.OpenTextFile(path, 1).ReadAll
        Set x = Http("PUT", url, body)
    Else
        On Error GoTo 0
        Set x = Http("PUT", url, st.Read)
    End If
    st.Close
    If x.Status <> 200 Then Err.Raise 1, , "PUT " & url & " -> " & x.Status
End Sub

Sub RunJob(id)
    Dim dir, spec, lines, cmd, i, name, rc, f
    dir = ROOT & "\" & id
    If fso.FolderExists(dir) Then fso.DeleteFolder dir, True
    fso.CreateFolder dir
    Download BASE & "/jobs/" & id & "/job.txt", dir & "\job.txt"
    Set f = fso.OpenTextFile(dir & "\job.txt", 1)
    spec = f.ReadAll: f.Close
    lines = Split(spec, vbLf)
    ' line 0: command; line 1: inputs (comma list); line 2: outputs (comma list)
    cmd = Trim(Replace(lines(0), vbCr, ""))
    For Each name In Split(Trim(Replace(lines(1), vbCr, "")), ",")
        If name <> "" Then Download BASE & "/jobs/" & id & "/" & name, dir & "\" & name
    Next
    LogLine "job " & id & ": " & cmd
    rc = sh.Run("cmd.exe /c cd /d """ & dir & """ && (" & cmd & ") > stdout.txt 2>&1", 0, True)
    For Each name In Split(Trim(Replace(lines(2), vbCr, "")), ",")
        If name <> "" And fso.FileExists(dir & "\" & name) Then Upload dir & "\" & name, BASE & "/jobs/" & id & "/" & name
    Next
    If fso.FileExists(dir & "\stdout.txt") Then Upload dir & "\stdout.txt", BASE & "/jobs/" & id & "/stdout.txt"
    Http "PUT", BASE & "/jobs/" & id & "/done", CStr(rc)
    LogLine "job " & id & " rc=" & rc
End Sub

Dim x, id
LogLine "agent start"
Do
    On Error Resume Next
    Set x = Http("GET", BASE & "/jobs/next?t=" & Timer, Null)
    If Err.Number = 0 And x.Status = 200 Then
        id = Trim(x.responseText)
        If id <> "" Then
            RunJob id
            If Err.Number <> 0 Then
                LogLine "job " & id & " failed: " & Err.Description
                Http "PUT", BASE & "/jobs/" & id & "/done", "-1 " & Err.Description
            End If
        End If
    End If
    Err.Clear
    On Error GoTo 0
    WScript.Sleep 2000
Loop
