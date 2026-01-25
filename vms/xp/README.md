# vms/xp

This folder holds a Windows XP VM (UTM) used to run the **Windows Mobile 5 emulator** so we can execute the WinCE ARM `jar2jxe.exe` tool.

## Why XP?

- The official WM5 emulator + old J9/WEME tooling is easiest to run on XP (VS2005 era)
- We use the emulator to run `jar2jxe.exe` and generate `.jxe` files

## Directory Contents

| Path | Description |
|------|-------------|
| `mount-fs/` | Shared folder exposed inside the XP VM |
| `mount-fs/run.lnk` | Shortcut with current `jar2jxe.exe` arguments (WM5 does not allow direct CLI or BAT files; install TotalCommanderCE `tcmdpocketarm.cab` and run via the link) |
| `en_vs_2005_pro_dvd.iso.url` | VS2005 archive link (target: `en_vs_2005_pro_dvd.iso`) |
| `en_windows_xp_professional_with_service_pack_3_x86_cd_vl_x14-73974.iso.url` | XP SP3 archive link |

## Typical Workflow

1. Boot the XP VM in UTM
2. Install Visual Studio 2005 (required by the WM5 SDK/emulator tooling)
3. Start the Windows Mobile 5 emulator inside XP
4. In the emulator, open `Storage Card` (mapped to `vms/xp/mount-fs/`)
5. Run `run.lnk` or execute `jar2jxe.exe` manually
6. Outputs (`cases.jxe`, etc.) are written back to the shared folder

## Notes

- `run.lnk` uses the WinCE path style, e.g., `\Storage Card\...`
- If you change the args, update the length prefix in `run.lnk`
- For file transfer to/from XP, you can use `copyparty` (works with IE, runs from host machine)
- The WM5 emulator supports folder mapping from XP, exposed as `Storage Card`
