/* autorun.c - WM5 emulator-side job runner, built for WinCE ARM (see build notes in host.py).
 *
 * Sits at \Storage Card\2577\autorun.exe, so the OS starts it when the emulator's shared folder
 * (the "storage card") appears at boot: no saved state, no taps. Loops forever over
 * \Storage Card\jobs\*.cmd; each file is two lines, "exe path" then "arguments". Runs it,
 * waits, writes "<name>.done" holding the exit code, deletes the .cmd. Pure coredll, no CRT.
 */
#include <windows.h>

#define JOBS L"\\Storage Card\\jobs\\"

static int ReadLine(const char **p, const char *end, wchar_t *out, int max)
{
    int n = 0;
    while (*p < end && **p != '\n' && n < max - 1) {
        if (**p != '\r') out[n++] = (wchar_t)(unsigned char)**p;
        (*p)++;
    }
    if (*p < end) (*p)++;
    out[n] = 0;
    return n;
}

static void RunOne(const wchar_t *name)
{
    wchar_t path[MAX_PATH], exe[MAX_PATH], args[1024], done[MAX_PATH];
    char buf[2048];
    const char *p, *end;
    DWORD got = 0, rc = 0xFFFFFFFF;
    HANDLE f;
    PROCESS_INFORMATION pi;

    wsprintf(path, L"%s%s", JOBS, name);
    f = CreateFile(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (f == INVALID_HANDLE_VALUE) return;
    ReadFile(f, buf, sizeof(buf) - 1, &got, NULL);
    CloseHandle(f);
    p = buf; end = buf + got;
    ReadLine(&p, end, exe, MAX_PATH);
    ReadLine(&p, end, args, 1024);

    if (CreateProcess(exe, args, NULL, NULL, FALSE, 0, NULL, NULL, NULL, &pi)) {
        /* J9 tools keep their "J9 Console (finished)" window - and the process - alive
         * until someone closes it; nobody is watching, so close it for them. */
        while (WaitForSingleObject(pi.hProcess, 1000) == WAIT_TIMEOUT) {
            HWND console = FindWindow(NULL, L"J9 Console (finished)");
            if (console) PostMessage(console, WM_CLOSE, 0, 0);
        }
        GetExitCodeProcess(pi.hProcess, &rc);
        CloseHandle(pi.hThread);
        CloseHandle(pi.hProcess);
    } else {
        rc = 0x80000000 | GetLastError();
    }

    wsprintf(done, L"%s%s", JOBS, name);
    lstrcpy(done + lstrlen(done) - 4, L".done");
    f = CreateFile(done, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 0, NULL);
    if (f != INVALID_HANDLE_VALUE) {
        char text[16];            /* decimal, by hand: WinCE coredll has no wsprintfA */
        int n = 0, i;
        DWORD v = rc;
        do { text[n++] = (char)('0' + v % 10); v /= 10; } while (v);
        for (i = 0; i < n / 2; i++) { char t = text[i]; text[i] = text[n - 1 - i]; text[n - 1 - i] = t; }
        WriteFile(f, text, n, &got, NULL);
        CloseHandle(f);
    }
    DeleteFile(path);
}

int WINAPI WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPWSTR lpCmd, int nShow)
{
    for (;;) {
        WIN32_FIND_DATA fd;
        HANDLE h = FindFirstFile(JOBS L"*.cmd", &fd);
        if (h != INVALID_HANDLE_VALUE) {
            do {
                RunOne(fd.cFileName);
            } while (FindNextFile(h, &fd));
            FindClose(h);
        }
        Sleep(1000);
    }
    return 0;
}
