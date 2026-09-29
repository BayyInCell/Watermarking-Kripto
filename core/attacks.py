"""Simulasi serangan terhadap citra ber-watermark (semua mengembalikan PIL RGB, ukuran sama)."""
import io
import numpy as np
from PIL import Image

def jpeg(img, q):
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=int(q)); buf.seek(0)
    return Image.open(buf).convert("RGB")

def crop(img, keep):
    """Pertahankan `keep` (0-1) luas citra di tengah (offset kelipatan 8), sisanya hitam."""
    w, h = img.size; s = keep ** 0.5
    cw, ch = int(w * s), int(h * s)
    l, t = (w - cw) // 2 // 8 * 8, (h - ch) // 2 // 8 * 8
    out = Image.new("RGB", (w, h)); out.paste(img.crop((l, t, l + cw, t + ch)), (l, t))
    return out

def resize(img, scale):
    """Perkecil lalu kembalikan ke ukuran semula (bicubic)."""
    w, h = img.size
    small = img.resize((max(8, int(w * scale)), max(8, int(h * scale))), Image.BICUBIC)
    return small.resize((w, h), Image.BICUBIC)

def _u8(a): return Image.fromarray(np.clip(np.rint(a), 0, 255).astype(np.uint8))

def gaussian(img, sigma):
    a = np.asarray(img, dtype=np.float64)
    return _u8(a + np.random.default_rng().normal(0, float(sigma), a.shape))

def brightness(img, delta):
    return _u8(np.asarray(img, dtype=np.float64) + float(delta))

def contrast(img, factor):
    return _u8((np.asarray(img, dtype=np.float64) - 128) * float(factor) + 128)

ATTACKS = {"jpeg": jpeg, "crop": crop, "resize": resize, "gaussian": gaussian,
           "brightness": brightness, "contrast": contrast}
