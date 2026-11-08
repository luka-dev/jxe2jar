# src

Python implementation of **JXE -> JAR** conversion for IBM J9/CDC (ROM class) images.

## Overview

This tool:
- Reads J9 `rom.classes` from a `.jxe` (ZIP) and reconstructs standard `.class` files
- Rewrites J9/JIT-specific bytecodes into standard JVM bytecode
- Rebuilds constant pools, fields, methods, and Code attributes

## Entry Point

- `jxe2jar.py` - CLI to convert a `.jxe` into a `.jar`

## Usage

```sh
python3 src/jxe2jar.py input.jxe output.jar
python3 src/jxe2jar.py input.jxe output.jar --strip-synthetic
python3 src/jxe2jar.py input.jxe output.jar --dont-infer-enclosing
```

## Flags

| Flag | Description |
|------|-------------|
| (default) | Every class is converted; the JXE's non-`rom.classes` entries are copied through; `EnclosingMethod` is synthesized for ROM-erased anon classes (`Outer$N`) - enclosing class and method taken from the `new` site when unambiguous - so decompilers inline them |
| `--strip-synthetic` | Clear `ACC_SYNTHETIC` on classes/methods/fields (for strict javap) |
| `--dont-infer-enclosing` | Turn off the default `EnclosingMethod` synthesis |

## Key Logic and Format Knowledge

### J9 ROM Layout
Parsing implemented in `jxe.py`. Constant-pool slot types come from the ROM itself: index
`>= ramConstantPoolCount` is the long/double tail, below it the `cpShapeDescription` nibble
(1 string, 2 class, 3 static field ref, 0 scalar / method / instance field ref), and header
word 19 points at the romizer's kind-run stream that says int vs float / long vs double for
every scalar slot. The header carries no classfile version.

### Modified UTF-8
Decoder in `common.py`, with validation and SRP fallbacks.

### Constant Pool Reconstruction
Implemented in `constpool.py`:
- Supports INTEGER/FLOAT/LONG/DOUBLE/STRING/CLASS/REF (1:1 with ROM slots, extras appended)
- Encodes JVM modified UTF-8 (NUL as C0 80, astral chars as surrogate pairs)
- Preserves method descriptors for invokeinterface argument counts

### Field ConstantValue Recovery
Implemented in `jxe2jar.py`:
- Supports static final primitives/String values via ROM field metadata; a String constant is
  the ROM pool slot indexed by the field's constant word (no name-based heuristics)
- ConstantValue on final *instance* fields is not in the ROM at all (J9 keeps static constants only)

### Bytecode Transforms
Implemented in `bytecode.py`:
- J9 wide opcodes -> standard `wide` form
- `invokeinterface` count byte computed from method descriptor
- `ldc` upgraded to `ldc_w` if CP index > 255
- J9's devirtualized `invokespecial` restored to `invokevirtual` exactly where bcutil
  created it: Object's six finals (any owner) and the class's own final methods
- J9 wide forms (`CB-D4` 4 bytes, `D5` 6 bytes) re-encoded as JVM `wide` of the same length
- Switch padding recalculated based on output position
- J9 return opcodes mapped to standard returns
- The romizer's trailing `nop` padding (bytecode size is stored in u32 words) is dropped

## Output Classfile Notes

- Classfile version is 46, or 49 when the class needs Java 5 (enum/annotation flags, bridge/varargs,
  `Signature`, `ldc` of a class constant); never above 49 (no `StackMapTable` in the ROM)
- `ACC_SUPER` is enforced for non-interfaces
- `ACC_SYNTHETIC` is preserved unless `--strip-synthetic` is used

## Known Limitations

- ROM metadata outside standard classfile fields is not preserved
- Some J9-specific optimizations may be dropped during bytecode rewrite
- For strict `javap` output on old classfile versions, `--strip-synthetic` may be required

## Validation

- Comprehensive edge-case suite in `test/custom_edgecases/`
- Large LSD JXE (`test/jxes/MU1316-lsd.jxe`) converts fully with current code
