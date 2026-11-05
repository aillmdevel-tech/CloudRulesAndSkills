#!/usr/bin/env python3
"""Inventory a folder of scene/asset dumps (e.g. LevelCopier output). Read-only.

usage: scan_assets.py DIR [--json report.json] [--max-json-mb 50]

Reports: files by extension and size, glTF/GLB summaries with external URI checks,
JSON structure sketches (keys, types, array lengths, transform-like numeric ranges),
missing references and large files. Stdlib only; never modifies anything.
"""
import argparse
import collections
import json
import os
import struct
import sys

MODEL = {".glb", ".gltf", ".fbx", ".obj", ".dae", ".blend", ".3ds", ".stl", ".ply", ".usdz", ".usd"}
TEX = {".png", ".jpg", ".jpeg", ".webp", ".ktx2", ".ktx", ".basis", ".dds", ".tga", ".hdr", ".exr", ".bmp", ".avif"}
AUDIO = {".mp3", ".ogg", ".wav", ".m4a", ".aac", ".flac", ".opus", ".webm"}
TRANSFORM_KEYS = {"position", "pos", "translation", "rotation", "rot", "quaternion", "euler",
                  "scale", "size", "x", "y", "z", "w", "cframe", "orientation"}


def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{u}" if u == "B" else f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}TB"


def read_gltf(path):
    with open(path, "rb") as f:
        data = f.read()
    if path.lower().endswith(".glb"):
        if data[:4] != b"glTF":
            return {"error": "not a GLB (bad magic)"}
        version, length = struct.unpack_from("<II", data, 4)
        clen, ctype = struct.unpack_from("<II", data, 12)
        if ctype != 0x4E4F534A:
            return {"error": "first chunk is not JSON"}
        doc = json.loads(data[20:20 + clen].decode("utf-8"))
        has_bin = len(data) > 20 + clen
    else:
        doc = json.loads(data.decode("utf-8"))
        has_bin = False
    base = os.path.dirname(path)
    uris, missing = [], []
    for kind in ("buffers", "images"):
        for item in doc.get(kind, []):
            uri = item.get("uri")
            if uri and not uri.startswith("data:"):
                uris.append(uri)
                if not os.path.exists(os.path.join(base, uri)):
                    missing.append(uri)
    tris = 0
    for m in doc.get("meshes", []):
        for p in m.get("primitives", []):
            idx = p.get("indices")
            if idx is not None and idx < len(doc.get("accessors", [])):
                tris += doc["accessors"][idx].get("count", 0) // 3
    return {
        "generator": doc.get("asset", {}).get("generator"),
        "scenes": len(doc.get("scenes", [])), "nodes": len(doc.get("nodes", [])),
        "meshes": len(doc.get("meshes", [])), "materials": len(doc.get("materials", [])),
        "textures": len(doc.get("textures", [])), "images": len(doc.get("images", [])),
        "animations": [a.get("name", f"#{i}") for i, a in enumerate(doc.get("animations", []))],
        "skins": len(doc.get("skins", [])), "approx_triangles": tris,
        "extensionsUsed": doc.get("extensionsUsed", []), "embedded_bin": has_bin,
        "external_uris": uris, "missing": missing,
        "root_node_names": [doc["nodes"][n].get("name") for n in
                            (doc.get("scenes", [{}])[doc.get("scene", 0)].get("nodes", []) if doc.get("scenes") else [])][:15],
    }


class Sketch:
    def __init__(self):
        self.types = collections.defaultdict(collections.Counter)
        self.ranges = {}
        self.arrays = collections.defaultdict(list)
        self.strings = collections.defaultdict(set)

    def walk(self, v, path="$", depth=0):
        if depth > 12:
            return
        t = type(v).__name__
        self.types[path][t] += 1
        if isinstance(v, dict):
            for k, x in v.items():
                self.walk(x, f"{path}.{k}", depth + 1)
        elif isinstance(v, list):
            self.arrays[path].append(len(v))
            for x in v[:200]:
                self.walk(x, path + "[]", depth + 1)
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            leaf = path.split(".")[-1].rstrip("[]").lower()
            parent = path.split(".")[-2].rstrip("[]").lower() if path.count(".") > 1 else ""
            if leaf in TRANSFORM_KEYS or parent in TRANSFORM_KEYS:
                lo, hi = self.ranges.get(path, (v, v))
                self.ranges[path] = (min(lo, v), max(hi, v))
        elif isinstance(v, str):
            s = self.strings[path]
            if len(s) < 4:
                s.add(v[:60])

    def report(self, limit=60):
        out = []
        for p in list(self.types)[:limit]:
            line = f"    {p}: " + "/".join(f"{t}x{n}" for t, n in self.types[p].items())
            if p in self.arrays:
                ls = self.arrays[p]
                line += f"  len {min(ls)}..{max(ls)}"
            if p in self.ranges:
                lo, hi = self.ranges[p]
                line += f"  range {lo:.4g}..{hi:.4g}"
            if p in self.strings:
                line += "  e.g. " + ", ".join(repr(x) for x in sorted(self.strings[p])[:3])
            out.append(line)
        if len(self.types) > limit:
            out.append(f"    ... {len(self.types) - limit} more paths")
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--json")
    ap.add_argument("--max-json-mb", type=float, default=50)
    a = ap.parse_args()
    root = os.path.abspath(a.dir)
    if not os.path.isdir(root):
        sys.exit("not a directory: " + root)

    by_ext = collections.defaultdict(lambda: [0, 0])
    files = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith(".") and d != "node_modules"]
        for f in fn:
            p = os.path.join(dp, f)
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            ext = os.path.splitext(f)[1].lower()
            by_ext[ext][0] += 1
            by_ext[ext][1] += sz
            files.append((p, ext, sz))

    report = {"root": root, "files": len(files), "by_ext": {}, "models": {}, "json": {}, "large": [], "missing": []}
    print(f"ROOT {root}\n{len(files)} files\n\nBY EXTENSION")
    for ext, (n, sz) in sorted(by_ext.items(), key=lambda kv: -kv[1][1]):
        kind = "model" if ext in MODEL else "texture" if ext in TEX else "audio" if ext in AUDIO else "json" if ext == ".json" else ""
        print(f"  {ext or '(none)':10} {n:6} files {human(sz):>9}  {kind}")
        report["by_ext"][ext] = {"count": n, "bytes": sz}

    print("\nMODELS (glTF/GLB)")
    for p, ext, sz in files:
        if ext in (".glb", ".gltf"):
            rel = os.path.relpath(p, root)
            try:
                info = read_gltf(p)
            except Exception as e:  # noqa: BLE001
                info = {"error": str(e)}
            report["models"][rel] = info
            if "error" in info:
                print(f"  {rel}: ERROR {info['error']}")
                continue
            print(f"  {rel} ({human(sz)}): nodes {info['nodes']} meshes {info['meshes']} mats {info['materials']} "
                  f"tex {info['textures']} tris~{info['approx_triangles']} skins {info['skins']} anims {len(info['animations'])}"
                  + (f" ext {info['extensionsUsed']}" if info["extensionsUsed"] else ""))
            if info["animations"]:
                print(f"      clips: {', '.join(map(str, info['animations'][:12]))}")
            for m in info["missing"]:
                print(f"      MISSING uri: {m}")
                report["missing"].append(f"{rel} -> {m}")
    others = [os.path.relpath(p, root) for p, e, _ in files if e in MODEL and e not in (".glb", ".gltf")]
    if others:
        print(f"  non-glTF models needing conversion: {len(others)} e.g. {others[:5]}")

    print("\nJSON STRUCTURE")
    names = {os.path.basename(p).lower() for p, _, _ in files}
    for p, ext, sz in files:
        if ext != ".json":
            continue
        rel = os.path.relpath(p, root)
        if sz > a.max_json_mb * 1e6:
            print(f"  {rel}: skipped ({human(sz)} > --max-json-mb)")
            continue
        try:
            with open(p, encoding="utf-8") as f:
                doc = json.load(f)
        except Exception as e:  # noqa: BLE001
            print(f"  {rel}: PARSE ERROR {e}")
            continue
        sk = Sketch()
        sk.walk(doc)
        print(f"  {rel} ({human(sz)})")
        for line in sk.report():
            print(line)
        refs = set()
        for path, vals in sk.strings.items():
            for v in vals:
                if os.path.splitext(v)[1].lower() in MODEL | TEX | AUDIO:
                    refs.add(os.path.basename(v).lower())
        miss = sorted(r for r in refs if r not in names)
        if miss:
            print(f"    referenced files not found in dump (sampled): {miss[:10]}")
            report["missing"] += [f"{rel} -> {m}" for m in miss]
        report["json"][rel] = {"paths": len(sk.types)}

    print("\nLARGE FILES (>20MB)")
    for p, ext, sz in sorted(files, key=lambda x: -x[2]):
        if sz < 20e6:
            break
        print(f"  {human(sz):>9} {os.path.relpath(p, root)}")
        report["large"].append(os.path.relpath(p, root))

    print(f"\nMISSING REFERENCES: {len(report['missing'])}")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("report ->", a.json)


if __name__ == "__main__":
    main()
