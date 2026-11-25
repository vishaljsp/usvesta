from django.core.management.base import BaseCommand
from django.conf import settings
from cloth_app.models import *   # <-- apne model ka naam daalo
from PIL import Image
import os
from django.core.files.base import ContentFile
from io import BytesIO


class Command(BaseCommand):
    help = "Convert old product images to WEBP and update database paths"

    def handle(self, *args, **kwargs):
        products = Product.objects.all()

        for product in products:
            if not product.product_image:
                continue

            old_path = product.product_image.path
            ext = old_path.lower().split('.')[-1]

            if ext not in ["jpg", "jpeg", "png"]:
                continue

            print(f"Converting: {old_path}")

            # Convert image to WebP
            img = Image.open(old_path).convert("RGB")
            buffer = BytesIO()
            img.save(buffer, "WEBP", quality=80)
            buffer.seek(0)

            # New filename
            new_name = product.product_image.name.rsplit(".", 1)[0] + ".webp"

            # Save new file
            product.product_image.save(new_name, ContentFile(buffer.read()), save=False)
            product.save()

            # Delete old file
            if os.path.exists(old_path):
                os.remove(old_path)

        print("🎉 All old product product_images successfully converted to WEBP!")
