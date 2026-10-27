"""Align small variable text to shared vertical zones without changing letter spacing.

Usage: python -I scripts/variable_hinting.py fonts
"""

from pathlib import Path
from copy import deepcopy
from array import array
import argparse, hashlib, unicodedata
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.ttLib.tables import otTables


def push(*values):
    return [
        "PUSHW[ ]" if any(v < 0 or v > 255 for v in values) else "PUSHB[ ]",
        *[str(v) for v in values],
    ]


def prog(a):
    p = Program()
    p.fromAssembly(a)
    return p


def hint_font(source: Path, target: Path) -> dict:
    """Hint one unhinted variable font while retaining its public glyph IDs."""
    source = Path(source)
    target = Path(target)
    input_bytes = source.read_bytes()
    f = TTFont(source, recalcTimestamp=False)
    order = f.getGlyphOrder()
    original_order = list(order)
    g = f["glyf"]
    c = f.getBestCmap()
    assert not any(getattr(g[n], "program", Program()).getBytecode() for n in order)
    f["gvar"]
    f["hmtx"]
    f["post"]
    if "HVAR" in f and f["HVAR"].table.AdvWidthMap is None:
        m = otTables.VarIdxMap()
        m.mapping = {n: i for i, n in enumerate(original_order)}
        f["HVAR"].table.AdvWidthMap = m
    marks = {n for cp, n in c.items() if unicodedata.category(chr(cp)).startswith("M")}
    if "GDEF" in f and f["GDEF"].table.GlyphClassDef:
        marks |= {
            n for n, v in f["GDEF"].table.GlyphClassDef.classDefs.items() if v == 3
        }
    children = {
        a.glyphName for n in order if g[n].isComposite() for a in g[n].components
    }
    assert all(not g[n].isComposite() for n in children)
    clones = {n: n + ".raw" for n in sorted(children)}
    assert not set(clones.values()) & set(order)
    for n, clone in clones.items():
        g[clone] = deepcopy(g[n])
        g[clone].program = Program()
        f["hmtx"][clone] = f["hmtx"][n]
        f["gvar"].variations[clone] = deepcopy(f["gvar"].variations.get(n, []))
        if "HVAR" in f:
            for key in ("AdvWidthMap", "LsbMap", "RsbMap"):
                m = getattr(f["HVAR"].table, key)
                if m is not None:
                    m.mapping[clone] = m.mapping[n]
    order = original_order + list(clones.values())
    f.setGlyphOrder(order)
    # Derive the varying x-height from the actual x outline and its existing deltas.
    x = g[c[ord("x")]]
    ys = [y for _, y in x.coordinates]
    idx = ys.index(max(ys))
    xheight = ys[idx]
    f["cvt "] = newTable("cvt ")
    f["cvt "].values = array("h", [-150, 0, xheight, 710])
    variations = []
    for v in f["gvar"].variations[c[ord("x")]]:
        v = deepcopy(v)
        if any(z is None for z in v.coordinates):
            coords, controls = g._getCoordinatesAndControls(
                c[ord("x")], f["hmtx"].metrics
            )
            v.calcInferredDeltas(coords, controls.endPts)
        dy = v.coordinates[idx][1]
        if dy:
            variations.append(TupleVariation(v.axes, [0, 0, dy, 0]))
    if variations:
        f["cvar"] = newTable("cvar")
        f["cvar"].version = 1
        f["cvar"].variations = variations
    # Function 0 initializes original and rounded twilight zone anchors.
    a = [
        *push(0),
        "FDEF[ ]",
        "SVTCA[0]",
        "RTG[ ]",
        *push(0),
        "SZP0[ ]",
        *push(0),
        "SZP1[ ]",
        *push(1),
        "SZP2[ ]",
    ]
    for i in range(4):
        a += [*push(i, i), "MIAP[0]", *push(i), "MDAP[1]"]
    a += ["ENDF[ ]"]
    # Function 1 receives a public contour point and chooses its current varied interval.
    a += [
        *push(1),
        "FDEF[ ]",
        "DUP[ ]",
        "GC[1]",
        *push(0),
        "RCVT[ ]",
        "LTEQ[ ]",
        "IF[ ]",
        *push(0, 2),
        "CALL[ ]",
        "ELSE[ ]",
        "DUP[ ]",
        "GC[1]",
        *push(3),
        "RCVT[ ]",
        "GTEQ[ ]",
        "IF[ ]",
        *push(3, 2),
        "CALL[ ]",
        "ELSE[ ]",
        "DUP[ ]",
        "GC[1]",
        *push(0),
        "LTEQ[ ]",
        "IF[ ]",
        *push(0),
        "SRP1[ ]",
        *push(1),
        "SRP2[ ]",
        "ELSE[ ]",
        "DUP[ ]",
        "GC[1]",
        *push(2),
        "RCVT[ ]",
        "LTEQ[ ]",
        "IF[ ]",
        *push(1),
        "SRP1[ ]",
        *push(2),
        "SRP2[ ]",
        "ELSE[ ]",
        *push(2),
        "SRP1[ ]",
        *push(3),
        "SRP2[ ]",
        "EIF[ ]",
        "EIF[ ]",
        "IP[ ]",
        "EIF[ ]",
        "EIF[ ]",
        "ENDF[ ]",
    ]
    # Function 2 receives point, zone; translate a mark by that zone's displacement.
    a += [
        *push(2),
        "FDEF[ ]",
        "RCVT[ ]",
        "DUP[ ]",
        "ROUND[00]",
        "SWAP[ ]",
        "SUB[ ]",
        "SHPIX[ ]",
        "ENDF[ ]",
    ]
    f["fpgm"] = newTable("fpgm")
    f["fpgm"].program = prog(a)
    records = {}
    for n in original_order:
        glyph = g[n]
        if glyph.numberOfContours == 0:
            continue
        if n in marks:
            records[n] = {"mode": "standalone mark preserved"}
            continue
        pieces = []
        if glyph.isComposite():
            base = next((z for z in glyph.components if z.glyphName not in marks), None)
            zone = 2
            if base:
                base_ymax = g[base.glyphName].yMax + base.y
                zone = 3 if base_ymax > 620 else 2
            offset = 0
            for comp in glyph.components:
                name = comp.glyphName
                assert comp.getComponentInfo()[1][:4] == (1, 0, 0, 1)
                count = len(g[name].coordinates)
                markzone = (
                    (zone if g[name].yMin + comp.y > 0 else 1)
                    if name in marks
                    else None
                )
                pieces.extend((i, markzone) for i in range(offset, offset + count))
                offset += count
                comp.glyphName = clones[name]
        else:
            pieces = [(i, None) for i in range(len(glyph.coordinates))]
        a = [
            "SVTCA[0]",
            "MPPEM[ ]",
            *push(9),
            "GTEQ[ ]",
            "MPPEM[ ]",
            *push(24),
            "LTEQ[ ]",
            "AND[ ]",
            "IF[ ]",
            *push(0),
            "CALL[ ]",
        ]
        for i, zone in pieces:
            a += (
                [*push(i, 1), "CALL[ ]"]
                if zone is None
                else [*push(i, zone, 2), "CALL[ ]"]
            )
        a += ["EIF[ ]"]
        glyph.program = prog(a)
        records[n] = {
            "mode": "composite" if glyph.isComposite() else "simple",
            "points": len(pieces),
            "rigid_mark_points": sum(z is not None for _, z in pieces),
        }
    f["maxp"].maxZones = 2
    f["maxp"].maxTwilightPoints = 4
    f["maxp"].maxFunctionDefs = 3
    f["maxp"].maxStackElements = 16
    f["maxp"].maxSizeOfInstructions = max(
        len(getattr(g[n], "program", Program()).getBytecode()) for n in order
    )
    f["head"].flags |= 1 << 3
    f.save(target)
    result = {
        "input": str(source),
        "output": str(target),
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "output_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "public_glyphs": len(original_order),
        "raw_clones": clones,
        "xheight": xheight,
        "cvar_tuples": len(variations),
        "glyphs": records,
        "bytes_before": len(input_bytes),
        "bytes_after": target.stat().st_size,
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fonts", type=Path)
    args = parser.parse_args()
    paths = sorted(args.fonts.glob("MedeoSans/variable/*.ttf")) + sorted(
        args.fonts.glob("MedeoMono/variable/*.ttf")
    )
    if len(paths) != 4:
        parser.error(f"expected four Sans/Mono variable fonts, found {len(paths)}")
    for path in paths:
        result = hint_font(path, path)
        print(
            f'{path.name}: {result["public_glyphs"]} glyphs, {len(result["raw_clones"])} unhinted components'
        )
