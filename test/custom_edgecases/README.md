# custom_edgecases

This folder contains **edge‑case Java 1.2 test classes** used to validate
`jar2jxe` output and the Python `jxe2jar` reverse conversion.

Goal
- Exercise rare bytecodes, constant pool variants, and ROM field metadata.
- Catch bugs in decoding/rewriting (wide ops, invokeinterface counts, Unicode, etc.).

Classes and why they exist
- `Hello` – baseline class with fields and simple methods.
- `MathOps` – arithmetic and simple control flow.
- `TryCatch` + `TryCatch$Boom` – exceptions + catch tables.
- `TryFinally` – finally blocks (legacy jsr/ret patterns in 1.2).
- `TryFinallyReturn` – return inside try/finally.
- `RetFinallyConstructor` – finally in constructor path.
- `Thrower` – explicit `athrow` path.
- `SynchronizedTest` – synchronized methods.
- `SynchronizedBlock` – monitorenter/monitorexit (block form).
- `SynchronizedThrow` – monitorenter/monitorexit on exception path.
- `SwitchTest` – basic switch.
- `SwitchVariants` – tableswitch vs lookupswitch.
- `WideLocals` – wide local indices + `iinc_w`.
- `ArrayTest` – object array usage.
- `ArraysPrimitives` – all primitive arrays + load/store opcodes.
- `MultiArray` – `multianewarray` opcode.
- `NullChecks` – `ifnull` / `ifnonnull`.
- `Constants` – static final primitives + String ConstantValue.
- `ManyConstants` – large constant pool pressure.
- `FloatDoubleBits` – NaN/Inf/±0.0 and bit‑exact float/double constants.
- `UnicodeStrings` – empty + UTF‑8 edge cases (uses \\u escapes).
- `ClassLiterals` – class literal usage.
- `InterfaceInvoke` + `InterfaceInvoke$*` – interface calls and dispatch.
- `InterfaceInvokeMany` + `InterfaceInvokeMany$*` – invokeinterface with many args.
- `Inheritance` + `Inheritance$*` – inheritance + virtual calls.
- `InnerClasses` + `InnerClasses$*` – inner classes and synthetic members.
- `NativeAbstract` + `NativeAbstract$Impl` – native + abstract method flags.
- `CastInstanceof` + `CastInstanceof$*` – checkcast/instanceof (incl. arrays).
- `StaticFinalNonConst` – static final values not eligible for ConstantValue.

Build and use
- Build: `sh test/custom_edgecases/build.sh`
- Convert JAR→JXE (WM5 emulator + `jar2jxe.exe`)
- Convert back: `python3 src/jxe2jar.py cases.jxe cases.from_jxe.jar`
