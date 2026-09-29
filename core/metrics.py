"""Metrik pengujian: PSNR, Normalized Correlation (NC), Bit Error Rate (BER)."""
import numpy as np

def psnr(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    mse = np.mean((a - b) ** 2)
    return float("inf") if mse == 0 else float(10 * np.log10(255.0 ** 2 / mse))

def nc(w, w2):
    """NC pada representasi bipolar (+1/-1): 1 = identik, ~0 = acak, -1 = terbalik."""
    a, b = 2.0 * np.asarray(w) - 1, 2.0 * np.asarray(w2) - 1
    return float(np.sum(a * b) / np.sqrt(np.sum(a * a) * np.sum(b * b)))

def ber(w, w2):
    return float(np.mean(np.asarray(w) != np.asarray(w2)))
