import qrcode
import os

# Create a QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data('upi://pay?pa=example@upi&pn=John%20Doe&am=100.00')
qr.make(fit=True)

# Create an image from the QR Code
img = qr.make_image(fill_color="black", back_color="white")

# Save the image
output_path = os.path.join(os.path.dirname(__file__), "sample_qr.png")
img.save(output_path)

print(f"QR code saved to {output_path}") 