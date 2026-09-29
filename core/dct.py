"""DCT 2D 8x8 ditulis dari nol (tanpa scipy/cv2). Matriks basis DCT-II ortonormal."""
import numpy as np

N = 8

def _basis():
    C = np.zeros((N, N))
    for k in range(N):
        a = np.sqrt(1.0 / N) if k == 0 else np.sqrt(2.0 / N)
        for n in range(N):
            C[k, n] = a * np.cos((2 * n + 1) * k * np.pi / (2 * N))
    return C

C = _basis()

def to_blocks(ch):
    """(H,W) -> (jumlah_blok, 8, 8); H dan W harus kelipatan 8."""
    h, w = ch.shape
    return ch.reshape(h // N, N, w // N, N).transpose(0, 2, 1, 3).reshape(-1, N, N)

def from_blocks(b, h, w):
    return b.reshape(h // N, w // N, N, N).transpose(0, 2, 1, 3).reshape(h, w)

def dct2(b):  return C @ b @ C.T      # maju
def idct2(b): return C.T @ b @ C      # balik
