# src

Python implementation of **JXE → JAR** conversion for IBM J9/CDC (ROM class) images.

What this tool does
- Reads J9 `rom.classes` from a `.jxe` (ZIP) and reconstructs standard `.class` files.
- Rewrites J9/JIT‑specific bytecodes into standard JVM bytecode.
- Rebuilds constant pools, fields, methods, and Code attributes.

Main entry point
- `jxe2jar.py` – CLI to convert a `.jxe` into a `.jar`.

Usage
```
python3 src/jxe2jar.py input.jxe output.jar
python3 src/jxe2jar.py input.jxe output.jar --skip-java-lang
python3 src/jxe2jar.py input.jxe output.jar --skip-libs libs/
python3 src/jxe2jar.py input.jxe output.jar --strip-synthetic
```

Flags
- `--skip-java-lang` skips `java/*`, `javax/*`, `sun/*`, etc.
- `--skip-libs DIR` skips classes present in JARs under `DIR`.
- `--strip-synthetic` clears ACC_SYNTHETIC on classes/methods/fields (for strict javap).

Key logic and format knowledge
- **J9 ROM layout** parsing in `jxe.py`.
- **Modified UTF‑8** decoder in `common.py`, with validation and SRP fallbacks.
- **Constant pool reconstruction** in `constpool.py`:
  - Supports INTEGER/FLOAT/LONG/DOUBLE/STRING/CLASS/REF.
  - Encodes UTF‑8 with `surrogatepass` for emoji/surrogate sequences.
  - Preserves method descriptors for invokeinterface argument counts.
- **Field ConstantValue** recovery in `jxe2jar.py`:
  - Supports static final primitives/String values via ROM field metadata.
  - Handles empty string heuristics when ROM omits explicit empty string constant.
- **Bytecode transforms** in `bytecode.py`:
  - J9 wide opcodes → standard `wide` form.
  - `invokeinterface` count byte computed from method descriptor.
  - `ldc` upgraded to `ldc_w` if CP index > 255.
  - Switch padding recalculated based on output position.
  - J9 return opcodes mapped to standard returns.

Output classfile notes
- Classfile version is clamped into a JVM‑friendly range (45..52) for tooling.
- ACC_SUPER is enforced for non‑interfaces.
- ACC_SYNTHETIC is preserved unless `--strip-synthetic` is used.

Known limitations
- ROM metadata outside standard classfile fields is not preserved.
- Some J9‑specific optimizations may be dropped during bytecode rewrite.
- For strict `javap` output on old classfile versions, `--strip-synthetic` may be required.

Validation
- Comprehensive edge‑case suite is in `test/custom_edgecases/`.
- Large LSD JXE (`test/jxes/MU1316-lsd.jxe`) converts fully with current code.
