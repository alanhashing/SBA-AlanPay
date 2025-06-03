import qrcode
import qrcode.image.pil
import qrcode.image.svg
from io import BytesIO

def create_qr_codeas_svg(string: str) -> BytesIO:
    qr = qrcode.QRCode()
    qr.add_data(string)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgImage)
    buffer = BytesIO()
    img.save(buffer)
    return buffer

def create_qr_codeas_png(string: str) -> BytesIO:
    qr = qrcode.QRCode()
    qr.add_data(string)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.pil.PilImage)
    buffer = BytesIO()
    img.save(buffer)
    return buffer
