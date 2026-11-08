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
| `FloatDoubleBits` | NaN/Inf/+/-0.0 and bit-exact float/double constants |
| `UnicodeStrings` | Empty + UTF-8 edge cases (uses `\u` escapes) |
| `ClassLiterals` | Class literal usage |
| `InterfaceInvoke` + `InterfaceInvoke$*` | Interface calls and dispatch |
| `InterfaceInvokeMany` + `InterfaceInvokeMany$*` | invokeinterface with many args |
| `Inheritance` + `Inheritance$*` | Inheritance + virtual calls |
| `InnerClasses` + `InnerClasses$*` | Inner classes and synthetic members |
| `NativeAbstract` + `NativeAbstract$Impl` | Native + abstract method flags |
| `CastInstanceof` + `CastInstanceof$*` | checkcast/instanceof (incl. arrays) |
| `StaticFinalNonConst` | Static final values not eligible for ConstantValue |
| `SipushArgs` | sipush-range values as method args (reproduces the sipush-as-branch bug) |
| `AllReturnTypes` | Every return type: void/boolean/byte/char/short/int/float/long/double/Object/array + synchronized variants |
| `FinalCalls` + `FinalCalls$*` | Every call shape the romizer may devirtualise: own/inherited final, private on another instance, `super.m()`, `Outer.super.m()` (javac `access$N01` accessor), final class, Object's final methods on every receiver type |
| `BigConstants` | String constants of 12 KB and 33 KB (CJK) - the old reader capped J9UTF8 at 10000 bytes and returned "" - plus ConstantValue on final *instance* fields (J9 keeps static ones only), `native ... throws` (the native exception-info block was skipped), and methods ending in `goto` / `athrow` / a switch so the romizer's u32 nop padding sits behind a terminal instruction |
| `FloatTyping` | int vs float and long vs double with identical bit patterns in one class, floats in ternaries and behind long/double arguments, ConstantValue of each kind |
| `WideForms` | long/float/double/object locals above slot 255 (every wide load/store) and wide `iinc` with large and negative constants |

## Build and Use

1. Build:
   ```sh
   sh test/custom_edgecases/build.sh
   ```
2. Convert JAR -> JXE with the real `jar2jxe.exe`, unattended: `python3 tools/wm5/host.py jar2jxe out/cases.jar out/cases.jxe --startup cases.Hello` (see `tools/wm5/README.md`)
3. Convert back and let the JVM judge (verifier, version 46, opcode-exact vs `cases.jar`):
   ```sh
   python3 test/test_roundtrip_verify.py
   ```
