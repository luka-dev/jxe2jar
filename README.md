# jxe2jar_lsd_jxe

Tools and notes for converting **IBM J9/CDC JXE (rom.classes)** images back to
standard Java `.class` files / `.jar` archives.

What this repo contains
- `src/` – Python implementation of **JXE → JAR** conversion.
- `test/custom_edgecases/` – exhaustive edge‑case suite (Java 1.2) to validate the converter.
- `test/jxes/` – input JXE samples (e.g., `MU1316-lsd.jxe`).
- `out/` – conversion outputs and logs.
- `vms/` – virtualized environments used to run legacy tooling (XP VM -> WM5 emulator -> jar2jxe).
- The converter is improved and validated through edge‑case tests and a JAR → JXE round‑trip pipeline.

Testing workflow
1) Build edge‑case JAR:  
   `sh test/custom_edgecases/build.sh`
2) Convert JAR -> JXE with `jar2jxe.exe` (see `vms/xp/README.md`).
3) Convert JXE -> JAR with Python:  
   `python3 src/jxe2jar.py input.jxe output.jar`

Large sample (LSD)
- Input: `test/jxes/MU1316-lsd.jxe` - a JXE from **AUDI MHI2Q HU** (real‑world, complex device image).
- Output: `out/lsd4/lsd.from_jxe.jar`
- Log: `out/lsd4/convert.log`
- All **30,543** classes are reconstructed with current converter.

Notes
- The converter preserves `ACC_SYNTHETIC` by default.  
  Use `--strip-synthetic` if you need strict `javap` output for 45.0 classes.
- Some classfile versions are clamped to a JVM‑friendly range to keep tooling happy.
- Some large binaries/ISOs are referenced via `.url` files that point to the original archives:
  - `vms/xp/en_vs_2005_pro_dvd.iso.url`
  - `vms/xp/en_windows_xp_professional_with_service_pack_3_x86_cd_vl_x14-73974.iso.url`

See also
- `src/README.md` – format knowledge and implementation details. !!!
- `test/custom_edgecases/README.md` – test coverage list.
- `vms/xp/README.md` – WM5 emulator + XP VM instructions.

Credits
- Thanks to the original repo, forks, and contributors: https://github.com/moradek/jxe2jar
