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

## Decompiling

**Recommendation:** Use Vineflower for primary analysis — fewer artifacts, cleaner inner class handling, no broken anonymous imports. Keep CFR output alongside for cross-referencing when VF struggles with a method.

### Decompiling with Vineflower

```sh
java -Xmx20g -jar tools/vineflower-1.11.2.jar \
  --decompile-generics=true \
  --decompile-enums=true \
  --decompile-assert=true \
  --decompile-finally=true \
  --decompile-inner=true \
  --decompile-java4=true \
  --decompile-switch-expressions=true \
  --remove-bridge=true \
  --remove-synthetic=true \
  --remove-empty-try-catch=true \
  --remove-getclass=true \
  --hide-default-constructor=true \
  --hide-empty-super=true \
  --override-annotation=true \
  --inline-simple-lambdas=true \
  --use-lvt-names=true \
  --use-method-parameters=true \
  --boolean-as-int=true \
  --simplify-stack=true \
  --incorporate-returns=true \
  --pattern-matching=true \
  --ternary-in-if=true \
  --ensure-synchronized-monitors=true \
  --ignore-invalid-bytecode=true \
  --decompiler-comments=true \
  --dump-bytecode-on-error=true \
  --variable-renaming=tiny \
  --rename-parameters=true \
  --include-runtime=current \
  --banner="" \
  --indent-string="    " \
  --preferred-line-length=120 \
  --thread-count=14 \
  -e libs/client-runtime-3.3.0.jar \
  -e libs/ec.base-3.1.8.jar \
  -e libs/html-5.0.bv6.jar \
  -e libs/jquery-1.11.3.bv1.jar \
  -e libs/jquery-1.11.3.jar \
  -e libs/org.apache.commons.logging-4.3.1.jar \
  -e libs/org.apache.xerces-2.9.0.jar \
  -e libs/org.json-ld-3.1.8.jar \
  -e libs/org.osgi.framework-1.10.0.jar \
  -e libs/org.osgi.util.tracker-1.5.4.jar \
  -e libs/osgi.annotation-8.0.1.jar \
  -e libs/shared-3.3.0.jar \
  out/MU1316-lsd.jar out/MU1316-lsd-vf
```

Key options explained:
- `--variable-renaming=tiny --rename-parameters=true` — camelCase variable names derived from type (J9 ROM has no debug info / LocalVariableTable)
- `--decompile-inner --remove-synthetic --remove-bridge` — inline anonymous classes, hide compiler-generated methods
- `--ignore-invalid-bytecode` — don't crash on J9-converted bytecode edge cases
- `--indent-string="    " --preferred-line-length=120` — readable formatting
- `--include-runtime=current` — gives Vineflower access to the host JDK's standard library (`java.lang`, `java.util`, etc.) for resolving `@Override` on standard interfaces like `Runnable`, `Iterator`, `Comparable`
- `-Xmx20g` — large heap for 30k-class JAR

**External library references (`-e`):**
Vineflower can only add `@Override` annotations and resolve generics when it knows the parent class/interface. Classes inside the JAR resolve automatically, but SDK/framework classes that were excluded during conversion (via `--skip-libs`) are missing. Adding them back as external references with `-e` gives Vineflower the type information it needs without including them in the output.

Add any JAR that was part of the original runtime classpath:
```sh
-e libs/org.osgi.framework-1.10.0.jar   # OSGi interfaces (Activator, BundleContext, etc.)
-e libs/ec.base-3.1.8.jar               # eSolutions base framework
-e libs/shared-3.3.0.jar                # shared SDK classes
-e libs/client-runtime-3.3.0.jar        # client runtime APIs
# ... etc. — skip -javadoc.jar and -sources.jar, only use compiled JARs
```

### Decompiling with CFR

```sh
java -jar tools/cfr-0.152.jar out/MU1316-lsd.jar \
  --outputdir out/MU1316-lsd-cfr \
  --silent true \
  --comments true \
  --showversion false \
  --removeboilerplate true \
  --removeinnerclasssynthetics true \
  --decodelambdas true \
  --decodefinally true \
  --sugarasserts true \
  --sugarenums true \
  --sugarboxing true \
  --decodeenumswitch true \
  --decodestringswitch true \
  --arrayiter true \
  --collectioniter true \
  --tryresources true \
  --hidebridgemethods true \
  --hidelangimports true \
  --innerclasses true \
  --removebadgenerics true \
  --removedeadmethods true \
  --relinkconst true \
  --relinkconststring true \
  --liftconstructorinit true \
  --override true \
  --renameillegalidents true \
  --recover true \
  --allowcorrecting true \
  --tidymonitors true \
  --labelledblocks true \
  --usenametable true \
  --eclipse true
```

Key options explained:
- `--sugar*` / `--decode*` — recover high-level constructs (enums, asserts, boxing, lambdas, switches, try-with-resources, for-each)
- `--removeboilerplate --removedeadmethods --removebadgenerics` — clean up compiler artifacts
- `--hidebridgemethods --removeinnerclasssynthetics` — hide synthetic access methods
- `--renameillegalidents` — fix identifiers that aren't valid Java (e.g. `$1`)
- `--recover --allowcorrecting` — best-effort recovery on broken bytecode

### Post-processing: fix_class_literals.py

Java 1.2 code uses a synthetic `class$()` method pattern instead of `Foo.class` literals. Neither CFR nor Vineflower collapses this pattern from J9-converted bytecode, leaving ugly ternaries like:

```java
(class$de$audi$app$foo$Bar == null
    ? (class$de$audi$app$foo$Bar = class$("de.audi.app.foo.Bar"))
    : class$de$audi$app$foo$Bar).getName()
```

The `fix_class_literals.py` script replaces these with clean `.class` references:

```java
de.audi.app.foo.Bar.class.getName()
```

It also removes the leftover synthetic `static Class class$...` fields and `class$()` methods.

```sh
# Dry-run (report only)
python3 tools/fix_class_literals.py out/MU1316-lsd-vf/

# Apply in-place
python3 tools/fix_class_literals.py out/MU1316-lsd-vf/ --apply

# Verbose (show each file)
python3 tools/fix_class_literals.py out/MU1316-lsd-vf/ --apply -v
```

Works on both CFR and Vineflower output. Fixes ~2,400 class literals across ~900 files.

## See Also

- [`src/README.md`](src/README.md) – Format knowledge and implementation details
- [`test/custom_edgecases/README.md`](test/custom_edgecases/README.md) – Test coverage list
- [`vms/xp/README.md`](vms/xp/README.md) – WM5 emulator + XP VM instructions

## Credits

Thanks to the original repo, forks, and contributors:
- https://github.com/moradek/jxe2jar
- https://github.com/andrewleech/jxe2jar
