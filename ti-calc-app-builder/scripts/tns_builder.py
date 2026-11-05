#!/usr/bin/env python3
"""tns_builder.py - pure-Python port of Luna 2.1 (ndless-nspire/Luna, MPL-1.1, by Olivier Armand).

Converts a Lua script, or one or more Python scripts, into a TI-Nspire .tns document.
No compiler, no zlib headers, no third-party packages: Python 3.8+ standard library only.

Usage:
  python tns_builder.py APP.lua APP.tns            # Lua script app (Nspire OS 3.0.2+)
  python tns_builder.py main.py [helper.py ...] APP.tns   # Python (CX II OS 5.2+)
  python tns_builder.py --selftest                 # verify the DES implementation

Output matches Luna's byte layout (*TIMLP header, TI-encrypted Problem1.xml, TIPD end record).
"""
import os, sys, zlib, struct

# ---------------------------------------------------------------- DES (FIPS 46-3)
_IP = [58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,
       57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7]
_FP = [40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,
       36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,34,2,42,10,50,18,58,26,33,1,41,9,49,17,57,25]
_E = [32,1,2,3,4,5,4,5,6,7,8,9,8,9,10,11,12,13,12,13,14,15,16,17,16,17,18,19,20,21,20,21,22,23,24,25,
      24,25,26,27,28,29,28,29,30,31,32,1]
_P = [16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25]
_PC1 = [57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,60,52,44,36,
        63,55,47,39,31,23,15,7,62,54,46,38,30,22,14,6,61,53,45,37,29,21,13,5,28,20,12,4]
_PC2 = [14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,26,8,16,7,27,20,13,2,
        41,52,31,37,47,55,30,40,51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32]
_SHIFTS = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]
_S = [
 [14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7,0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8,4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0,15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13],
 [15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10,3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5,0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15,13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9],
 [10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8,13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1,13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7,1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12],
 [7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15,13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9,10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4,3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14],
 [2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9,14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6,4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14,11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3],
 [12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11,10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8,9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6,4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13],
 [4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1,13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6,1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2,6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12],
 [13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7,1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2,7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8,2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]

def _perm(v, table, nbits):
    out = 0
    for p in table:
        out = (out << 1) | ((v >> (nbits - p)) & 1)
    return out

def _subkeys(key8):
    k = _perm(int.from_bytes(key8, "big"), _PC1, 64)
    c, d = k >> 28, k & 0xFFFFFFF
    keys = []
    for s in _SHIFTS:
        c = ((c << s) | (c >> (28 - s))) & 0xFFFFFFF
        d = ((d << s) | (d >> (28 - s))) & 0xFFFFFFF
        keys.append(_perm((c << 28) | d, _PC2, 56))
    return keys

def _des_block(block, keys):
    v = _perm(block, _IP, 64)
    l, r = v >> 32, v & 0xFFFFFFFF
    for k in keys:
        x = _perm(r, _E, 32) ^ k
        o = 0
        for i in range(8):
            six = (x >> (42 - 6 * i)) & 0x3F
            row = ((six & 0x20) >> 4) | (six & 1)
            o = (o << 4) | _S[i][row * 16 + ((six >> 1) & 0xF)]
        l, r = r, l ^ _perm(o, _P, 32)
    return _perm((r << 32) | l, _FP, 64)

_K1 = _subkeys(bytes([0x16,0xA7,0xA7,0x32,0x68,0xA7,0xBA,0x73]))
_K2 = _subkeys(bytes([0xD9,0xA8,0x86,0xA4,0x34,0x45,0x94,0x10]))
_K3 = _subkeys(bytes([0x3D,0x80,0x8C,0xB5,0xDF,0xB3,0x80,0x6B]))

def _ede3(block8):
    v = int.from_bytes(block8, "big")
    v = _des_block(v, _K1)
    v = _des_block(v, _K2[::-1])   # decrypt with K2
    v = _des_block(v, _K3)
    return v.to_bytes(8, "big")

_KEYSTREAM = None
def _keystream():
    """TI document cipher: 3DES-EDE of a counter (IVEC_BASE + n, n mod 1024). Period 8 KiB."""
    global _KEYSTREAM
    if _KEYSTREAM is None:
        out = bytearray()
        for n in range(1024):
            iv = bytes(4) + struct.pack("<I", (0x6FE21307 + n) & 0xFFFFFFFF)
            out += _ede3(iv)
        _KEYSTREAM = bytes(out)
    return _KEYSTREAM

def doccrypt(data):
    ks = _keystream()
    return bytes(b ^ ks[i % 8192] for i, b in enumerate(data))

# ---------------------------------------------------------------- Luna constants
LUA_HEADER = bytes.fromhex(
 "54495843303130302D312E303F3E3C70726F6220786D6C6E733D2275726E3A54492E50A85F5B1F0A22207665723D22312E30"
 "222070626E616D653D22223E3C73796D3E0E013C6361726420636C61793D2230222068313D22F10000FF222068323D22F100"
 "00FF222077313D22F10000FF222077323D22F10000FF223E3C697344756D6D79436172643E300E033C666C61673E300E043C"
 "7764677420786D6C6E733A73633D2275726E3A54492E53AC84F22A4170702220747970653D2254492E53AC84F22A41707022"
 "207665723D22312E30223E3C73633A6D466C6167733E300E063C73633A76616C75653E2D310E073C73633A73637269707420"
 "76657273696F6E3D22353132222069643D2230223E3C215B43444154415B")
LUA_FOOTER = b"]]>\x0E\x08\x0E\x05\x0E\x02\x0E\x00"
TIEN_HEADER = bytes.fromhex("0FCED8D28106865B99DDA23DD9E94BD431BB50B64DB3292470604938"
                            "1C30F899004B9264E458E6BC")
DEFAULT_DOC = bytes.fromhex(
 "0FCED8D28106865B4A4AC5CEA916F2D51DA82F6E0022F2F0C1A606774D7EA6C03AF05C74BAAA4460CD58E670D740F69C17DC"
 "F09477BFCADEF70209C962B15DEF22FA5137A0819148E1834DAD08312DD0D3E32D60AB13C2982BED395B092439922F0C7A4C"
 "9574913B0CF460CC7327CB077E7FA91787E2ACA23BCCA0C4E38E89F0C0519FC2BECE2845C3D41190A6EC53A0FB5B466B41AD"
 "E953BB97DBB1D268E2F6360F2636759BE91F48ADE92967005819C3C01276A04A73F3B1D30918D606DD9724533E22A4FB8250"
 "7B7C12884E7D4180FE72922987E85C5672FF29168C425B8B9BA7D2086DD398FF91A99EF393A82E1CB2A96B6ADFF6CE2D1517"
 "CE6EC04F9A9C0EDF198D2DFA699F11D22012E07914044E628F0A2A18725A8B80B33C9BD567594B514DE0C33828C3DCCD3922"
 "128C4055")
PY_HEADER = (b'TIXC0100-1.0?><prob xmlns="urn:TI.Problem" ver="1.0" pbname=""><sym>\x0E\x01<card clay="0" '
             b'h1="10000" h2="10000" w1="10000" w2="10000"><isDummyCard>0\x0E\x03<flag>0\x0E\x04<wdgt '
             b'xmlns:py="urn:TI.PythonEditor" type="TI.PythonEditor" ver="1.0"><py:data><py:name>')
PY_FOOTER = (b"\x0E\x07<py:dirf>-10000000\x0E\x08\x0E\x06<py:mFlags>1024\x0E\x09<py:value>10\x0E\x0A"
             b"\x0E\x05\x0E\x02\x0E\x00")

def _fix_cdata(src):
    return src.replace(b"]]>", b"]]]]><![CDATA[>")

_BLOCK = set(list(range(0, 7)) + list(range(14, 26)) + list(range(28, 32)))
def _is_text(data):
    """Mirror of zlib's detect_data_type(): text if no block-listed control bytes and >=1 text byte."""
    if any(b in _BLOCK for b in data):
        return False
    return any(b in (9, 10, 13) or b >= 32 for b in data)

def _raw_deflate(data):
    c = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15, 8, zlib.Z_DEFAULT_STRATEGY)
    return c.compress(data) + c.flush()

def _encrypted_xml(xmlc):
    return TIEN_HEADER + doccrypt(_raw_deflate(xmlc))

class _TnsWriter:
    def __init__(self, tiversion=0x0500):
        self.buf = bytearray(); self.central = bytearray(); self.count = 0; self.tiversion = tiversion
    def add(self, name, payload, method):
        """method 0x0D = stored TI-encrypted; 8 = deflate (payload is raw, gets deflated here)."""
        nameb = name.encode()
        crc = zlib.crc32(payload) & 0xFFFFFFFF
        usize = len(payload)
        data = _raw_deflate(payload) if method == 8 else payload
        offset = len(self.buf)
        magic = (b"*TIMLP" + ("%04X" % self.tiversion).encode()) if self.count == 0 else b"PK\x03\x04"
        self.buf += magic + struct.pack("<HHHHHIIIHH", 20, 0, method, 0x0000, 0x0020, crc, len(data), usize, len(nameb), 0)
        self.buf += nameb + data
        internal_fa = 1 if (method == 8 and _is_text(payload)) else 0   # zlib Z_TEXT detection, as minizip does
        self.central += b"PK\x01\x02" + struct.pack("<HHHHHHIIIHHHHHII", 0, 20, 0, method, 0x0000, 0x0020,
                       crc, len(data), usize, len(nameb), 0, 0, 0, internal_fa, 0, offset) + nameb
        self.count += 1
    def finish(self):
        cd_off = len(self.buf)
        return bytes(self.buf + self.central + b"TIPD" + struct.pack("<HHHHIIH", 0, 0, self.count, self.count,
                     len(self.central), cd_off, 0))

def build(inputs, out_path):
    lua = [p for p in inputs if p.lower().endswith(".lua")]
    py = [p for p in inputs if p.lower().endswith(".py")]
    if lua and py:
        raise SystemExit("Mix of .lua and .py is not supported; build them as separate documents.")
    if len(lua) > 1:
        raise SystemExit("Only one Lua script per .tns (Luna rule).")
    if not lua and not py:
        raise SystemExit("Give a .lua file or one or more .py files.")
    w = _TnsWriter(0x0500)
    w.add("Document.xml", DEFAULT_DOC, 0x0D)
    if lua:
        src = open(lua[0], "rb").read()
        w.add("Problem1.xml", _encrypted_xml(LUA_HEADER + _fix_cdata(src) + LUA_FOOTER), 0x0D)
    else:
        first = os.path.basename(py[0]).encode()
        if len(first) > 240:
            raise SystemExit("Python script filenames are limited to 240 characters.")
        w.add("Problem1.xml", _encrypted_xml(PY_HEADER + first + PY_FOOTER), 0x0D)
        for p in py:
            w.add(os.path.basename(p), open(p, "rb").read(), 8)
    data = w.finish()
    with open(out_path, "wb") as f:
        f.write(data)
    return len(data)

def _selftest():
    # FIPS 81 / classic DES test vector: key 133457799BBCDFF1, pt 0123456789ABCDEF -> 85E813540F0AB405
    k = _subkeys(bytes.fromhex("133457799BBCDFF1"))
    ct = _des_block(0x0123456789ABCDEF, k)
    ok = ct == 0x85E813540F0AB405
    print("DES self-test:", "PASS" if ok else "FAIL %016X" % ct)
    return ok

if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(0 if _selftest() else 1)
    if len(a) < 2:
        print(__doc__); sys.exit(1)
    n = build(a[:-1], a[-1])
    print("OK: wrote %s (%d bytes)" % (a[-1], n))
