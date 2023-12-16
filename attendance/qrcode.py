import qrcode
from io import BytesIO
from django.core.files import File

def generate_qr_code():
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data('ATTENDANCE_QR')  # This is the text that will be encoded in the QR code
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    # You can save this image in your Django model or file system as needed
    return File(buffer, name='attendance_qr.png')