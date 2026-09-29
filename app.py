"""Backend Flask: /api/embed, /api/attack, /api/extract, /api/psnr."""
import base64, io
from flask import Flask, jsonify, render_template, request
from PIL import Image
from core import attacks, keys, metrics, watermark as wm

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
LOGO = 32

def _img(field):
    f = request.files.get(field)
    if not f: raise ValueError(f"file '{field}' wajib diisi")
    return Image.open(f.stream).convert("RGB")

def _url(img):
    buf = io.BytesIO(); img.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

@app.errorhandler(Exception)
def _err(e):
    code = 400 if isinstance(e, (ValueError, KeyError, OSError)) else 500
    return jsonify(error=str(e)), code

@app.get("/")
def index(): return render_template("index.html")

@app.post("/api/embed")
def embed():
    img, mode = _img("image"), request.form.get("mode", "text")
    strength = float(request.form.get("strength", 30))
    if mode == "logo":
        bits, meta = wm.logo_to_bits(_img("logo"), LOGO), {"mode": "logo"}
    else:
        text = request.form.get("text", "").strip()
        if not text: raise ValueError("teks watermark kosong")
        bits, meta = wm.text_to_bits(text), {"mode": "text"}
    meta.update(size=list(img.size), nbits=len(bits))
    key = keys.new_key()                                   # CSPRNG
    out = wm.embed(img, bits, key, strength)
    kid = keys.save_record(key, bits, meta)
    return jsonify(key_id=kid, image=_url(out), psnr=metrics.psnr(img, out), nbits=len(bits))

@app.post("/api/attack")
def attack():
    img, name = _img("image"), request.form.get("attack")
    if name not in attacks.ATTACKS: raise ValueError("serangan tidak dikenal")
    out = attacks.ATTACKS[name](img, float(request.form.get("param", 0)))
    return jsonify(image=_url(out), psnr=metrics.psnr(img, out))

@app.post("/api/extract")
def extract():
    key, orig_bits, meta = keys.load_record(request.form.get("key_id"))
    img = _img("image")
    if list(img.size) != meta["size"]:
        img = img.resize(tuple(meta["size"]), Image.BICUBIC)
    got = wm.extract(img, meta["nbits"], key)
    res = dict(nc=metrics.nc(orig_bits, got), ber=metrics.ber(orig_bits, got))
    if meta["mode"] == "logo": res["logo"] = _url(wm.bits_to_logo(got, LOGO))
    else: res["text"] = wm.bits_to_text(got)
    return jsonify(res)

@app.post("/api/psnr")
def psnr():
    return jsonify(psnr=metrics.psnr(_img("a"), _img("b").resize(_img("a").size)))

if __name__ == "__main__":
    app.run(debug=False)
