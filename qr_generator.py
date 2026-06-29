import qrcode
import os

QR_DIR = "static/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

def generate_qr(batch_id: str, verify_url: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    path = f"{QR_DIR}/{batch_id}.png"
    img.save(path)
    return path