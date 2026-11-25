from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
import os


def convert_to_webp(image_field, max_width=None, quality=92, method=6):
    if not image_field:
        return

    try:
        current_name = (getattr(image_field, "name", "") or "").lower()
        if current_name.endswith(".webp"):
            return

        # Ensure file pointer is at start
        if hasattr(image_field, "file") and hasattr(image_field.file, "seek"):
            image_field.file.seek(0)

        img = Image.open(image_field.file if hasattr(image_field, "file") else image_field)
        img = ImageOps.exif_transpose(img)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        if max_width and img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=quality, method=method)
        buffer.seek(0)

        base, _ = os.path.splitext(image_field.name)
        new_name = f"{base}.webp"

        image_field.save(new_name, ContentFile(buffer.read()), save=False)

    except Exception as e:
        print("WEBP conversion error:", e)