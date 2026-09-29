# Watermark DCT blind (Flask)

Instalasi & jalankan:

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python app.py            # buka http://127.0.0.1:5000

Tes unit (9 tes):

    python -m unittest discover -s tests -v      # atau: pytest

Catatan: kunci 256-bit dibangkitkan `secrets` tiap penyisipan dan disimpan di `instance/records/`
(permission 600, jangan di-commit). Ganti lokasi dengan env `WM_DATA_DIR`.
