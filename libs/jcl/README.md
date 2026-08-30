# Firmware JCL (API constraint) - per platform

The J9 2.3 CDC Foundation Profile 1.1 class library the firmware ships, used as the
**API ceiling** for decompiler resolution (`VF_JCL=...`) instead of a generic SE8 rt.jar.

Two platforms kept separate - **do not cross them** (a MHI2Q literal that coincidentally
matches a MHI2 constant is not a real reference):

Folder = the firmware (full name). Each has its own `ext/` + `core-lsd.jar` + `jcl.jar`.

| dir | platform | ext | core-lsd |
|-----|----------|-----|----------|
| `MHI2Q_US_AUG22_P5087_MU1316/` | MHI2Q | own (308) | own MU1316 lsd (1166) |
| `MHI2_ER_VWG13_K4525_MU1367/`   | MHI2 | own (308) | own MU1367 lsd (1400) |
| `MHI2_ER_AU37x_P5089_MU1326/` | MHI2 | **stand-in = MU1367** (308) | own MU1326 lsd (996) |
| `MIBstd2_FW_0516/` | VW MIB std2 | j9jce (45) | **complete** jclFoundation11 (973, NOT a subset - plain jar from the build tree) |
| `_generic-SE8/rt.jar` | (not firmware) | full Java SE 8 rt.jar (19991) - generic fallback, over-permissive | - |

`ext` is ~99% J9-2.3-CDC-generic (MHI2Q MU1316 vs MHI2 MU1367 differ in only 2 classes,
`org/conscrypt/Platform*` = OpenSSL binding).

Each folder:
- `ext/*.jar` - **exact device extension classes**, copied byte-for-byte from that platform's
  `jre/lib/jclFoundation11/{ext,opt-ext}/` (jsse, jce, jceprov, nio, crypto, socks5,
  objectSwapper, xiploader, MCFObjectReader). Real device bytes, no reverse.
- `core-lsd.jar` - the **core** `java.*`/`javax.*`/`com.ibm.oti.*` classes, recovered from that
  platform's romized `lsd.jxe`. **This is a use-subset**, not the whole CDC core: the device
  romizes the core XIP into the boot image (not a plain file in any extract), so only what the
  app references is recoverable. Closure-consistent, and complete for any reference the apps make.
- `jcl.jar` - merged `ext` (device, wins on collision) + `core-lsd`. **Point `VF_JCL` here.**

Every folder has the same layout: `ext/`, `core-lsd.jar`, `jcl.jar`.

## Use as decompiler API constraint

```sh
VF_JCL=libs/jcl/MHI2Q_US_AUG22_P5087_MU1316/jcl.jar bash tools/vineflower.sh out/MU1316-...-final.jar out/...-vf
VF_JCL=libs/jcl/MHI2_ER_VWG13_K4525_MU1367/jcl.jar  bash tools/vineflower.sh out/MU1367-...-final.jar out/...-vf
```

`vineflower.sh` resolves against `VF_JCL` first (real firmware API), SE8 rt.jar stays as a
fallback for anything the (partial) core is missing.

## Completeness note

- **ext**: 100% (byte-exact device jars).
- **core**: use-subset from lsd (device core is romized-XIP, not extractable as classfiles from
  these dumps). The literal-complete core needs either the XIP boot rom carved + `jxe2jar`, or a
  pull from the live QNX VM's mapped runtime, or an external IBM WEME CDC FP 1.1 `classes.zip`.
