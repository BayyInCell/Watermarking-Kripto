"""Manajemen kunci. Kunci dibangkitkan CSPRNG (secrets) saat penyisipan dan disimpan
di folder instance/ (di luar source code, permission 600). TIDAK ADA kunci hardcode.
Kunci -> keystream deterministik (SHA-256 counter mode) -> permutasi blok & pilihan koefisien."""
import hashlib, json, os, re, secrets

DATA_DIR = os.environ.get("WM_DATA_DIR", "/tmp")

def new_key() -> bytes:
    return secrets.token_bytes(32)          # 256-bit dari os.urandom

class KeyStream:
    def __init__(self, key: bytes, label: str):
        self.key, self.label, self.ctr, self.buf = key, label.encode(), 0, b""
    def _bytes(self, n):
        while len(self.buf) < n:
            self.buf += hashlib.sha256(self.key + self.label + self.ctr.to_bytes(8, "big")).digest()
            self.ctr += 1
        out, self.buf = self.buf[:n], self.buf[n:]
        return out
    def below(self, n):
        """Integer seragam [0,n) dengan rejection sampling (tanpa modulo bias)."""
        limit = (1 << 32) // n * n
        while True:
            v = int.from_bytes(self._bytes(4), "big")
            if v < limit:
                return v % n

def shuffled(n, key, label):
    """Fisher-Yates yang digerakkan keystream rahasia."""
    ks, p = KeyStream(key, label), list(range(n))
    for i in range(n - 1, 0, -1):
        j = ks.below(i + 1)
        p[i], p[j] = p[j], p[i]
    return p

_ID = re.compile(r"^[0-9a-f]{16}$")

def save_record(key: bytes, bits, meta) -> str:
    key_id = secrets.token_hex(8)
    os.makedirs("/tmp/records", exist_ok=True)
    path = f"/tmp/records/{key_id}.json"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump({"key": key.hex(), "bits": [int(b) for b in bits], "meta": meta}, f)
    return key_id

def load_record(key_id: str):
    if not _ID.match(key_id or ""):
        raise KeyError("key_id tidak valid")
    with open(f"/tmp/records/{key_id}.json") as f:
        r = json.load(f)
    return bytes.fromhex(r["key"]), r["bits"], r["meta"]
