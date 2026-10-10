"""Lit un FBX binaire : facteur d'unité et taille brute de chaque géométrie.

Sert à vérifier qu'à l'import Roblox (Scale Unit = Stud) l'arme fait la
bonne taille : les valeurs brutes du fichier sont lues comme des studs.
"""
import struct
import sys
import zlib


def _read_node(f, version):
    if version >= 7500:
        end, nprops, _plen = struct.unpack("<QQQ", f.read(24))
    else:
        end, nprops, _plen = struct.unpack("<III", f.read(12))
    name = f.read(ord(f.read(1))).decode()
    if end == 0:
        return None
    props = []
    for _ in range(nprops):
        t = f.read(1)
        if t == b"Y": props.append(struct.unpack("<h", f.read(2))[0])
        elif t == b"C": props.append(f.read(1) != b"\0")
        elif t == b"I": props.append(struct.unpack("<i", f.read(4))[0])
        elif t == b"F": props.append(struct.unpack("<f", f.read(4))[0])
        elif t == b"D": props.append(struct.unpack("<d", f.read(8))[0])
        elif t == b"L": props.append(struct.unpack("<q", f.read(8))[0])
        elif t in b"fdlib":
            n, enc, clen = struct.unpack("<III", f.read(12))
            data = f.read(clen)
            if enc:
                data = zlib.decompress(data)
            fmt = {b"f": "f", b"d": "d", b"l": "q", b"i": "i", b"b": "b"}[t]
            props.append(list(struct.unpack("<%d%s" % (n, fmt), data)))
        elif t in b"SR":
            n = struct.unpack("<I", f.read(4))[0]
            props.append(f.read(n))
    children = []
    while f.tell() < end:
        c = _read_node(f, version)
        if c is None:
            break
        children.append(c)
    f.seek(end)
    return (name, props, children)


def load(path):
    with open(path, "rb") as f:
        f.read(23)
        version = struct.unpack("<I", f.read(4))[0]
        nodes = []
        while True:
            n = _read_node(f, version)
            if n is None:
                break
            nodes.append(n)
    return nodes


def walk(nodes, name):
    for n in nodes:
        if n[0] == name:
            yield n
        yield from walk(n[2], name)


if __name__ == "__main__":
    nodes = load(sys.argv[1])
    for p in walk(nodes, "P"):
        if p[1] and p[1][0] in (b"UnitScaleFactor", b"OriginalUnitScaleFactor"):
            print(p[1][0].decode(), p[1][-1])
    for g in walk(nodes, "Geometry"):
        v = next(walk(g[2], "Vertices"))[1][0]
        xs, ys, zs = v[0::3], v[1::3], v[2::3]
        name = g[1][1].split(b"\x00")[0].decode()
        print(f"{name:28s} brut X={max(xs)-min(xs):.3f} Y={max(ys)-min(ys):.3f} Z={max(zs)-min(zs):.3f}")
    for m in walk(nodes, "Model"):
        lcl = [p[1] for p in walk(m[2], "P") if p[1] and p[1][0] in (b"Lcl Scaling", b"Lcl Translation")]
        name = m[1][1].split(b"\x00")[0].decode()
        print("Model", name, [(l[0].decode(), [round(x, 3) for x in l[-3:]]) for l in lcl])
