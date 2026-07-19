# jxe2jar

Tools and notes for converting **IBM J9/CDC JXE (rom.classes)** images back to standard Java `.class` files / `.jar` archives.

## Repository Structure

| Directory | Description |
|-----------|-------------|
| `src/` | Python implementation of **JXE -> JAR** conversion |
| `tools/` | Decompile pipeline and post-decompile helpers: `vineflower.sh`, `annotate_constants.py`, `xref.py`, `decompile_fallback.py`, `int2hex.py` |
| `test/custom_edgecases/` | Exhaustive edge-case suite (Java 1.2) to validate the converter |
| `out/` | Conversion outputs and logs |
| `vms/` | Virtualized environments for legacy tooling (XP VM -> WM5 emulator -> jar2jxe) |

The converter is validated through edge-case tests and a **JAR -> JXE -> JAR** round-trip pipeline.

## Conversion Logic

The converter parses a JXE image into per-class ROM structures (`src/jxe.py`), then
reassembles each into a standard `.class` file: the constant pool is rebuilt
(`src/constpool.py`), J9 bytecode is translated to standard JVM bytecode
(`src/bytecode.py`), and the classfile plus its attributes are written out
(`src/jxe2jar.py`). Most of that is a mechanical 1:1 mapping.

The sections below document the **non-obvious fixups** - the specific points where the
J9 ROM format diverges from a standard classfile, so a naive copy would produce
something the JVM verifier or a decompiler rejects. Each is tagged with the file it
lives in. If you are only patching classes and hit a *"where does X come from"*
question, this is the map.

### Classfile version  (`src/jxe2jar.py`)
- **Before:** Wrote ROM class version as-is (can be non-standard).
- **Now:**
  - Infers minimal version from class/field/method flags (minimum 46).
  - Bumps to 49 when synthetic/enum/annotation/bridge/varargs flags are present so `javac`/`javap` accept output.
  - **No version >= 50.** The J9 romizer strips `StackMapTable`, which the type-checking verifier (class version >= 50) *requires* - so any >= 50 stamp yields a class that fails `-Xverify:all` with *"Expecting a stack map frame"*. Version <= 49 keeps every class on the old inference verifier, which needs no stack maps. An earlier heuristic bumped to 51 on a raw `0xBA in bytecode` byte-scan for invokedynamic; that false-positived on 1559 firmware classes with zero real invokedynamic (and the converter emits no `BootstrapMethods`, so a genuine one couldn't be produced anyway). Removed - firmware is javac-7 max with no invokedynamic. Result: whole-jar `v>=50` count 1559 -> 0, all now verifiable.

### Devirtualized `invokespecial` -> `invokevirtual`  (`src/bytecode.py`)
- **Problem:** J9's romizer devirtualizes `invokevirtual` of a *final* method into `invokespecial` (a final method binds statically). Standard bytecode forbids `invokespecial` to a superclass method on a receiver not assignable to the current class, so HotSpot's verifier rejects it with *"Incompatible object argument for invokespecial"*. The near-universal trigger is the `x.getClass()` idiom - the NPE-guard the compiler inserts, and `this.getClass() != o.getClass()` in `equals()` - where the receiver is a parameter, not `this`.
- **Fix:** during bytecode translation, `invokespecial` whose target is one of `java/lang/Object`'s final methods (`getClass`, `wait`, `notify`, `notifyAll`) is rewritten to `invokevirtual`. Safe because these are final: virtual and non-virtual dispatch are identical and no `super`-call is possible. Constructors (`<init>`), private-method calls, and genuine `super.m()` (receiver `this`, verifies fine) are left untouched. Resolution needs the methodref's class+name, so both const-pool build paths (`J9CONST.REF` and the `J9CONST.LONG`-decoded ref) carry `ref_class`/`ref_name` into the transform table.
- **Result:** on a 404-class verification sample, `-Xverify:all` failures went 19 -> 0. (This was a pre-existing bug masked on `v51` classes by the missing-stack-map error; it surfaced only once versions were capped at 49. It never affected decompilation - VF/CFR render these classes fine either way.)

### Constant-pool tail integrity  (`src/jxe.py`, `src/constpool.py`)
Whole-jar `-Xverify:all` also surfaced three narrow correctness bugs in how the ROM constant pool is read, each affecting a handful of classes:
- **Dropped CP slot -> index shift.** The reader looped `rom_constant_pool_count` times and, on `EOFError` from a slot whose pointer-chase ran off the end (J9 padding in the ram/rom-count gap), silently skipped the entry. That left the entry list one short, shifting every later CP index by one and silently rewiring all references after it. Fixed by appending a placeholder constant on `EOFError` so list indices stay aligned with ROM indices (`jxe.py`). Two classes were affected (`ParserTokenManager`, `TimeUnit$4`).
- **Null/garbage CP entries reach the classfile.** Those padding slots can decode to a `CONSTANT_Class` with an empty name, or a field/method ref whose name is really a type descriptor (`Lx/Y;`) or whose descriptor is garbage (`JJTANDNODE`) - all rejected by the loader (`Illegal class name` / `Illegal field name` / `illegal signature`). They are always unreferenced. `constpool.py` now substitutes a valid placeholder name (`java/lang/Object` for classes) and, via `_sanitized_ref`, replaces an illegal member name/descriptor with an inert `_pad:Ljava/lang/Object;`. The descriptor check is exact (a primitive descriptor is a single char - `JJTANDNODE` is *not* `long` just because it starts with `J`).
- **Net result:** whole-jar `-Xverify:all` -> **0 VerifyError, 0 ClassFormatError** across all classes (remaining non-OK are benign: `java.*` package classes the app loader refuses to define, and classes whose supertypes were excluded via `--skip-libs`).

### Modified UTF-8 for string constants  (`src/constpool.py`)
Classfile `CONSTANT_Utf8` uses JVM **Modified UTF-8** (JVMS 4.4.7), not standard UTF-8. The converter previously wrote `str.encode("utf-8", "surrogatepass")`, which differs in two loader-enforced ways: `U+0000` must be `0xC0 0x80` (never a bare `0x00`), and a supplementary char must be its UTF-16 surrogate pair as two 3-byte sequences (never a single 4-byte sequence). Plain ASCII/BMP text is identical, so this only bites strings carrying NULs or astral chars - e.g. `java.text.CollationRules`, whose rule string embeds `U+0000..U+001F`, was rejected with *"Illegal UTF8 string in constant pool"*. `_encode_utf8` now emits proper Modified UTF-8. (Surfaced only when converting the JDK/`java.*` classes too - pass `--skip-jdk <emptyfile>` to convert every ROM class, not just the firmware ones.)

### InnerClasses reconstruction from real ROM metadata  (`src/jxe2jar.py`, `src/jxe.py`)
The `InnerClasses` attribute is rebuilt from the **actual J9 ROM fields**, not guessed from `$` names. J9 preserves per class (unlike `StackMapTable`): `outerClassName`, `memberAccessFlags`, the `innerClasses` list and, as optional info, `simpleName` (flag `0x80`) and an `EnclosingMethod` marker (flag `0x40`). `build_inner_meta` reads these (the header layout was corrected - `outerClassName` sits one word later than the old field map assumed), so each entry's outer/name/flags are exact - a nested interface keeps `interface+abstract`, a private member stays `private`, etc.

Per class, the entry set mirrors javac: itself, its enclosing nest chain, its members, and every nested class it references. References are collected from the constant pool, the superclass/interfaces (which live outside the CP), all field/method descriptors, and - crucially - the *output* constant pool's UTF-8 entries, since some refs (e.g. a synthetic `<init>(Outer$1)` accessor call) are reconstructed during conversion and never appear as J9 ROM constants.

One flag J9 leaves at 0 is recovered: the `ACC_STATIC` on a synthetic/anonymous nested class. A non-static inner class captures its enclosing instance in a synthetic `this$0` field, so that field's *absence* means the class is static - an exact, build-independent tell. (An earlier `ACC_FINAL` heuristic only correlated on some builds: cross-variant validation found MHI2Q_CN anonymous classes that are static but not final.)

Validated byte-for-byte against each firmware's own pre-romization jars, across US, JP and CN builds: **InnerClasses match exactly (100%)** (fw_util_commons 98/98, fw_util_tracing 209/209 per build).

### Exceptions attribute / `throws` clauses  (`src/jxe2jar.py`)
J9 keeps each method's declared checked exceptions (`throw_exceptions`), which the converter used to drop - so decompiled methods showed no `throws`. The standard `Exceptions` attribute is now emitted from them (~10.5% of methods carry one). Validated byte-for-byte against the firmware jars (fw_util_commons 45/45, fw_util_tracing 117/117).

*What is not recoverable:* a survey of the ROM optional-info flags shows the romizer strips `Signature` (generics - present on only 0.9%), `LocalVariableTable`/`LineNumberTable` (debug info / real variable names - 0%), runtime `Annotations` (0%) and `SourceFile` (0%). So generics stay erased and locals keep Vineflower's `jad` type-based names - those are a hard ROM limit, not a converter gap.

### Post-decompile tooling
- **`tools/annotate_constants.py`** - recover inlined `static final int` names. javac
  inlines constants at the call site, but the names survive in registry interfaces, so
  `getChoiceModel(402127)` becomes `getChoiceModel(/* NAV_MAP_SERVICELIST_GOOGLE_EARTH_CHOICE */ 402127)`
  and `getText(871)` becomes `getText(/* TEXT_CONST_EVO_INPUTFIELD_DELETE_PROMPT */ 871)`.
  Config-driven (one dict per accessor family); resolution is context-aware - model IDs
  live in `*ModelBank` files (which beats enum-value collisions), `*_CHOICE`/`TEXT_` hints
  and the caller's package domain pick the alias, and a per-accessor value floor drops the
  small per-class indices. ~9100 call sites on MU1316-lsd.
- **`tools/xref.py`** - bytecode cross-reference. `--callers <owner>[.member]` lists which
  classes reference a class/method/field (precise, read from constant pools - not grep);
  `--uses`/`--dump` for the other directions. Answers "who calls this?" during RE.
- **`tools/decompile_fallback.py`** - re-decompiles any residual Vineflower stub
  (`// $VF: Couldn't be decompiled`) with CFR and replaces the file.
- **`tools/int2hex.py`** - decimal->hex for bitmask/flag/colour literals.

*Not recoverable* (romizer-stripped, confirmed by an optional-flags survey): real local
variable names (0% debug info - Vineflower's `jad` type-based names are the ceiling),
generics on 99% of classes, runtime annotations, and log-level names (the `log(100000, ...)`
verbosity numbers have no `static final int` source constant, unlike model/text IDs).

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
  - **Float constant recovery:** J9 stores both `int` and `float` as `J9CONST.INT` (type 0) - the ROM format has no int/float distinction. A bytecode pre-pass with stack simulation (`_find_float_constants`) walks each method before translation, tracking which `ldc`/`ldc_w` constant pool entries flow into float-consuming operations (`fstore`, `fadd`, `fcmpg`, `putfield` with `F` descriptor, `invoke*` with `F` parameters, etc.). Identified entries are reclassified from `CONST.INTEGER` to `CONST.FLOAT` via `new_cp_transform`. The stack simulation correctly models `getfield` (pop objectref + push value), array loads (pop index + arrayref + push value), and other opcodes to keep parameter positions aligned with invoke descriptors.
  - **Float constants inside ternary branches:** the linear stack pass above clears its stack at every branch, so a float constant that lives in one arm of `cond ? A : B` is never seen flowing into the float consumer - it stays typed `int`, the other arm stays `float`, and decompilers throw *"No common supertype for ternary expression"*. A second pass `_find_ternary_float_constants` pattern-matches the ternary shape (`ifXX L1 ; armA ; goto L2 ; L1: armB ; L2:`) and, when one arm's terminal push is an int-ldc and the other's is unambiguously float (`fconst`/`fload`/`faload`/`fneg`/`i2f`/`l2f`/`d2f`/f-arith/f-returning `invoke`, or an ldc already reclassified float), reclassifies the int-ldc to float. int-vs-float is the only trigger, so genuine int constants are never mis-typed. This alone took the MU1316 LSD decompile from 15 -> ~1 un-decompilable class (the remainder is an unrelated VF parsing bug on an IBM stdlib method). Bounds on the `goto`/`goto_w` offset (`T < l2 <= n`) are load-bearing - without them a malformed offset crashes the whole class's conversion.

### Bytecode Translation
- **Before:** Basic mapping, missing J9 wide opcodes and invokeinterface handling.
- **Now:**
  - Wide opcodes are normalized to JVM `wide`.
  - `invokeinterface` count is computed from the descriptor.
  - `ldc` is promoted to `ldc_w` when CP index > 255.
  - J9 prefix opcodes are expanded correctly (e.g., implicit `aload_0` prefix).
  - J9 return opcodes are mapped to standard JVM returns based on method signature:
    - `JBreturn0` / `JBsyncReturn0` / `JBreturnFromConstructor` / `JBretFromNative0` -> `return`
    - `JBreturn1` / `JBsyncReturn1` / `JBretFromNative1` -> `ireturn` / `freturn` / `areturn`
    - `JBreturn2` / `JBsyncReturn2` -> `lreturn` / `dreturn`
    - `JBretFromNativeF` / `JBretFromNativeD` / `JBretFromNativeJ` -> typed returns
    - `JBgenericReturn` / `JBreturnToMicroJIT` -> inferred from descriptor
  - J9 runtime/debug opcodes (`JBasyncCheck`, `JBbreakpoint`, `JBimpdep1`, `JBimpdep2`) -> `nop`
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
2. Convert JAR -> JXE with `jar2jxe.exe` (see [`vms/xp/README.md`](vms/xp/README.md)).
3. Convert JXE -> JAR with Python:
   ```sh
   python3 src/jxe2jar.py input.jxe output.jar
   ```

## Usage Notes

- JDK/JRE classes are skipped by default using `src/rt.classes`.
- Use `--skip-jdk /path/to/rt.jar` to override the JDK/JRE skip list.
- Use `--skip-classes` to provide additional JAR/JMOD/list files or a directory.
- The converter preserves `ACC_SYNTHETIC` by default. Use `--strip-synthetic` if you need strict `javap` output for 45.0 classes.
- Classfile versions are inferred from flags with a minimum of 46 and never exceed 49 (keeps every class on the stack-map-free inference verifier; see Classfile Version above).
- Some large binaries/ISOs are referenced via `.url` files pointing to original archives:
  - `vms/xp/en_vs_2005_pro_dvd.iso.url`
  - `vms/xp/en_windows_xp_professional_with_service_pack_3_x86_cd_vl_x14-73974.iso.url`

## Decompiling

**Recommendation:** Use Vineflower for primary analysis - fewer artifacts, cleaner inner class handling, no broken anonymous imports. Keep CFR output alongside for cross-referencing on the rare method VF still can't do.

**Vineflower version - use 1.12.0, renamer `jad`.** Two settings decide how many methods come out
as `// $VF: Couldn't be decompiled` stubs on J9-converted classes:
- `--variable-renaming=jad` (not `tiny`): `tiny`/`TinyNameProvider` throws NPE during LVT renaming.
- **VF 1.12.0** (not 1.11.2): 1.11.2's `ExitHelper.cleanUpUnreachableBlocks` NPEs on methods with
  unreachable blocks; fixed upstream in 1.12.0.

Measured on `service.core.registration` bundle (455 classes): **1.11.2 `tiny` -> 399** broken files,
**1.11.2 `jad` -> 1**, **1.12.0 `jad` -> 0**.

### Decompiling with Vineflower

Use the wrapper script which sets all options, adds JDK8 rt.jar, and auto-includes `libs/*.jar`:

```sh
bash tools/vineflower.sh out/MU1316-lsd.jar                    # output: out/MU1316-lsd-vf/
bash tools/vineflower.sh out/MIB3G-lsd.jar out/custom-dir      # custom output dir
```

The wrapper auto-selects the newest `tools/vineflower-*.jar` and picks the runtime itself.
**Two Javas are involved:**
- **VF 1.12.0 runs on Java 17+** (its own classes are class-file 61). The wrapper finds one via
  `/usr/libexec/java_home -v 17+`, or honours `VINEFLOWER_JAVA=/path/to/java17+/bin/java`.
- **`--include-runtime` stays the JDK 8** under `jvms/zulu8.../` (its `rt.jar` is what the *target*
  1.2/1.3 firmware classes are resolved against). That JDK8 must still be present.

<details>
<summary>Equivalent manual command</summary>

```sh
# note: run with a Java 17+ (VF 1.12.0 needs it); --include-runtime still points at JDK 8.
java17+ -Xmx30g -jar tools/vineflower-1.12.0.jar \
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
  --variable-renaming=jad \
  --rename-parameters=true \
  "--include-runtime=path/to/jdk8" \
  "--banner=" \
  "--indent-string=    " \
  --preferred-line-length=120 \
  --thread-count=14 \
  --old-try-dedup \
  --verify-merges \
  --warn-inconsistent-inner-attributes=false \
  --add-external=path/to/jdk8/jre/lib/rt.jar \
  --add-external=libs/client-runtime-3.3.0.jar \
  --add-external=libs/ec.base-3.1.8.jar \
  --add-external=libs/html-5.0.bv6.jar \
  --add-external=libs/jquery-1.11.3.bv1.jar \
  --add-external=libs/jquery-1.11.3.jar \
  --add-external=libs/org.apache.commons.logging-4.3.1.jar \
  --add-external=libs/org.apache.xerces-2.9.0.jar \
  --add-external=libs/org.json-ld-3.1.8.jar \
  --add-external=libs/org.osgi.framework-1.10.0.jar \
  --add-external=libs/org.osgi.util.tracker-1.5.4.jar \
  --add-external=libs/osgi.annotation-8.0.1.jar \
  --add-external=libs/shared-3.3.0.jar \
  out/MU1316-lsd.jar out/MU1316-lsd-vf
```

</details>

Key options explained:
- `--variable-renaming=jad --rename-parameters=true` - readable variable names derived from type (J9 ROM has no debug info / LocalVariableTable). Use `jad`, **not** `tiny` - `tiny` (`TinyNameProvider`) NPEs during LVT renaming and leaves methods as un-decompiled stubs.
- `--decompile-inner --remove-synthetic --remove-bridge` - inline anonymous classes, hide compiler-generated methods
- `--ignore-invalid-bytecode` - don't crash on J9-converted bytecode edge cases
- `--indent-string="    " --preferred-line-length=120` - readable formatting
- `--include-runtime=path/to/jdk8` - gives Vineflower access to JDK8's standard library for resolving `@Override` on standard interfaces like `Runnable`, `Iterator`, `Comparable`
- `-Xmx30g` - large heap for 30k-class JAR
- `--add-external=path` - use `--add-external=` (not `-e`) when passing via scripts; `-e` only works on the command line

**External library references (`--add-external`):**
Vineflower can only add `@Override` annotations and resolve generics when it knows the parent class/interface. Classes inside the JAR resolve automatically, but SDK/framework classes that were excluded during conversion (via `--skip-libs`) are missing. Adding them back as external references with `--add-external=` gives Vineflower the type information it needs without including them in the output. Skip `-javadoc.jar` and `-sources.jar` - only use compiled JARs.

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
- `--sugar*` / `--decode*` - recover high-level constructs (enums, asserts, boxing, lambdas, switches, try-with-resources, for-each)
- `--removeboilerplate --removedeadmethods --removebadgenerics` - clean up compiler artifacts
- `--hidebridgemethods --removeinnerclasssynthetics` - hide synthetic access methods
- `--renameillegalidents` - fix identifiers that aren't valid Java (e.g. `$1`)
- `--recover --allowcorrecting` - best-effort recovery on broken bytecode

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
Works on both CFR and Vineflower output.

### Post-processing: int2hex.py

Decompilers output all integer constants in decimal. Values that are bitmasks, flags, or bit patterns are more readable in hex (e.g. `6291488` -> `0x600020`). The `int2hex.py` script heuristically identifies these and converts them.

Heuristics used (each contributes a score):
- **Power of 2** - `4194304` -> `0x400000`
- **All-ones mask** - `2147483647` -> `0x7FFFFFFF`
- **Nibble-aligned** - trailing zero nibbles, e.g. `65536` -> `0x10000`
- **Sparse bits** - few bits set in a large value (bitmask pattern)
- **Dense mask** - most bits set (e.g. `0x3FFFFF`)
- **Context** - nearby bitwise operators (`&`, `|`, `~`) or hex literals on the same line

```sh
# Dry-run (report only)
python3 tools/int2hex.py out/MU1316-lsd-vf/

# Apply in-place
python3 tools/int2hex.py out/MU1316-lsd-vf/ --apply

# Lower threshold for more aggressive conversion (more false positives)
python3 tools/int2hex.py out/MU1316-lsd-vf/ --threshold 1.0 --apply

# Export CSV report for manual review
python3 tools/int2hex.py out/MU1316-lsd-vf/ --report report.csv
```

Default threshold is 2.0 (conservative - bitmasks, masks, powers of 2). Use `--threshold 1.0` for aggressive conversion of borderline values like config IDs.

## See Also

- [`src/README.md`](src/README.md) - Format knowledge and implementation details
- [`test/custom_edgecases/README.md`](test/custom_edgecases/README.md) - Test coverage list
- [`vms/xp/README.md`](vms/xp/README.md) - WM5 emulator + XP VM instructions

## Credits

Thanks to the original repo, forks, and contributors:
- https://github.com/moradek/jxe2jar
- https://github.com/andrewleech/jxe2jar
