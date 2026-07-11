#!/usr/bin/env python3
"""Generate a professional QR code for SUS ENERGY contact page with embedded logo."""

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw, ImageFont
import os

# Config
URL = "https://susenergysl.com/pages/contact-us.html"
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets/images/sus-energy-logo.png")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "qr")
OUTPUT_PNG = os.path.join(OUTPUT_DIR, "sus-energy-qr.png")
OUTPUT_SVG = os.path.join(OUTPUT_DIR, "sus-energy-qr.svg")

# QR code styling
QR_SIZE = 1024
BOX_SIZE = 20
BORDER = 4
LOGO_SCALE = 0.22  # logo takes 22% of QR code width

# Colors — SUS ENERGY brand
FOREGROUND = (10, 10, 10)       # near-black for scannability
BACKGROUND = (255, 255, 255)    # white background
LOGO_BG = (255, 255, 255)       # white circle behind logo


def generate_qr():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Create QR code with high error correction (H = 30% recovery)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=BOX_SIZE,
        border=BORDER,
    )
    qr.add_data(URL)
    qr.make(fit=True)

    # Generate styled image with rounded modules
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(
            back_color=BACKGROUND,
            front_color=FOREGROUND,
        ),
    ).convert("RGBA")

    # Resize to target size
    img = img.resize((QR_SIZE, QR_SIZE), Image.LANCZOS)

    # Load and prepare logo
    logo = Image.open(LOGO_PATH).convert("RGBA")

    # Create circular logo with white background
    logo_size = int(QR_SIZE * LOGO_SCALE)
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

    # Create circular mask
    mask = Image.new("L", (logo_size, logo_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, logo_size - 1, logo_size - 1), fill=255)

    # White circle background behind logo for contrast
    circle_bg_size = logo_size + 16
    circle_bg = Image.new("RGBA", (circle_bg_size, circle_bg_size), (0, 0, 0, 0))
    circle_draw = ImageDraw.Draw(circle_bg)
    circle_draw.ellipse(
        (0, 0, circle_bg_size - 1, circle_bg_size - 1),
        fill=LOGO_BG + (255,),
    )

    # Paste white circle onto QR center
    center = (QR_SIZE - circle_bg_size) // 2
    img.paste(circle_bg, (center, center), circle_bg)

    # Paste logo with circular mask
    logo_center = (QR_SIZE - logo_size) // 2
    img.paste(logo, (logo_center, logo_center), mask)

    # Add subtle text below QR code
    final_height = QR_SIZE + 80
    final = Image.new("RGBA", (QR_SIZE, final_height), BACKGROUND + (255,))
    final.paste(img, (0, 0))

    draw = ImageDraw.Draw(final)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    except (OSError, IOError):
        font = ImageFont.load_default()

    text = "Scan to visit SUS ENERGY"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (QR_SIZE - text_width) // 2
    text_y = QR_SIZE + 20
    draw.text((text_x, text_y), text, fill=FOREGROUND, font=font)

    # Save as high-quality PNG
    final_rgb = final.convert("RGB")
    final_rgb.save(OUTPUT_PNG, "PNG", dpi=(300, 300))
    print(f"QR code saved: {OUTPUT_PNG}")

    # Also save a plain version without text (for embedding)
    plain = img.copy()
    plain_rgb = plain.convert("RGB")
    plain_path = os.path.join(OUTPUT_DIR, "sus-energy-qr-plain.png")
    plain_rgb.save(plain_path, "PNG", dpi=(300, 300))
    print(f"Plain QR saved: {plain_path}")

    return OUTPUT_PNG


if __name__ == "__main__":
    generate_qr()
