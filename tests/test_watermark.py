import secrets, unittest
import numpy as np
from PIL import Image
from core import attacks, keys, metrics, watermark as wm
from core.dct import dct2, idct2

TEXT = "2210631170001"

def sample(n=256):
    r = np.random.default_rng(1); x, y = np.meshgrid(np.arange(n), np.arange(n))
    a = 110 + 50 * np.sin(x / 17) + 40 * np.cos(y / 23) + r.normal(0, 6, (n, n))
    return Image.fromarray(np.clip(np.stack([a, a * .9, a * .8], -1), 0, 255).astype(np.uint8))

class WatermarkTests(unittest.TestCase):
    def setUp(self):
        self.orig, self.key = sample(), secrets.token_bytes(32)   # kunci acak tiap tes
        self.bits = wm.text_to_bits(TEXT)
        self.out = wm.embed(self.orig, self.bits, self.key)

    def test_dct_roundtrip(self):
        b = np.random.default_rng(0).normal(size=(5, 8, 8))
        self.assertTrue(np.allclose(idct2(dct2(b)), b))

    def test_text_roundtrip(self):
        got = wm.extract(self.out, len(self.bits), self.key)
        self.assertEqual(wm.bits_to_text(got), TEXT)

    def test_logo_roundtrip(self):
        logo = Image.new("L", (32, 32), 255); logo.paste(0, (8, 8, 24, 24))
        bits = wm.logo_to_bits(logo)
        out = wm.embed(self.orig, bits, self.key)
        self.assertEqual(metrics.ber(bits, wm.extract(out, len(bits), self.key)), 0)

    def test_psnr_imperceptible(self):
        self.assertGreater(metrics.psnr(self.orig, self.out), 35)

    def test_wrong_key_fails(self):
        got = wm.extract(self.out, len(self.bits), secrets.token_bytes(32))
        self.assertGreater(metrics.ber(self.bits, got), 0.25)

    def test_survives_jpeg70_and_brightness(self):
        for att in (attacks.jpeg(self.out, 70), attacks.brightness(self.out, 30)):
            self.assertLess(metrics.ber(self.bits, wm.extract(att, len(self.bits), self.key)), 0.05)

    def test_capacity_error(self):
        with self.assertRaises(ValueError):
            wm.embed(Image.new("RGB", (16, 16)), np.ones(100, int), self.key)

    def test_permutation_deterministic_and_valid(self):
        p = keys.shuffled(500, self.key, "blocks")
        self.assertEqual(sorted(p), list(range(500)))
        self.assertEqual(p, keys.shuffled(500, self.key, "blocks"))

    def test_metrics_values(self):
        self.assertEqual(metrics.nc([1, 0, 1], [1, 0, 1]), 1)
        self.assertEqual(metrics.ber([1, 0], [0, 0]), 0.5)

if __name__ == "__main__":
    unittest.main()
