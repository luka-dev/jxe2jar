# jxe2jar_lsd_jxe

Tools and notes for converting **IBM J9/CDC JXE (rom.classes)** images back to
standard Java `.class` files / `.jar` archives.

What this repo contains
- `src/` – Python implementation of **JXE -? JAR** conversion.
- `test/custom_edgecases/` – exhaustive edge‑case suite (Java 1.2) to validate the converter.
- `test/jxes/` – input JXE samples (e.g., `MU1316-lsd.jxe`).
- `out/` – conversion outputs and logs.
- `vms/` – virtualized environments used to run legacy tooling (XP VM -> WM5 emulator -> jar2jxe).
- The converter is improved and validated through edge‑case tests and a JAR -? JXE round‑trip pipeline.

Parsing / conversion logic differences (core code)
* Classfile version
  * Before: wrote ROM class version as-is (can be non-standard).
  *  Now: clamps to JVM-friendly range (major 45-52, minor 0) so javap/decompilers will accept output.
* Field parsing and constants
  * Before: ignored ROM field constant values.
  * Now: J9ROMField captures constant slots (const_value/const_value2/const_value3) and jxe2jar.py emits ConstantValue for static final fields (int/float/long/double/String).
* Constant pool handling
  * Before: limited constant types and minimal UTF-8 handling.
  * Now: supports INTEGER/FLOAT/LONG/DOUBLE/STRING/REF, preserves descriptors, and encodes UTF-8 with surrogatepass to keep odd ROM strings stable.
* Bytecode translation
  * Before: basic mapping, missing J9 wide opcodes and invokeinterface handling.
  * Now: wide opcodes are normalized to JVM wide, invokeinterface count is computed from descriptor, ldc is promoted to ldc_w when CP index > 255, switch padding uses output offset, and invalid/missing CP refs are handled defensively.
* Code attribute layout
  * Before: conditional 45.3 layout (u8/u8/u16 for stack/locals/code_len).
  * Now: always JVM-standard u16/u16/u32 layout.
* Flag cleanup
  * Before: synthetic flags passed through blindly.
  * Now: --strip-synthetic option clears ACC_SYNTHETIC on classes/methods/fields for strict tooling.

Testing workflow
1) Build edge‑case JAR:  
   `sh test/custom_edgecases/build.sh`
2) Convert JAR -> JXE with `jar2jxe.exe` (see `vms/xp/README.md`).
3) Convert JXE -> JAR with Python:  
   `python3 src/jxe2jar.py input.jxe output.jar`

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
- Thanks to the original repo, forks, and contributors: https://github.com/moradek/jxe2jar & https://github.com/andrewleech/jxe2jar
