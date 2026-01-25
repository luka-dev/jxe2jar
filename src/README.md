# src

Python implementation of **JXE → JAR** conversion for IBM J9/CDC (ROM class) images.

## Overview

This tool:
- Reads J9 `rom.classes` from a `.jxe` (ZIP) and reconstructs standard `.class` files
- Rewrites J9/JIT-specific bytecodes into standard JVM bytecode
- Rebuilds constant pools, fields, methods, and Code attributes

## Entry Point

- `jxe2jar.py` – CLI to convert a `.jxe` into a `.jar`

## Usage

```sh
python3 src/jxe2jar.py input.jxe output.jar
python3 src/jxe2jar.py input.jxe output.jar --skip-libs libs/
python3 src/jxe2jar.py input.jxe output.jar --skip-jdk /path/to/rt.jar
python3 src/jxe2jar.py input.jxe output.jar --strip-synthetic
```

## Flags

| Flag | Description |
|------|-------------|
| (default) | JDK/JRE classes are skipped using `src/rt.classes` |
| `--skip-jdk PATH` | Override the JDK/JRE skip list (e.g., `rt.jar`) |
| `--skip-classes PATH` | Add classes from a JAR/JMOD/list file (or a directory of JARs) |
| `--skip-libs DIR` | Skip classes present in JARs under `DIR` |
| `--strip-synthetic` | Clear `ACC_SYNTHETIC` on classes/methods/fields (for strict javap) |

## Key Logic and Format Knowledge

### J9 ROM Layout
Parsing implemented in `jxe.py`.

### Modified UTF-8
Decoder in `common.py`, with validation and SRP fallbacks.

### Constant Pool Reconstruction
Implemented in `constpool.py`:
- Supports INTEGER/FLOAT/LONG/DOUBLE/STRING/CLASS/REF
- Encodes UTF-8 with `surrogatepass` for emoji/surrogate sequences
- Preserves method descriptors for invokeinterface argument counts

### Field ConstantValue Recovery
Implemented in `jxe2jar.py`:
- Supports static final primitives/String values via ROM field metadata
- Handles empty string heuristics when ROM omits explicit empty string constant

### Bytecode Transforms
Implemented in `bytecode.py`:
- J9 wide opcodes → standard `wide` form
- `invokeinterface` count byte computed from method descriptor
- `ldc` upgraded to `ldc_w` if CP index > 255
- Switch padding recalculated based on output position
- J9 return opcodes mapped to standard returns

## Output Classfile Notes

- Classfile version is inferred from flags/opcodes with a minimum of 46 (no upper cap)
- `ACC_SUPER` is enforced for non-interfaces
- `ACC_SYNTHETIC` is preserved unless `--strip-synthetic` is used

## Known Limitations

- ROM metadata outside standard classfile fields is not preserved
- Some J9-specific optimizations may be dropped during bytecode rewrite
- For strict `javap` output on old classfile versions, `--strip-synthetic` may be required

## Validation

- Comprehensive edge-case suite in `test/custom_edgecases/`
- Large LSD JXE (`test/jxes/MU1316-lsd.jxe`) converts fully with current code
