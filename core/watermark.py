"""Watermark DCT blind (tanpa citra asli) pada koefisien frekuensi menengah kanal Y.
Satu bit per blok 8x8: pasangan koefisien (c1,c2) dipilih rahasia per blok;
bit 1 -> c1 - c2 >= strength ; bit 0 -> c2 - c1 >= strength.
Payload diulang ke seluruh blok (redundansi) dan diekstraksi dengan majority vote."""
import numpy as np
from PIL import Image
from .dct import dct2, idct2, to_blocks, from_blocks
from .keys import KeyStream, shuffled

# pasangan koefisien frekuensi menengah (u+v = 6..7), simetris
PAIRS = [((4, 3), (3, 4)), ((5, 2), (2, 5)), ((3, 3), (4, 2)), ((2, 4), (4, 1))]

# ---------- payload <-> bit ----------
def text_to_bits(text):
    return np.unpackbits(np.frombuffer(text.encode("utf-8"), dtype=np.uint8)).astype(int)

def bits_to_text(bits):
    b = np.packbits(np.asarray(bits, dtype=np.uint8)[: len(bits) // 8 * 8]).tobytes()
    return b.decode("utf-8", errors="replace")

def logo_to_bits(img, size=32):
    g = img.convert("L").resize((size, size), Image.LANCZOS)
    return (np.asarray(g) < 128).astype(int).ravel()       # piksel gelap = 1

def bits_to_logo(bits, size=32):
    a = np.where(np.asarray(bits).reshape(size, size) == 1, 0, 255).astype(np.uint8)
    return Image.fromarray(a, "L").resize((size * 6, size * 6), Image.NEAREST)

# ---------- inti ----------
def _plan(nb, key):
    order = shuffled(nb, key, "blocks")
    ks = KeyStream(key, "pairs")
    return order, [ks.below(len(PAIRS)) for _ in range(nb)]

def _luma_blocks(img):
    y, cb, cr = img.convert("YCbCr").split()
    y = np.asarray(y, dtype=np.float64).copy()
    H, W = y.shape
    h, w = H // 8 * 8, W // 8 * 8
    return y, cb, cr, h, w, dct2(to_blocks(y[:h, :w] - 128.0))

def embed(img, bits, key, strength=30.0):
    bits = np.asarray(bits, dtype=int)
    y, cb, cr, h, w, blocks = _luma_blocks(img)
    if len(blocks) < len(bits):
        raise ValueError(f"Citra terlalu kecil: {len(blocks)} blok < {len(bits)} bit")
    order, pairs = _plan(len(blocks), key)
    for i, b in enumerate(order):
        (u1, v1), (u2, v2) = PAIRS[pairs[i]]
        c1, c2 = blocks[b, u1, v1], blocks[b, u2, v2]
        d, bit = c1 - c2, bits[i % len(bits)]
        if bit == 1 and d < strength:
            s = (strength - d) / 2; c1, c2 = c1 + s, c2 - s
        elif bit == 0 and d > -strength:
            s = (d + strength) / 2; c1, c2 = c1 - s, c2 + s
        blocks[b, u1, v1], blocks[b, u2, v2] = c1, c2
    y[:h, :w] = from_blocks(idct2(blocks), h, w) + 128.0
    Y = Image.fromarray(np.clip(np.rint(y), 0, 255).astype(np.uint8), "L")
    return Image.merge("YCbCr", (Y, cb, cr)).convert("RGB")

def extract(img, nbits, key):
    _, _, _, _, _, blocks = _luma_blocks(img)
    order, pairs = _plan(len(blocks), key)
    votes = np.zeros(nbits)
    for i, b in enumerate(order):
        (u1, v1), (u2, v2) = PAIRS[pairs[i]]
        votes[i % nbits] += 1 if blocks[b, u1, v1] - blocks[b, u2, v2] > 0 else -1
    return (votes > 0).astype(int)
