# custom_edgecases

This folder contains **edge-case Java 1.2 test classes** used to validate `jar2jxe` output and the Python `jxe2jar` reverse conversion.

## Goal

- Exercise rare bytecodes, constant pool variants, and ROM field metadata
- Catch bugs in decoding/rewriting (wide ops, invokeinterface counts, Unicode, etc.)

## Test Classes

| Class | Purpose |
|-------|---------|
| `Hello` | Baseline class with fields and simple methods |
| `MathOps` | Arithmetic and simple control flow |
| `TryCatch` + `TryCatch$Boom` | Exceptions + catch tables |
| `TryFinally` | Finally blocks (legacy jsr/ret patterns in 1.2) |
| `TryFinallyReturn` | Return inside try/finally |
| `RetFinallyConstructor` | Finally in constructor path |
| `Thrower` | Explicit `athrow` path |
| `SynchronizedTest` | Synchronized methods |
| `SynchronizedBlock` | monitorenter/monitorexit (block form) |
| `SynchronizedThrow` | monitorenter/monitorexit on exception path |
| `SwitchTest` | Basic switch |
| `SwitchVariants` | tableswitch vs lookupswitch |
| `WideLocals` | Wide local indices + `iinc_w` |
| `ArrayTest` | Object array usage |
| `ArraysPrimitives` | All primitive arrays + load/store opcodes |
| `MultiArray` | `multianewarray` opcode |
| `NullChecks` | `ifnull` / `ifnonnull` |
| `Constants` | Static final primitives + String ConstantValue |
| `ManyConstants` | Large constant pool pressure |
| `FloatDoubleBits` | NaN/Inf/±0.0 and bit-exact float/double constants |
| `UnicodeStrings` | Empty + UTF-8 edge cases (uses `\u` escapes) |
| `ClassLiterals` | Class literal usage |
| `InterfaceInvoke` + `InterfaceInvoke$*` | Interface calls and dispatch |
| `InterfaceInvokeMany` + `InterfaceInvokeMany$*` | invokeinterface with many args |
| `Inheritance` + `Inheritance$*` | Inheritance + virtual calls |
| `InnerClasses` + `InnerClasses$*` | Inner classes and synthetic members |
| `NativeAbstract` + `NativeAbstract$Impl` | Native + abstract method flags |
| `CastInstanceof` + `CastInstanceof$*` | checkcast/instanceof (incl. arrays) |
| `StaticFinalNonConst` | Static final values not eligible for ConstantValue |

## Build and Use

1. Build:
   ```sh
   sh test/custom_edgecases/build.sh
   ```
2. Convert JAR → JXE (WM5 emulator + `jar2jxe.exe`)
3. Convert back:
   ```sh
   python3 src/jxe2jar.py cases.jxe cases.from_jxe.jar
   ```
