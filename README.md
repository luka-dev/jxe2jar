# jxe2jar

Tools and notes for converting **IBM J9/CDC JXE (rom.classes)** images back to standard Java `.class` files / `.jar` archives.

## Repository Structure

| Directory | Description |
|-----------|-------------|
| `src/` | Python implementation of **JXE → JAR** conversion |
| `test/custom_edgecases/` | Exhaustive edge-case suite (Java 1.2) to validate the converter |
| `out/` | Conversion outputs and logs |
| `vms/` | Virtualized environments for legacy tooling (XP VM → WM5 emulator → jar2jxe) |

The converter is validated through edge-case tests and a **JAR → JXE → JAR** round-trip pipeline.

## Conversion Logic

### Classfile Version
- **Before:** Wrote ROM class version as-is (can be non-standard).
- **Now:**
  - Infers minimal version from flags/opcodes (minimum 46, no upper cap).
  - Bumps to 49 when synthetic/enum/annotation flags are present so `javac`/`javap` accept output.

### Field Parsing and Constants
- **Before:** Ignored ROM field constant values.
- **Now:**
  - `J9ROMField` captures constant slots (`const_value`, `const_value2`, `const_value3`).
  - `jxe2jar.py` emits `ConstantValue` for static final fields (int/float/long/double/String).
  - Recovers constants from ROM metadata even when the constant pool slot is placeholder/omitted.

### Constant Pool Handling
- **Before:** Limited constant types and minimal UTF-8 handling.
- **Now:**
  - Supports INTEGER/FLOAT/LONG/DOUBLE/STRING/REF and preserves descriptors.
  - Encodes UTF-8 with `surrogatepass` to keep odd ROM strings stable.
  - Decodes J9 ROM "LONG" slots into proper field/method refs using ROM base offsets.
  - **Float constant recovery:** J9 stores both `int` and `float` as `J9CONST.INT` (type 0) — the ROM format has no int/float distinction. A bytecode pre-pass with stack simulation (`_find_float_constants`) walks each method before translation, tracking which `ldc`/`ldc_w` constant pool entries flow into float-consuming operations (`fstore`, `fadd`, `fcmpg`, `putfield` with `F` descriptor, `invoke*` with `F` parameters, etc.). Identified entries are reclassified from `CONST.INTEGER` to `CONST.FLOAT` via `new_cp_transform`. This fixed ~1,200 classes across MU1316-lsd.jxe where values like `100.0f` appeared as `(float)1120403456` in decompiled output.

### Bytecode Translation
- **Before:** Basic mapping, missing J9 wide opcodes and invokeinterface handling.
- **Now:**
  - Wide opcodes are normalized to JVM `wide`.
  - `invokeinterface` count is computed from the descriptor.
  - `ldc` is promoted to `ldc_w` when CP index > 255.
  - J9 prefix opcodes are expanded correctly (e.g., implicit `aload_0` prefix).
  - J9 return opcodes are mapped to standard JVM returns based on method signature:
    - `JBreturn0` / `JBsyncReturn0` / `JBreturnFromConstructor` / `JBretFromNative0` → `return`
    - `JBreturn1` / `JBsyncReturn1` / `JBretFromNative1` → `ireturn` / `freturn` / `areturn`
    - `JBreturn2` / `JBsyncReturn2` → `lreturn` / `dreturn`
    - `JBretFromNativeF` / `JBretFromNativeD` / `JBretFromNativeJ` → typed returns
    - `JBgenericReturn` / `JBreturnToMicroJIT` → inferred from descriptor
  - J9 runtime/debug opcodes (`JBasyncCheck`, `JBbreakpoint`, `JBimpdep1`, `JBimpdep2`) → `nop`
  - Branch and switch offsets are rewritten using output offset maps to avoid `javap` errors.
  - Switch padding uses output offset so alignment is correct.
  - Invalid/missing CP refs are handled defensively instead of crashing.

### Code Attribute Layout
- **Before:** Conditional 45.3 layout (u8/u8/u16 for stack/locals/code_len).
- **Now:**
  - Always JVM-standard u16/u16/u32 layout.
  - Exception table offsets are rewritten after bytecode expansion.

### Flag Cleanup
- **Before:** Synthetic flags passed through blindly.
- **Now:** `--strip-synthetic` option clears `ACC_SYNTHETIC` on classes/methods/fields for strict tooling.

### CLI Behavior
- **Before:** Minimal `python JXE2JAR.py input.jxe output.jar`.
- **Now:** argparse with options: `--skip-jdk`, `--skip-classes`, `--skip-libs`, `--strip-synthetic`.

## Testing Workflow

1. Build edge-case JAR:
   ```sh
   sh test/custom_edgecases/build.sh
   ```
2. Convert JAR → JXE with `jar2jxe.exe` (see [`vms/xp/README.md`](vms/xp/README.md)).
3. Convert JXE → JAR with Python:
   ```sh
   python3 src/jxe2jar.py input.jxe output.jar
   ```

## Usage Notes

- JDK/JRE classes are skipped by default using `src/rt.classes`.
- Use `--skip-jdk /path/to/rt.jar` to override the JDK/JRE skip list.
- Use `--skip-classes` to provide additional JAR/JMOD/list files or a directory.
- The converter preserves `ACC_SYNTHETIC` by default. Use `--strip-synthetic` if you need strict `javap` output for 45.0 classes.
- Classfile versions are inferred from flags/opcodes with a minimum of 46 (no upper cap).
- Some large binaries/ISOs are referenced via `.url` files pointing to original archives:
  - `vms/xp/en_vs_2005_pro_dvd.iso.url`
  - `vms/xp/en_windows_xp_professional_with_service_pack_3_x86_cd_vl_x14-73974.iso.url`

## See Also

- [`src/README.md`](src/README.md) – Format knowledge and implementation details
- [`test/custom_edgecases/README.md`](test/custom_edgecases/README.md) – Test coverage list
- [`vms/xp/README.md`](vms/xp/README.md) – WM5 emulator + XP VM instructions

## Credits

Thanks to the original repo, forks, and contributors:
- https://github.com/moradek/jxe2jar
- https://github.com/andrewleech/jxe2jar
